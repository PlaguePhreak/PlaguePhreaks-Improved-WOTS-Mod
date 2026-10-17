# New map locations: research (for v0.24.3)

**Status: all 10 locations below are now built in the Override files (pending test).** Lae, Buna, Gasmata, Cairns and Horn Island start owned by their historical side (Allies and Japan swap in campaign002). Finschhafen, Kiriwina, Madang, Wewak and Manus start empty (neutral, level 0) so either side can capture them. Files changed in both campaigns: `campaign/campaignXXX/mapLandLocations.txt`, `campaign/campaignXXX/seaWaypoints.txt` (new in the repo) and `language/english/campaign/campaignXXX/mapLocationNames.txt` (new in the repo). Start a NEW campaign to see them; old saves keep the old 22 locations.

History is from general knowledge of the Pacific War and should be double-checked before we write descriptions. Map positions are estimates (see "How positions were worked out") and must be checked in game.

## What a location needs (how the game defines one)
Each location is one line in `Override/campaign/campaign00X/mapLandLocations.txt` (both campaigns, same list). Fields used today, e.g. Rabaul:
`locationID`, `currentFaction` (0 = player side of that campaign, 1 = enemy, 2 = neutral), `locationPosition` {x,y}, `createShips` (true for ship-building home ports), `portLevel` 0-5, `airfieldLevel` 0-5, `aircraftPrefabs`, `integrity`, `troops`, `supplies`, `fuel`, `engineering` (two numbers each: player, enemy), `inTheAir`, `destroyedAir`.

Three more things outside that line (all found in the decompiled code):
1. **Display name**: `language/campaign/campaignXXX/mapLocationNames.txt`. Names are matched to locations by line number (`CampaignManager.CreateLandLocations`), so the new name must sit on the same line number as its location. Safest: add new locations at the END of both files.
2. **Sea waypoint**: `campaign/campaignXXX/seaWaypoints.txt` needs a waypoint with the same name as the location, `isLocation: true`, its position, and links to its north / south / east / west neighbour waypoints (`CampaignManager.CreateSeaWaypoints`). Ships and AI missions sail between these. Copies from the game folder are in the project folder (`game_files/`), not in the repo.
3. **Optional**: `sea_missions.txt` (AI patrols/convoys that start at or target the location), `setup.txt` lists (`mustControl` = bases the player must hold to win, `maxPortAt` / `maxAirAt`), and CP income (each location held gives `commandPointsPerLocation`, plus CP per port and air base level).

A neutral land location (like `newgeorgia`, faction 2, levels 0) is the lowest-effort kind: one line, one name, one waypoint.

## What the real game files show (checked 17 Oct 2026)
Copies are now in the project folder under `game_files/campaign001` and `campaign002` (`seaWaypoints.txt`, `mapLocationNames.txt`).
- `mapLocationNames.txt` has 22 lines, one per location, in exactly the same order as `mapLandLocations.txt` (BORPOP first, VELLA LA VELLA last). New names must be added at the end of both language files, in the same order as the new lines at the end of `mapLandLocations.txt`.
- `seaWaypoints.txt` has 70 waypoints. A location is a waypoint with `isLocation: true` and the same name as its `locationID`, e.g. `{"waypointName":"cooktown","isLocation":true,"pos":["-0.32","-0.346","0.002"],"sNorthWP":["Coral6"],"sSouthWP":[],"sEastWP":["Coral0"],"sWestWP":[]}`. `pos` is x, y and a radius. The four lists say which waypoints a ship can sail to going north, south, east or west.
- Links must be added in both directions: the new location lists its neighbours, and each neighbour needs the new location added to its own lists (otherwise ships can sail out but never in, or the other way round).
- Port Moresby only links south (to `Coral6`), so the PNG north coast is currently a gap: there is no waypoint near Lae or Buna. Nearest existing waypoints:
  - Lae (-0.271, 0.161): `Bism6` (-0.232, 0.193), `Bism5` (-0.258, 0.230), `Sol0` (-0.183, 0.131)
  - Buna (-0.229, 0.048): `Sol0`, `Coral7` (-0.128, -0.054)
  - Cairns (-0.307, -0.440): `Coral0` (-0.199, -0.327), `Coral6` (-0.257, -0.109)
  - Gasmata (-0.173, 0.192): `Sol0`, `Bism6`
