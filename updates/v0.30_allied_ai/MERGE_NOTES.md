# 0.30 Allied AI: what changed, for merging

Base: 0.29.11 (md5 cc71debb, includes 0.29.10). Output DLL md5 88d600298b3c3c1a8fb056ae353b6e33.
Built with tools/dll_patcher plus a new `HooksAllied()` (copy in build_tools/Program_with_HooksAllied.cs, env HOOKS_ALLIED=1):
`NOHOOKS=1 HOOKS_ALLIED=1 STRINGS=dnspy_reference/06_ModVersion_strings.txt dotnet run -- <0.29.11 dll> patch.dll <managed dir> out.dll`.
patch.dll = 01 ModAllied + 02 ModSeaResolve + 03 ModAllyWindow + 04 ModConvoy, compiled with csc -langversion:7.3 against
the 0.29.11 DLL, nuget Unity3D.SDK 2017.4.40.1 UnityEngine.dll, a small UnityEngine.UI stub (build_tools/UnityEngine.UI_stub.cs,
version 1.0.0.0) and the net35 reference assemblies. No KEEP list needed.
Checks: assembly references unchanged; ilverify (8.0.0) error list identical to 0.29.11, none in the new classes;
all six hooks read back correctly in ILSpy.

## Classes
- NEW `ModAllied` (static, nested `Group`): spawns/steers RAN groups (faction 0, painted factionColours[3] each tick),
  jobs Patrol/Escort/Attack/Strike/Home/Refit/Deliver, merchant runs (cargo from Cooktown to the neediest faction-0 port,
  unloaded straight into the base arrays, no troops, no takeover check), carrier strikes (faction-0 air groups via
  CampaignInterface.CreateNewMobileObject + CampaignAI.MoveMobileNextFrame), free refit, Remove() (adds the ships' cost back
  to commandPointSpent[0] before DestroyMapMobileObject, which would otherwise refund CP), SendTo()/Sea()/NearestOpenSea()
  (routes to sea waypoints so FindRoute works). Groups are found again after a load by name prefix "RAN ".
  Off unless campaignData.nations0 contains "australia".
- NEW `ModSeaResolve` (static, nested `Ship`, `Side`): auto resolve for fights where our side is allied or the convoy
  (not air vs air). 400-run estimate, damage via cellVariables, then CampaignManager.ProcessMobileObjectPostCombat by reflection.
- NEW `ModAllyWindow` (MonoBehaviour, IMGUI): copy of the 0.29.9 ModAirResolveWindow look; info window, offer, result.
  GameObject "ModAllyWindow". No campaign map button (ModAutoRescue's row 3 untouched).
- `ModConvoy` (whole class replaced): Spawn names it "SUPPLY CONVOY" (customName) and sends it with ModAllied.SendTo to
  the port's sea waypoint; Tick re-finds it after a load (new `Find()`), re-routes (new `HomePort()`), re-sends after 60 idle
  minutes (new field `idle`), unloads on arrival and removes it with ModAllied.Remove. Daily unchanged.
- `ModVersion`: strings only (0.29.11 -> 0.30).

## Hooks (stock classes, one line each)
1. CampaignManager.CheckDaily: `ModAllied.Daily();` after `ModConvoy.Daily();`
2. CampaignManager.Check1Min: `ModAllied.Tick();` after `ModConvoy.Tick();`
3. CampaignInterface.SelectMapObject: first line `if (ModAllied.Blocks(obj)) return;`
4. CampaignManager.CheckMobileEncounters: `canAutoResolve = ModAirResolve.CanResolve(a, b) | ModAllied.CanResolve(a, b);`
5. EngagementPanel.AutoResolve: first line `if (ModAllied.AutoResolve()) return;` (before ModAirResolve.Open)
6. ActionReport.CreateActionReport: after the 2nd DisplayData: `if (ModAllied.InBattle()) pointsGained = 0;`

## Watch for in later merges
- No ModOptions toggle: `ModAllied.On` is the switch.
- Allied groups live in CampaignManager.playerMobile with faction 0, so anything that loops playerMobile sees them
  (ModAirRescue pick-ups do, on purpose).
