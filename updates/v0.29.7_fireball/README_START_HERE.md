# 0.29.7: the blast starts small, bursts into a fireball, then smokes

One DLL with everything:
- **0.29.5:** mod models load from `StreamingAssets\override\ModAssets`.
- **The new logbook:** the BOOK button, 16 pages.
- **0.29.6 splash:** torpedo hits use the game's own splash, made bigger.
- **0.29.6 resolve window:** the air auto resolve window in the game's own look.
- **New in 0.29.7:** the explosion rework below.

So you only need this one DLL. It replaces both 0.29.6 DLLs and the logbook DLL.

## What changed

The explosion now plays out like your picture series. See `explosion_stages_preview.jpg`.

1. **It starts small.** For the first half second there's a flash low on the ship, a little fire and a puff of white.
2. **Then it bursts.** A blinding flash, then the fireball swells out to full size over about a second. Black wreckage, sparks and burning debris fly out of it and rain back down.
3. **Then the smoke rolls in.** About 2 seconds after the burst, grey smoke rolls out at the sides and along the water. The fireball turns to black smoke as it climbs.
4. **Far fewer streamers.** The fire jets go from 8 to 3 and are shorter. The wreckage trails go from 6 to 3.

A smaller magazine blast goes through the same steps, only faster and smaller. Everything else is the same as before:
- each blast is sized by its shells
- both magazines blow on a broken back
- smoke lasts only until the ship is under

## Install

1. Close the game.
2. Go to `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`.
3. Rename `Assembly-CSharp.dll` to `Assembly-CSharp_backup.dll`.
4. Copy `Assembly-CSharp.dll` from this folder into `Managed\`.
5. Start the game. The menu should say **Version 0.29.7**, and the BOOK should say Page 1 / 16.

## Knobs

These are at the top of `ModWreckArt`:

| Knob | Default | What it does |
|---|---|---|
| `IgniteTime` | 0.5 | Seconds of the small start before the burst |
| `FireballGrow` | 0.8 | Seconds the fireball takes to swell to full size |
| `SmokeDelay` | 2 | Seconds after the burst before the smoke rolls in |
| `Embers` | 40 | Burning debris pieces from a full blast |
| `Streamers` | 3 | Fire jets in a big blast (was 8) |
| `WreckTrails` | 3 | Wreckage trails (was 6) |
| `StreamerReach` | 0.35 | How far the fire jets fly (was 0.45) |

## Checks

- Built on the logbook DLL, so it is 0.29.5 plus the new ModGuide. The splash change is in it too.
- The auto resolve window class is the same, method for method, as in the resolve window DLL. ModGuide is the same as in the logbook DLL.
- The DLL verifier lists the same harmless warnings as that DLL.
- Every patched method matches what was compiled.
- The logbook pages are in the DLL.
- Not tested in the game yet. The preview is a rough render of the same code, so the in-game fire glows brighter.
- The logbook's torpedo page still talks about "water towers". It can be updated next time.

## dnSpy (only if doing it by hand)

1. `ModWreckArt`: Edit Class with `01_ModWreckArt.cs.txt`.
2. `ModSinking`: Edit Class with `02_ModSinking.cs.txt`.
3. `ModVersion`: change the strings as in `03_ModVersion_strings.txt`.
4. `ModAirResolveWindow`: Edit Class with `04_ModAirResolveWindow.cs.txt`.
5. `ModGuide`: Edit Class with `05_ModGuide.cs.txt`.
