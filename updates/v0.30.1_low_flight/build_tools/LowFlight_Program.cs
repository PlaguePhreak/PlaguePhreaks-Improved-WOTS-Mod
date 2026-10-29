using System; using System.IO; using System.Linq; using Mono.Cecil; using Mono.Cecil.Cil;
// Low flight 0.30.1: changes number constants (ldc.r4) in place, like dnSpy "Edit IL instructions".
// Usage: Low apply <in.dll> <out.dll>   |   Low dump <dll> <Type> <Method> <values...>
var m = ModuleDefinition.ReadModule(args[1]);
if (args[0] == "dump") {
  var t = m.Types.First(x => x.Name == args[2]);
  foreach (var md in t.Methods.Where(x => x.Name == args[3] && x.HasBody)) {
    var ins = md.Body.Instructions; var vals = args.Skip(4).Select(float.Parse).ToArray();
    Console.WriteLine("== " + md.FullName);
    for (int i = 0; i < ins.Count; i++) if (ins[i].OpCode == OpCodes.Ldc_R4 && vals.Contains((float)ins[i].Operand))
      Console.WriteLine("  IL_" + ins[i].Offset.ToString("x4") + " " + ins[i].Operand + "  next " + ins[i+1].OpCode);
  }
  return;
}
var edits = new (string type, string method, int il, float from, float to)[] {
  ("ModFlight",   "Pitch",             0x0125, 10f,  2.5f), // gun aim: no nose-down allowed below (y-10)*1.5 -> (y-2.5)*1.5
  ("ModFlight",   "Pitch",             0x015c, 12f,  2f),   // gun aim: forced nose-up below 120 m -> below 20 m
  ("ModDogfight", "SetHeight",         0x0028, 20f,  2f),   // dogfight wanted height floor 200 m -> 20 m
  ("ModDogfight", "GunRun",            0x03a0, 20f,  2f),   // gun run wanted height floor 200 m -> 20 m
  ("ModDogfight", "Fly",               0x0657, 20f,  2f),   // leaving the battle: floor 200 m -> 20 m
  ("ModDogfight", "Move",              0x0080, 30f,  4f),   // extend away (move 4): floor 300 m -> 40 m
  ("ModDogfight", "Move",              0x0244, 30f,  4f),   // extend / bait run (move 6): floor 300 m -> 40 m
  ("ModDogfight", "Move",              0x06cd, 20f,  2f),   // chase low target (move 1): floor 200 m -> 20 m
  ("ModDogfight", "NeedsPullOut",      0x009c, 100f, 30f),  // dive pull-out safety margin 100 m -> 30 m
  ("UnitAI",      "BreakAwayFromUnit", 0x0119, 4f,   2f),   // stock break-away floor 40 m -> 20 m
  ("UnitAI",      "BreakAwayFromUnit", 0x0129, 4f,   2f),
};
var bytes = File.ReadAllBytes(args[1]);
var pe = new System.Reflection.PortableExecutable.PEReader(new MemoryStream(bytes));
int FileOff(int rva) { foreach (var h in pe.PEHeaders.SectionHeaders) if (rva >= h.VirtualAddress && rva < h.VirtualAddress + h.VirtualSize) return rva - h.VirtualAddress + h.PointerToRawData; throw new Exception("rva"); }
foreach (var e in edits) {
  var md = m.Types.First(x => x.Name == e.type).Methods.Single(x => x.Name == e.method && x.HasBody);
  var ins = md.Body.Instructions.Single(x => x.Offset == e.il);
  if (ins.OpCode != OpCodes.Ldc_R4 || (float)ins.Operand != e.from) throw new Exception("unexpected IL at " + e.type + "." + e.method + " IL_" + e.il.ToString("x4"));
  int body = FileOff(md.RVA); int hdr = (bytes[body] & 3) == 2 ? 1 : (bytes[body + 1] >> 4) * 4;
  int at = body + hdr + e.il;
  if (bytes[at] != 0x22 || BitConverter.ToSingle(bytes, at + 1) != e.from) throw new Exception("raw bytes differ at " + e.type + "." + e.method);
  BitConverter.GetBytes(e.to).CopyTo(bytes, at + 1);
  Console.WriteLine($"{e.type}.{e.method} IL_{e.il:x4}: {e.from} -> {e.to}");
}
File.WriteAllBytes(args[2], bytes);
Console.WriteLine("written " + args[2]);
