# 0.32.10 globe test 10 (0.32.9 + the 0.30 fuel hotfix)

Built on 0.32.9 globe test 9. DLL md5: 89192094a7a60b704430cb2073af189a. Not tested in game yet.

## What changed since 0.32.9
- The task force fuel hotfix from "Version 0.30 Mega Patch fuel hotfix" is folded in: fuel now drains every 5 game
  minutes whether or not F9 (show all enemies) is on. Same change as that hotfix (CampaignManager.Check5Min only).
  Checked: this DLL's CampaignManager is the hotfix DLL's CampaignManager plus exactly the known 0.32 globe hooks.

Everything from 0.32.1 to 0.32.9 is included (globe, clicks, rings, weather, 110 km battle square, minimap picture, zone disc).

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. Keep the override file ModAssets/globe/earth.jpg you already have.

## Test
1. Load a campaign, do not press F9, run time with a moving task force: its fuel counts down from 10.0 days.
2. Start a campaign battle: the grey zone disc on the tactical map is the 110 km one.
