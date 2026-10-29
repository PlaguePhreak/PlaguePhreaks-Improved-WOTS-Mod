# 0.32.13 globe test 13 = 0.30 hotfix 2 + the globe

DLL md5: 480b04b8061f2ab00eb6700cba3ab368. Not tested in game yet.

## What is in it
- Everything from "0.30 Mega Patch 01 hotfix 2" (the 14 tester fixes) and the 0.30.1 low-flight change.
- Everything from the globe line up to 0.32.12 (round-Earth distances, the globe with clicks, rings, weather,
  the 110 km battle square and minimap, no yellow edge line on world maps, no menu globe).
- New: when a campaign ends, the globe throws away its own pieces, so opening a second campaign in the same
  sitting gets fresh icons (before, the second campaign's globe had no icons until the game was restarted).

## Install
1. Back up WarOnTheSea_Data\Managed\Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over it.
3. override\ModAssets\globe\earth.jpg must be in StreamingAssets\override\ModAssets\globe\ (same file as before).

## dnSpy
This build was made by re-applying the globe classes and hooks onto the hotfix 2 DLL, so the by-hand route is:
start from the hotfix 2 DLL, add the three classes in dnspy_reference (ModGeo, ModGlobe, ModBattleMap), then the
hooks listed in MERGE_NOTES.md (sections 0.32.1 to 0.32.9).
