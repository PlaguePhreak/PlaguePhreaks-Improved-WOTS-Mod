# 0.32.4 globe test 4: the map's own icons and names on the globe (globe phase 3)

Built on 0.32.3 globe test 3. DLL md5: 41a9a1a3bfd455bb8554becba020476d. Not tested in game yet.

Phase 3 of the globe plan. Only the DLL changes; the Earth picture is the same as 0.32.2/0.32.3 (the `override` folder is included again for a fresh install).

## New in this build

- **The flat map's own icons on the globe.** Every base, task force, air group and spotted enemy shows the same symbol and colour it has on the flat map (ports, airfields, your ship and plane symbols, enemy contacts), instead of plain dots. They grow as you zoom in.
- **Names.** Zoom in a little and every icon gets its name under it, the same names as on the flat map.
- **Scroll out to the globe.** On the flat map, zoom all the way out with the wheel; one more notch opens the globe looking at the spot the map was showing. Zoom right in on the globe to go back, as before. So the whole thing now works as one map: wheel out to the Earth, wheel in to the theatre.
- The 3D button and F10 still work too.

## Install

1. Close the game.
2. In `WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp.dll.0323` (or delete it if you still have an older backup).
3. Copy `Assembly-CSharp.dll` from this folder into `WarOnTheSea_Data\Managed\`.
4. Copy the `override` folder from this folder into `WarOnTheSea_Data\StreamingAssets\` and say yes to merging. It adds one picture: `override\ModAssets\globe\earth.jpg` (the Earth, 4096 x 2048). Without it the globe is a plain blue ball with a grid.
5. Start the game. The main menu should say **Version 0.32.4 globe test 4**.

## What you get

- A new **3D** button in the column of mod buttons at the top left of the campaign map (fifth button, under SAR). **F10** does the same.
- The campaign map is replaced by a 3D Earth on a black, starry background, with a thin blue halo.
- **Day and night** from the campaign clock. The campaign clock is local time for the theatre, so noon on the clock puts the sun over the middle of the map.
- The current **theatre is outlined in gold**.
- **Dots:** round dots are bases, in the owner's colour (blue, red, grey, yellow); bigger ports and airfields are bigger dots. White squares are your task forces, pale blue squares your air groups, red squares spotted enemy forces. They refresh once a second.
- **Controls:** drag with the left or right mouse button to spin, mouse wheel to zoom, arrow keys to turn. The globe starts looking at the middle of the theatre.
- **Back to the map:** press 3D or F10 again, or zoom in past the closest point. Zooming in drops you onto the flat map at the spot in the middle of the view (if that spot is inside the theatre).
- While the globe is on, the flat map ignores the mouse and the keys, so you do not select or move things by accident. The game's panels and buttons still work.
- The clock keeps running: time compression is unchanged.

## Please test

1. Main menu says **Version 0.32.4 globe test 4**.
2. Open a campaign. Zoom the flat map all the way out with the wheel, then one more notch: the globe should open looking at the same area.
3. On the globe: every base should show the same symbol and colour as on the flat map, and your task forces their ship symbol. Zoom in a little: names appear under the icons. Zoom out: they hide.
4. Zoom right in: back on the flat map at that spot. Scroll out again: globe. Do this a few times; it should always come back cleanly.
5. Spin the globe so the theatre goes round the edge: icons should hide as they pass over the horizon and come back on the other side.
6. Open a panel (for example the task force list) while the globe is on: its buttons should work, and the globe should not spin when you drag on the panel.
7. Start a battle with the globe on: it should close, and the campaign map come back as normal afterwards.
8. Send me `output_log.txt` and a screenshot of the globe zoomed in on the theatre.

## Knobs (dnSpy, class `ModGlobe`, top of the class)

| Knob | Default | What it does |
|---|---|---|
| Enabled | true | false removes the button and the key |
| Key | F10 (291) | the key that opens and closes the globe |
| ZoomMin / ZoomMax / ZoomStart | 1.3 / 4.5 / 2.8 | camera distance in globe radii |
| ZoomStep | 0.12 | how much one wheel notch zooms |
| DragSpeed | 0.22 | degrees per pixel dragged (scales with zoom) |
| KeySpeed | 45 | degrees per second on the arrows |
| Night | 0.16 | how dark the night side is (0 black, 1 no night) |
| Twilight | 0.10 | width of the day/night blend |
| UtcOffsetHours | 99 (auto) | the clock's offset from UTC; 99 works it out from the theatre centre |
| MarkerSize | 0.014 | size of the dots, in radii |
| AutoDropToMap | true | zooming in past the closest point returns to the flat map |
| ShowMarkers | true | the icons and names |
| IconPx | 22 | icon size on screen at the starting zoom |
| LabelZoom | 2.2 | names show when the camera is closer than this (radii) |
| LabelPx | 12 | name text size |
| OpenOnScrollOut | true | scrolling out past the farthest flat-map zoom opens the globe |


## Not in this build

The globe is campaign only. The battle minimap, the battle square and forces joining from far away are phase 6 of the plan, after labels (phase 3), clicking and orders on the globe (phase 4) and routes and circles (phase 5).
