// Window of the WOTS mod installer.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace WotsInstaller
{
    public class MainForm : Form, IUi
    {
        readonly Installer inst;
        readonly TextBox pathBox = new TextBox();
        readonly Label stateLabel = new Label();
        readonly TextBox logBox = new TextBox();
        readonly Button zipBtn = new Button(), installBtn = new Button(), restoreBtn = new Button(), browseBtn = new Button(), closeBtn = new Button(), localBtn = new Button();
        readonly Label onlineLabel = new Label();
        readonly string exeDir, localDir;
        readonly Updater updater;
        readonly bool hasLocal;
        List<Release> releases;
        GameState state;
        bool busy;

        public MainForm(string startPath)
        {
            exeDir = AppDomain.CurrentDomain.BaseDirectory;
            localDir = Path.Combine(exeDir, "Mod Files");
            hasLocal = File.Exists(Path.Combine(localDir, "Assembly-CSharp.dll"));
            inst = new Installer(localDir, this);
            var cache = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WOTS Mod Installer");
            updater = new Updater(this, cache);
            var src = Path.Combine(exeDir, "update_source.txt");
            if (File.Exists(src))
                foreach (var l in File.ReadAllLines(src))
                {
                    var i = l.IndexOf('='); if (i < 0) continue;
                    var k = l.Substring(0, i).Trim().ToLowerInvariant(); var v = l.Substring(i + 1).Trim();
                    if (k == "repo") updater.Repo = v;
                    if (k == "api") updater.ApiBase = v.TrimEnd('/');
                }

            Text = inst.ModName + " - Installer";
            ClientSize = new Size(720, 470);
            ClientSize = new Size(720, 490);
            MinimumSize = new Size(600, 400);
            Font = new Font("Segoe UI", 9f);
            StartPosition = FormStartPosition.CenterScreen;

            var title = new Label { Text = inst.ModName, Font = new Font("Segoe UI", 13f, FontStyle.Bold), AutoSize = true, Location = new Point(12, 10) };
            var pl = new Label { Text = "War on the Sea folder:", AutoSize = true, Location = new Point(12, 50) };
            pathBox.SetBounds(12, 70, 600, 24); pathBox.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            pathBox.Leave += (s, e) => Check(pathBox.Text);
            browseBtn.Text = "Browse..."; browseBtn.SetBounds(620, 69, 88, 26); browseBtn.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            browseBtn.Click += (s, e) => Browse();
            stateLabel.SetBounds(12, 102, 696, 36); stateLabel.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            onlineLabel.SetBounds(12, 138, 530, 20); onlineLabel.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            onlineLabel.Text = "Checking for the newest version online...";
            installBtn.Text = "Install / update"; installBtn.SetBounds(12, 162, 170, 34);
            installBtn.Click += (s, e) => Run(Job.Online);
            localBtn.Text = "Install from Mod Files"; localBtn.SetBounds(190, 162, 170, 34);
            localBtn.Click += (s, e) => Run(Job.Local);
            localBtn.Visible = hasLocal;
            zipBtn.Text = "Make GitHub upload zips"; zipBtn.SetBounds(546, 132, 162, 26); zipBtn.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            zipBtn.Visible = hasLocal; // only in the author's copy (players have no Mod Files folder)
            zipBtn.Click += (s, e) => MakeZips();
            restoreBtn.Text = "Restore original files"; restoreBtn.SetBounds(hasLocal ? 368 : 190, 162, 170, 34);
            restoreBtn.Click += (s, e) => Run(Job.Restore);
            closeBtn.Text = "Close"; closeBtn.SetBounds(620, 162, 88, 34); closeBtn.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            closeBtn.Click += (s, e) => Close();
            logBox.Multiline = true; logBox.ReadOnly = true; logBox.ScrollBars = ScrollBars.Vertical; logBox.WordWrap = true;
            logBox.SetBounds(12, 206, 696, 252); logBox.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            logBox.BackColor = Color.White;
            Controls.AddRange(new Control[] { zipBtn, title, pl, pathBox, browseBtn, stateLabel, onlineLabel, installBtn, localBtn, restoreBtn, closeBtn, logBox });

            Log(inst.ModName + " installer.");
            if (hasLocal) Log("Mod Files folder found next to the installer: " + (inst.ModVersion != "" ? inst.ModVersion : "version not set") + ".");
            var stock = SafeStock();
            if (stock != null) Log("Made for: " + stock.Label + ".");
            Log("The installer backs up your files first. 'Restore original files' undoes everything.");
            Log("");

            var found = startPath ?? LoadLastPath() ?? GameFinder.Find();
            if (found != null) { pathBox.Text = found; Check(found); }
            else { stateLabel.Text = "Could not find War on the Sea automatically. Click Browse and pick the game folder."; SetButtons(false); }
            CheckOnline();
        }

        enum Job { Online, Local, Restore }

        // Author tool: packs the game's override folder into zips under 2 GB for a GitHub release.
        void MakeZips()
        {
            if (state == null || busy) return;
            var outDir = Path.Combine(exeDir, "Release upload");
            if (!Ask("Make upload zips", "This takes your game's override folder\n" + state.OverrideDir + "\nleaves out files that are the same as the base game's, and puts the rest in\n" + outDir + "\nas a folder plus zips under 2 GB each (for the GitHub release).\n\nIt can take a while and needs free space for two copies of the mod files. Go?")) return;
            busy = true; zipBtn.Enabled = installBtn.Enabled = localBtn.Enabled = restoreBtn.Enabled = false;
            var ovDir = state.OverrideDir;
            var t = new Thread(() =>
            {
                try
                {
                    Log(""); Log("---- Making GitHub upload zips ----");
                    long lim = 1800L * 1024 * 1024; long mb;
                    if (long.TryParse(Environment.GetEnvironmentVariable("WOTS_ZIP_LIMIT_KB") ?? "", out mb)) lim = mb * 1024;
                    var defDir = Path.Combine(Path.GetDirectoryName(ovDir), "default");
                    var made = Updater.MakeUploadZips(ovDir, defDir, outDir, this, lim);
                    var dll = Path.Combine(localDir, "Assembly-CSharp.dll");
                    if (File.Exists(dll)) File.Copy(dll, Path.Combine(outDir, "Assembly-CSharp.dll"), true);
                    File.Copy(Application.ExecutablePath, Path.Combine(outDir, "WOTS Mod Installer.exe"), true);
                    Log("Done. Upload everything in '" + outDir + "' to the GitHub release (" + made.Count + " zips + DLL + installer).");
                    try { Process.Start("explorer.exe", "\"" + outDir + "\""); } catch { }
                }
                catch (Exception e) { Log("ERROR: " + e.Message); Tell("Could not make the zips", e.Message); }
                BeginInvoke((Action)(() => { busy = false; zipBtn.Enabled = true; Check(state.GameDir); }));
            });
            t.IsBackground = true; t.Start();
        }

        void CheckOnline()
        {
            var t = new Thread(() =>
            {
                string text;
                try
                {
                    var all = updater.GetReleases();
                    var latest = Updater.Latest(all);
                    releases = all;
                    if (latest == null) text = "No release online yet." + (hasLocal ? " Use 'Install from Mod Files'." : "");
                    else
                    {
                        text = "Newest version online: " + latest.Label + (latest.Date.Length >= 10 ? " (" + latest.Date.Substring(0, 10) + ")" : "");
                        if (state != null && state.Installed && state.InstalledVersion == latest.Label) text += ". You have it.";
                    }
                }
                catch (Exception e) { releases = null; text = "Could not reach GitHub (" + e.Message + ")." + (hasLocal ? " 'Install from Mod Files' still works." : ""); }
                BeginInvoke((Action)(() => { onlineLabel.Text = text; if (state != null && !busy) SetButtons(true); }));
            });
            t.IsBackground = true;
            t.Start();
        }

        StockFp SafeStock() { try { return inst.LoadStock(); } catch (Exception e) { Log("Fingerprint error: " + e.Message); return null; } }

        void Browse()
        {
            using (var d = new FolderBrowserDialog { Description = "Pick the War on the Sea folder (the one with WarOnTheSea.exe)" })
            {
                if (Directory.Exists(pathBox.Text)) d.SelectedPath = pathBox.Text;
                if (d.ShowDialog(this) == DialogResult.OK) { pathBox.Text = d.SelectedPath; Check(d.SelectedPath); }
            }
        }

        void Check(string picked)
        {
            var dir = Installer.NormaliseGameDir(picked);
            if (dir == null)
            {
                state = null;
                stateLabel.Text = "That folder is not War on the Sea (no WarOnTheSea_Data\\Managed\\Assembly-CSharp.dll in it).";
                SetButtons(false);
                return;
            }
            pathBox.Text = dir;
            try { state = inst.Inspect(dir); }
            catch (Exception e) { state = null; stateLabel.Text = "Could not read the game files: " + e.Message; SetButtons(false); return; }
            stateLabel.Text = "Found the game. " + state.Describe;
            installBtn.Text = state.Installed ? "Update from internet" : "Install from internet";
            SetButtons(true);
            SaveLastPath(dir);
        }

        void SetButtons(bool on)
        {
            var latest = releases == null ? null : Updater.Latest(releases);
            installBtn.Enabled = on && latest != null;
            localBtn.Enabled = on && hasLocal;
            restoreBtn.Enabled = on && state != null && (state.Installed || state.ManifestButChanged);
            browseBtn.Enabled = true;
        }

        void Run(Job job)
        {
            if (state == null) return;
            if (GameRunning()) { Tell("Game is running", "Close War on the Sea first, then try again."); return; }
            if (!CanWrite(state.ManagedDir) || !CanWrite(state.GameDir))
            {
                if (Ask("Administrator rights needed", "Windows needs administrator rights to change files in the game folder.\n\nRestart the installer as administrator?"))
                {
                    try
                    {
                        Process.Start(new ProcessStartInfo(Application.ExecutablePath, "\"" + state.GameDir + "\"") { Verb = "runas", UseShellExecute = true });
                        Close();
                    }
                    catch { }
                }
                return;
            }
            installBtn.Enabled = localBtn.Enabled = restoreBtn.Enabled = browseBtn.Enabled = closeBtn.Enabled = false;
            busy = true;
            var s = state;
            var t = new Thread(() =>
            {
                try
                {
                    Log("");
                    if (job == Job.Restore) { Log("---- Restoring ----"); inst.Restore(s); }
                    else if (job == Job.Local) { Log("---- Installing from Mod Files ----"); inst.SetSource(localDir); inst.Install(s); }
                    else
                    {
                        Log("---- Installing from the internet ----");
                        var all = updater.GetReleases();
                        releases = all;
                        var latest = Updater.Latest(all);
                        if (latest == null) Tell("No release", "There is no release online yet.");
                        else
                        {
                            Log("Newest release: " + latest.Label);
                            var dir = updater.Prepare(latest, all, inst.ModName);
                            inst.SetSource(dir);
                            inst.Install(s);
                            inst.SetSource(localDir);
                            try { Directory.Delete(dir, true); } catch { } // the unpacked copy; downloads stay cached
                        }
                    }
                }
                catch (Exception e)
                {
                    Log("ERROR: " + e);
                    Tell("Something went wrong", e.Message + "\n\nYour backup is in the '" + Installer.BackupFolderName + "' folder inside the game folder. Send the text in the log window to the mod author.");
                }
                inst.SetSource(localDir);
                BeginInvoke((Action)(() => { busy = false; closeBtn.Enabled = true; Check(s.GameDir); CheckOnline(); }));
            });
            t.IsBackground = true;
            t.Start();
        }

        static bool GameRunning()
        {
            try { return Process.GetProcessesByName("WarOnTheSea").Length > 0; } catch { return false; }
        }

        static bool CanWrite(string dir)
        {
            try
            {
                var f = Path.Combine(dir, "wots_installer_write_test.tmp");
                File.WriteAllText(f, "x");
                File.Delete(f);
                return true;
            }
            catch { return false; }
        }

        string SettingsFile { get { return Path.Combine(exeDir, "installer_last_game_folder.txt"); } }
        string LoadLastPath()
        {
            try { var p = File.ReadAllText(SettingsFile).Trim(); return Installer.IsGameDir(p) ? p : null; } catch { return null; }
        }
        void SaveLastPath(string p) { try { File.WriteAllText(SettingsFile, p); } catch { } }

        // ---------------------------------------------------------------- IUi (thread safe)
        public void Log(string line)
        {
            if (InvokeRequired) { BeginInvoke((Action)(() => Log(line))); return; }
            logBox.AppendText(line + Environment.NewLine);
        }

        public bool Ask(string title, string question)
        {
            if (InvokeRequired) return (bool)Invoke((Func<bool>)(() => Ask(title, question)));
            return MessageBox.Show(this, question, title, MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes;
        }

        public bool AskRisky(string title, string question)
        {
            if (InvokeRequired) return (bool)Invoke((Func<bool>)(() => AskRisky(title, question)));
            return MessageBox.Show(this, question, title, MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button2) == DialogResult.Yes;
        }

        public void Tell(string title, string text)
        {
            if (InvokeRequired) { Invoke((Action)(() => Tell(title, text))); return; }
            MessageBox.Show(this, text, title, MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }

    // Finds War on the Sea in the Steam libraries.
    public static class GameFinder
    {
        public static string Find()
        {
            foreach (var lib in SteamLibraries())
            {
                var d = Path.Combine(Path.Combine(Path.Combine(lib, "steamapps"), "common"), "War on the Sea");
                if (Installer.IsGameDir(d)) return d;
            }
            // common non-Steam spots
            foreach (var drive in SafeDrives())
                foreach (var rel in new[] { @"SteamLibrary\steamapps\common\War on the Sea", @"Steam\steamapps\common\War on the Sea", @"Games\War on the Sea", @"GOG Games\War on the Sea", @"War on the Sea" })
                {
                    var d = Path.Combine(drive, rel);
                    if (Installer.IsGameDir(d)) return d;
                }
            return null;
        }

        static IEnumerable<string> SafeDrives()
        {
            DriveInfo[] all;
            try { all = DriveInfo.GetDrives(); } catch { yield break; }
            foreach (var d in all)
            {
                bool ok;
                try { ok = d.DriveType == DriveType.Fixed && d.IsReady; } catch { ok = false; }
                if (ok) yield return d.RootDirectory.FullName;
            }
        }

        static IEnumerable<string> SteamLibraries()
        {
            var roots = new List<string>();
            AddReg(roots, Registry.CurrentUser, @"Software\Valve\Steam", "SteamPath");
            AddReg(roots, Registry.LocalMachine, @"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath");
            AddReg(roots, Registry.LocalMachine, @"SOFTWARE\Valve\Steam", "InstallPath");
            roots.Add(@"C:\Program Files (x86)\Steam");
            var libs = new List<string>();
            foreach (var r in roots)
            {
                if (!Directory.Exists(r)) continue;
                if (!libs.Contains(r)) libs.Add(r);
                var vdf = Path.Combine(Path.Combine(r, "steamapps"), "libraryfolders.vdf");
                if (!File.Exists(vdf)) continue;
                try
                {
                    foreach (var line in File.ReadAllLines(vdf))
                    {
                        // "path"		"E:\\SteamLibrary"   (new format)  or  "1"  "E:\\SteamLibrary" (old format)
                        var parts = line.Split('"');
                        if (parts.Length < 5) continue;
                        var key = parts[1]; var val = parts[3].Replace(@"\\", @"\");
                        int dummy;
                        if ((key == "path" || int.TryParse(key, out dummy)) && Directory.Exists(val) && !libs.Contains(val)) libs.Add(val);
                    }
                }
                catch { }
            }
            return libs;
        }

        static void AddReg(List<string> list, RegistryKey hive, string key, string name)
        {
            try
            {
                using (var k = hive.OpenSubKey(key))
                {
                    var v = k == null ? null : k.GetValue(name) as string;
                    if (!string.IsNullOrEmpty(v)) list.Add(v.Replace('/', '\\'));
                }
            }
            catch { }
        }
    }
}
