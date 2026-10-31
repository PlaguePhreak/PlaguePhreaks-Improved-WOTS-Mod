// Fingerprint of the original (stock) game DLL. Lets the installer tell which parts of
// Assembly-CSharp.dll the mod changed and which parts another mod changed, without
// shipping the original game DLL.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;

namespace WotsInstaller
{
    public class StockType
    {
        public string Header;
        public Dictionary<string, string> Fields = new Dictionary<string, string>();
        public Dictionary<string, string> Methods = new Dictionary<string, string>();
    }

    public class StockFp
    {
        public string Md5 = "";
        public string Label = "";
        public Dictionary<string, StockType> Types = new Dictionary<string, StockType>();

        public static string FileMd5(string path)
        {
            using (var md5 = MD5.Create())
            using (var s = File.OpenRead(path))
                return BitConverter.ToString(md5.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
        }

        public static StockFp FromModule(ModuleDefinition m, string md5, string label)
        {
            var fp = new StockFp { Md5 = md5, Label = label };
            foreach (var t in Fp.AllTypes(m))
            {
                var st = new StockType { Header = Fp.Hash(Fp.TypeHeader(t)) };
                foreach (var f in t.Fields) st.Fields[f.Name] = Fp.Hash(Fp.FieldText(f));
                foreach (var me in t.Methods) st.Methods[Fp.MethodKey(me)] = Fp.MethodHash(me);
                fp.Types[t.FullName] = st;
            }
            return fp;
        }

        public void Save(TextWriter w)
        {
            w.WriteLine("WOTSFP 1");
            w.WriteLine("md5\t" + Md5);
            w.WriteLine("label\t" + Label);
            foreach (var kv in Types)
            {
                w.WriteLine("T\t" + kv.Key + "\t" + kv.Value.Header);
                foreach (var f in kv.Value.Fields) w.WriteLine("F\t" + f.Key + "\t" + f.Value);
                foreach (var me in kv.Value.Methods) w.WriteLine("M\t" + me.Key + "\t" + me.Value);
            }
        }

        public static StockFp Load(TextReader r)
        {
            var fp = new StockFp();
            string line = r.ReadLine();
            if (line != "WOTSFP 1") throw new InvalidDataException("Not a stock fingerprint file.");
            StockType cur = null;
            while ((line = r.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var p = line.Split('\t');
                switch (p[0])
                {
                    case "md5": fp.Md5 = p[1]; break;
                    case "label": fp.Label = p[1]; break;
                    case "T": cur = new StockType { Header = p[2] }; fp.Types[p[1]] = cur; break;
                    case "F": cur.Fields[p[1]] = p[2]; break;
                    case "M": cur.Methods[p[1]] = p[2]; break;
                }
            }
            return fp;
        }
    }
}
