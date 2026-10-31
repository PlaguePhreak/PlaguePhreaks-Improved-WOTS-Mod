// Install / restore logic of the WOTS mod installer (no UI code here).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

namespace WotsInstaller
{
    public interface IUi
    {
        void Log(string line);
        bool Ask(string title, string question);   // Yes / No
        bool AskRisky(string title, string question); // Yes / No, No is the default button
        void Tell(string title, string text);
    }

    public class GameState
    {
        public string GameDir, DataDir, ManagedDir, DllPath, BackupDir, OverrideDir;
        public bool Installed;            // installed by this installer and DLL unchanged since
        public bool ManifestButChanged;   // installed by this installer, DLL changed since (game update?)
        public string InstalledVersion = "";
        public string GameModVersion = "";   // ModVersion.Current found in the game DLL
        public string Describe = "";
    }

    public class Installer
    {
        public const string BackupFolderName = "WOTS Mod Backup";
        public const string MarkerType = "ModVersion"; // class that only PlaguePhreak's mod has

        string modDir; // "Mod Files" next to the exe, or a downloaded release
        readonly IUi ui;
        public string ModName = "PlaguePhreak's Improved WOTS Mod";
        public string ModVersion = "";

        public Installer(string modDir, IUi ui)
        {
            this.ui = ui;
            SetSource(modDir);
        }

        public void SetSource(string dir)
        {
            modDir = dir;
            ModVersion = "";
            var info = Path.Combine(modDir, "mod_info.txt");
            if (File.Exists(info))
                foreach (var l in File.ReadAllLines(info))
                {
                    var i = l.IndexOf('=');
                    if (i < 0) continue;
                    var k = l.Substring(0, i).Trim().ToLowerInvariant(); var v = l.Substring(i + 1).Trim();
                    if (k == "name") ModName = v;
                    if (k == "version") ModVersion = v;
                }
        }

        public string ModDll { get { return Path.Combine(modDir, "Assembly-CSharp.dll"); } }
        // Mod Files\override (any capitalisation) mirrors the game's StreamingAssets\override
        public string ModOverride
        {
            get
            {
                if (Directory.Exists(modDir))
                    foreach (var d in Directory.GetDirectories(modDir))
                        if (string.Equals(Path.GetFileName(d), "override", StringComparison.OrdinalIgnoreCase)) return d;
                return Path.Combine(modDir, "override");
            }
        }

        // ------------------------------------------------------------ game folder
        public static bool IsGameDir(string dir)
        {
            return dir != null && File.Exists(Path.Combine(dir, "WarOnTheSea_Data", "Managed", "Assembly-CSharp.dll"));
        }

        public static string NormaliseGameDir(string picked)
        {
            if (string.IsNullOrEmpty(picked)) return null;
            var d = picked.TrimEnd('\\', '/');
            for (int i = 0; i < 4 && d != null; i++)
            {
                if (IsGameDir(d)) return d;
                d = Path.GetDirectoryName(d);
            }
            var sub = Path.Combine(picked, "War on the Sea");
            return IsGameDir(sub) ? sub : null;
        }

