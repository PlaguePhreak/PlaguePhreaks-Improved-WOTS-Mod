# 0.31.2 scout fans, massed strikes, sized strikes and fighter cover

Built on 0.31.1 (all-ship magazine blasts, with the changelog box fix), md5 4f27f0de.
DLL md5: b3ca23065f53a9886c5387cce888dde4. Not tested in game yet.

## Install

1. Close the game.
2. Back up `Wars on the Sea_Data\Managed\Assembly-CSharp.dll` by renaming it to `Assembly-CSharp.dll.0311`.
3. Copy `Assembly-CSharp.dll` from this folder into `Wars on the Sea_Data\Managed\`.
4. Optional: copy `enemy_ai.txt` to `Wars on the Sea_Data\StreamingAssets\override\ModAssets\`. The numbers in it are already built in, so this is only needed to change them. If you copied the 0.31 `enemy_ai.txt` there, replace it with this one, because some names changed.
5. Start the game. The main menu should say **Version 0.31.2**.

## What changed

1. **Scout fans.**
   - Every enemy airfield sends out several single planes on evenly spaced bearings, fanned toward your side of the map. Each plane flies out, crosses over to the next bearing, then flies home. This is the sweep pattern in your screenshot.
   - Flying boats go first, then bombers. Fighters only go when nothing else is left.
   - Scouts never stop a base from launching a strike.
   - The pop-up for a force shows at most once every 2 hours, and only one scout shadows each of your forces.

   | | Very Easy | Easy | Balanced | Hard | Elite |
   |---|---|---|---|---|---|
   | Scouts per airfield per wave | 2 | 3 | 4 | 6 | 8 |
   | Waves a day | 1 | 2 | 2 | 3 | 3 |
   | Fan width | 60° | 90° | 120° | 150° | 180° |
   | Most scouts up at once | 8 | 12 | 20 | 30 | 40 |

2. **Strikes gather, then attack together.** When two or more bases or carriers can reach your ships:
   - Groups from the far ones fly to a rally point 90 to 130 km short of your force.
   - The bases closer than that wait on the ground.
   - When everyone has arrived, or the first group has waited 15 to 45 minutes, the whole force turns in, and the near bases launch at the same moment.
   - This is the build-up in your second screenshot.
   - Air targets and single launchers still go straight in.

3. **Strike size follows the target.**
   - Each ship is worth points: destroyer 1, light cruiser 2, heavy cruiser 3, light carrier 4, carrier or battlecruiser 5, battleship 6.
   - On Balanced an airfield sends 3 strike planes per point, plus fighters equal to 60% of the strike planes as escort.
   - A single destroyer draws about 3 bombers and 2 fighters. A battleship group gets the whole wing.
   - Very Easy sends 2 planes per point and Elite sends 4.
   - Search planes never go on strikes.
   - A base can now launch a second, smaller strike with the planes it still has on the ground.

4. **Fighter cover (CAP) over enemy ships.**
   - Every hour, each enemy group worth enough points gets fighters from the nearest airfield in range, about 1 fighter per point on Balanced and at least 2.
   - The minimum is 8 points on Very Easy, 4 on Balanced and 2 on Elite.
   - The game's own "call for air cover" now uses the same size instead of sending every fighter.
   - Cover flights don't use up the base's strike turn.

Carrier strikes still use the game's own sizes.

## What to test

1. Start a new campaign on Balanced or harder and run the map to the first flying hour. Fans of single enemy planes should spread out from the enemy airfields.
2. Let a scout find one of your groups. You should get one pop-up, and one scout should follow the group.
3. Wait for the strike. In the log, look for "groups gathering ... km out", then "goes in". On the map the red planes should gather before they head for you.
4. Put one destroyer near an enemy base. It should be attacked by a few planes, not the whole wing.
5. Find an enemy battleship or cruiser group near its airfields. It should have fighters flying over it.

Every log line from this update starts with **`[EAI]`**.

## 0.31.2 scout fans and massed strikes: what changed, for merging

- **Base:** 0.31.1 all-ship blasts, which already includes the changelog box fix (md5 4f27f0dea7d73e8364df81a196fc3bf4).
- **Output:** md5 b3ca23065f53a9886c5387cce888dde4.
- **Checks:**
  - The new IL in the output matches the compiled patch: 153 methods, 0 differences.
  - Compared with 0.31.1, the only stock method that changed is CampaignAI.CheckAirfieldLaunchFighterAirSupport, and ModVersion changed by strings only.
  - ModSinking, ModWreckArt and ModOptions are untouched.
  - The dotnet-ilverify error list is the same as 0.31.1's.

## Classes changed

- `ModEnemyAI`: knobs only.
  - Removed: `ScoutSorties`, `StrikeWaitMin`.
  - Added: `ScoutLines`, `ScoutWaves`, `ScoutArc`, `ScoutMax`, `RallyKm`, `RallyWaitMin`, `PlanesPerPoint`, `StrikeMinPlanes`, `EscortShare`, `CapMinValue`, `CapPerPoint`.
- `ModEnemyScouts`:
  - New wave timing (`Waves`) and new helpers `Fan`, `Launch(ml, dirOut, dirCross, km)`, `ScoutTypeAt`, `OnGround`, `ScoutsOut`, `Turn`, `Shadowed`, plus a pop-up cooldown.
  - `SkipSpottedWaypoint` now also skips gathering strike groups.
  - Removed: `SearchTypeAt`, `Launch(ml)`.
  - `Scout` gains `home` and `typeIndex`.
- `ModEnemyCampaign`:
  - New `Package` class and new methods `React`, `LaunchInto`, `Gathering`, `Gather`, `Release` for the rally.
  - `AirfieldStrike` now sizes strikes with `Value`, `Pref` and `StrikeMinPlanes`.
  - New fighter cover: `AirSupport`, `AirSupportResult`, `LaunchCap`, `CoverPatrols` and `Covered`. `CoverPatrols` is called from `Hour`.
  - Removed: `Strike`, `strikes`, `Queue`, `Launch()`.
- `ModVersion`: strings only. 0.31.1 becomes 0.31.2, with changelog lines and the version label.

## Stock hooks

One new hook. The 19 hooks from 0.31 are unchanged.

| Class.Method | Change |
|---|---|
| CampaignAI.CheckAirfieldLaunchFighterAirSupport | first line `if (ModEnemyCampaign.AirSupport(ml, mmoTarget)) return ModEnemyCampaign.AirSupportResult();` |

When the Enemy AI switch is off, every changed method falls back to stock.

## Rebuild

The patcher has new environment switches:
- `HOOKS_ENEMY2=1` adds the one new hook.
- `PRUNE=<types>` drops the old members that nothing uses any more.

```
NOHOOKS=1 HOOKS_ENEMY2=1 PRUNE=ModEnemyAI,ModEnemyScouts,ModEnemyCampaign,ModEnemyBattle STRINGS=strings2.txt dotnet Patcher.dll base0311.dll patch.dll <refs> out.dll
```
