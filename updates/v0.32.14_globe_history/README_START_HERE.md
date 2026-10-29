# 0.32.14 globe test 14: historical events, globe labels, day/night switch

DLL md5: 26db617fc64a05f05ac84f8ca2b11f29. Built on the tester hotfix 2 DLL (so hotfix 2 and the low-flight change are in).
Not tested in game yet.

## What is new
- **Historical events.** Campaigns with a `campaign/<id>/history.txt` get events on their real dates: a warning pop-up a
  week ahead, then the place changes hands or command points are won or lost, depending on whether you have enough
  warships or carriers within range. Worlds at War Allies and Axis ship with 38 events each (Wake to Okinawa). The
  stock and Guadalcanal campaigns have no file and are unchanged.
- **Sea and country names on the globe**, taken from the flat map's own labels, sized with the zoom.
- **SUN button** (under 3D, shown while the globe is open) or the **N key** turns the night shadow on and off.
- Goes with the Worlds at War pack's sharper 16384-pixel world map (separate zip, WorldsAtWar_test1_Override.zip).

## Install
1. Back up WarOnTheSea_Data\Managed\Assembly-CSharp.dll and copy this folder's Assembly-CSharp.dll over it.
2. override\ModAssets\globe\earth.jpg must be in StreamingAssets\override\ModAssets\globe\ (same file as before).
3. For the events and the sharper map, install the Worlds at War zip again (it only adds and replaces its own files).

## dnSpy
Only ModGlobe changed and ModHistory is new; CampaignManager.CheckDaily has one new line. See MERGE_NOTES.md (top section).
