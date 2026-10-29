# 0.32.7 merge notes

- **Base:** 0.32.6 globe test 6 (md5 60c18f7a5faa26a4b0da79ac2f984f95).
- **Output:** md5 a5cfe8c63cee171a6f4a0f35e2cd914e.
- **Changed:** class ModGlobe only. No new hooks. Version strings (ModVersion) 0.32.6 -> 0.32.7 and a changelog entry.

## ModGlobe changes
- New knobs Rings, Weather, Notes, RingWidth, WeatherAlpha; new fields ringObj, ringMesh, ringSig, weatherRoot, weatherPatches, weatherDirs, weatherSig, weatherTimer.
- Drive: after the phase 4 calls, Cursor(ci, overUi), RingLines(ci), WeatherPatches(ci).
- Cursor: sets WMSK.cursorLocation to the mouse's map point so the game's MapRuler and MapMarker keys (CampaignInterface.Update) act at the globe mouse position.
- RingLines: for each MapRadii.mapRadiiMeshRenderers entry that is enabled, ring radius in metres = localScale.y / 400 * mapWidthMetres (the disc prefab is scale units wide on the 200-unit map), angular radius = metres / ModGeo.Radius(d); colour from the disc material's _Color (alpha at least 0.35, port ring 0.6x). One mesh (render queue 3004), rebuilt only when sizes, visibility or the view change.
- WeatherPatches: one 4x4 patch per WeatherManager.weatherMeshes cell at its local position (x/200, y/100), 0.1 map units square, texture and tint copied from the cell's sharedMaterial every second when it changes; far-side patches disabled.
- Markers: adds entries for MapLocation components under CampaignInterface.mapMarkerParent (map notes, clickable) and label-only entries for WeatherManager.seaStateMeshes text.

Verified: CampaignManager decompile identical to 0.32.2 through 0.32.6; ilverify list identical to 0.32.6 apart from one expected line for ModGlobe.Markers (it now touches a UI Image).
