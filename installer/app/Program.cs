// Entry point. Mono.Cecil.dll is embedded in the exe so players get one file.
using System;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Windows.Forms;

namespace WotsInstaller
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
            {
                var name = new AssemblyName(e.Name).Name;
                using (var st = typeof(Program).Assembly.GetManifestResourceStream("embedded." + name + ".dll"))
                {
                    if (st == null) return null;
                    var buf = new byte[st.Length];
                    st.Read(buf, 0, buf.Length);
                    return Assembly.Load(buf);
                }
            };
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Start(args);
        }

        [MethodImpl(MethodImplOptions.NoInlining)]
        static void Start(string[] args)
        {
            Application.Run(new MainForm(args.Length > 0 && Directory.Exists(args[0]) ? args[0] : null));
        }
    }
}
