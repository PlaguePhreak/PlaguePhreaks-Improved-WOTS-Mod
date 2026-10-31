# 0.32.17 globe test 17: 0.30 hotfix 3 folded into the globe line

Base: the 0.30 Mega Patch 01 hotfix 3 DLL (md5 6b0de454) with every globe-line change re-applied
(= everything in 0.32.16: globe phases 1-6, Worlds at War events and news, fuel rings, 3D world map switch).

## What is new since 0.32.16
Both hotfix 3 fixes:
1. A plane used by a carrier or airfield but missing from the campaign's `airUnits.txt` no longer stops
   "Enter battle" or save loading. Its entry from `unit/air/allUnitsList.txt` is used and the log says `[AIRLIST] ...` once.
2. Oil slicks draw right after the ocean, under smoke and the compass tape (`[SINK] oil slick draw order ...`).

Nothing else changed. Menu says "Version 0.32.17 globe test 17". Old saves load.

## Install
1. Back up `WarOnTheSea_Data\Managed\Assembly-CSharp.dll`.
2. Copy `Assembly-CSharp.dll` from this folder over it.
3. `override` is unchanged from 0.32.15/0.32.16 (globe earth texture); copy only if you do not have it yet.

## Files
- `Assembly-CSharp.dll` md5 432dcaf7b55206ee46a50f2271cecd80
- `build_tools/` the six mod sources, strings file, Cecil patcher source + csproj
- `dnspy_reference/` decompiled classes as they are in this DLL
