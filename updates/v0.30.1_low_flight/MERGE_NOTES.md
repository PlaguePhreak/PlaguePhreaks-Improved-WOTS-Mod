# 0.30.1 low flight: merge notes
- Base: 0.30 Mega Patch 01 (eb5ffe6bb393f51c096b83386086fb2f). Output f3c92a38f5a174a4b9263d753ce115a2.
- Raw in-place patch of 11 `ldc.r4` operands (19 bytes differ). No types, methods, hooks or strings changed. Tool: build_tools/LowFlight_Program.cs (`apply <in> <out>`, checks old values, fails if IL differs).
- ModFlight.Pitch IL_0125 10->2.5, IL_015c 12->2; ModDogfight.SetHeight IL_0028 20->2; GunRun IL_03a0 20->2; Fly IL_0657 20->2; Move IL_0080 30->4, IL_0244 30->4, IL_06cd 20->2; NeedsPullOut IL_009c 100->30; UnitAI.BreakAwayFromUnit IL_0119/IL_0129 4->2.
- To merge into a 0.32.x globe DLL: run the tool on it if those classes are unchanged there (it verifies each value), else make the dnSpy edits in README.
- Const fields ModDogfight.MinHeight (20) etc. still show the old values; they are inlined and unused at runtime.
- Verified: ilspy decompile of ModFlight, ModDogfight, UnitAI differs from base only on those lines.
