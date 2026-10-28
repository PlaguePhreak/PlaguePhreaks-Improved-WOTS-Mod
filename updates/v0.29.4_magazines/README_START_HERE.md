# v0.29.4: torpedo water towers and magazine blasts by what's in them

This replaces 0.29.3 and keeps everything in it: the plane wreck parts, the bigger oil slicks and all of 0.29.2. You install it the same way: copy one DLL, no dnSpy needed.

## Install

1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename your current `Assembly-CSharp.dll` to `Assembly-CSharp.dll.0.29.3_backup`.
3. Copy `Assembly-CSharp.dll` from this folder into that `Managed` folder.
4. The `ModAssets\plane_parts` and `mod_wreck` folders stay as they are. Nothing new to copy.
5. Start the game. The main menu should say **Version 0.29.4**.

## What changed

- **Torpedo hits throw up a tower of water.** Every torpedo that hits a ship throws up a white column of water about 100 m high, give or take 15%. Spray flies higher than the column. Then the water falls back, foam spreads along the sea, and a mist drifts off downwind for about 10 seconds. A torpedo hit no longer makes a fireball or smoke on its own.
- **A broken back sets off both magazines.** When a torpedo breaks a destroyer's back, the fore magazine goes up a quarter of a second after the hit. The aft magazine goes up about a second later. Both get fire on the ship and the game's own blast effects on top. Then the ship kicks up, splits and sinks as in 0.29.1.
- **Each magazine blast depends on what's in it.** The mod counts the shells left in that magazine from the ship's guns, how full it is, and what kind they are.
  - **Full** (a destroyer magazine): the whole Barham show. A fireball about 150 m across, a towering black cloud, fire jets, wreckage and sparks.
  - **Half full:** clearly smaller, still with a black cloud.
  - **A quarter full:** a medium fireball that burns out grey. No black cloud and no lasting smoke.
  - **Nearly empty:** a flash and a small burst, little more than a puff.
  - **HE shells** blow harder than AP shells, which carry less explosive.
  - **AA rounds** (under 60 mm) keep cooking off for a few seconds after the blast: sharp pops with sparks flying out.
  - **Star shells** fly out of the blast burning bright white.
  - **A flooded magazine** only half goes off, with a burst of white steam.
- **Every magazine explosion uses this**, not only the ones that sink the ship. A magazine with less than 5% of its shells left can no longer blow the ship apart. The game still does its own damage.
- **Smoke is only for big blasts, and it doesn't linger.** Only a big blast (more than about 90 m across) leaves smoke rising over the spot. The smoke stops when the ship is fully under water and clears about half a minute later. Over a ship that stays afloat, it stops after 20 seconds. The game's fire and smoke on the burning ship is also only added for big blasts, and it goes out when that part of the ship goes under.

See `explosion_preview.jpg`. It's a rough render of the same particle code: the water tower, then a full, half, quarter and nearly empty magazine, all at the same scale.

## What to look for in the log

Each line starts with `[SINK]`:

- `<ship> torpedo hit: a 96 m tower of water`
- `<ship> torpedo BROKE ITS BACK at square ...: both magazines go up, the ship breaks in two`
- `<ship> fore magazine 3,2: 410 of 640 rounds (64% full, 10.2 t of shells: AP ..., HE ..., star ..., AA ...) -> blast 131 m (big: black cloud and smoke until the ship is under)`
- `smoke over the blast stops after 95 s` (`[WRECK]`) shows when the smoke stopped.

Please send me a few of those magazine lines from a battle. They show what the game really keeps in each magazine. If the blasts look too big or too small, I'll tune `BlastK` from them.

## Knobs

These are at the top of `ModWreckArt`:

| Knob | Default | What it does |
|---|---|---|
| `BlastK` | 1 | Overall blast size. Size = BlastK × cube root of the explosive weight in kg |
| `BlastMin` / `BlastMax` | 2.5 / 45 | Smallest and biggest blast (game units, 1 = 10 m) |
| `BigBlast` | 9 | Blasts at least this big get the black cloud, fire jets and lasting smoke |
| `PallMin` | 20 | Seconds of smoke over a ship that doesn't sink |
| `PallLife` | 25 | Seconds each smoke puff lasts, so how long it takes to clear |
| `CookOffMax` | 80 | Most AA cook-off pops after one blast |
| `FlaresMax` | 14 | Most star shells thrown out |
| `TowerHeight` | 10 | Torpedo water tower height (10 = 100 m) |
| `TowerPuffs` | 170 | Puffs of water in the column |
| `TowerGravity` | 1.2 | How fast the water falls back |

These are at the top of `ModSinking`:

| Knob | Default | What it does |
|---|---|---|
| `EmptyMagazine` | 0.05 | A magazine with less than this part of its shells left can't sink the ship |
| `AftMagDelay` | 0.7 | Seconds between the fore and aft magazine on a broken back |

## Checks done

- **Compile:** compiled against your 0.29.3 DLL.
- **Unity 5.6 check:** it only uses Unity calls your game already uses. The one exception is the PNG loader, which keeps its old body.
- **Patch:** patched with my patcher. `ModWreckArt` and `ModSinking` were updated and the menu text changed. One new hook was added in `DamageableSea.ApplyDamage`, right after the `ModHitLog.BeginHit` line: `ModSinking.TorpedoHit(this, ammunitionDamage, collision);`.
- **Patched methods:** every patched method matches what was compiled. The 0.29.3 classes (ModWreckParts, ModWreckPiece, ModAirDamage) are untouched.
- **DLL verifier:** it lists exactly the same harmless stock warnings as your 0.29.3 DLL.
- **Ammo counts:** the light AA guns (WeaponAAA) don't keep a round count in the game. The mod assumes about 1000 25 mm rounds per AA mount, always full.
- **Not tested in the game.** I can't run it here, so watch the first torpedo hits and magazine blasts.

## dnSpy reference (only if you want to do it by hand instead of copying the DLL)

1. `ModWreckArt`: Edit Class with `01_ModWreckArt.cs.txt`, then compile.
2. `ModSinking`: Edit Class with `02_ModSinking.cs.txt`, then compile.
3. `ModVersion`: Edit Class with `03_ModVersion.cs.txt`.
4. `DamageableSea.ApplyDamage`: Edit Method. Right after the first line, `ModHitLog.BeginHit(this, ammunitionDamage, directHit);`, add this line:
   `ModSinking.TorpedoHit(this, ammunitionDamage, collision);`
   Then compile.
5. File > Save Module.
