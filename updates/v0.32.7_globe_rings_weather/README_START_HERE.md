# 0.32.7 globe test 7 (phase 5: rings, weather, map notes)

Built on 0.32.6 globe test 6. DLL md5: a5cfe8c63cee171a6f4a0f35e2cd914e. Not tested in game yet.

## What is new on the globe
1. Base range rings. Each base's spotting ring (and the smaller port ring) is drawn as a true circle on the Earth, the same size and visibility as the flat map's discs. Rings disappear when the flat map hides them.
2. Weather. The flat map's weather cells are drawn as patches on the globe with the same cloud texture and tint, and each cell's sea state and cloud text shows when you zoom in (same zoom as the names).
3. Map notes (the markers you place with the map-note key) show with their icon and text, and can be clicked like on the flat map.
4. The ruler key and the map-note key now work on the globe at the mouse position.

Knobs in ModGlobe (dnSpy, top of the class): Rings, Weather, Notes (on/off), RingWidth (0.003), WeatherAlpha (0.7).

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. The override file ModAssets/globe/earth.jpg is unchanged since 0.32.2. Keep the one you have.

## Test
1. Open the globe: rings around your bases, matching the flat map.
2. Toggle the flat map's range display (if you use it) and check the globe follows.
3. Zoom in: weather patches and the sea state text per cell.
4. Press the map-note key with the mouse over the sea on the globe: the note editor opens, the note appears at that spot.
5. Press the ruler key on the globe and move the mouse: the ruler line draws from where you pressed.
6. Send output_log.txt plus a screenshot if anything looks off.

Next: phase 6, the battle square (battle loads the area around the fight, far forces can sail in) and the battle minimap.