        public GameState Inspect(string gameDir)
        {
            var s = new GameState();
            s.GameDir = gameDir;
            s.DataDir = Path.Combine(gameDir, "WarOnTheSea_Data");
            s.ManagedDir = Path.Combine(s.DataDir, "Managed");
            s.DllPath = Path.Combine(s.ManagedDir, "Assembly-CSharp.dll");
            s.BackupDir = Path.Combine(gameDir, BackupFolderName);
            var sa = Path.Combine(s.DataDir, "StreamingAssets");
            s.OverrideDir = Path.Combine(sa, "override");
            if (Directory.Exists(sa))
                foreach (var d in Directory.GetDirectories(sa))
                    if (string.Equals(Path.GetFileName(d), "override", StringComparison.OrdinalIgnoreCase)) s.OverrideDir = d;
            var man = Manifest.Load(s.BackupDir);
            var cur = StockFp.FileMd5(s.DllPath);
            if (man != null)
            {
                s.InstalledVersion = man.Get("version");
                if (man.Get("installedMd5") == cur) { s.Installed = true; s.Describe = "Mod installed" + (s.InstalledVersion != "" ? " (" + s.InstalledVersion + ")" : "") + "."; }
                else { s.ManifestButChanged = true; s.Describe = "The mod was installed, but the game DLL has changed since (game update or another mod)."; }
            }
            else
            {
                var stock = LoadStock();
                if (stock != null && cur == stock.Md5) s.Describe = "Original game DLL (no DLL mods).";
                else if (HasMarker(s.DllPath)) s.Describe = "A copy of this mod was put in by hand (not with this installer).";
                else s.Describe = "Game DLL is modded by something else (another DLL mod?). The mod will be merged into it.";
            }
            var gv = DllVersion(s.DllPath);
            s.GameModVersion = gv ?? "";
            if (!string.IsNullOrEmpty(gv)) s.Describe += " Mod build in the game: " + gv + ".";
            return s;
        }

        // ModVersion.Current of a mod DLL (e.g. "0.32.19"), or null
        public static string DllVersion(string dll)
        {
            try
            {
                using (var m = ModuleDefinition.ReadModule(new MemoryStream(File.ReadAllBytes(dll))))
                {
                    var t = m.GetType(MarkerType);
                    if (t == null) return null;
                    foreach (var f in t.Fields) if (f.Name == "Current" && f.HasConstant) return f.Constant as string;
                    return "";
                }
            }
            catch { return null; }
        }

        // compares "0.32.19" style numbers; >0 when a is newer
        public static int CompareVersions(string a, string b)
        {
            var pa = (a ?? "").Split('.', ' ', '-'); var pb = (b ?? "").Split('.', ' ', '-');
            for (int i = 0; i < Math.Max(pa.Length, pb.Length); i++)
            {
                int x, y;
                bool nx = int.TryParse(i < pa.Length ? pa[i] : "0", out x), ny = int.TryParse(i < pb.Length ? pb[i] : "0", out y);
                if (!nx || !ny) { int c = string.CompareOrdinal(i < pa.Length ? pa[i] : "", i < pb.Length ? pb[i] : ""); if (c != 0) return c; continue; }
                if (x != y) return x.CompareTo(y);
            }
            return 0;
        }

        static bool HasMarker(string dll)
        {
            try
            {
                using (var m = ModuleDefinition.ReadModule(new MemoryStream(File.ReadAllBytes(dll))))
                    return m.GetType(MarkerType) != null;
            }
            catch { return false; }
        }

        StockFp stockCache;
        public StockFp LoadStock()
        {
            if (stockCache != null) return stockCache;
            var file = Path.Combine(modDir, "stock.fp");
            if (File.Exists(file)) { using (var r = new StreamReader(file)) stockCache = StockFp.Load(r); return stockCache; }
            var asm = typeof(Installer).Assembly;
            foreach (var n in asm.GetManifestResourceNames())
                if (n.EndsWith("stock.fp", StringComparison.OrdinalIgnoreCase))
                    using (var r = new StreamReader(asm.GetManifestResourceStream(n))) { stockCache = StockFp.Load(r); return stockCache; }
            return null;
        }

        ModuleDefinition ReadModule(string path, string managedDir)
        {
            var res = new DefaultAssemblyResolver();
            res.RemoveSearchDirectory(".");
            res.RemoveSearchDirectory("bin");
            res.AddSearchDirectory(managedDir);
            return ModuleDefinition.ReadModule(new MemoryStream(File.ReadAllBytes(path)),
                new ReaderParameters { AssemblyResolver = res, ReadingMode = ReadingMode.Immediate });
        }

