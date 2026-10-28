# v0.29.2: a massive explosion like HMS Barham, smoke that hangs around for minutes

Replaces 0.29.1. It's the same kind of install: two copies, no dnSpy.

## Install

1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, replace `Assembly-CSharp.dll` with the one from this folder. Keep your 0.29 backup (`Assembly-CSharp.dll.0.29_backup`) if you made one.
3. `mod_wreck\puff.png` is the same file as in 0.29.1. If you already copied it into `...\StreamingAssets\override\mod_wreck\`, there's nothing to do.
4. Start the game: the main menu should say **Version 0.29.2**.

## What changed since 0.29.1

- **One massive explosion instead of the starburst.** A blinding flash, then one huge fireball bursts out of the sea and flares yellow for a moment. It turns into a wide, towering cloud of black smoke, with pale grey billows rolling out at the sides. It is wider than it is tall, like the Barham film.
- **Yellow fire bursts through the smoke** for the first 3 to 4 seconds.
- **Black chunks of the ship** (about 50 jagged pieces of plating) tumble up through the air and fall back into the sea.
- **Streamers toned way down:** 8 short jets of fire and smoke instead of 48 long ones. There are 6 thin grey wreckage trails instead of 14, plus spray along the water and sparks.
- **The smoke lasts.** After the blast, a pall of smoke keeps rising over the spot and drifts with the game's wind. It starts black, then gets greyer and thinner, and stops after 7 minutes of battle time. A broken ship takes about 1.5 minutes to sink, so the smoke hangs there for about 5 minutes after it's gone. Each puff of it lasts about 70 seconds.
- The torpedo "kick-up" before the break is unchanged.

`explosion_preview.jpg` is my rough simulation of the blast at 0.5, 1.5, 4 and 8 seconds, not a game screenshot.

## Knobs (top of ModWreckArt)

| Knob | Default | What it does |
|---|---|---|
| `BlastReach` | 1.5 | Overall size, in ship lengths |
| `FireballPuffs` | 140 | How many big fire and smoke puffs the fireball is made of |
| `FireballSize` | 1 | Size of those puffs |
| `CloudTime` | 6 | Seconds the fireball keeps boiling up |
| `Streamers` | 8 | Fire jets |
| `WreckTrails` | 6 | Grey wreckage trails |
| `Chunks` | 50 | Black chunks of the ship |
| `Sparks` | 100 | Sparks |
| `SmokeLinger` | 420 | Seconds the smoke pall keeps going |
| `PallLife` | 70 | Seconds each puff of the pall lasts |

Tell me what to change and I'll send a new DLL.

## Checks done

- Compiled against your installed DLL.
- Patched with my patcher (ModWreckArt, ModSinking and the menu text): every patched method matches what was compiled.
- The DLL verifier lists exactly the same harmless stock warnings as your current DLL.
