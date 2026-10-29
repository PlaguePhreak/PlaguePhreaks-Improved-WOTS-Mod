# 0.32.4 globe phase 3: what changed, for merging

- **Base:** 0.32.3 globe test 3 (md5 3e129f892ec09ecad67281ac93883fd3). Only `ModGlobe` and the ModVersion strings change; the hook is the same.
- **Output:** md5 41a9a1a3bfd455bb8554becba020476d.
- **Checks:** ilspycmd of CampaignManager identical to 0.32.3. ModGlobe decompiles cleanly.
- **Icons and names** are Unity UI objects (`Image` + two `Text`, name and shadow) under a full-screen `ModGlobeOverlay` RectTransform that is a child of the invisible click blocker (so they sit above the blocker and below the game's panels, and vanish with it). Each refresh (1 s) copies `sprite` and `color` from the entity's own `SpriteRenderer` child on the flat map (`MapLocation`, `GameObjectAnimator` of playerMobile, `spottedContacts[i].gameObjectAnimator`), so the look is exactly the flat map's. Every frame `PlaceEntries` projects each entry's globe point with `cam.WorldToScreenPoint` and `RectTransformUtility.ScreenPointToLocalPointInRectangle` (camera null for a screen-space-overlay canvas, else `canvas.worldCamera`), hides entries past the horizon (dot test), scales them by `ZoomStart*Radius/dist` (0.6 to 2.4) and shows names when `dist < LabelZoom*Radius`. Font = `TooltipManager.instance.toolTipText.font`, fallback Arial.
- **Scroll out opens the globe:** `ScrollOut` runs each frame the globe is off: wheel axis (sign flipped if `map.invertZoomDirection`) negative, `map.GetZoomLevel() >= map.zoomMaxDistance - 0.005` (the log showed level 0.950 = max on the Solomons), pointer not over UI; then `map.GetCurrentMapLocation(out loc)` gives the map point under the screen centre and `On(lat, lon)` starts the globe there.
- The 3D dot markers from 0.32.2 are gone.
- UI stub for compiling gained `Image.preserveAspect`, `Text.fontStyle/horizontalOverflow/verticalOverflow`.

## Hook (1)

1. `CampaignManager.StartCampaign(string filepath)`: `ModGlobe.Ensure(this);` just before `StartCoroutine(SetupCampaign(filepath))`.

## How it is drawn (no shaders, no bundles, nothing else in the scene touched)

- Everything sits at y = -300000, far from the campaign scene, and is drawn by its own camera (depth = Camera.main + 5, solid black clear). The game's flat-map camera keeps rendering underneath and is overdrawn. The game's UI canvas (screen-space overlay) stays on top.
- Every material uses `Particles/Alpha Blended` (in the build: it is Shader.Find'ed by the mod already), with vertex colours and explicit render queues (stars 3000, halo 3001, Earth 3002, theatre ribbon 3003, dots 3004) as a painter's order, because that shader does not write depth. Dots and ribbon segments on the far side are hidden by a dot-product test every frame.
- Day/night = vertex colours on the 96 x 192 sphere, recomputed every 0.5 s from `CampaignInterface.dateTime` (declination from day of year, hour angle from the clock minus `UtcOffsetHours`, auto = round(theatre centre longitude / 15)). No Unity light is created.
- Input: while on, `map.allowUserDrag/Zoom/Keys` are false (restored on off) and an invisible full-screen `Image` (raycastTarget) is parented first in the root canvas, so WMSK's `respectOtherUI` check sees "over UI" and ignores clicks; the globe's own drag and wheel handling ignores the mouse when `EventSystem.RaycastAll` hits any UI object other than that blocker.
- Off happens on: button/F10, zoom-in drop (`map.FlyToLocation(point, 0.6, min(zoomMax, zoomMin*6))`), `OnDisable` (battle, menu), or `CampaignManager.gameObject` inactive.
- Lat/lon from map points use `ModGeo.Lat/Lon` (240 px per degree from `mapOriginXY`); `ModGlobe.MapPoint` is the inverse.

## Rebuild

```
csc ... -out:UnityEngine.UI.dll build_tools/UnityEngine.UI_stub.cs           (stub, AssemblyVersion 1.0.0.0; now has Graphic.canvas + EventSystems)
csc -nostdlib -langversion:7.3 -t:library -nowarn:0436 -out:patch_globe.dll -r:net35 refs -r:UnityEngine.dll (2017.4.40.1) -r:UnityEngine.UI.dll -r:base0321.dll ModGlobe.cs
NOHOOKS=1 HOOKS_GLOBE=1 STRINGS=build_tools/strings_globe.txt dotnet Patcher.dll base0321.dll patch_globe.dll <refs dir with the stub> out.dll
```

## Known limits (next phases)

- Look only: no selecting or ordering on the globe (phase 4). No labels yet (phase 3). No routes, range circles or weather (phase 5).
- Scrolling out on the flat map does not open the globe yet; the `[GLOBE] on` log line prints the WMSK zoom level so that can be tuned next.
- The Earth picture is 23 pixels per degree; at the closest zoom it looks soft. A 8192 x 4096 picture is a drop-in (4x the memory).
