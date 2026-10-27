# v0.28.18 update: shredded wings can fail

One file. In dnSpy: **Edit Class** on `ModAirDamage`, delete everything, paste all of `1_ModAirDamage.cs.txt`, **Compile**, then **File > Save Module**.
Built on the 0.28.11 ModAirDamage (the newest one). Nothing else changes, no new hooks.

## What changed
- Before: wing hits stopped at 80% wing damage (`MaxWing`). The plane flew badly but a wrecked wing never killed it, so a B-17 shot only in the wings kept flying.
- Now: once a wing is at 80%, every further wing hit can break the main spar. Chance per hit = 15% + 2.5 x the hit's share of the plane's toughness, at most 95%.
  - B-17 (toughness 156) hit by a .50 cal: about 1 in 4 per wing hit.
  - Wildcat (toughness 36) hit by a Zero's 20 mm: nearly certain.
- When the spar breaks, a wing piece is thrown off and the plane is lost on its next flight tick.
- Log: `[BREAKUP] B17-F id ... WING SPAR BREAKS: a hit for 7.5 (5% of toughness) on a wing already at 80% damage` and then `[LOSS] ... wing spar broke (wing shot to pieces)`.

## Knobs (top of ModAirDamage)
- `SparBase = 0.15f`, `SparPerRel = 2.5f`. Lower them to make wings tougher.
- `SparMax = 0.95f`. The highest chance for any single hit.
