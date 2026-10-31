// Downloads mod releases from GitHub Releases.
// A release needs the asset "Assembly-CSharp.dll". Override files come from the newest release
// (this one or an older one) that has "override.zip", plus every "override_update.zip" in the
// releases after it, applied oldest first. So the big override.zip is uploaded only when the art changes.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Web.Script.Serialization;

namespace WotsInstaller
{
    public class ReleaseAsset { public long Id, Size; public string Name, Url; }

    public class Release
    {
        public string Tag, Name, Date, Notes;
        public bool Prerelease;
        public List<ReleaseAsset> Assets = new List<ReleaseAsset>();
        public ReleaseAsset Asset(string name)
        {
            return Assets.FirstOrDefault(a => string.Equals(a.Name, name, StringComparison.OrdinalIgnoreCase));
        }
        public string Label { get { return string.IsNullOrEmpty(Name) ? Tag : Name; } }
    }

    public class Updater
    {
        public const string DefaultRepo = "PlaguePhreak/PlaguePhreaks-Improved-WOTS-Mod";
        public const string DllAsset = "Assembly-CSharp.dll", OverrideAsset = "override.zip", OverrideUpdateAsset = "override_update.zip";

        public string Repo = DefaultRepo;
        public string ApiBase = "https://api.github.com";
        public string CacheDir;
        readonly IUi ui;

        public Updater(IUi ui, string cacheDir)
        {
            this.ui = ui;
            CacheDir = cacheDir;
            try { ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls12; } catch { }
        }

        WebClient Client()
        {
            var w = new WebClient();
            w.Headers[HttpRequestHeader.UserAgent] = "WOTS-Mod-Installer";
            return w;
        }

        // newest first; drafts skipped; only releases that carry the DLL
        public List<Release> GetReleases()
        {
            string json;
            using (var w = Client())
            {
                w.Headers[HttpRequestHeader.Accept] = "application/vnd.github+json";
                json = w.DownloadString(ApiBase + "/repos/" + Repo + "/releases?per_page=50");
            }
            var list = new List<Release>();
            var arr = new JavaScriptSerializer { MaxJsonLength = int.MaxValue }.DeserializeObject(json) as object[];
            if (arr == null) return list;
            foreach (var o in arr)
            {
                var d = o as Dictionary<string, object>;
                if (d == null || true.Equals(Get(d, "draft"))) continue;
                var r = new Release
                {
                    Tag = Get(d, "tag_name") as string,
                    Name = Get(d, "name") as string,
                    Date = Get(d, "published_at") as string ?? "",
                    Notes = Get(d, "body") as string ?? "",
                    Prerelease = true.Equals(Get(d, "prerelease"))
                };
                var assets = Get(d, "assets") as object[];
                if (assets != null)
                    foreach (var ao in assets)
                    {
                        var a = ao as Dictionary<string, object>;
                        if (a == null) continue;
                        r.Assets.Add(new ReleaseAsset
                        {
                            Id = Convert.ToInt64(Get(a, "id") ?? 0),
                            Size = Convert.ToInt64(Get(a, "size") ?? 0),
                            Name = Get(a, "name") as string,
                            Url = Get(a, "browser_download_url") as string
                        });
                    }
                list.Add(r);
            }
            list.Sort((a, b) => string.CompareOrdinal(b.Date, a.Date));
            return list;
        }

        static object Get(Dictionary<string, object> d, string k) { object v; return d.TryGetValue(k, out v) ? v : null; }

        public static Release Latest(List<Release> all)
        {
            return all.FirstOrDefault(r => r.Asset(DllAsset) != null);
        }

