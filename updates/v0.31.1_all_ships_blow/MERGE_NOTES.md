# 0.31.1 merge notes

- **Base:** 0.31 with the changelog box fix (v0.31_changelog_box, md5 27f98098). **Output:** md5 b405c961.
- **Classes changed:** `ModSinking` only (full source in `dnspy_reference/ModSinking.cs.txt`), plus ModVersion strings only (Current 0.31.1, the menu Version line, and one changelog line). ModVersion.Build is otherwise the changelog box version.
- **ModSinking changes:**
  - new knobs `BreakOthers`, `FullSplitChance`, `LethalFull`
  - `BreakMerchants` and `BreakCruisers` now default to true
  - `AfterMagazine`: lethal = !empty && (squares > LethalCells || Full >= LethalFull), and the split chance rises with fullness
  - `Breaks()`: every type except Submarine
- **Hooks:** none added.
- **Patch command:** `KEEP=ModWreckArt.LoadPng NOHOOKS=1`.
