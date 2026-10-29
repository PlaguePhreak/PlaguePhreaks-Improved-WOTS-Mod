# 0.29.10 bail-out rescues: what changed (for merging with 0.30 Allied AI)

Base: 0.29.9 (md5 78d7890b). Output DLL md5 093cc798.
Built with tools/dll_patcher: NOHOOKS=1, STRINGS=dnspy_reference/04_ModVersion_strings.txt,
KEEP=ModCampaignRescue.FitMessagePanel,ModBailOut.Crew,ModBailOut.ShotDown,ModBailOut.Note,ModBailOut.Say.
patch.dll = 01_NEW_ModAirRescue + 02_ModParachute + ModCampaignRescue (Update only) + ModBailOut (needed to compile; bodies kept).
ilverify error list unchanged from 0.29.9. No stock (game) class touched.

## Classes
- NEW `ModAirRescue` (static): all the logic.
- `ModParachute` (mod class): new public fields `side`, `planeName`, `counted`, private `pickTimer`; new method `FollowOrigin`;
  `Init` sets side/planeName; `Waiting` and `Land` call `FollowOrigin()`; `Land` calls `ModAirRescue.Splash(this)`;
  `Water` calls `ModAirRescue.TryPickup(this)` once a second.
- `ModCampaignRescue.Update` (mod class): one line `ModAirRescue.CampaignTick();` before `ModCrew.CampaignRescueCheck();`.
- `ModVersion`: 0.29.9 -> 0.29.10 strings only.

## Hooks
Only the two ModParachute calls and the one ModCampaignRescue line above. Nothing in CampaignManager, CampaignAI, EngagementManager or other stock classes.

## Data
Uses ModCrew's survivor records (campaignData.modSurvivors) unchanged; aircrew records are names ending in " aircrew".
No new save fields.

## To merge into 0.30
Apply the same patch (patch.dll from these sources + the KEEP list) on the 0.30 DLL, or paste 01/02 and the one line in dnSpy.
If 0.30 Allied AI task forces should also pick up airmen: ModAirRescue.Pickups only looks at CampaignManager.playerMobile with currentFaction 0.
