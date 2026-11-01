using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

// 0.32.20 IL hooks: start fleets (S1) and merchant leader (S3). Usage: Fix20 <in.dll> <refDir> <out.dll>
static class F
{
    static ModuleDefinition A;
    static TypeDefinition T(string n) => A.Types.First(x => x.FullName == n);
    static MethodDefinition M(string t, string n) => T(t).Methods.Single(x => x.Name == n);

    static int Main(string[] a)
    {
        var res = new DefaultAssemblyResolver(); res.AddSearchDirectory(a[1]);
        A = ModuleDefinition.ReadModule(a[0], new ReaderParameters { AssemblyResolver = res, ReadingMode = ReadingMode.Immediate });

        // S1: CampaignAI.CreateStandingMissions: ModStartFleets.Add(list..list6) before ModShipPick.FixStart(list, list2)
        {
            var m = M("CampaignAI", "CreateStandingMissions");
            var il = m.Body.GetILProcessor();
            var ins = m.Body.Instructions;
            var fix = ins.Single(i => i.OpCode == OpCodes.Call && i.Operand is MethodReference r && r.DeclaringType.Name == "ModShipPick" && r.Name == "FixStart");
            var ld1 = fix.Previous.Previous; // ldloc list
            if (!ld1.OpCode.Name.StartsWith("ldloc")) throw new Exception("S1: unexpected IL before FixStart");
            // the six lists are the first six locals stored right after "newobj List`1::.ctor" at the top of the method
            var locs = ins.Where(i => i.OpCode == OpCodes.Newobj && ((MethodReference)i.Operand).DeclaringType.Name == "List`1")
                          .Take(6).Select(i => (VariableDefinition)StoreVar(m, i.Next)).ToList();
            if (locs.Count != 6 || locs.Any(v => v == null)) throw new Exception("S1: list locals not found");
            var t0 = ((GenericInstanceType)locs[0].VariableType).GenericArguments[0].FullName;
            if (t0 != "System.String[]") throw new Exception("S1: first list is " + t0);
            var add = A.ImportReference(M("ModStartFleets", "Add"));
            foreach (var v in locs) il.InsertBefore(ld1, il.Create(OpCodes.Ldloc, v));
            il.InsertBefore(ld1, il.Create(OpCodes.Call, add));
            // the inserted code sits inside the same try block; branches that pointed at ld1 must now point at our first ldloc
            var first = ld1; for (int k = 0; k < 7; k++) first = first.Previous;
            foreach (var i in ins) if (i.Operand == ld1 && i != first) i.Operand = first;
            foreach (var h in m.Body.ExceptionHandlers) { if (h.TryStart == ld1) h.TryStart = first; if (h.HandlerStart == ld1) h.HandlerStart = first; if (h.TryEnd == ld1) h.TryEnd = first; }
            Console.WriteLine("S1 hook: ModStartFleets.Add before ModShipPick.FixStart, locals " + string.Join(",", locs.Select(v => v.Index)));
        }

        // S3a: EngagementAI.RetreatAllMerchants: ModMerchantLead.BeforeRetreat(this.otherSea) first
        {
            var m = M("EngagementAI", "RetreatAllMerchants");
            var il = m.Body.GetILProcessor();
            var f = T("EngagementAI").Fields.Single(x => x.Name == "otherSea");
            var start = m.Body.Instructions[0];
            il.InsertBefore(start, il.Create(OpCodes.Ldarg_0));
            il.InsertBefore(start, il.Create(OpCodes.Ldfld, f));
            il.InsertBefore(start, il.Create(OpCodes.Call, A.ImportReference(M("ModMerchantLead", "BeforeRetreat"))));
            Console.WriteLine("S3 hook: RetreatAllMerchants -> ModMerchantLead.BeforeRetreat(otherSea)");
        }

        // S3b: EngagementAI.SwitchToNewLeader: "Unit unit = list2[0];" -> "Unit unit = ModMerchantLead.Pick(list2);"
        {
            var m = M("EngagementAI", "SwitchToNewLeader");
            var ins = m.Body.Instructions;
            var hits = ins.Where(i => i.OpCode == OpCodes.Ldc_I4_0 && i.Next.OpCode == OpCodes.Callvirt && i.Next.Operand is MethodReference r && r.Name == "get_Item"
                                      && r.DeclaringType is GenericInstanceType g && g.GenericArguments[0].Name == "Unit" && i.Previous.OpCode.Name.StartsWith("ldloc") && i.Next.Next.OpCode.Name.StartsWith("stloc")).ToList();
            if (hits.Count < 1) throw new Exception("S3b: list2[0] not found");
            var z = hits[0];
            var get = z.Next;
            z.OpCode = OpCodes.Nop; z.Operand = null;
            get.OpCode = OpCodes.Call; get.Operand = A.ImportReference(M("ModMerchantLead", "Pick"));
            Console.WriteLine("S3 hook: SwitchToNewLeader list[0] -> ModMerchantLead.Pick (" + hits.Count + " candidate(s), first used)");
        }

        A.Write(a[2]);
        Console.WriteLine("written " + a[2]);
        return 0;
    }

    static object StoreVar(MethodDefinition m, Instruction i)
    {
        var b = m.Body;
        if (i.OpCode == OpCodes.Stloc_0) return b.Variables[0];
        if (i.OpCode == OpCodes.Stloc_1) return b.Variables[1];
        if (i.OpCode == OpCodes.Stloc_2) return b.Variables[2];
        if (i.OpCode == OpCodes.Stloc_3) return b.Variables[3];
        if (i.OpCode == OpCodes.Stloc_S || i.OpCode == OpCodes.Stloc) return i.Operand;
        return null;
    }
}