        // ------------------------------------------------------------ install
        public bool Install(GameState s)
        {
            if (!File.Exists(ModDll)) { ui.Tell("Missing file", "Mod Files\\Assembly-CSharp.dll is missing next to the installer."); return false; }
            var stock = LoadStock();
            if (stock == null) { ui.Tell("Missing file", "The original-game fingerprint (stock.fp) is missing."); return false; }

            // never put an older build over a newer one without a clear warning
            var gameVer = DllVersion(s.DllPath);
            var newVer = DllVersion(ModDll);
            ui.Log("Mod build in your game: " + (string.IsNullOrEmpty(gameVer) ? "none" : gameVer) + ". Mod build in this installer: " + (string.IsNullOrEmpty(newVer) ? "?" : newVer) + ".");
            if (!string.IsNullOrEmpty(gameVer) && !string.IsNullOrEmpty(newVer))
            {
                int c = CompareVersions(gameVer, newVer);
                if (c > 0 && !ui.AskRisky("Your game has a NEWER build",
                        "Your game has mod build " + gameVer + ".\nThis installer has build " + newVer + ", which is OLDER.\n\n" +
                        "Yes = put the older build " + newVer + " in anyway (" + gameVer + " is kept in the backup and comes back with Restore).\n" +
                        "No = stop, nothing is changed."))
                { ui.Log("Stopped: the game already has a newer build."); return false; }
                if (c == 0) ui.Log("Same build as in your game: reinstalling it.");
            }

            Directory.CreateDirectory(s.BackupDir);
            var man = Manifest.Load(s.BackupDir);
            var backupDll = Path.Combine(s.BackupDir, "Assembly-CSharp.dll");
            var cur = StockFp.FileMd5(s.DllPath);
            bool firstInstall = man == null;

            // 1. decide the base DLL (the player's DLL without this mod)
            if (man != null && man.Get("installedMd5") == cur && File.Exists(backupDll))
            {
                ui.Log("Updating: the mod is merged again into your DLL from before the mod (backup).");
            }
            else
            {
                if (man != null)
                {
                    if (!ui.Ask("Game DLL changed", "The game DLL changed since the mod was installed (probably a game update or another mod).\n\nThe installer will treat the DLL you have now as the new original and back it up. Continue?"))
                        return false;
                }
                File.Copy(s.DllPath, backupDll, true);
                man = new Manifest();
                man.Set("backupMd5", cur);
                man.Set("backupDate", DateTime.Now.ToString("yyyy-MM-dd HH:mm"));
                ui.Log("Backed up your game DLL to " + backupDll);
            }
            var baseMd5 = StockFp.FileMd5(backupDll);

            // 2. build the new DLL
            var tmp = s.DllPath + ".new";
            if (baseMd5 == stock.Md5)
            {
                ui.Log("Your DLL is the original game DLL: copying the mod DLL as it is.");
                File.Copy(ModDll, tmp, true);
            }
            else if (HasMarker(backupDll))
            {
                if (!ui.Ask("Old copy of the mod found",
                    "Your game DLL already has a copy of this mod that was put in by hand, so it can't be merged again.\n\n" +
                    "Yes = replace it with this version (any other DLL mod in that file is lost).\n" +
                    "No = stop. (To start clean, use Steam > War on the Sea > Properties > Installed Files > Verify integrity, then run the installer again.)"))
                { CleanupFailed(s, man, firstInstall); return false; }
                File.Copy(ModDll, tmp, true);
                man.Set("replacedManualCopy", "yes");
            }
            else
            {
                ui.Log("Your DLL has other changes (another DLL mod or a different game version). Merging...");
                if (!Merge(backupDll, s, stock, tmp)) { CleanupFailed(s, man, firstInstall); return false; }
            }

            // 3. check the result loads, then swap it in
            try { using (var chk = ReadModule(tmp, s.ManagedDir)) { if (chk.GetType(MarkerType) == null) throw new Exception("mod classes missing"); } }
            catch (Exception e) { File.Delete(tmp); ui.Tell("Install failed", "The new DLL did not pass the check: " + e.Message + "\nNothing was changed."); CleanupFailed(s, man, firstInstall); return false; }
            File.Copy(tmp, s.DllPath, true);
            File.Delete(tmp);
            man.Set("installedMd5", StockFp.FileMd5(s.DllPath));
            man.Set("version", ModVersion);
            man.Set("installDate", DateTime.Now.ToString("yyyy-MM-dd HH:mm"));
            ui.Log("Installed Assembly-CSharp.dll into " + s.ManagedDir);

            // 4. Override files: first undo the previous install's files, then copy the new ones
            RestoreOverride(s, man);
            SnapshotOverride(s);
            InstallOverride(s, man);
            man.Save(s.BackupDir);
            ui.Log("Done. " + ModName + (ModVersion != "" ? " " + ModVersion : "") + " is installed.");
            return true;
        }