- The campaign002 waypoint file is almost identical to campaign001 (a few Japan-side link differences, e.g. at `Bism4`), so edit both.
- Neutral land locations in the current files (faction 2) are all in the Solomons: `kolombangara`, `malaita`, `newgeorgia`, `rennell`, `russell`, `santacruz`, `santaisabel`, `vellalavella`.

## How positions were worked out
Fitted from known towns already on the map (Port Moresby, Rabaul, Cooktown, Guadalcanal). About 0.0294 map x per degree of longitude and 0.059 map y per degree of latitude. Check: it puts Tulagi at (0.116, 0.021) vs `florida` (0.116, 0.024) and Munda at (0.031, 0.067) vs `newgeorgia` (0.039, 0.062), so it is good to about 0.01.

## Proposed list

### Group A: exist or matter at the campaign start (7 Aug 1942)
| Location | Est. x, y | Side at start | Why it matters | Suggested start |
|---|---|---|---|---|
| **Lae** (with Salamaua) | -0.271, 0.161 | Japan | Taken by Japan in March 1942; its airfield flew Zero and bomber raids on Port Moresby and the Allied PNG coast. Recaptured Sept 1943. Natural Japanese forward air base opposite Port Moresby. | Japan, port 1, air base 3-4 |
| **Buna** (with Gona, Dobodura) | -0.229, 0.048 | Japan | Japanese beachhead since the July 1942 landings for the Kokoda Track push. Bloody Buna-Gona campaign Nov 1942 - Jan 1943; the Allied airfields at Dobodura came after. | Japan, port 0-1, air base 0-1 (small) |
| **Cairns** | -0.307, -0.440 | Allies | Main Queensland north coast port and seaplane/flying boat base, staging for convoys and reinforcements towards Port Moresby and Milne Bay. Fills the gap south of Cooktown. Very close to the south edge of the map, so check it fits. | Allies, port 2-3, air base 2-3 |
| **Gasmata** | -0.173, 0.192 | Japan | South coast of New Britain; small Japanese airstrip since Feb 1942, used as a forward base and a landing point against the Papuan coast. | Japan, port 0, air base 1-2 |
| **Horn Island / Thursday Island** | -0.409, -0.067 | Allies | Torres Strait; Allied fighter strip and naval anchorage covering the Cape York approach. | Allies, port 1, air base 2-3 |

### Group B: appear later in the war (could start neutral and be taken)
| Location | Est. x, y | Why it matters |
|---|---|---|
| **Finschhafen** | -0.245, 0.167 | Huon Peninsula base, Japanese barge hub 1942-43, Allied landing Sept 1943. Lies close to Lae, so use one or the other for a first pass. |
| **Kiriwina** (Trobriand Is.) | -0.151, 0.056 | Allied airfields in 1943 for fighters covering New Guinea and New Britain. |
| **Madang / Wewak** | -0.306, 0.250 / -0.368, 0.349 | Japanese north New Guinea air and supply bases (build-up from late 1942, check dates). Further from the current action; low priority for now. |
| **Manus (Lorengau)** | -0.262, 0.439 | Admiralty Islands; Japanese airfield, later a major Allied fleet base (1944). Close to the north edge. |

### Already covered, no new location needed
- Tulagi / Gavutu: on `florida`; Aug 1942 landings.
- Munda: `newgeorgia`.
- Buin / Kahili: near `shortland` and `bougainville`.
- Espiritu Santo and Efate: `newhebrides`.
- Townsville, Darwin and Noumea: off the south and west edge of the map.

