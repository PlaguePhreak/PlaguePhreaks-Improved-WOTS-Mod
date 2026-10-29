# dnSpy steps for 0.32.1 (only if you build it by hand; the DLL in this folder already has all of this)

Open the 0.30 Mega Patch 01 `Assembly-CSharp.dll` in dnSpy.

1. Right-click the `-` (top) namespace, **Add Class (C#)**. Delete what is there, paste all of `ModGeo.cs.txt`, **Compile**.
2. `CampaignManager` > `GetDistanceInMetresBetweenMapObjects` > **Edit Method (C#)**. Replace the three lines inside with:
   `return ModGeo.Metres(a, b);` and **Compile**.
3. `CampaignManager` > `GenerateCampaignEngagement` > **Edit Method (C#)**. Find
   `zero = (obj2.currentMap2DLocation - obj.currentMap2DLocation) * campaignData.mapWidthMetres * 0.1f;`
   and change it to
   `zero = ModGeo.Battle((obj2.currentMap2DLocation - obj.currentMap2DLocation) * campaignData.mapWidthMetres * 0.1f, obj);` **Compile**.
4. `CampaignManager` > `GetValidNeighbouringMobiles` > **Edit Method (C#)**. Find the line with
   `(gameObjectAnimator.currentMap2DLocation - battleMobile.currentMap2DLocation) * campaignData.mapWidthMetres * 0.1f`
   and wrap it the same way: `ModGeo.Battle( ...that part... , battleMobile)`. **Compile**.
5. `CampaignManager` > `GetXYPixelCoord` > **Edit Method (C#)**. Change the last line `return obj2;` (the name may differ) to `return ModGeo.WrapPixel(obj2);` **Compile**.
6. `TerrainTiles` > `GetDEMTile` > **Edit Method (C#)**. Add as the first line: `x = ModGeo.WrapTile(x);` **Compile**.
7. `MapRadii` > `SetMapRadii` > **Edit Method (C#)**. Add as the last line, just before the final `}`: `ModGeo.Radii();` **Compile**.
8. `ModVersion`: change `Current` to "0.32.1" and the menu text to "Version 0.32.1 globe test 1".
9. **File > Save Module**.