        // Downloads (or reuses) everything for this release and lays it out like "Mod Files". Returns that folder.
        public string Prepare(Release rel, List<Release> all, string modName)
        {
            var idx = all.IndexOf(rel);
            var older = all.Skip(idx).ToList(); // rel and everything older, newest first
            var baseRel = older.FirstOrDefault(r => r.Asset(OverrideAsset) != null);
            var updates = new List<ReleaseAsset>();
            foreach (var r in older)
            {
                if (r == baseRel) break;
                var u = r.Asset(OverrideUpdateAsset);
                if (u != null) updates.Add(u);
            }
            updates.Reverse(); // oldest first

            var key = Safe(rel.Tag) + "_" + rel.Asset(DllAsset).Id;
            var build = Path.Combine(Path.Combine(CacheDir, "builds"), key);
            if (File.Exists(Path.Combine(build, "ready.txt")))
            {
                ui.Log("Using the files already downloaded for " + rel.Label + ".");
                return build;
            }
            if (Directory.Exists(build)) Directory.Delete(build, true);
            Directory.CreateDirectory(build);

            var dll = Download(rel.Asset(DllAsset));
            File.Copy(dll, Path.Combine(build, "Assembly-CSharp.dll"), true);
            File.WriteAllLines(Path.Combine(build, "mod_info.txt"), new[] { "name=" + modName, "version=" + rel.Label });

            var ov = Path.Combine(build, "override");
            if (baseRel != null)
            {
                var zip = Download(baseRel.Asset(OverrideAsset));
                ui.Log("Unpacking " + OverrideAsset + " from " + baseRel.Label + "...");
                Extract(zip, ov);
            }
            foreach (var u in updates)
            {
                var zip = Download(u);
                ui.Log("Unpacking " + u.Name + "...");
                Extract(zip, ov);
            }
            if (baseRel == null && updates.Count == 0) ui.Log("This release has no override files: only the DLL will be installed.");
            File.WriteAllText(Path.Combine(build, "ready.txt"), DateTime.Now.ToString("s"));

            // keep only this build's folder to save disk space
            foreach (var d in Directory.GetDirectories(Path.Combine(CacheDir, "builds")))
                if (!string.Equals(d, build, StringComparison.OrdinalIgnoreCase)) try { Directory.Delete(d, true); } catch { }
            return build;
        }

        static string Safe(string s)
        {
            foreach (var c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s;
        }

        string Download(ReleaseAsset a)
        {
            var dir = Path.Combine(CacheDir, "downloads");
            Directory.CreateDirectory(dir);
            var path = Path.Combine(dir, a.Id + "_" + Safe(a.Name));
            if (File.Exists(path) && new FileInfo(path).Length == a.Size)
            {
                ui.Log("Already downloaded: " + a.Name);
                return path;
            }
            ui.Log(string.Format("Downloading {0} ({1:0.0} MB)...", a.Name, a.Size / 1048576.0));
            var part = path + ".part";
            var req = (HttpWebRequest)WebRequest.Create(a.Url);
            req.UserAgent = "WOTS-Mod-Installer";
            req.AllowAutoRedirect = true;
            using (var resp = req.GetResponse())
            using (var src = resp.GetResponseStream())
            using (var dst = File.Create(part))
            {
                var buf = new byte[1 << 16];
                long done = 0; int lastPct = -10; int n;
                while ((n = src.Read(buf, 0, buf.Length)) > 0)
                {
                    dst.Write(buf, 0, n);
                    done += n;
                    if (a.Size > 0)
                    {
                        int pct = (int)(done * 100 / a.Size);
                        if (pct >= lastPct + 10) { lastPct = pct - pct % 10; ui.Log("  " + lastPct + "%"); }
                    }
                }
            }
            if (a.Size > 0 && new FileInfo(part).Length != a.Size) { File.Delete(part); throw new IOException("Download of " + a.Name + " was cut off. Try again."); }
            if (File.Exists(path)) File.Delete(path);
            File.Move(part, path);
            // drop older downloads with the same name
            foreach (var f in Directory.GetFiles(dir, "*_" + Safe(a.Name)))
                if (!string.Equals(f, path, StringComparison.OrdinalIgnoreCase)) try { File.Delete(f); } catch { }
            return path;
        }

        // Extracts over 'dest'. If every entry sits in a top folder called "override", that folder is stripped.
        static void Extract(string zip, string dest)
        {
            using (var z = ZipFile.OpenRead(zip))
            {
                var files = z.Entries.Where(e => e.Name.Length > 0).ToList();
                bool strip = files.Count > 0 && files.All(e => e.FullName.Replace('\\', '/').StartsWith("override/", StringComparison.OrdinalIgnoreCase));
                var root = Path.GetFullPath(dest);
                foreach (var e in files)
                {
                    var rel = e.FullName.Replace('\\', '/');
                    if (strip) rel = rel.Substring("override/".Length);
                    var target = Path.GetFullPath(Path.Combine(root, rel.Replace('/', Path.DirectorySeparatorChar)));
                    if (!target.StartsWith(root, StringComparison.OrdinalIgnoreCase)) continue; // no ../ tricks
                    Directory.CreateDirectory(Path.GetDirectoryName(target));
                    e.ExtractToFile(target, true);
                }
            }
        }
    }
}
