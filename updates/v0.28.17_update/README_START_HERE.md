# v0.28.17 update: bomber stall freeze, long shots at runners, wings that fail, ship panel crash

Three classes to paste and one one-line stock edit. In dnSpy, for each class: **Edit Class**, delete everything, paste the whole file, **Compile**.
When everything is in: **File > Save Module**.

1. **ModFlight**: paste `1_ModFlight.cs.txt` (built on the 0.28.8 ModFlight, the newest).
2. **ModDogfight**: paste `2_ModDogfight.cs.txt` (built on the 0.28.11 ModDogfight, the newest).
3. **ModAirDamage**: paste `3_ModAirDamage.cs.txt` (built on the 0.28.11 ModAirDamage, the newest).
4. **UnitReference.GetAAAText**: one line, see `4_stock_edit_UnitReference.txt`.
5. Optional: in **ModVersion** change `Current` to `"0.28.17"` so the main menu shows the new version.

No new hooks. 0.28.14 (panel), 0.28.15 (stick) and 0.28.16 (chase cam) are not touched.

## What changed

**Bombers no longer hang in mid air (ModFlight).** A B-17 and a B-25 sat at speed 0 in the air for over 10 minutes. Four causes, four fixes:
- Planes come into a battle standing still in the air (the game spawns them at speed 0). A plane first seen in the air now starts at its wanted speed, at least 1.5 x its stall speed. Log: `[FLIGHT] B17-F id ... appeared in the air at a standstill: starts at 410 km/h`.
- The rudder gave every plane a 3 deg/s turn even when stalled, and for a B-17 (best turn 4.5 deg/s) that turn cost as much drag as a hard bank, so it could never speed up. The rudder turn is now at most 35% of the plane's best turn and fades to nothing as the speed falls (`RudderShare`).
- Turn drag is only paid for the turn the plane can really make at its speed.
- A plane below its stall speed now falls: it gains speed at half of g whatever its nose does, and sinks while it has no flying speed (`StallFall`, `StallSink`). A plane that stalls very low can now hit the sea, as it would for real.

**Chasers take long shots (ModDogfight).** A fighter chasing a plane that is running away and that it cannot catch now fires from out to 800 m, but only with the nose within 3 degrees of the aim point and in 1.5 s bursts. Before, it held fire until 300 m and never got there. Hits out there are rare, as they were for real. Log: `[GUN] Wildcat id ... long shot at A7M2 Sam running away at 760 m`. Knobs: `ChaseFireRange`, `ChaseFireCone`, `ChaseBurst`.

**Shredded wings can fail (ModAirDamage).** Once a wing is at 80% damage, each further wing hit can break the main spar and the plane is lost. Chance per hit = 15% + 2.5 x the hit's share of the plane's toughness, at most 95% (B-17 hit by a .50 cal: about 1 in 4; Wildcat hit by 20 mm: nearly certain). Log: `[BREAKUP] ... WING SPAR BREAKS` and `[LOSS] ... wing spar broke`. Knobs: `SparBase`, `SparPerRel`, `SparMax`.

**Ship info panel crash fixed (stock UnitReference).** Clicking a ship with no AA guns while the info panel was on the AA tab threw an error. It now shows an empty AA page.

## Change Log entry (paste at the top of the list)

v0.28.17 - Bombers no longer hang in the air, long shots at runners, wings that fail
---------------------------------------------------------------------------------
* Fix: planes no longer hang in the air at speed 0 after a stall (B-17, B-25). Planes enter a battle with flying speed, the rudder turn of big planes is smaller and fades with speed, and a stalled plane falls until it flies again.
* A fighter chasing a plane it cannot catch fires short bursts from out to 800 m when its nose is right on the target.
* A wing already shot to 80% can break under further hits and the plane is lost. Before, a B-17 could fly on with its wings shredded.
* Fix: the ship info panel no longer throws an error for a ship without AA guns (stock bug).
