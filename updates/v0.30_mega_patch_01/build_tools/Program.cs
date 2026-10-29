using Mono.Cecil; using Mono.Cecil.Cil;
// usage: dump <dll> <outdir>   -> writes every ldstr of every type method to outdir/<Type>.txt (json-ish)
//        patch <in> <map.json> <out>  map: [{type, old, new}]
var mode=args[0];
var res=new DefaultAssemblyResolver();
foreach(var dd in (Environment.GetEnvironmentVariable("REFDIRS")??"").Split(':')) if(dd!="") res.AddSearchDirectory(dd);
var asm=AssemblyDefinition.ReadAssembly(args[1],new ReaderParameters{AssemblyResolver=res});
var mod=asm.MainModule;
if(mode=="dump"){
  Directory.CreateDirectory(args[2]);
  foreach(var t in mod.GetTypes()){
    if(!t.Name.StartsWith("Mod")) continue;
    var lst=new List<object>();
    foreach(var m in t.Methods){ if(!m.HasBody) continue;
      foreach(var ins in m.Body.Instructions) if(ins.OpCode==OpCodes.Ldstr) lst.Add(new{method=m.Name,s=(string)ins.Operand}); }
    File.WriteAllText(Path.Combine(args[2],t.Name+".json"),System.Text.Json.JsonSerializer.Serialize(lst,new System.Text.Json.JsonSerializerOptions{WriteIndented=true}));
  }
  return;
}
if(mode=="cmp"){
  var b=AssemblyDefinition.ReadAssembly(args[2]).MainModule;
  var ta=mod.GetTypes().ToList(); var tb=b.GetTypes().ToList();
  Console.WriteLine($"types {ta.Count} {tb.Count}");
  int diff=0;
  foreach(var t in ta){ var u=tb.First(x=>x.FullName==t.FullName);
    if(t.Methods.Count!=u.Methods.Count||t.Fields.Count!=u.Fields.Count){Console.WriteLine("MEMBERS "+t.FullName);diff++;}
    for(int i=0;i<t.Methods.Count;i++){var m=t.Methods[i];var n=u.Methods[i]; if(!m.HasBody) continue;
      var x=m.Body.Instructions; var y=n.Body.Instructions;
      bool same=x.Count==y.Count;
      for(int k=0;same&&k<x.Count;k++){ if(x[k].OpCode!=y[k].OpCode) same=false; else if(x[k].OpCode!=OpCodes.Ldstr && (x[k].Operand?.ToString()??"")!=(y[k].Operand?.ToString()??"")) same=false; }
      if(!same){Console.WriteLine("BODY "+t.FullName+"::"+m.Name);diff++;}
      else for(int k=0;k<x.Count;k++) if(x[k].OpCode==OpCodes.Ldstr && (string)x[k].Operand!=(string)y[k].Operand) Console.WriteLine("str "+t.Name+"::"+m.Name);
    }}
  Console.WriteLine("structural diffs "+diff); return;
}
if(mode=="patch"){
  var map=System.Text.Json.JsonSerializer.Deserialize<List<Dictionary<string,string>>>(File.ReadAllText(args[2]));
  int bad=0;
  foreach(var e in map){
    int n=0;
    foreach(var t in mod.GetTypes()){ if(t.Name!=e["type"]) continue;
      foreach(var m in t.Methods){ if(!m.HasBody) continue;
        foreach(var ins in m.Body.Instructions) if(ins.OpCode==OpCodes.Ldstr && (string)ins.Operand==e["old"]){ ins.Operand=e["new"]; n++; } } }
    Console.WriteLine($"{e["type"]}: {n} x  [{(e["old"].Length>50?e["old"].Substring(0,50):e["old"]).Replace("\n","\\n")}]");
    if(n==0) bad++;
  }
  if(bad>0){Console.WriteLine("MISSING "+bad); Environment.Exit(1);}
  asm.Write(args[3]); Console.WriteLine("written");
}
