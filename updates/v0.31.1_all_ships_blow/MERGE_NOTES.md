# 0.31.1 merge notes

- **Base:** 0.31 (md5 6ced6053). **Output:** md5 262e06a0.
- **Classes changed:** `ModSinking` only (full source in `dnspy_reference/ModSinking.cs.txt`), plus the `ModVersion.Current` const 0.31 -> 0.31.1 (no other ModVersion strings).
- **ModSinking changes:**
  - new knobs `BreakOthers`, `FullSplitChance`, `LethalFull`
  - `BreakMerchants` and `BreakCruisers` now default to true
  - `AfterMagazine`: lethal = !empty && (squares > LethalCells || Full >= LethalFull), and the split chance rises with fullness
  - `Breaks()`: every type except Submarine
- **Hooks:** none added.
- **Patch command:** `KEEP=ModWreckArt.LoadPng NOHOOKS=1`.
