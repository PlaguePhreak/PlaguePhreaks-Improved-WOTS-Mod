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
        readonly Button installBtn = new Button(), restoreBtn = new Button(), browseBtn = new Button(), closeBtn = new Button();
        readonly string exeDir;
        GameState state;

        public MainForm(string startPath)
        {
            exeDir = AppDomain.CurrentDomain.BaseDirectory;
            inst = new Installer(Path.Combine(exeDir, "Mod Files"), this);

            Text = inst.ModName + " - Installer";
            ClientSize = new Size(720, 470);
            MinimumSize = new Size(600, 400);
            Font = new Font("Segoe UI", 9f);
            StartPosition = FormStartPosition.CenterScreen;

            var title = new Label { Text = inst.ModName + (inst.ModVersion != "" ? "  " + inst.ModVersion : ""), Font = new Font("Segoe UI", 13f, FontStyle.Bold), AutoSize = true, Location = new Point(12, 10) };
            var pl = new Label { Text = "War on the Sea folder:", AutoSize = true, Location = new Point(12, 50) };
            pathBox.SetBounds(12, 70, 600, 24); pathBox.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            pathBox.Leave += (s, e) => Check(pathBox.Text);
            browseBtn.Text = "Browse..."; browseBtn.SetBounds(620, 69, 88, 26); browseBtn.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            browseBtn.Click += (s, e) => Browse();
            stateLabel.SetBounds(12, 102, 696, 36); stateLabel.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            installBtn.Text = "Install mod"; installBtn.SetBounds(12, 140, 160, 34);
            installBtn.Click += (s, e) => Run(true);
            restoreBtn.Text = "Restore original files"; restoreBtn.SetBounds(180, 140, 180, 34);
            restoreBtn.Click += (s, e) => Run(false);
            closeBtn.Text = "Close"; closeBtn.SetBounds(620, 140, 88, 34); closeBtn.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            closeBtn.Click += (s, e) => Close();
            logBox.Multiline = true; logBox.ReadOnly = true; logBox.ScrollBars = ScrollBars.Vertical; logBox.WordWrap = true;
            logBox.SetBounds(12, 184, 696, 274); logBox.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            logBox.BackColor = Color.White;
            Controls.AddRange(new Control[] { title, pl, pathBox, browseBtn, stateLabel, installBtn, restoreBtn, closeBtn, logBox });

            Log(inst.ModName + (inst.ModVersion != "" ? " " + inst.ModVersion : "") + " installer.");
            var stock = SafeStock();
            if (stock != null) Log("Made for: " + stock.Label + ".");
            Log("The installer backs up your files first. 'Restore original files' undoes everything.");
            Log("");

            var found = startPath ?? LoadLastPath() ?? GameFinder.Find();
            if (found != null) { pathBox.Text = found; Check(found); }
            else { stateLabel.Text = "Could not find War on the Sea automatically. Click Browse and pick the game folder."; SetButtons(false); }
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
            installBtn.Text = state.Installed ? "Update / reinstall mod" : "Install mod";
            SetButtons(true);
            restoreBtn.Enabled = state.Installed || state.ManifestButChanged;
            SaveLastPath(dir);
        }

        void SetButtons(bool on) { installBtn.Enabled = on; restoreBtn.Enabled = on; browseBtn.Enabled = true; }

        void Run(bool install)
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
            installBtn.Enabled = restoreBtn.Enabled = browseBtn.Enabled = closeBtn.Enabled = false;
            var s = state;
            var t = new Thread(() =>
            {
                try
                {
                    Log("");
                    Log(install ? "---- Installing ----" : "---- Restoring ----");
                    if (install) inst.Install(s); else inst.Restore(s);
                }
                catch (Exception e)
                {
                    Log("ERROR: " + e);
                    Tell("Something went wrong", e.Message + "\n\nYour backup is in the '" + Installer.BackupFolderName + "' folder inside the game folder. Send the text in the log window to the mod author.");
                }
                BeginInvoke((Action)(() => { closeBtn.Enabled = true; Check(s.GameDir); }));
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
