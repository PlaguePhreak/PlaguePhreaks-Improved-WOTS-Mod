# 0.32.12 globe test 12 (no yellow edge line on world maps)

Built on 0.32.10 globe test 10 (the 0.32.11 menu globe is left out: the main menu keeps its video).
DLL md5: 305427dcbc8de6164fda8c19788be684. Not tested in game yet.

## What is new
- The yellow outline that marks the campaign map's area on the globe is skipped when the map goes right round the
  world (Worlds at War). It still shows on the Pacific campaigns, where it marks the theatre edge.
- Knob: ModGlobe.Theatre (true/false) turns that outline off everywhere. MenuGlobe is now false.

## Install
1. Back up WarOnTheSea_Data\Managed\Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over it.
3. override\ModAssets\globe\earth.jpg must be in StreamingAssets\override\ModAssets\globe\ (same file as before).

## dnSpy
Only ModGlobe changed (BuildRibbon has the new early return; MenuGlobe field default false). dnspy_reference\ModGlobe.cs.txt
is the decompile of this build. MERGE_NOTES.md lists every hook since 0.30 Mega Patch 01.
