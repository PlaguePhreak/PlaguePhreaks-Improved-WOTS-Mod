# Parachutes and the new airman: bail-outs from shot-down planes

Builds on your current build (0.28.18). It does not touch the 0.28.18 hotfix or the 0.29 sinking pack, so it can go in before or after them.
I can't run the game, so back up `Assembly-CSharp.dll` first. I did compile the new code against your own `Assembly-CSharp.dll` and `UnityEngine.dll` here, and it built with no errors.

## Step 1: the model files (already done for you)
I copied the `ModAssets\parachutes\` folder into your game folder:
`E:\SteamLibrary\steamapps\common\War on the Sea\ModAssets\parachutes\`
It holds 12 files: the canopies, the airmen in three poses, and their textures. If the folder is ever missing, copy `ModAssets` from this pack into the main game folder, next to `WarOnTheSea.exe`.

## Step 2: dnSpy, in this order
1. **ModBailOut** (NEW): in the tree, right-click the `-` (empty) namespace under Assembly-CSharp > **Add Class (C#)...**, select all, delete, paste all of `1_NEW_ModBailOut.cs.txt`, **Compile**. This one file holds three classes: ModBailOut, ModParachute and ModChuteAssets.
2. **Two one-line additions in ModAirDamage**, exact places in `2_ModAirDamage_two_lines.txt`:
   - A) `ModAirDamage.Refresh`, first line: `ModBailOut.Crew(ua);`
   - B) `ModAirDamage.Falling`, first line: `ModBailOut.ShotDown(ua);`
3. **File > Save Module**.

## What it does
- **New cockpit crew.** The stock crew figures in every cockpit are replaced by the new airman: the seated pose, US or Japanese kit, sized and placed to sit where the old figure sat.
- **Bail-outs.** When a plane is shot down above 120 m, each crew member has a 60% chance to get out. The chance is lower below 300 m, and half for Japanese crews, since many flew without a parachute. They leave one after another, 1 to 3 seconds after the hit. If the plane blows up first, most of them don't make it. If it hits the sea first, nobody gets out.
- **The parachute.** Same motion as the animation you reviewed. He pitches forward but stays head-up in free fall, the canopy streams out and snaps open after about 1.5 s, then he sways down at 6 m/s drifting with the wind.
- **In the water.** A small splash, and he floats in his life vest. The canopy tips over and lies flat on the sea, then sinks after a minute. The airman stays for 15 battle minutes. Later, these are the survivors that PBYs will pick up (Roadmap `[BAILOUT]`).
- At most 40 parachutes at once, to keep big air battles smooth.

## In the log (output_log.txt)
- `[BAILOUT] parachute and airman models loaded from ...`: the files were found.
- `[BAILOUT] could not load the models ...`: the ModAssets folder is missing or in the wrong place. Bail-outs and the new crew are then off, and nothing else changes.
- `[BAILOUT] B-25J (ours) shot down at 1450 m: 3 of 6 crew try to bail out`

## Settings (top of ModBailOut)
`NewCockpitCrew` (true/false), `MinHeight`, `JumpChance`, `JapanChance`, `MaxChutes`, `FloatSeconds`.

## Not in this pack
Sounds (later, as you said), PBY rescues and the survivors event (on the Roadmap), and the ModVersion text. The menu still says 0.28.18, because the 0.29 pack changes that file too.
