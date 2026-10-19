# v0.28 Air combat update: the rest of the 0.26 roadmap in one go [FLIGHT]

Status: **written and compiled against the real game types, NOT run in the game.** Everything below is untested behaviour. Tags in the log: `[BOMBS]`, `[COLLIDE]`, `[ACRO]`, `[FORMATION]`, `[DAMAGE]`, `[PARTS]`, `[OVERSPEED]`, `[AUTORESOLVE]`, plus the usual `[BATTLE]` and `[HIT]`.

Credits: **fuel fires are Kiko's idea, parts falling off a damaged plane is Avaricles' idea.** They are also named in the code comments, the Change Log and the in-game book.

## What is in it

| Roadmap item | What it does |
|---|---|
| Aircraft table | All 135 aircraft have a row (ModAirFlight) and toughness, gun damage, armour and gunner values (ModAirStats). The stock Hellcat, Corsair, Dauntless and Helldiver follow the new rows. |
| Fighters drop bombs | A fighter with bombs flies 10% more drag and a 12% higher wing loading until it drops them. It drops them when an enemy fighter comes within 3 km, when it is attacked, when it starts a defence, or when it leaves. It waits while a friendly ship is under it. Log `[BOMBS]`. |
| Bomber and escort altitude | Escort fighters following a bomber formation fly at least 400 m above it. Bomber chasers are capped to 35% of a group (`HunterShare`), pass floors stop low passes (US 1500 m, Japan 1000 m) and a forced climb follows a low pass when enemy fighters are near. |
| Collisions | Planes can hit each other (ModAirCollide). Scrape under 90 km/h closing speed, bad hit 90 to 325 km/h, head-on above that loses both. Pilots see it coming 55 / 80 / 92 / 98% (by rank) and break away. |
| Manoeuvres | Immelmann, pitchback, high-g barrel roll, barrel roll attack, scissors, decoy, combat spread, a Recover move (fix for Wildcats that cannot regain energy). All wired into the sandwich and defensive split. |
| Formation (0.26.6) | Followers fly a slot off the leader. The leader slows to the slowest follower. Combat spread widens the slots when a fight is near (500 to 1000 m). |
| Damage affects flight (0.26.7) | Engine, wing, fuel, tail hit shares. Power, turn, roll, stall and control scale per plane. Fuel leak and fire. Bingo fuel exit. Ammo exit. |
| Altitude curves | Power full to the critical altitude, then falls per km (floor 35%). Stall speed rises with altitude. |
| Per-aircraft flight file | `unit/air/<key>/<key>_flight.txt` overrides row fields (JSON). See below. |
| Flight readout | F10 in battle shows the selected aircraft: speed, energy, engine, wing, fuel, bombs, collisions, current move. |
| Speed limit removed (0.26.8) | The hard clamp is gone. Past 1.04 x structural speed the wings can break off and parts fall. A sanity cap of 1.4 x dive speed remains for safety. |
| Air auto resolve (0.26.9) | The Auto Resolve button on an air meeting opens a window with the percent chance of victory. Resolve plays out the fight. |
| `ModFlightLog` | `Interval` is back at 10 seconds. |

### The four fixes from the last log

1. **Wildcats cannot regain energy:** new move 6 *Recover*. A plane below 80% of its reference energy for 4 s extends and climbs until 105% (max 14 s, then a 10 s rest).
2. **Sams escape the low fight, Wildcats do not:** Recover plus the bomber hunter cap plus the pass floors.
3. **`[BATTLE]` average E looked cumulative:** now two figures: `E last 60 s` and `whole battle E`. The totals reset after a 30 s gap.
4. **Bomber chasing drags the fight down:** hunter share 35%, within 4 km only, low pass triggers a forced climb.

## Files

| File | dnSpy action | Where |
|---|---|---|
| `flight_0.28_ModAirDamage.cs.txt` | part of the one-go install | new |
| `flight_0.28_ModAirCollide.cs.txt` | **Add Class** | new |
| `flight_0.28_ModAirFormation.cs.txt` | **Add Class** | new |
| `flight_0.28_ModAirResolve.cs.txt` | **Add Class** | new |
| `flight_0.28_ModAirReadoutUI.cs.txt` | **Add Class** | new |
| `flight_0.28_ModAirFlight.cs.txt` | **Edit Class** (replace all) | existing |
| `flight_0.28_ModAirStats.cs.txt` | **Edit Class** (replace all) | existing |
| `flight_0.28_ModFlight.cs.txt` | **Edit Class** (replace all) | existing |
| `flight_0.28_ModDogfight.cs.txt` | **Edit Class** (replace all) | existing |
| `flight_0.28_ModFlightLog.cs.txt` | **Edit Class** (replace all) | existing |

`ModAirStats` replaces the stock-only table from 0.26.4.6; it now has all 135 rows and a `RowFor(key)` method that `ModAirResolve` uses. `ModAirToughness`, `ModAirArmour`, `ModGunnerDamage` and `ModFixedGunDamage` from 0.26.4.6 keep working as before.

## Install, in this order (updated: the classes depend on each other, so everything compiles in ONE go)

Do NOT add or edit the classes one at a time: they use each other, so a single class alone gives "does not contain a definition" errors.