        void CleanupFailed(GameState s, Manifest man, bool firstInstall)
        {
            // first-time install that failed: leave no backup folder behind
            if (firstInstall)
            {
                try { Directory.Delete(s.BackupDir, true); } catch { }
            }
            else man.Save(s.BackupDir);
        }

        bool Merge(string baseDll, GameState s, StockFp stock, string outPath)
        {
            using (var target = ReadModule(baseDll, s.ManagedDir))
            using (var mod = ReadModule(ModDll, s.ManagedDir))
            {
                // how close is the player's DLL to the game version the mod was made for?
                int same = 0, total = 0;
                var tm = new Dictionary<string, TypeDefinition>();
                foreach (var t in Fp.AllTypes(target)) tm[t.FullName] = t;
                foreach (var kv in stock.Types)
                {
                    TypeDefinition t; tm.TryGetValue(kv.Key, out t);
                    var have = new Dictionary<string, string>();
                    if (t != null) foreach (var m in t.Methods) have[Fp.MethodKey(m)] = Fp.MethodHash(m);
                    foreach (var m in kv.Value.Methods) { total++; string h; if (have.TryGetValue(m.Key, out h) && h == m.Value) same++; }
                }
                double pct = total == 0 ? 0 : 100.0 * same / total;
                ui.Log(string.Format("Your DLL matches the original {0} in {1:0.0}% of game methods.", stock.Label, pct));
                if (pct < 90 && !ui.Ask("Different game version?",
                    string.Format("Only {0:0}% of your game DLL matches {1}, the version this mod was made for. Your game may be a different version.\n\nInstall anyway? (You can undo it with Restore.)", pct, stock.Label)))
                    return false;

                var mg = new Merger(target, mod, stock);
                var rep = mg.Plan();
                ui.Log("Plan: " + rep.Summary());
                foreach (var n in rep.Notes) ui.Log("  note: " + n);
                if (rep.Conflicts.Count > 0)
                {
                    foreach (var c in rep.Conflicts) ui.Log("  clash: " + c);
                    var sb = new StringBuilder();
                    sb.AppendLine(rep.Conflicts.Count + " place(s) were changed by both this mod and another mod:");
                    sb.AppendLine();
                    foreach (var c in rep.Conflicts.Take(12)) sb.AppendLine("- " + c);
                    if (rep.Conflicts.Count > 12) sb.AppendLine("- ... and " + (rep.Conflicts.Count - 12) + " more (see the log).");
                    sb.AppendLine();
                    sb.AppendLine("Yes = install anyway. This mod's version is used in those places, so the other mod's change there is lost (everything else of the other mod stays).");
                    sb.AppendLine("No = cancel, nothing is changed.");
                    if (!ui.Ask("Clash with another mod", sb.ToString())) return false;
                }
                mg.Apply();
                target.Write(outPath);
                ui.Log("Merged DLL written.");
                return true;
            }
        }

