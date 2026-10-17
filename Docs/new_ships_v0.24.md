# v0.24 New ships (v0.24.1) and new aircraft (v0.24.2)

Status: files built, NOT tested (I can't run the game). Pending test.

## Credit
- **RamZ**: 84 warships and 93 aircraft come from his public Unit Catalog (he has said it is for public use). They are his work, not ours. He is also credited for the TTE merchant ships, which are believed to be his work.
- **TTE team**: 20 more warships and 22 aircraft (lists below), used with credit to them.
Credit is in the in-game book (CUSTOM SHIPS, CUSTOM AIRCRAFT and CREDITS pages) and in the README.

## What was added
- **v0.24.1 New ships**: 84 RamZ ships (Japan, USA, Australia) and 20 TTE ships = 104 ships. "Australia" covers Perth, County, Leander, N Class, T/U/V Class, Battle and Colossus classes (British designs that served in the RAN), set to the Australian nation.
- **v0.24.2 New aircraft**: 115 aircraft: 90 from RamZ, Corsair Mk II, Firebrand Mk 4 and Walrus Mk I (which the new Australian ships carry), and 22 from the TTE team.
- Both campaigns get the new units. Campaign 001 (player USA/Australia, AI Japan) and campaign 002 (player Japan). The player side can buy any new ship that was in service by the start date straight away; ships from after 7 Aug 1942 unlock at their historical date ("orderAvailable"). The AI side gets them at the historical date.
- New ships are in the shipyard list next to ships of the same nation and type.

## Files changed in the Override folder
- `unit\sea\allUnitsList.txt` (200 ships), `unit\sea\mountData.txt` (+56 mounts), `campaign\campaign001\seaUnits.txt` and `campaign002\seaUnits.txt` (+104 each), `language\english\dictionary\weapons.txt` (+134), `language\english\unit\sea\<ship>.txt` (104 new, each with a pool of ship names)
- `unit\air\allUnitsList.txt` (135 aircraft), `campaign\campaign001\airUnits.txt` and `campaign002\airUnits.txt` (+115 each), `language\english\unit\air\<aircraft>.txt` (115 new)
- Built from your current game files, so your other changes in these files are kept.

## Install (numbered steps)
0. **Get RamZ's ammunition folder first.** Your extracted `override` folder has no `ammunition` folder, but the new ships need it (their torpedoes and the `mod_ordnance` file live there). Without it the ships spawn as "Unknown" and sink. Open `Ram_s Unit Catalog 1.05d.7z` with 7-Zip File Manager, go into `override`, and extract the `ammunition` folder to `E:\mods\WOTS\custom mod\Ram_s Unit Catalog Release\override\ammunition`.
1. Open `Extras\copy_v0.24_files.bat` in Notepad and check the three paths at the top (RamZ folder, TTE folder, game folder). Change them if yours differ.
2. Double-click `copy_v0.24_files.bat`. It copies the 104 ship folders and 115 aircraft folders (3D models, a few GB) and RamZ's `materials\ammunition.txt`. It first saves your old one as `ammunition_original.txt` in the same folder.
3. Copy this repo's `Override` folder over the game's `override` folder and choose "Replace" when asked.
4. Do the book edit in `Docs\guide_book.md` (dnSpy, the ModGuide class) so the book shows the new pages.
5. Start the game, open the Museum and check that the new ships and aircraft load and float or fly.
6. Start a NEW campaign and check the ships and aircraft appear in the shipyard and air list.

Install ships and aircraft together: the new carriers carry the RamZ aircraft, so a missing aircraft folder can break a ship.

## Things to know
- All costs, supply/fuel (`resourceCost`), `sunkYield` and dates are my estimates (cost is RamZ's value; x2 for battleships, battlecruisers and carriers, x1.3 for heavy cruisers). Change them in `seaUnits.txt` / `airUnits.txt` if too cheap or dear.
- Some RamZ ships duplicate stock ones (Essex, Iowa and others); both show up in the shipyard.
- RamZ's `ammunition.txt` replaces the stock file (it is much bigger). To undo, copy `ammunition_original.txt` back over it.
- Gun mounts: an id that already exists in your `mountData.txt` is kept as it is; only new ids were added (RamZ's version wins over TTE's). So a few guns may differ slightly from RamZ's.
- Kamikawa Maru had no name file in TTE, so one was written (Kamikawa Maru, Kiyokawa Maru, Kinugawa Maru). TTE Perth was skipped because RamZ's Perth (perth42) covers it.
- Stock Yamato, Balao and Tench were already in the ship list but not in `seaUnits.txt`; I left them alone.
- Untested. If a ship crashes the Museum, send me its name.

## RamZ ships (84)
### Battleships (10)

| Ship | Nation | Unit ID |
|---|---|---|
| North Carolina (1943) | USA | northcarolina43 |
| South Dakota (1943) | USA | southdakota43 |
| Iowa (1945) | USA | missouri45 |
| Nebraska (1944) | USA | nebraska44 |
| Nevada (1944) | USA | nevada44 |
| Iowa (1944) | USA | iowa44 |
| Satsuma (1945) | Japan | satsuma45 |
| Yamato (1945) | Japan | yamato45 |
| Kongō (1944) | Japan | kongo44 |
| Fusō (1944) | Japan | fuso44 |

### Battlecruisers (1)

| Ship | Nation | Unit ID |
|---|---|---|
| Constellation (1943) | USA | constellation43 |

### Aircraft Carriers (16)

| Ship | Nation | Unit ID |
|---|---|---|
| Saratoga (1944) | USA | saratoga44 |
| Midway (1946) | USA | midway46 |
| Midway (1945) | USA | midway45 |
| Enterprise (1944) | USA | enterprise44 |
| Lexington (1941) | USA | lexington41 |
| Saratoga (1942) | USA | saratoga42 |
| Hornet (1942) | USA | hornet42 |
| Yorktown (1942) | USA | yorktown42 |
| Essex (1944) | USA | essex44 |
| Ranger (1942) | USA | ranger42 |
| Colossus (1945) | Australia | colossus45 |
| G15 (1945) | Japan | hakuryu45 |
| G14 (1945) | Japan | sekiryu45 |
| Zuikaku (1944) | Japan | zuikaku44 |
| Taihō (1944) | Japan | taiho44 |
| Shōkaku (1942) | Japan | shokaku42 |

### Light Carriers (3)

| Ship | Nation | Unit ID |
|---|---|---|
| Sangamon | USA | sangamon |
| Independence (1943) | USA | independence43 |
| Saipan (1945) | USA | saipan |

### Heavy Cruisers (13)

| Ship | Nation | Unit ID |
|---|---|---|
| Portland (1942) | USA | portland42 |
| Baltimore (1943) | USA | baltimore43 |
| Alaska (1944) | USA | alaska45 |
| Wichita (1944) | USA | wichita44 |
| New Orleans(1945) | USA | neworleans45 |
| Puerto Rico (1945) | USA | puertorico45 |
| Des Moines (1948) | USA | desmoines48 |
| County (1942) | Australia | county42 |
| Aoba (1944) | Japan | aoba44 |
| Maya (1944) | Japan | maya44 |
| Mogami (1944) | Japan | mogami44 |
| Myōkō (1944) | Japan | myoko44 |
| Tone (1944) | Japan | tone44 |

### Light Cruisers (13)

| Ship | Nation | Unit ID |
|---|---|---|
| Atlanta (1942) | USA | atlanta42 |
| Cleveland (1942) | USA | cleveland42 |
| St. Louis (1942) | USA | stlouis42 |
| Oakland (1943) | USA | oakland43 |
| Atlanta (1944) | USA | atlanta44 |
| Oakland (1945) | USA | oakland45 |
| Austin (1947) | USA | austin47 |
| Worcester (1947) | USA | worcester47 |
| Perth (1942) | Australia | perth42 |
| Leander (1944) | Australia | leander44 |
| Agano (1944) | Japan | agano44 |
| Isuzu (1944) | Japan | isuzu44 |
| Agano-Kai (1945) | Japan | agano_kai45 |

### Destroyers (19)

| Ship | Nation | Unit ID |
|---|---|---|
| Benson (1942) | USA | benson42 |
| Fletcher (1942) | USA | fletcher42 |
| Mahan (1942) | USA | mahan42 |
| Porter (1942) | USA | porter42 |
| Somers (1942) | USA | somers42 |
| Fletcher (1943) | USA | fletcher43 |
| Porter (1944) | USA | porter44 |
| Sumner (1944) | USA | sumner44 |
| Gearing (1945) | USA | gearing45 |
| N Class (1944) | Australia | n_class44 |
| T,U,V Class (1944) | Australia | tuv_class44 |
| Battle (1945) | Australia | battle45 |
| Ayanami (1942) | Japan | ayanami42 |
| Shiratsuyu (1942) | Japan | shiratsuyu42 |
| Kagero (1943) | Japan | kagero43 |
| Akizuki (1944) | Japan | akizuki44 |
| Shimakaze (1944) | Japan | shimakaze44 |
| Yūgumo (1944) | Japan | yugumo44 |
| Kitakaze (1945) | Japan | kitakaze45 |

### Destroyer Escorts (4)

| Ship | Nation | Unit ID |
|---|---|---|
| Rudderow (1944) | USA | rudderow44 |
| Tacoma (1944) | USA | tacoma44 |
| Chidori (1942) | Japan | chidori42 |
| Mutsuki (1942) | Japan | mutsuki42 |

### Submarines (5)

| Ship | Nation | Unit ID |
|---|---|---|
| Salmon (1944) | USA | salmon44 |
| Balao GUPPY | USA | balaoguppy |
| Gato (1943) | USA | gato43 |
| Balao (1944) | USA | balao44 |
| Type B3 | Japan | typeb3 |

## TTE ships (20)

| Ship | Type | Nation | Unit ID |
|---|---|---|---|
| Akitsu Maru | Light Carrier | Japan | akitsu_maru |
| Tribal | Destroyer | Australia | arunta |
| Bogue | Light Carrier | USA | bogue |
| Chitose | Light Carrier | Japan | chitose |
| Clemson & Wickes | Destroyer | USA | clemson |
| Colorado | Battleship | USA | colorado |
| Hiyō | Aircraft Carrier | Japan | hiyo |
| Hosho | Light Carrier | Japan | hosho |
| Kamikawa Maru | Light Carrier | Japan | kamikawa_maru |
| Kitakami | Light Cruiser | Japan | kitakami |
| New Mexico | Battleship | USA | new_mexico |
| Nisshin | Light Carrier | Japan | nisshin |
| Omaha | Light Cruiser | USA | omaha |
| Pennsylvania | Battleship | USA | pennsylvania |
| Ryūhō | Light Carrier | Japan | ryuho |
| Taiyō | Light Carrier | Japan | taiyo |
| Tennessee | Battleship | USA | tennessee |
| Type-A | Submarine | Japan | type_a1 |
| Type-C | Submarine | Japan | type_c |
| Yūbari | Light Cruiser | Japan | yubari |

## RamZ aircraft (93)

| Aircraft | Nation | Unit ID |
|---|---|---|
| SOC-1 Seagull | USA | soc1 |
| TBD-1 Devastator | USA | tbd1 |
| OS2U-3 Kingfisher | USA | os2u3 |
| P-43A-1 Lancer | USA | p43a1 |
| F2A-3 Buffalo | USA | f2a3 |
| F4F-3 Wildcat | USA | f4f3 |
| P-39D Airacobra | USA | p39d |
| P-40F-10 Warhawk | USA | p40f |
| SB2U-3 Vindicator | USA | sb2u3 |
| SBD-3 Dauntless | USA | sbd3 |
| B-26B Marauder | USA | b26b |
| F4F-4 Wildcat | USA | f4f4 |
| F4U-1A Corsair | USA | f4u1a |
| TBF-1C Avenger | USA | tbf1c |
| B-17G Flying Fortress | USA | b17g |
| B-25J-20 Mitchell | USA | b25j20 |
| F4U-1D Corsair | USA | f4u1d |
| F6F-3 Hellcat | USA | f6f3 |
| FM-2 Wildcat | USA | fm2 |
| P-38G-10 Lightning | USA | p38g10 |
| P-38K-1 Lightning | USA | p38k |
| P-47D-28 Thunderbolt | USA | p47d28 |
| PBJ-1J Mitchell | USA | pbj1j |
| SB2C-1C Helldiver | USA | sb2c1c |
| SBD-5 Dauntless | USA | sbd5 |
| B-29A Superfortress | USA | b29a |
| BTD-1 Destroyer | USA | btd1 |
| F4U-2 Corsair | USA | f4u2 |
| F6F-5 Hellcat | USA | f6f5 |
| F6F-5N Hellcat | USA | f6f5n |
| P-38J-15 Lightning | USA | p38j15 |
| P-38L-5 Lightning | USA | p38l5 |
| P-51D-20 Mustang | USA | p51d20 |
| P-63C-5 Kingcobra | USA | p63c5 |
| PB4Y-2 Privateer | USA | pb4y |
| PV-2D Harpoon | USA | pv2d |
| SB2C-4 Helldiver | USA | sb2c4 |
| SBD-6 Dauntless | USA | sbd6 |
| TBM-3 Avenger | USA | tbm3 |
| A-26C-45 Invader | USA | a26c45 |
| AU-1 Corsair | USA | au1 |
| F2G-1 Corsair | USA | f2g1_corsair |
| F2G-2 Corsair | USA | f2g2_corsair |
| F4U-4 Corsair | USA | f4u4_corsair |
| F4U-4B Corsair | USA | f4u4b_corsair |
| F7F-3 Tigercat | USA | f7f3 |
| F8F-1B Bearcat | USA | f8f1b |
| P-47M-1 Thunderbolt | USA | p47m1 |
| P-47N-15 Thunderbolt | USA | p47n15 |
| P-51H-5 Mustang | USA | p51h5 |
| P-61C-1 Black Widow | USA | p61c |
| P-82B Twin Mustang | USA | p82b |
| A2D-1 Skyshark | USA | a2d1 |
| AD-2 Skyraider | USA | ad2 |
| AM-1 Mauler | USA | am1 |
| Walrus Mk I | Australia | walrusmk1 |
| Beaufighter Mk VIc | Australia | beaufightermkvic |
| Corsair F Mk II | Australia | corsairmkii |
| Firebrand TF Mk IV | Australia | firebrandmk4 |
| D3A1 Val | Japan | d3a1 |
| A6M2 Mod 21 | Japan | a6m2mod21 |
| B5N2 Kate | Japan | b5n2 |
| E13A1 Jake | Japan | e13a1 |
| A6M3 Mod 22a | Japan | a6m3mod22a |
| A6M3 Mod 32 | Japan | a6m3mod32 |
| D3A2 Val | Japan | d3a2 |
| D4Y1-C Judy | Japan | d4y1c |
| N1K1 Rex | Japan | n1k1 |
| A6M5 Mod 52a | Japan | a6m5mod52a |
| D4Y2 Judy | Japan | d4y2 |
| A6M5 Mod 52c | Japan | a6m5mod52c |
| B6N2a Jill | Japan | b6n2a |
| B7A2 Grace | Japan | b7a2 |
| D4Y3a Judy | Japan | d4y3a |
| Ki-67 Otsu | Japan | ki67otsu |
| Ki-84 Frank | Japan | ki84otsu |
| N1K1-Ja George | Japan | n1k1ja |
| P1Y1 Ginga | Japan | p1y1 |
| A6M6 Mod 53c | Japan | a6m6c |
| A7M1 Sam | Japan | a7m1 |
| A7M2 Sam | Japan | a7m2 |
| A8K1 | Japan | a8k1 |
| D4Y5 Judy | Japan | d4y5 |
| G8N1 Rita | Japan | g8n1 |
| J5N2 Tenrai | Japan | j5n2 |
| J6K1 Jinpu | Japan | j6k1 |
| J7W1 Shinden | Japan | j7w1 |
| Ki-100 | Japan | ki100 |
| Ki-83 | Japan | ki83 |
| Ki-87 | Japan | ki87 |
| Ki-94-II | Japan | ki94ii |
| N1K2-Ja Shiden-Kai | Japan | n1k2ja |
| R2Y2 Keiun | Japan | r2y2 |

## TTE aircraft (22)

| Aircraft | Nation | Unit ID |
|---|---|---|
| P-39D Airacobra | USA | p400 |
| P-38E Lightning | USA | p38e |
| J2F-5 Duck | USA | j2f |
| PBY-5a Catalina | USA | pby |
| PBM-3 Mariner | USA | pbm |
| A-20G Havoc | USA | a20 |
| B-24D Liberator | USA | b24 |
| B-25J Mitchell | USA | b25j |
| Kittyhawk MkIA | Australia | p40 |
| Beaufighter Mk21 | Australia | beaufighter |
| Beaufort MkI | Australia | beaufort |
| Sunderland MkIII | Australia | sunderland |
| A5M4 Claude | Japan | a5m4 |
| A6M2-N Rufe | Japan | a6m2n |
| Ki-43-II Hayabusa | Japan | ki43 |
| Ki-45 Toryu | Japan | ki45 |
| Ki-49-IIb Donryu | Japan | ki49 |
| J1N1 Gekko | Japan | j1n1 |
| E14Y Glen | Japan | e14y |
| H6K4 Mavis | Japan | h6k |
| H8K2 Emily | Japan | emily |
| G3M2 Nell | Japan | g3m |

## If a TTE aircraft has no bombs
The TTE aircraft use bomb and torpedo files (for example `bomb_us_1600lb_ap`, `bomb_ij_800kg`). The script copies TTE's extra ammunition files only when the game lacks them. If a loadout is empty in the game, tell me the aircraft name.