1. Close any open Add Class / Edit Class window.
2. In dnSpy, right-click the existing `ModFlight` class > **Edit Class**.
3. Select all the code in the window, delete it, and paste the whole file `ALL_IN_ONE_all_10_classes.cs.txt` (it holds all 10 classes).
4. Press **Compile**. Not tested in dnSpy yet: if you get "already defined" or any other error, take a screenshot and send it to me. Do not save a half-compiled result.
5. When it compiles with no errors, do the 3 hooks one by one (Edit Method; text is in `3_hooks/hooks.txt`):
   - **`DamageableAir.ApplySmallCalibreDamageToAir`**: after the line `float num3 = modDamage / num;` add `ModAirDamage.OnDamage(parentUnit, num2, hitPoint, num3);`
   - **`EngagementPanel.AutoResolve()`**: as the very first lines add `if (ModAirResolve.Open()) { return; }`
   - **`CampaignManager`**, about line 1304: replace `campaignData.canAutoResolve = false;` with `campaignData.canAutoResolve = ModAirResolve.CanResolve(mobileMapObject, mobileMapObject2);`
6. File > Save Module. Start a 1v1 Wildcat vs Zero custom battle and check the log.

The single files in `1_add_new_classes` and `2_replace_existing_classes` are the same code, kept for reading; you do not need them for the install.

If a hook will not compile, drop it: the rest still works, you only lose damage effects, the resolve window and the auto-resolve button on the campaign map.

## Per-aircraft flight file

Put a text file at `unit/air/<key>/<key>_flight.txt` (for example `unit/air/f4f4/f4f4_flight.txt`). It holds JSON that overwrites fields of that aircraft's row, so you can tune one type without touching code:

```
{"maxSpeed":5.6,"turnRate":38,"critAlt":410,"altLoss":0.12}
```

The file is looked up in the Override folder first, then the game folder. Missing file means the built-in row. A field name that does not exist in the row is silently ignored (Unity JSON). Field names are the ones in `ModAirFlight.Row`.

## Tuning (all constants, top of each class)

| Class | Constant | Default | Effect |
|---|---|---|---|
| ModAirDamage | `EngineHitShare` etc. | 0.30 / 0.60 / 0.75 / 0.85 | where hits land |
| ModAirDamage | `FireMin`, `FireMax` | 8, 25 s | burn time before the plane is lost |
| ModAirDamage | `BingoFuel` | 0.15 | fuel left that makes a plane leave |
| ModAirDamage | `BreakupStart`, `BreakupFull`, `BreakupRate` | 1.04, 1.14, 0.8 | overspeed wing break-up |
| ModAirDamage | `BombDrag`, `BombWingLoading` | 0.10, 1.12 | bomb penalty on fighters |
| ModAirCollide | radius | 0.42 x max(length, width) | how close counts as a hit |
| ModAirFormation | `SpreadOn`, `SpreadRange` | on, 1200 units | combat spread |
| ModAirFormation | `EscortRise` | 40 units (400 m) | escort height above bombers |
| ModDogfight | `RecoverBelow`, `RecoverUntil` | 0.8, 1.05 | recover move |
| ModDogfight | `HunterShare` | 0.35 | share of a group that may chase bombers |
| ModDogfight | `USPassFloor`, `JPPassFloor` | 150, 100 units | lowest allowed attack pass |
| ModAirResolve | `Samples`, `MaxRounds`, `HitChance` | 600, 14, 0.2 | auto-resolve odds |
| ModFlightLog | `Interval` | 10 s | seconds between log lines per plane |

## Test priority

1. **Re-test the 0.27.1 base:** 1v1 Wildcat vs Zero, then 4v4, then a larger fight. Check the `[BATTLE]` lines (two energy figures) and that Wildcats now regain energy.
2. **Bombs, collisions, new manoeuvres, formation:** look for `[BOMBS]`, `[COLLIDE]`, `[ACRO]` and `[FORMATION]` lines.
3. **Bomber and escort altitude:** the fight should not collapse to 1 to 2 km.
4. **Damage effects and overspeed break-up:** F10 readout; a long vertical dive with a Wildcat should only just reach break-up.
5. **Auto-resolve window and log polish.**

## Assumptions and what is not proven

* None of this has run in the game. The code compiles against the real game types in a test harness; the F10 readout and the resolve window are IMGUI and were never drawn.
* Part shedding hides renderers whose names contain wing, aileron, flap, tail, rudder, elevator, stab or fin. The real mesh names are unknown. The `[PARTS]` line logs the mesh names it found, so if nothing falls off, the log tells us what to match.
* Altitude power loss, stall scaling and compressibility are my assumptions, not table values.
* Escort geometry is a height rule only, not a full escort station.
* Auto-resolve odds are crude (a Python port gave 1v1 Wildcat vs Zero about 54%, 6 Wildcats vs 8 Zeros about 16%). A resolved strike simply keeps its survivors.
* Immelmann and pitchback ignore thrust in the entry check. Falling debris uses Unity's default gravity.
* Yaw is not implemented (kept on the roadmap for later).

## Merge note

PR 26 is for Aaron to merge. This update's files are on branch `claude/project-thread-pzq2e0`.