        // ------------------------------------------------------------ override files
        void InstallOverride(GameState s, Manifest man)
        {
            if (!Directory.Exists(ModOverride)) { ui.Log("No Override folder in Mod Files: only the DLL was installed."); return; }
            var created = new List<string>();
            var backedUp = new List<string>();
            var bakRoot = Path.Combine(s.BackupDir, "Override");
            var files = Directory.GetFiles(ModOverride, "*", SearchOption.AllDirectories);
            int n = 0, same = 0;
            foreach (var f in files)
            {
                var rel = f.Substring(ModOverride.Length).TrimStart('\\', '/');
                var dest = Path.Combine(s.OverrideDir, rel);
                Directory.CreateDirectory(Path.GetDirectoryName(dest));
                if (++n % 500 == 0) ui.Log("  checked " + n + " of " + files.Length + " files...");
                if (File.Exists(dest) && SameFile(f, dest)) { same++; continue; } // player already has this exact file: leave it alone
                if (File.Exists(dest))
                {
                    var bak = Path.Combine(bakRoot, rel);
                    Directory.CreateDirectory(Path.GetDirectoryName(bak));
                    File.Copy(dest, bak, true);
                    backedUp.Add(rel);
                }
                else created.Add(rel);
                File.Copy(f, dest, true);
            }
            File.WriteAllLines(Path.Combine(s.BackupDir, "override_created.txt"), created.ToArray());
            File.WriteAllLines(Path.Combine(s.BackupDir, "override_replaced.txt"), backedUp.ToArray());
            ui.Log(string.Format("Override: {0} files new, {1} replaced (originals saved in the backup), {2} already up to date.", created.Count, backedUp.Count, same));
        }

        public const string SnapshotName = "override before mod";

        // Full copy of the player's override folder, made once before the mod first touches it.
        void SnapshotOverride(GameState s)
        {
            var snap = Path.Combine(s.BackupDir, SnapshotName);
            if (Directory.Exists(snap) || !Directory.Exists(ModOverride)) return;
            if (!Directory.Exists(s.OverrideDir) || !Directory.EnumerateFiles(s.OverrideDir, "*", SearchOption.AllDirectories).Any())
            {
                Directory.CreateDirectory(snap); // empty marker: there was nothing to keep
                return;
            }
            ui.Log("You already have an override folder: saving a full copy of it first...");
            var files = Directory.GetFiles(s.OverrideDir, "*", SearchOption.AllDirectories);
            int n = 0;
            foreach (var f in files)
            {
                var dest = Path.Combine(snap, f.Substring(s.OverrideDir.Length).TrimStart('\\', '/'));
                Directory.CreateDirectory(Path.GetDirectoryName(dest));
                File.Copy(f, dest, true);
                if (++n % 1000 == 0) ui.Log("  saved " + n + " of " + files.Length + " files...");
            }
            ui.Log("Saved a copy of your override folder (" + files.Length + " files) in " + snap);
        }

        // After Restore: make sure every file of the saved copy is back exactly as it was.
        void RestoreSnapshot(GameState s)
        {
            var snap = Path.Combine(s.BackupDir, SnapshotName);
            if (!Directory.Exists(snap)) return;
            int fixedN = 0;
            foreach (var f in Directory.GetFiles(snap, "*", SearchOption.AllDirectories))
            {
                var dest = Path.Combine(s.OverrideDir, f.Substring(snap.Length).TrimStart('\\', '/'));
                if (File.Exists(dest) && SameFile(f, dest)) continue;
                Directory.CreateDirectory(Path.GetDirectoryName(dest));
                File.Copy(f, dest, true);
                fixedN++;
            }
            if (fixedN > 0) ui.Log("Put back " + fixedN + " more files from the saved copy of your override folder.");
            ui.Log("Your override folder is back as it was before the mod.");
        }

        static bool SameFile(string a, string b)
        {
            var fa = new FileInfo(a); var fb = new FileInfo(b);
            if (fa.Length != fb.Length) return false;
            using (var sa = fa.OpenRead()) using (var sb = fb.OpenRead())
            {
                var ba = new byte[65536]; var bb = new byte[65536];
                while (true)
                {
                    int ra = sa.Read(ba, 0, ba.Length);
                    int rb = sb.Read(bb, 0, ra);
                    if (ra != rb) return false;
                    if (ra == 0) return true;
                    for (int i = 0; i < ra; i++) if (ba[i] != bb[i]) return false;
                }
            }
        }

