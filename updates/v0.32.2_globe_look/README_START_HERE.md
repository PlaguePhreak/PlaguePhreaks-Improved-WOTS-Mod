# 0.32.2 globe test 2: the campaign map as a spinning Earth (globe phase 2)

Built on 0.32.1 globe test 1 (which is on 0.30 Mega Patch 01). DLL md5: 002f4e27a479b198ef28eb6df6ccb05d. Not tested in game yet.

This is phase 2 of the globe plan: the globe to look at. You still give orders on the flat map; the globe is a view that you can drop out of onto the map. Phase 3 and 4 put everything and every click on the globe.

## Install

1. Close the game.
2. In `WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp.dll.0321` (or delete it if you still have the `.030` backup).
3. Copy `Assembly-CSharp.dll` from this folder into `WarOnTheSea_Data\Managed\`.
4. Copy the `override` folder from this folder into `WarOnTheSea_Data\StreamingAssets\` and say yes to merging. It adds one picture: `override\ModAssets\globe\earth.jpg` (the Earth, 4096 x 2048). Without it the globe is a plain blue ball with a grid.
5. Start the game. The main menu should say **Version 0.32.2 globe test 2**.

## What you get

- A new **GLOBE** button in the column of mod buttons at the top left of the campaign map (fifth button, under SAR). **F10** does the same.
- The campaign map is replaced by a 3D Earth on a black, starry background, with a thin blue halo.
- **Day and night** from the campaign clock. The campaign clock is local time for the theatre, so noon on the clock puts the sun over the middle of the map.
- The current **theatre is outlined in gold**.
- **Dots:** round dots are bases, in the owner's colour (blue, red, grey, yellow); bigger ports and airfields are bigger dots. White squares are your task forces, pale blue squares your air groups, red squares spotted enemy forces. They refresh once a second.
- **Controls:** drag with the left or right mouse button to spin, mouse wheel to zoom, arrow keys to turn. The globe starts looking at the middle of the theatre.
- **Back to the map:** press GLOBE or F10 again, or zoom in past the closest point. Zooming in drops you onto the flat map at the spot in the middle of the view (if that spot is inside the theatre).
- While the globe is on, the flat map ignores the mouse and the keys, so you do not select or move things by accident. The game's panels and buttons still work.
- The clock keeps running: time compression is unchanged.

## Please test

1. Main menu says **Version 0.32.2 globe test 2**.
2. Open a campaign (any). Press the GLOBE button. You should see the Earth with the theatre outlined in gold and dots for the bases.
3. Spin, zoom in and out, use the arrows. Check nothing on the flat map got selected or moved when you click on the globe.
4. Let time run at x60 or faster: the night side should creep westward around the globe.
5. Zoom right in: the globe should give way to the flat map at the place you were looking at.
6. Press GLOBE again from the flat map, then press it again: the map should be exactly as you left it (same zoom, same selection).
7. Start a battle with the globe on: it should close itself and the battle load as normal. After the battle, the campaign map should be back as normal.
8. Send me `output_log.txt`. Look for lines starting with `[GLOBE]` and any red errors.

If the dots or the gold outline sit in the wrong place on the Earth picture (for example Guadalcanal's dot not on the island), tell me and send a screenshot: that means the theatre's `mapOriginXY` in setup.txt and the 240 pixels-per-degree rule do not agree, and I need to see by how much.

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
| ShowMarkers | true | the dots |
