using System; using System.IO; using System.Linq; using Mono.Cecil; using WotsInstaller;
class P {
  static ModuleDefinition Read(string path, string managed) {
    var res = new DefaultAssemblyResolver(); if (managed != null) res.AddSearchDirectory(managed); res.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
    return ModuleDefinition.ReadModule(new MemoryStream(File.ReadAllBytes(path)), new ReaderParameters { AssemblyResolver = res, ReadingMode = ReadingMode.Immediate });
  }
  static int Main(string[] a) {
    var managed = Environment.GetEnvironmentVariable("MANAGED");
    if (a[0] == "fp") { var m = Read(a[1], managed); using (var w = new StreamWriter(a[2])) StockFp.FromModule(m, StockFp.FileMd5(a[1]), a.Length>3?a[3]:"").Save(w); return 0; }
    if (a[0] == "merge") {
      var t = Read(a[1], managed); var mod = Read(a[2], managed); StockFp fp; using (var r = new StreamReader(a[3])) fp = StockFp.Load(r);
      var mg = new Merger(t, mod, fp); var rep = mg.Plan();
      Console.WriteLine("PLAN " + rep.Summary());
      foreach (var c in rep.Conflicts) Console.WriteLine("  CONFLICT " + c);
      foreach (var n in rep.Notes) Console.WriteLine("  NOTE " + n);
      mg.Apply(); t.Write(a[4]); Console.WriteLine("written " + a[4]); return 0;
    }
    if (a[0] == "othermod") { // synthetic second mod for tests: a[1]=in a[2]=out a[3]=TypeA.Method(untouched) a[4]=TypeB.Method(conflict)
      var m = Read(a[1], managed);
      var t = new TypeDefinition("", "OtherModMarker", TypeAttributes.Public | TypeAttributes.Class | TypeAttributes.Abstract | TypeAttributes.Sealed, m.TypeSystem.Object);
      var ping = new MethodDefinition("Ping", MethodAttributes.Public | MethodAttributes.Static, m.TypeSystem.Void);
      var log = m.ImportReference(typeof(object).Assembly.GetType("System.Object").GetMethod("ToString"));
      var dbg = new MethodReference("Log", m.TypeSystem.Void, new TypeReference("UnityEngine", "Debug", m, m.AssemblyReferences.First(r=>r.Name=="UnityEngine"))) ;
      dbg.Parameters.Add(new ParameterDefinition(m.TypeSystem.Object));
      var il = ping.Body.GetILProcessor(); il.Emit(Mono.Cecil.Cil.OpCodes.Ldstr, "[OTHERMOD] ping"); il.Emit(Mono.Cecil.Cil.OpCodes.Call, dbg); il.Emit(Mono.Cecil.Cil.OpCodes.Ret);
      t.Methods.Add(ping); m.Types.Add(t);
      foreach (var spec in new[]{a[3], a[4]}) {
        var tn = spec.Substring(0, spec.LastIndexOf('.')); var mn = spec.Substring(spec.LastIndexOf('.')+1);
        var md = m.GetType(tn).Methods.First(x=>x.Name==mn && x.HasBody);
        var first = md.Body.Instructions[0]; var p2 = md.Body.GetILProcessor(); p2.InsertBefore(first, p2.Create(Mono.Cecil.Cil.OpCodes.Call, ping));
        md.DeclaringType.Fields.Add(new FieldDefinition("otherModField", FieldAttributes.Public, m.TypeSystem.Int32));
      }
      m.Write(a[2]); Console.WriteLine("othermod written"); return 0;
    }
    return 1;
  }
}
