# TTE merchant ships, oilers and transports

23 ships from the TTE mod (WOTS 1.08g7), added with permission from the TTE team. ALL custom merchant ships in the mod are by the TTE team, used with their permission, and are not our own work. Credit: TTE team (placeholder: add their exact credit line here, in the README and on the last book page when you have it).
Ship names come from TTE. A version with the ONI 209 index names (like "15-KMFM") is in `Extras/ONI_209_names`.

## Ships added
- Allied: heywood, president_jackson, attack_transport, hospital_ship, arcturus, harris, mount_hood, patapsco (oiler), manley (destroyer-transport), mccawley
- Japanese: generic_maru, type_1b, type_1c, type_1k, type_2tl, type_3a, type_a_merchant, ural_maru, akita_maru, kasagisan_maru, taihosan_maru, hakushika_maru, aratama_maru

Already in the stock game, so not touched: c3_cargo, kamogawa_maru, nippon_maru, cimarron.

## Install (numbered steps)
Game folder: `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets\override`

1. Copy the 25 ship folders (they hold the 3D models, about 17 MB each) from
   `E:\mods\WOTS\custom mod\TTE Override\WarOnTheSea_Data\StreamingAssets\override\unit\sea`
   into the game's `override\unit\sea`. Folder names are the ship ids listed above.
2. Copy this repo's `Override` folder over the game's `override` folder and choose "Replace" when asked. It replaces:
   - `unit\sea\allUnitsList.txt`, `unit\sea\mountData.txt`
   - `campaign\campaign001\seaUnits.txt`, `campaign\campaign002\seaUnits.txt`
   - `language\english\dictionary\weapons.txt`
   - `language\english\unit\sea\<ship>.txt` (new files)
3. Start the game and open the Museum. Check every new ship loads and floats.
4. Start a NEW campaign and check they appear in the shipyard.

## Notes
- The merged files are built from your current game files, so your other changes in them are kept.
- One gun was added to `mountData.txt`: `4in50Mark14`. `5in38Mark12` uses the stock game's version, not TTE's.
- Campaign `resourceCost` values (supplies/fuel) are my estimates, matched to similar stock ships. Change them in `seaUnits.txt` if too cheap or dear.
- Untested: I can't run the game.

## Left out on purpose
kamikawa_maru and akitsu_maru are carriers (seaplane tenders) in TTE, not merchants. They can be added later if you want them.

## Convoys
No convoy file needs to change. The AI builds convoys by picking a random ship of type Merchant (transports) and Oiler from the units it has, so the new ships join the random mix automatically. The ship folders must be in the game, or the ships won't be picked.
Note: the hospital ship also counts as a merchant, so it can turn up in a convoy.
