# 0.32.1 globe phase 1: what changed, for merging

- **Base:** 0.30 Mega Patch 01 release DLL (md5 eb5ffe6bb393f51c096b83386086fb2f = 0.31.15 fire_static relabelled).
- **Output:** md5 dfaf539e8878e1c0728003f32bdc6b58.
- **Checks:** ilspycmd (-r UnityEngine 2017.4 + net35 refs) of CampaignManager, TerrainTiles, MapRadii: only the 6 hook lines below differ. dotnet-ilverify 8.0.0 error list identical to the base (669, normalised paths). Distances checked in Python against the same formulas (table in README).
- **New class:** `ModGeo` (static). No new Unity calls beyond Debug.Log, Mathf.Max, Vector2 maths.
- **Strings:** ModVersion.Current 0.31.15 -> 0.32.1, menu label "Version 0.32.1 globe test 1", a 0.32.1 entry prepended to both changelog texts.

## Hooks (6)

1. `CampaignManager.GetDistanceInMetresBetweenMapObjects(a, b)`: whole body is `return ModGeo.Metres(a, b);`
2. `CampaignManager.GenerateCampaignEngagement`: `zero = ModGeo.Battle((obj2.currentMap2DLocation - obj.currentMap2DLocation) * campaignData.mapWidthMetres * 0.1f, obj);`
3. `CampaignManager.GetValidNeighbouringMobiles`: `Vector2 vector = ModGeo.Battle((gameObjectAnimator.currentMap2DLocation - battleMobile.currentMap2DLocation) * campaignData.mapWidthMetres * 0.1f, battleMobile);`
4. `CampaignManager.GetXYPixelCoord`: `return ModGeo.WrapPixel(obj2);`
5. `TerrainTiles.GetDEMTile(x, y)`: first line `x = ModGeo.WrapTile(x);`
6. `MapRadii.SetMapRadii`: last line `ModGeo.Radii();`

## Rebuild

```
csc -nostdlib -langversion:7.3 -t:library -nowarn:0436 -out:patch_geo.dll -r:net35/mscorlib.dll -r:net35/System.dll -r:net35/System.Core.dll -r:UnityEngine.dll(Unity3D.SDK 2017.4.40.1) -r:base030.dll ModGeo.cs
NOHOOKS=1 HOOKS_GEO=1 STRINGS=build_tools/strings_geo.txt dotnet Patcher.dll base030.dll patch_geo.dll <refs dir> out.dll
```
Patcher = build_tools/Patcher_Program.cs (0.31.15 patcher + HooksGeo). Mono.Cecil 0.11.5.

## Not changed yet (later phases)

- WMSK draws moves as straight lines on the flat map; the time is now the round-Earth time for the leg.
- Scout fan offsets (CampaignInterface ~4049) and ModTFOverlay reach rings still use flat map shapes.
- Nearest-point sorts (Vector2.Distance in map units) are untouched; they only rank, so they are fine near the equator.
