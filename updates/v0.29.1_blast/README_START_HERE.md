# v0.29.1: 3D explosion and the "kick up" when a torpedo breaks a destroyer's back

This goes on top of the 0.29 all-in-one DLL you have installed now. No dnSpy this time: the DLL is already patched.

## Install (2 copies)

1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename your current `Assembly-CSharp.dll` to `Assembly-CSharp.dll.0.29_backup`.
3. Copy `Assembly-CSharp.dll` from this folder into that `Managed` folder.
4. Copy `mod_wreck\puff.png` from this folder into `...\WarOnTheSea_Data\StreamingAssets\override\mod_wreck\` (next to `burnt.png`).
5. Start the game: the main menu should say **Version 0.29.1**.

To go back, delete the new DLL and rename the backup to `Assembly-CSharp.dll`.

## What changed

**The explosion is 3D now.** The flat picture is gone. When a torpedo breaks a destroyer's back (or a magazine blows), you get:
- a fireball in the middle that keeps boiling up into a brown cloud for a few seconds,
- about 48 fire-and-smoke streamers shooting out in every direction, from nearly flat to nearly straight up. Each one is a burning head that leaves a line of smoke puffs behind it; the puffs start fire-lit orange and turn dark brown-grey, then fade after about 9 seconds,
- 14 thin grey trails of flying wreckage that go further out and arc down into the sea,
- white-hot sparks,
- a second, smaller blast next to it a moment later.

The streamers reach about 1.5 ship lengths (about 160 m for a Fletcher). It's made of real particles, so it looks right from any angle, including from above.
`explosion_preview.jpg` shows roughly how it develops (at 0.6, 1.5, 3 and 6 seconds). That picture is my rough copy of it, not a game screenshot, so it will look a bit different in the game.

**The break kicks up first.** When a torpedo breaks a destroyer's back, the middle now lifts first: both halves tip up at the break by 4.5 degrees in about 1.2 seconds, hang there for 0.6 seconds, then slam back down in 0.7 seconds and dip a little below the water. There's a big splash, and then the two halves start sinking in the V as before. This is all in game seconds, so at x8 or x10 time compression it's over in a blink. Watch it at x1.

## What to test

1. Torpedo a destroyer until its back breaks (Long Lances do it best). Watch it at x1.
2. `output_log.txt` should have `[WRECK] 3D explosion ready (smoke Sprites/Default, fire Particles/Additive, puff 256 px)`. The shader names may be different. If it says `no particle shader found`, the 3D blast is off: send me the log.
3. Tell me how it looks. These can be changed easily (at the top of ModWreckArt and ModSinking):
   - size: `BlastReach` (1.5 ship lengths) and `BlastMax`
   - how many streamers: `Streamers` (48), `WreckTrails` (14) and `Sparks` (90)
   - how long the smoke hangs in the air: `PuffLife` (9 s)
   - the kick: `HogAngle` (4.5 degrees, 0 = off), `HogRise`, `HogHold` and `HogFall`
4. If puffs show in front of the sea when they should be behind it, or the reverse, tell me (`BoomQueue`).

## How it's built

dnSpy can't add the game's particle prefabs, so the mod builds three particle systems in code for each blast: smoke, fire and sparks. It flies the streamer heads itself and drops a smoke puff every few metres along each path. `puff.png` is one soft smoke puff I rendered in Blender. If the file is missing, the mod draws a plainer puff on its own.

I patched your installed 0.29 DLL with my patcher, which does the same Edit Class steps you would do in dnSpy: ModWreckArt, ModSinking and the ModVersion menu text. I checked that the code compiles against your DLL, that every patched method matches what was compiled, and that the DLL verifier lists exactly the same (harmless, stock) warnings as your current DLL. I can't run the game, so this is the first real test.

`dnspy_reference\` has the full source of the three classes, in case you ever want to paste them by hand instead.