## Recommendation
Start v0.24.3 with Lae, Buna and Cairns (Aaron's picks), then add Gasmata and Horn Island if the first three work. All fit the Aug 1942 start date, and they put real targets on the Papuan north coast, which the map is missing today. Group B can come after the air base rework (v0.24.4).

The files needed to build these are now in the project folder (`game_files/`). Next step when Aaron says go: write the new lines, names and waypoints (with two-way links) for the chosen locations.

## Aircraft per location (added after the first build)
Every one of the 32 locations now has its own aircraft lists in `mapLandLocations.txt` (`aircraft0`, `aircraft0Numbers`, `aircraft1`, `aircraft1Numbers`). The game picks the list by who holds the base right now (faction 0 or 1, which is the Allies in campaign001 and Japan in campaign002), so a captured base switches to the captor's planes. If a location has no list, the side's default list in `setup.txt` is used.

Rules used:
- Up to 4 types per base (the strike screen has 4 slots, `maxAircraftTypesToLaunch`).
- `aircraftXNumbers` holds 5 rows (air base level 1 to 5) of one number per type. The first type is there from level 1, the second from level 2, the third from level 3, the fourth from level 4. Each type is capped at 8, and floatplanes and flying boats at 4.
- Only 1942-43 types, since a base list does not change with the date. Japan uses its own types (Navy at Rabaul, Kavieng, Lae; Army Ki-43, Ki-45, Ki-49 at Madang and Wewak). US bases use US types, and RAAF types (Kittyhawk, Beaufort, Walrus) mix in at Port Moresby, Milne Bay and the Queensland bases.

| Location | Allied list | Japanese list |
|---|---|---|
| Rabaul | F6F-3, B-24, SBD-3, TBF-1C | A6M2, G4M Betty, D3A Val, H6K Mavis |
| Kavieng | F6F-3, B-24, TBF-1C, P-38G | A6M2, G3M Nell, E13A Jake, Pete |
| Borpop | F6F-3, TBF-1C, B-24 | A6M2, B5N Kate, G3M Nell |
| Buka | F4U-1A, SBD-3, TBF-1C | A6M2, A6M3, D3A Val |
| Bougainville | F4U-1A, SBD-3, TBF-1C, B-25J | Pete, Jake, A6M2 |
| Shortland Is. | PBY, Kingfisher, OS2U | Pete, Jake, A6M2-N Rufe, H6K Mavis (seaplane base) |
| Santa Isabel | PBY, Kingfisher | Pete, Jake, Rufe, E13A (Rekata Bay seaplane base) |
| Florida Is. (Tulagi) | PBY, Kingfisher, OS2U | Pete, Jake, H6K |
| Guadalcanal | F4F-4, SBD-3, P-400, TBF-1C | A6M2, D3A Val, G4M Betty |
| Malaita, Rennell | PBY, Kingfisher | Pete, Jake |
| Santa Cruz | PBY, OS2U, F4F-3 | Pete, Jake, Rufe |
| Russell Is. | F4F-4, SBD-3, P-39D | A6M3, D3A2 |
| New Georgia, Kolombangara, Vella Lavella | F4U-1A / F6F-3, SBD-3, TBF-1C, P-38G | A6M3, D3A2, G4M, B5N |
| New Hebrides | F4F-4, SBD-3, B-17F, PBY | A6M2, G4M |
| Port Moresby | P-39D, Kittyhawk, B-26B, B-17F | A6M2, G4M, D3A |
| Milne Bay | Kittyhawk, P-400, Beaufort, Walrus | A6M3, D3A2 |
| Cooktown | P-39D, Kittyhawk, B-26B, PBY | A6M2, G4M, H6K |
| Cape Gloucester, Cape Hoskins | P-47D, P-38G, B-25J, A-20 | A6M3, D3A2, B5N / G4M, Ki-43 |
| Lae | Kittyhawk, P-38G, B-25J, A-20 | A6M2, A6M3, G4M Betty, D3A Val |
| Buna | P-40F, P-39D, B-25J, A-20 | A6M2, D3A Val |
| Gasmata | Kittyhawk, A-20 | A6M2, D3A Val, Pete |
| Cairns | PBY, Kingfisher, Kittyhawk, B-26B | H6K, E13A, Pete |
| Horn Island | Kittyhawk, P-39D, B-26B, PBY | A6M2, G4M |
| Finschhafen | P-38G, P-47D, A-20, B-25J | A6M3, D3A2, Pete, Jake |
| Kiriwina | Kittyhawk, P-38G, B-25J, A-20 | A6M3, D3A2 |
| Madang, Wewak | P-47D, P-38G, B-25J, A-20 | Ki-43, Ki-45, Ki-49, E13A |
| Manus | F6F-3, TBF-1C, SBD-3, PBY | Pete, Jake, Rufe |

Caveats: a few of these are historical judgement calls (for example Cairns and Horn Island aircraft, and the Army types at Madang and Wewak). Tell me which to change.
