# Worlds at War (test build 1): how to install

Two new campaigns on a whole-world map: **Worlds at War: Allies** and **Worlds at War: Axis**. Nothing in the DLL
changes for this part. Use it with 0.32.14 (or later): the historical events need the ModHistory class that 0.32.14 adds.

1. Unzip `WorldsAtWar_test1_Override.zip`.
2. Copy the `Override` folder from the zip over your game's `StreamingAssets/Override` folder. It only adds new files
   (campaign/wawallies, campaign/wawaxis, language/english/campaign/wawallies and wawaxis, maps/worldsatwar).
3. Open your `StreamingAssets/language/english/campaign/campaigns.txt` (or your Override copy) and add the two lines
   from `campaigns_lines.txt` as new lines under the existing campaign lines. Do not replace the whole file.
4. (rules.txt is included in both campaign language folders from this build on.)
5. Start the game, choose Campaign, and pick **Worlds at War: Allies** or **Worlds at War: Axis**.

## What is in it
- The whole world, 100W eastwards round to 100W (so the Americas are split at 100W, through land), pole to pole.
  Four 8192 x 4096 map images (16384 pixels round the world) and a 4096 x 2048 water mask, drawn from Natural Earth
  10m coastlines. The four images take about 512 MB of video memory; if the campaign map fails to load on a small
  graphics card, the old 4096-wide set is in maps_4096/ and drops straight in.
- 38 historical events on their real dates (campaign/<id>/history.txt, pop-ups h_*.txt): a warning a week ahead,
  then the place changes hands or points are won, depending on whether you have enough warships or carriers near it.
  Wake, Singapore, Java, Midway, Guadalcanal, Torch, Sicily, Normandy, Leyte, Okinawa and more, seen from each side.
- 134 ports and bases in every ocean, set for 8 December 1941: Allies (US, UK and Commonwealth, Dutch East Indies,
  Free French, Soviet Arctic ports), Axis (Japan and its islands, Germany and occupied Norway and France, Italy,
  Vichy Africa and Indochina) and neutrals (Spain, Portugal, Sweden, South America, Mexico, unoccupied islands).
- 1627 AI waypoints on a 5 degree grid with strait helpers, and about 95 AI missions per campaign
  (submarine and surface patrols, intercepts, bombardments, invasions, convoys, home and last-stand).
- Objectives: Allies take Truk, Kwajalein, Saipan, Rabaul, Singapore, Manila, Taranto, Brest, Tripoli and
  Wilhelmshaven while holding Pearl Harbor, San Diego, Sydney, Scapa Flow, Norfolk and Alexandria.
  Axis take Pearl Harbor, Midway, Singapore, Colombo, Darwin, Alexandria, Malta, Gibraltar, Scapa Flow and New York
  while holding Yokosuka, Truk, Wilhelmshaven, Taranto, Toulon and Saigon.

## Known limits of test 1
- **Ships.** The mod only has American, Australian and Japanese ships and planes. The Atlantic and Mediterranean
  therefore sail the same two navies as placeholders. British, German and Italian units need new ship models.
- **Canals.** Suez and Panama are land on the map, so ships go round Africa and Cape Horn. A canal shortcut needs a
  gap drawn in the water mask (easy to add once the rest works).
- **Map detail.** 4096-wide quads give about 23 pixels per degree, coarser than the Solomons map. 8192 quads are
  possible later if memory allows.
- **Battle terrain** outside the stock Pacific tiles falls back to open sea.
- Port and troop numbers, mission timing and the neutral list are first guesses.

## What to check on the first run
1. Does each campaign load, and does the map show the whole world with the seam through the Americas?
2. Scroll out: the globe opens. Are the ports on the right coasts in Europe, Africa and the Americas?
3. Plot a course from Pearl Harbor to Sydney, and from Scapa Flow to Gibraltar. Do the routes find their way?
4. Run a few days. Do Axis (or Allied) submarines and task forces leave their bases in all oceans?
5. Start a battle in the Mediterranean and one in the Atlantic. Do they load?
6. If it crashes or hangs, send `output_log.txt`.
