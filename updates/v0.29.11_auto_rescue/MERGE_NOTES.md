# 0.29.11 auto rescue (includes 0.29.10): what changed, for merging with 0.30 Allied AI

Base: 0.29.9 (md5 78d7890b). Output DLL md5 cc71debb. Replaces v0.29.10_bailout_rescue as the thing to merge.
Built with tools/dll_patcher: NOHOOKS=1, STRINGS=dnspy_reference/05_ModVersion_strings.txt (0.29.9 -> 0.29.11),
KEEP=ModCampaignRescue.FitMessagePanel,ModBailOut.Crew,ModBailOut.ShotDown,ModBailOut.Note,ModBailOut.Say.
patch.dll sources: 01 ModAirRescue, 02 ModAutoRescue, 03 ModParachute, ModCampaignRescue (Update + OnDisable + empty
FitMessagePanel stub, body kept), ModBailOut (0.29 all-in-one source, needed to compile; bodies kept).
ilverify error list unchanged from 0.29.9. No stock (game) class edited.

## Classes
- NEW `ModAirRescue` (static): airmen bookkeeping, map markers, pick-ups by flying boats/ships.
- NEW `ModAutoRescue` (static): the top-left button (ModTFOverlay.MakeButton row index 3) and auto launch.
  Launch mirrors CampaignAI.CreateAIMobileAir for faction 0: uses CampaignAI.instance.newTaskForce as scratch,
  ml.inTheAir += n, CampaignManager.ApplyCooldownToAirLauncher, CampaignInterface.CreateNewMobileObject (then puts
  CampaignInterface.currentMapObject back), CampaignAI.MoveMobileNextFrame. Setting kept in PlayerPrefs "ModAutoRescue".
- `ModParachute`: new public fields side, planeName, counted; private pickTimer; new FollowOrigin; Init/Waiting/Land/Water calls.
- `ModCampaignRescue`: Update gets `ModAirRescue.CampaignTick();` before `ModCrew.CampaignRescueCheck();`; NEW OnDisable -> ModAutoRescue.Hide().
- `ModVersion`: strings only.

## Watch for in the merge
- If 0.30 adds its own top-left map button, it must not use row index 3 (or move ModAutoRescue.ButtonIndex).
- Pick-ups and auto launch only look at CampaignManager.playerMobile / landMapLocations with faction 0.
  Allied AI task forces on our side will also pick up airmen if they are in playerMobile with currentFaction 0 and type 0.
