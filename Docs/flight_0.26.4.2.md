# 0.26.4.2 Manoeuvre pool (part 1) and target hold

Install: in dnSpy, open the `ModDogfight` class (Edit Class C#), select everything, paste the whole of
`flight_0.26.4.2_ModDogfight.cs.txt`, Compile, then File > Save Module. Nothing else changes (ModFlight stays as it is).
Keep the 0.26.4.5 edits (AttackUnit / AIRvsAIR) too.

## What is new
- **Target hold:** a fighter keeps its target for 12 to 20 s (8 s for wingman cover), even if the game's squad logic picks another. Re-picks are 15 s apart (were 5), a long turning fight re-picks after 25 s (was 12). Should stop the constant "switching from Wildcat to Wildcat".
- **Pursuit curves** (gun run): pure pursuit inside 150 m (aims at the target, not ahead); Trained+ pilots go to lag pursuit (aim a little behind, ease the speed) when fast and close (inside 250 m, 25% faster than the target).
- **Low yo-yo** (Veteran+): target far ahead and flying away, I am slow: dip below its turn plane, speed up 110%, steer onto it. 3.5 s.
- **Wingover** (Trained+): slow and the target is well off the nose (over 100 degrees): climbing turn then back to the target's height. 5 s.
- **Lag displacement roll** (Veteran+): about to overshoot a fighter: ease out to the outside of its turn, slightly up, slower. 3 s. Used before the zoom climb, 30% of overshoots when ready.
- **Out-of-plane break, defensive spiral, unloaded extension** (defence choices, only when the pilot is ready for a special move: 20%, 12% US only, 10% US Veteran+ only). Out-of-plane = 70% turn rate and 150 m up or down; spiral = full turn, 250 m dive, speed 80%; unloaded extension = nearly straight (15% turn), 80 m nose-down, speed 115%.
- All of the above share the "rare" rule: at most one special move every 25 to 50 s per pilot.
- **`[LOSS]` log line** for every fighter that is destroyed or removed from the battle: name, id, side, last height, phase, last enemy on its tail, and "(hit the sea or ground?)" when it was under 150 m. "REMOVED FROM THE BATTLE" means it left the area.

## Already in the game before this (so not new code)
Hit-and-run (the US single pass and zoom away) and the high-side pass (the "position above and to the side, then dive" phase) already exist. Not yet built: Immelmann, pitchback, high-g barrel roll, barrel roll attack (0.26.4.3), scissors, combat spread, defensive split, sandwich, decoy (0.26.4.4).

## Please check in the log
`[LOSS]` lines, new move names (low yo-yo, wingover, lag displacement roll, out-of-plane, defensive spiral, unloaded extension), and that "switching from" lines are far fewer.

## 0.26.4.2.1 (mountain battles, rarer moves)
Log of a battle over mountains: 7 Wildcats and 1 Zero lost; only 3 had a "SHOT DOWN" line (all high up, 2400 to 4100 m). The other 5 were destroyed in phase 5 (roll-over attack or split-S) at 880 to 1500 m, so they almost certainly flew into the ground.
- Needs BOTH files: replace `ModFlight` (flight_model_ModFlight.cs.txt) and `ModDogfight` (flight_0.26.4.2_ModDogfight.cs.txt).
- ModFlight: `GroundAt/GroundAhead` read the land height (`TerrainTiles.GetTerrainHeightAtWorldPosition`) under the plane and 6 km ahead... (up to 40 to 60 units = 400 to 600 m ahead). Roll-over attack needs 600 m of air under the plane, split-S 800 m. During any acrobatic move, under 250 m of air: the move is abandoned, the nose is pulled up 12 degrees, `[FLIGHT] ... acrobatic move abandoned` is logged.
- ModDogfight: over land, under 200 m of air under or ahead of a fighter in any manoeuvre: climb at full speed until clear.
- Rarer: the wait between special moves is now 40 to 80 s (was 25 to 50); low yo-yo and wingover weights lowered (low yo-yo happened 156 times in 15 minutes, the most common).

## 0.26.4.2.2 (ceiling ratchet, status line)
Log with 3 fights (Docs: output_log 5): in the last fight (Corsairs vs Zeros, 650 s) the planes crept higher and higher until 75% were above 7500 m, at the 8000 m limit (average height 5600 m in the first 4 minutes, 7660 m after). Every pass sets up "500 m above the target", and the target itself keeps climbing, so each loop is a little higher. At the ceiling there is no room to dive or zoom and that fight produced no kills at all in 650 s.
- ModDogfight: `MaxHeight` (the highest wanted height for fighters in a fight) is now 6500 m instead of 8000 m.
- New `[STATUS]` log line every 30 s: how many aircraft on each side are Attack_Unit, Follow_Unit, Follow_Nav_Points etc. This will show why a side "does not engage".

## 0.26.4.2.3 (target and manoeuvre rules, Aaron 18 Oct)
Log of Corsairs against Zeros (36 v 24): `[STATUS]` shows every plane was in Attack_Unit all the time (so they did engage), but 540 s gave 0 kills and 1 smoking plane, average height climbed from 5150 m to 6450 m (the ceiling) again, and there were about 430 target switches ("switching from ... to ...").
Rules now:
- **One special move every 1 to 2 minutes per pilot** (60 to 120 s; the first one 10 to 60 s into the fight). Yo-yo, lag roll, wingover, low yo-yo, split-S, roll-over, barrel roll, out-of-plane, spiral, extension and Thach Weave all count.
- **One main target per pilot, kept 5 minutes** (`TargetHoldSeconds` 300). It only changes when the target is destroyed, when more than 4 of our aircraft are on it, or when the 5 minutes are up. The game's squad logic can no longer swap it. Wingman cover (and the Thach Weave wingman) are the only short detours (8 s), then the pilot goes back to its main target.
- **Fight height band:** a fighter never aims higher than 1000 m above the height it started the fight at (`CombatBand`), and never above 6500 m. Stops the whole fight creeping up to the ceiling.
