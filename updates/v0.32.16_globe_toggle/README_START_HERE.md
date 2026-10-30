# 0.32.16 globe test 16: 3D world map on/off switch

Base: 0.32.15 (c8aedf34) = 0.30 Mega Patch 01 hotfix 2 + 0.30.1 low flight + globe line.

## What is new
- Mod Options, under "Interface features", has a new row: **3D world map (3D button, F10, scroll out on the campaign map)**.
- Default is ON. Set it OFF and the 3D and SUN buttons disappear, F10 does nothing, and scrolling out on the flat map stays on the flat map. If the globe is open when you switch it off, it closes.
- The switch can be flipped at any time, in or out of a campaign; it is saved with the other mod options.
- The round-Earth distance fixes (0.32.1) and the battle-square changes stay on regardless; the switch only hides the globe view.

## Install
1. Back up `WarOnTheSea_Data\Managed\Assembly-CSharp.dll`.
2. Copy `Assembly-CSharp.dll` from this folder over it.
3. The `override` folder is the same as 0.32.15 (globe earth texture). Copy it over `WarOnTheSea_Data\StreamingAssets\Override` only if you do not already have 0.32.15 installed.

## Files
- `Assembly-CSharp.dll` md5 1de10a3d03b1f48f2947f6b0cb05d52c
- `build_tools/` sources and the Mono.Cecil patcher (see MERGE_NOTES.md)
- `dnspy_reference/` decompiled classes as they are in this DLL
