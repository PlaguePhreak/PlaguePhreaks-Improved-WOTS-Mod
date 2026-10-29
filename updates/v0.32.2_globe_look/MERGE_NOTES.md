# 0.32.2 globe phase 2: what changed, for merging

- **Base:** 0.32.1 globe test 1 (md5 dfaf539e8878e1c0728003f32bdc6b58), itself 0.30 Mega Patch 01 + ModGeo.
- **Output:** md5 002f4e27a479b198ef28eb6df6ccb05d.
- **Checks:** ilspycmd of CampaignManager: only the one hook line below differs from 0.32.1. dotnet-ilverify 8.0.0 (without the UI stub in the reference set): the 0.30 base list (669) plus 4 lines for ModGlobe methods that touch UnityEngine.UI, the same "Failed to load assembly UnityEngine.UI" note every stock UI method gets in that setup; nothing else. ModGlobe decompiles cleanly; the UnityEngine.EventSystems types it uses (EventSystem, PointerEventData, RaycastResult) resolve to `UnityEngine.UI 1.0.0.0`, the same assembly the game's own code uses for them.
- **New class:** `ModGlobe : MonoBehaviour`, added to the CampaignManager game object at campaign start (same pattern as ModTFOverlay).
- **New asset:** `override/ModAssets/globe/earth.jpg` (4096 x 2048, Natural Earth II 50m hypsometric with shaded relief and water, 15 degree grid baked in; loaded through `AssetLoader.ImportTexture2D("ModAssets/globe/earth.jpg")`, so it lives in the override folder like every other mod asset).
- **Strings:** ModVersion.Current 0.32.1 -> 0.32.2, menu label "Version 0.32.2 globe test 2", a 0.32.2 entry prepended to both changelog texts.

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
