# 0.32.15 globe test 15: fuel range on the globe, weekly news

DLL md5: c8aedf34d247ed0ba5d153a6e127eaf5. Built on the tester hotfix 2 DLL (hotfix 2 + low flight included). Not tested in game yet.

## What is new
- **Fuel range on the globe.** With the FUEL overlay on (barrel button, F11), the selected task force shows two rings on
  the globe: the orange one-day ring the flat map already draws, and a thinner red ring for everything its remaining fuel
  can reach. Every task force label on the globe shows "4.2 d fuel  18 kn", red under three days, orange under five.
- **Weekly news.** Every Monday morning a pop-up carries the past week's headlines (land war, politics, the sea war as
  the papers reported it), from 8 December 1941 to the surrender in Tokyo Bay. It comes from campaign/<id>/news.txt, so
  only the Worlds at War campaigns have it. Turn it off in **Mod Options, World campaigns, Weekly news pop-up**.
- Built against the game's own Unity libraries, so the UI code is exactly what the game expects.

## Install
1. Back up WarOnTheSea_Data\Managed\Assembly-CSharp.dll and copy this folder's Assembly-CSharp.dll over it.
2. Install the Worlds at War zip again for the news files (news.txt in both campaign folders, event/news.txt).
3. override\ModAssets\globe\earth.jpg must be in StreamingAssets\override\ModAssets\globe\ (same file as before).

## dnSpy
ModNews is new, ModOptions and ModGlobe are replaced whole (dnspy_reference), CampaignManager.CheckDaily has one new
line after ModHistory.Daily(). See MERGE_NOTES.md.
