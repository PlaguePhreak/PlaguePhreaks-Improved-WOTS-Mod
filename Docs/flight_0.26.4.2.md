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
