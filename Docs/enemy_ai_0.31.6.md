# 0.31.6 enemy scouts use flying boats and floatplanes only

Built on 0.31.5 (chat reset, ship handling, fire), md5 a15c6704. DLL md5: 4b10558ea9c0ab237bcb49aa40ed50dd. Not tested in game yet.

## What changed
1. Enemy scout fans now fly only flying boats (Mavis, Emily, PBY and the like) and floatplane/scout aircraft (the game's Scout type). Bombers and fighters never go scouting.
2. Every enemy airfield gets a floatplane scout type, so there are enough scouts for the bigger fans on Hard and Elite:
   2, 3, 4, 6 and 6 planes at airfield levels 1 to 5. This also works in saved campaigns.
   The game picks the floatplane by itself from the planes it has for that side (Jake/Pete for Japan, Kingfisher/Seagull for the US).
   The log names the planes it found, in a line starting `[EAI] floatplane scouts in the game for this side:`.
3. Floatplanes, like flying boats, never go on strikes.
4. If an airfield runs out of scout planes, it simply sends fewer scouts.

## Install
1. Close the game.
2. Back up `Wars on the Sea_Data\Managed\Assembly-CSharp.dll` (rename it to `Assembly-CSharp.dll.0315`).
3. Copy `Assembly-CSharp.dll` from this folder into `Wars on the Sea_Data\Managed\`.
4. Start the game; the main menu should say **Version 0.31.6**.

## What to test
1. Load a campaign and run to the first flying hour. The enemy scouts on the map should all be flying boats or floatplanes.
2. In the log, check the `[EAI] enemy airfields get ... floatplane scouts` line and send it to me if the plane name looks wrong.
3. Open an enemy airfield: it should list the floatplane.

## For merging
Classes changed: `ModEnemyAI` (new `IsScoutPlane`, `FindFloatplane`, `EnsureFloatplanes`, `FloatNumbers`, `FloatPrefer`), `ModEnemyScouts` (`ScoutTypeAt` and the map start in `Tick`), `ModEnemyCampaign` (`AirfieldStrike` leaves Scout-type planes home), `ModVersion` (strings only, 0.31.5 to 0.31.6).
No stock method changed; no new hooks. ilverify error list same as 0.31.5.
