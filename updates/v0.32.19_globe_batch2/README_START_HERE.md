# 0.32.19 globe test 19: Worlds at War batch 2

Base: 0.32.18 "1 ship 1 model" (md5 4580b19b, itself on 0.32.17 = globe + 0.30 hotfix 3). Everything in those stays.
New md5: 1e160db71c3508f44fadab35a1500deb. Menu says "Version 0.32.19 globe test 19".

## What is new
1. **Convoy routes with purpose** (Worlds at War campaigns, `campaign/<id>/convoys.txt`, 16 routes).
   - Your side's convoys (HX, SC, PQ, Malta runs, Libya runs for the Axis player...) sail on a timetable from port to port, in yellow,
     and steer themselves. Escort them if you like. When one reaches its port it unloads supplies/fuel/troops there and scores
     victory points; if every merchant is sunk the other side scores. Pop-ups for arrivals and losses, a log line when one sails.
   - The enemy's convoys sail the same way, run by the game's own AI (it borrows a Convoy mission). Reaching port scores for them;
     sinking every merchant ship scores for you (pop-up). They are named when spotted, e.g. "Convoy HX-163".
   - A route only sails while both its ports are held by its side; at most 2 of one route are at sea at once.
2. **Victory points and an end date** (`campaign/<id>/score.txt`): ships sunk (by type), ports that changed hands (15 each) and
   convoys. The war ends 2 September 1945; the side with more points gets the victory (or defeat) screen with the final score.
   A pop-up a month before shows the standings. Standings are shown top right on the globe, with convoys at sea.
3. **Nation colouring on the globe**: land is tinted by the side holding the nearest port (your colour / enemy / neutral grey,
   the game's own faction colours), fading with distance, redrawn when a port falls. Knobs ModGlobe.Nations, NationKm, NationAlpha.
4. **Distance readout** at the cursor on the globe while plotting a course or using the ruler: great-circle km, and days (or hours)
   at the force's speed.
5. **Search box** at the top of the globe: type part of a port, task force, contact or sea name and press Enter; the globe spins
   there. Arrow keys, F10 and N are ignored while typing.

## Install
1. Back up `WarOnTheSea_Data\Managed\Assembly-CSharp.dll`, copy this folder's DLL over it.
2. Copy the `override` folder over `WarOnTheSea_Data\StreamingAssets\Override` (adds convoys.txt, score.txt and 4 pop-up frames
   per world campaign; the globe texture is unchanged).
3. Saves from 0.32.15 to 0.32.18 load. A world campaign saved before this build starts scoring from the load (ships already sunk count).

## Testing
- Start Worlds at War: Allies. Day 2 or 3: log line `[CONVOYS] Convoy HX-160 sailed from Halifax for Liverpool`, a yellow
  group off Halifax. Open the globe: standings top right, land tinted, search box at the top.
- Plot a course on the globe: the km/days readout follows the cursor.
- Log tags: [CONVOYS], [SCORE], [GLOBE] nation tint ... ms.
