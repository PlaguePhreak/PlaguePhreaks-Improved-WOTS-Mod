# 0.31.1 merge notes

- **Base:** 0.31 with the changelog box fix (v0.31_changelog_box, md5 27f98098). **Output:** md5 4f27f0de (replaces b405c961).
- **Classes changed:** `ModSinking` only (full source in `dnspy_reference/ModSinking.cs.txt`), plus ModVersion strings only (Current 0.31.1, the menu Version line, and one changelog line). ModVersion.Build is otherwise the changelog box version.
- **ModSinking changes:**
  - new knobs `BreakOthers`, `FullSplitChance`, `LethalFull`
  - `BreakMerchants`, `BreakCruisers`, `BreakOthers` default to false (torpedo break-back stays destroyers/escorts only, per Aaron)
  - `AfterMagazine`: lethal = !empty && (squares > LethalCells || Full >= LethalFull), and the split chance rises with fullness
  - `Breaks()`: knob per type, default BreakOthers, Submarine false (only gates TorpedoBreakBack; magazine lethality/split is ungated)
- **Hooks:** none added.
- **Patch command:** `KEEP=ModWreckArt.LoadPng NOHOOKS=1`.
