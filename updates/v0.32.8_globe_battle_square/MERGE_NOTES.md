# 0.32.8 merge notes

- **Base:** 0.32.7 globe test 7 (md5 a5cfe8c63cee171a6f4a0f35e2cd914e).
- **Output:** md5 492d80587a28e8e39f0027f990029474.
- **Changed:** ModGeo (two new knobs), new class ModBattleMap, three hooks, version strings 0.32.7 -> 0.32.8 and a changelog entry. ModGlobe unchanged (recompiled, identical).

## Hooks (dnSpy)
1. CampaignManager.GetValidNeighbouringMobiles: `if (distanceInMetresBetweenMapObjects >= 50000f)` -> `>= ModGeo.JoinRadiusMetres`.
2. EngagementAI.CheckUnitsOutOfZone: `> 5000f` -> `> ModGeo.ZoneRadiusUnits`.
3. TerrainTiles.InitialiseTerrain: `ModBattleMap.Apply();` before both returns (the early return when terrain is disabled, and the end).

## ModGeo
- `public static float JoinRadiusMetres = 110000f;` and `public static float ZoneRadiusUnits = 11000f;` next to the other knobs.

## ModBattleMap (new, dnspy_reference/ModBattleMap.cs.txt)
- Apply(): only for campaign engagements. Reads CampaignData.lastEncounterPixelCoords (the DEM cut centre, 240 px per degree, x may be wrapped round the world), cuts the 512 x 512 pixel square (centre - 256 to centre + 256) from the four campaign map quads (CampaignManager.mapMaterial _TexTL/_TexTR/_TexBL/_TexBR, each covering a quarter of mapPixelWidth x mapPixelWidth/2 from mapOriginXY), GetPixelBilinear, into a 512 x 512 texture; then Map.instance.mapImage's Image gets material = null and sprite = that texture. Outside-the-map pixels are dark blue. Logs [BMAP].

Verified: ilspy decompile diffs 0.32.7 -> 0.32.8 are exactly the three hook lines; ilverify list identical to 0.32.7 apart from one expected line for ModBattleMap.Apply (UI Image).
