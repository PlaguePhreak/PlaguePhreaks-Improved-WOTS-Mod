# v0.25.2 Starting task forces rework (draft, untested)

Status: files and code written, not compiled or tested (the game cannot be run here). Needs the formations from `formations_v0.25.2.md` (formation numbers 9 to 17 below) and a NEW campaign to take effect. Back up your DLL and both `sea_missions.txt` files first.

## Your forces
Order of ships in each force matters: ship 1 leads and the next four fill the "big ship" slots of the formation (see formations_v0.25.2.md). Forces with fewer than 5 big ships put their destroyers in the remaining middle slots.

### US (campaign001)
| Force | Formation | Start | Ships |
|---|---|---|---|
| Enterprise Carrier Force | 12 Escorted Ring | Coral4 (next to New Hebrides) | Enterprise, North Carolina, Portland, Minneapolis, Atlanta, Balch, Benham, Ellet, Maury, Grayson |
| Washington Surface Action Group | 17 Surface Action Line | Coral2 | Washington, South Dakota (the extra US battleship), Indianapolis, Vincennes, New Orleans, Fletcher, Radford, Jenkins |
| San Francisco Cruiser Force | 9 Escorted Wedge | Sol4 | San Francisco, Helena, Buchanan, Aaron Ward, Cushing |
| Astoria Cruiser Force | 10 Escorted Box | Coral3 | Astoria, Juneau, Mayo, Niblack, Madison |
| Australia Surface Force | 11 Escorted Diamond | Coral6 (by Port Moresby) | HMAS Australia, HMAS Canberra, HMAS Hobart, Arunta, Warramunga, Napier |
| 4 destroyer patrols (2-3 ships, random), named after the first ship, e.g. "Farragut Destroyer Patrol" | line | Coral1, Coral5, Coral7, Coral0 | random from the Farragut, Mahan, Sims, Benham pool |
| 3-4 submarines (random) | | Sol3, Sol6, Slot8, Sol2 | Gato, Greenling, Grouper, Drum |

### Japan (campaign002)
| Force | Formation | Start | Ships |
|---|---|---|---|
| Shokaku Carrier Force | 15 Kido Butai (2 Carriers) | Bism2 (next to Rabaul) | Shokaku, Zuikaku, Hiei, Tone, Chikuma, Akigumo, Hatsukaze, Yukikaze, Amatsukaze, Maikaze, Yubari |
| Kongo Surface Action Group | 17 Surface Action Line | SPac3 | Kongo, Fuso, Myoko, Nachi, Haguro, Shigure, Samidare, Akizuki |
| Chokai Cruiser Force | 9 Escorted Wedge | SPac6 | Chokai, Tenryu, Yudachi, Murasame, Harusame |
| Suzuya Cruiser Force | 13 Escorted Echelon | Bism3 | Suzuya, Kumano, Kitakami, Amagiri, Asagiri, Yugiri |
| 4 destroyer patrols (2-3 ships, random), named after the first ship, e.g. "Farragut Destroyer Patrol" | line | Sol1, SPac4, Bism0, Bism6 | random from the Fubuki, Akatsuki, Asashio pool |
| 3-4 submarines (random) | | SPac8, Sol5, SPac2, SPac5 | I-15, I-17, I-19, I-16 |

Ships are skipped (and logged as `[STARTFLEET]` errors in output_log.txt) if a class or ship name does not exist. The new-class names were checked against the unit files; the older vanilla ones (Enterprise, Hiei and so on) come from the earlier tested v0.17.4 list.

## The AI forces (data, both campaigns)
`Override/campaign/campaign001/sea_missions.txt` (AI Japan) and `campaign002/sea_missions.txt` (AI US) are updated. The first 8 lines keep their positions, because the game's air groups use mission number 5 as a default (CampaignAI.missionIndex = 5), and new missions are added at the END of the file (lines 50 to 53).
- AI Japan: carrier force (2 carriers, battleship, 2 heavy cruisers, 5 destroyers, formation 15) at Bism2; surface action group (2 battleships, 3 heavy cruisers, 3 destroyers) at SPac3; two cruiser forces (SPac6, Bism3); destroyer patrols Bism0 (2), Sol1 (3), SPac4 (4), Bism6 (3); 4 submarines SPac8, Sol5, SPac2, SPac5.
- AI US: carrier force (1 carrier, battleship, heavy cruiser, light cruiser, 5 destroyers, formation 12) at Coral4; surface action group at Coral2; two cruiser forces (Sol4, Coral5); destroyer patrols Coral6 (2), Coral3 (3), Coral1 (4), Coral7 (3); 4 submarines Sol3, Sol6, Sol2, Slot8.
- AI forces are not named (as agreed). No force starts with a merchant or oiler in first place.

## Install
1. Copy both `sea_missions.txt` files over `Override/campaign/campaign001/` and `campaign002/`.
2. In dnSpy open **CampaignAI** > **CreateStandingMissions** > right-click > **Edit Method (C#)...**, select the whole method and paste `create_standing_missions_v0.25.2.cs.txt` over it, **Compile**, **File > Save Module**.
3. Start a NEW campaign. Check output_log.txt for `[STARTFLEET]` lines (one per force) and for any error line.

## Notes
- This replaces the earlier v0.17.4 method; the names of your forces are new (custom names).
- Untested: whether the new forces and formations look right on the map, vanilla ship names, and the AI balance (the extra battleships and second carrier).