        void RestoreOverride(GameState s, Manifest man)
        {
            var createdList = Path.Combine(s.BackupDir, "override_created.txt");
            var replacedList = Path.Combine(s.BackupDir, "override_replaced.txt");
            var bakRoot = Path.Combine(s.BackupDir, "Override");
            int del = 0, back = 0;
            var dirs = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            if (File.Exists(createdList))
                foreach (var rel in File.ReadAllLines(createdList))
                {
                    if (rel.Trim() == "") continue;
                    var p = Path.Combine(s.OverrideDir, rel);
                    if (File.Exists(p)) { File.Delete(p); del++; }
                    dirs.Add(Path.GetDirectoryName(p));
                }
            if (File.Exists(replacedList))
                foreach (var rel in File.ReadAllLines(replacedList))
                {
                    if (rel.Trim() == "") continue;
                    var bak = Path.Combine(bakRoot, rel);
                    if (!File.Exists(bak)) continue;
                    var p = Path.Combine(s.OverrideDir, rel);
                    Directory.CreateDirectory(Path.GetDirectoryName(p));
                    File.Copy(bak, p, true);
                    back++;
                }
            // remove folders the mod created that are now empty
            foreach (var d in dirs.OrderByDescending(x => x.Length))
            {
                var cur = d;
                while (cur != null && cur.Length > s.OverrideDir.Length && Directory.Exists(cur) && !Directory.EnumerateFileSystemEntries(cur).Any())
                {
                    Directory.Delete(cur);
                    cur = Path.GetDirectoryName(cur);
                }
            }
            if (Directory.Exists(bakRoot)) Directory.Delete(bakRoot, true);
            if (File.Exists(createdList)) File.Delete(createdList);
            if (File.Exists(replacedList)) File.Delete(replacedList);
            if (del + back > 0) ui.Log(string.Format("Override: removed {0} mod files, put back {1} original files.", del, back));
        }

        // ------------------------------------------------------------ restore
        public bool Restore(GameState s)
        {
            var man = Manifest.Load(s.BackupDir);
            var backupDll = Path.Combine(s.BackupDir, "Assembly-CSharp.dll");
            if (man == null || !File.Exists(backupDll))
            {
                ui.Tell("Nothing to restore", "There is no backup from this installer in " + s.BackupDir + ".\n\nTo get the original game files back, use Steam > War on the Sea > Properties > Installed Files > Verify integrity of game files.");
                return false;
            }
            if (man.Get("installedMd5") != StockFp.FileMd5(s.DllPath))
            {
                if (!ui.Ask("Game DLL changed", "The game DLL has changed since the mod was installed (a game update or another mod).\n\nRestoring puts back the DLL from before the mod, which may be older. If the game was updated, Steam's 'Verify integrity of game files' is the better choice.\n\nRestore anyway?"))
                    return false;
            }
            File.Copy(backupDll, s.DllPath, true);
            ui.Log("Put back your original Assembly-CSharp.dll.");
            RestoreOverride(s, man);
            RestoreSnapshot(s);
            Directory.Delete(s.BackupDir, true);
            ui.Log("Restore finished. The game is back to how it was before the mod.");
            return true;
        }
    }

    // key=value file in the backup folder
    public class Manifest
    {
        readonly Dictionary<string, string> v = new Dictionary<string, string>();
        public string Get(string k) { string x; return v.TryGetValue(k, out x) ? x : ""; }
        public void Set(string k, string x) { v[k] = x ?? ""; }
        public static Manifest Load(string dir)
        {
            var f = Path.Combine(dir, "install.txt");
            if (!File.Exists(f)) return null;
            var m = new Manifest();
            foreach (var l in File.ReadAllLines(f))
            {
                var i = l.IndexOf('=');
                if (i > 0) m.v[l.Substring(0, i)] = l.Substring(i + 1);
            }
            return m;
        }
        public void Save(string dir)
        {
            Directory.CreateDirectory(dir);
            var lines = new List<string> { "# Written by the WOTS mod installer. Do not edit; delete this folder only after Restore." };
            foreach (var kv in v) lines.Add(kv.Key + "=" + kv.Value);
            File.WriteAllLines(Path.Combine(dir, "install.txt"), lines.ToArray());
        }
    }
}
