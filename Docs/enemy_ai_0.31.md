# 0.31 Enemy AI rework: install and test

Built on 0.30 Allied AI (which has 0.29.11 bail-out rescues and everything before it).
DLL md5: 6ced6053ed1efb04faa781aaafc09d59. Not tested in game yet.

## Install

1. Close the game.
2. Back up your current `Wars on the Sea_Data\Managed\Assembly-CSharp.dll` (rename it to `Assembly-CSharp.dll.030`).
3. Copy the `Assembly-CSharp.dll` from this folder into `Wars on the Sea_Data\Managed\`.
4. Optional: copy `enemy_ai.txt` to `Wars on the Sea_Data\StreamingAssets\override\ModAssets\enemy_ai.txt` if you want to change the numbers. You don't need it, because the same numbers are built in.
5. Start the game. The changelog should say **0.31**.

## What you will see

- **Mod Options** has a new section, "Enemy AI (strength follows the difficulty settings)", with two switches:
  - "Enemy AI rework". Turn it off and the enemy behaves exactly as in 0.30.
  - "Enemy scout reports pop-up". This shows "TF X has been spotted by an enemy scout plane" and pauses the map.
- **New campaigns only:** every enemy airfield gets more aircraft types.
  - Japan: Zero, Val, Kate, Betty, Nell (G3M), Mavis (H6K), Emily, Irving (J1N1).
  - USA: Wildcat, P-400, Dauntless, Avenger, B-26, B-17, PBY.
  - Saved campaigns keep their old airfields.
- **Scout patrols:** bases with a flying boat or search plane send scouts out twice a day, at the first flying hour and at 12:00. On Very Easy, Easy and Balanced they stay home in rain or storms.
  - When a scout spots you, enemy HQ only reacts after a delay. If you shoot the scout down before then, the report is lost.
  - From Easy up, the scout stays near your force for a while to keep tracking it.
- **Coordinated strikes:** bases close to the target wait so that all the waves arrive together. Search planes are never sent on strikes.
- **Map AI:**
  - The enemy chases further and with less of a size advantage.
  - It remembers you for longer, and it searches the last place it saw you.
  - On Elite it sends a surface group straight at any force it spots.
- **Battle AI:**
  - The enemy rethinks more often. From Balanced up, a ship no longer turns away after the first hit.
  - Its fire is spread over your ships, and from Hard up it picks on cripples first.
  - Retreating ships lay smoke, and scouts stay overhead.
  - Some enemy pilots are one rank better.
  - On Elite the whole force only runs when it is down to a third of your strength.

Campaign numbers follow **Campaign Difficulty**, which is set when the campaign starts. Battle numbers follow **Combat Difficulty**. Both use the steps Very Easy, Easy, Balanced, Hard and Elite.

## What to test

1. Start a **new** campaign on Hard or Elite. Open an enemy airfield and check that it lists the new aircraft.
2. Let the map run to the first flying hour. Enemy scouts should fly out from the bases.
3. Let a scout find one of your forces. The pop-up should name that force.
4. Shoot a scout down before its report is due. That base should not send a strike.
5. Let a strike come in. Waves from different bases should arrive at about the same time.
6. Fight a surface battle.
   - Damaged enemy ships should keep fighting, unless they are badly slowed.
   - Retreating ships should lay smoke.
   - Enemy fire should be spread across your ships.
7. Turn "Enemy AI rework" off in Mod Options and check that the enemy is back to the 0.30 behaviour.

The log file is `output_log.txt` or `Player.log`. Every line from this update starts with **`[EAI]`**. If something looks wrong, send me those lines.

## Not built yet

- Bombers pressing on through losses (the `PressOn` knob does nothing yet).
- Enemy fighters giving cover to their bombers first.
- A special long-range torpedo attack on Elite. The existing torpedo coordination is kept.
- Outgunned enemy forces holding at long range instead of running.

## 0.31 Enemy AI: what changed, for merging

Base: 0.30 Allied AI DLL (md5 88d600298b3c3c1a8fb056ae353b6e33). Output md5 6ced6053ed1efb04faa781aaafc09d59.
Checks done:
- The new classes' IL in the output matches the compiled patch.
- Compared with 0.30, only the 19 hooked stock methods below, ModOptions and ModVersion changed.
- The dotnet-ilverify 8.0.0 error list is the same as 0.30's, and none of the errors are in the new classes.

## New classes

- `ModEnemyAI`: the difficulty tables (5 steps) and the reader for `override\ModAssets\enemy_ai.txt`. Also holds `AfterInit`, which sets the airfield aircraft on a new campaign, and `FixLocations`.
- `ModEnemyScouts`: scout patrol launch and steering, shadowing, delayed reports and the pop-up (message key `ModEnemyScoutSpotted`).
- `ModEnemyCampaign`: the map planner's numbers, the reaction to a sighting with timed strikes, the last known position search and the Elite hunt.
- `ModEnemyBattle`: battle rethink, the retreat rules, smoke, spreading fire, target choice, scouts staying overhead and the pilot rank shift.

## Changed mod classes

- `ModOptions`: Count goes from 18 to 20. New keys `enemyai` (index 18) and `scoutpopup` (index 19), new properties `EnemyAI` and `ScoutPopup`, and a new header row "Enemy AI". The options file is read by key, so old files still load.
- `ModVersion`: strings only (0.30 -> 0.31, plus the changelog).
- `ModFlight.Rank`: every return is wrapped in `ModEnemyBattle.ShiftRank(rank, u)`.

## Stock hooks (19)

| # | Class.Method | Change |
|---|---|---|
| 1 | CampaignManager.Check1Min | `ModEnemyScouts.Tick()` after `ModAllied.Tick()` |
| 2 | CampaignAI.MakeStrategicDecision | `0.8f` -> `ModEnemyCampaign.InterceptChance(0.8f)` |
| 3 | CampaignManager.CheckAISeaIntercept | `200000f` -> `ModEnemyCampaign.ChaseRange(200000f)` |
| 4 | CampaignAI.ShouldChaseSpotted | `0.75f` -> `ModEnemyCampaign.ChaseRatio(0.75f)` |
| 5 | CampaignManager.CheckMobileEncounters | `0.009f` -> `ModEnemyScouts.ShipScoutChance(0.009f)` (0.30's canAutoResolve hook is untouched) |
| 6 | CampaignAI.GetIncerceptForceMission | `cpThresholdsForGroupSize[2]` -> `ModEnemyCampaign.InterceptCP(...)` |
| 7 | CampaignAI.AddAIDecisionDelay | first line `days = ModEnemyCampaign.ScaleDelay(days)` |
| 8 | Utilities.GetMaxSpotTime | return value through `ModEnemyCampaign.SpotTime(stock, mmo)` |
| 9 | CampaignAI.OnPlayerSpotted | first line `if (ModEnemyCampaign.OnSpotted(mmoPlayer)) return` |
| 10 | CampaignManager.SpotContact | first line `ModEnemyScouts.Contact(mmoContact)`; `AirReturnToBase(observer)` -> `ModEnemyScouts.ReturnOrShadow(this, observer)` |
| 11 | CampaignAI.GetNewSpottedWaypoint | first line `if (ModEnemyScouts.SkipSpottedWaypoint(goa)) return -1` |
| 12 | CampaignAI.CheckAirfieldLaunchAirstrikeOnMobile | first line `if (ModEnemyCampaign.AirfieldStrike(ml, mmoTarget)) return` |
| 13 | CampaignData.InitialiseCampaignData | last line `ModEnemyAI.AfterInit(this, filePath)` |
| 14 | EngagementAI.InitialiseEngagementAI | last line `ModEnemyBattle.Begin()` |
| 15 | EngagementAI.Update | first line `ModEnemyBattle.Tick()` |
| 16 | EngagementAI.CheckDefensiveConditions | after the global retreat `if`, `if (ModEnemyBattle.Defensive()) return` |
| 17 | EngagementAI.OnDetectUnit | `MultipleUnitsAttackTarget(otherSea, detectedUnit)` -> `ModEnemyBattle.SplitFire(this, otherSea, detectedUnit)` |
| 18 | EngagementAI.GetBestPrimaryGunTarget | first line `var u = ModEnemyBattle.PickGunTarget(attacker); if (u != null) return u` |
| 19 | ModFlight.Rank | see above |

When the switch is off, every hook returns the stock value or does nothing.

Overlap with 0.30 is only in Check1Min and CheckMobileEncounters, on different lines. No overlap with 0.29.10/0.29.11.

## Rebuild

`build_tools/` holds:
- the C# sources, `compile.sh` (Roslyn, net35 refs, Unity 2017.4 UnityEngine.dll, UI stub);
- the patcher `Program_with_HooksEnemy.cs` (the 0.30 patcher plus `HooksEnemy()`), and `strings.txt`.

Run:

```
NOHOOKS=1 HOOKS_ENEMY=1 STRINGS=strings.txt dotnet Patcher.dll base030.dll patch.dll <managed refs> out.dll
```
