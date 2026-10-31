# 0.32.20 "1.0 prep 1"

Base: 0.32.19 (md5 1e160db7). Everything in 0.32.19 stays.
New DLL md5: 84b5ca8a0f2c1eaf4cae0eae36655b54. The main menu says "Version 0.32.20 (1.0 prep 1)".

## What is new
1. **Historical start fleets (S1).** A NEW campaign of The Pacific War, Worlds at War: Allies or Worlds at War: Axis starts you
   with the task forces that were at sea or in port on 8 December 1941. The list is in `campaign/<id>/startfleets.txt`.
   - Allies / Pacific War: Enterprise (west of Oahu), Lexington (towards Midway), Saratoga (San Diego), the Pearl Harbor
     cruisers, the Asiatic Fleet (Philippines), 2 submarines off Wake. Worlds at War: Allies also gets the Iceland battle force,
     Yorktown + Ranger (Norfolk), Wasp (Bermuda), North Carolina + Washington (Norfolk) and the Australian squadron (Sydney).
   - Axis: Kido Butai (north of Hawaii, sailing home to Kure), the Southern Force and Malaya cruisers (off Malaya), the
     Philippines force, Ryujo's force (off Davao), the Main Body (Kure), the Wake invasion force (Kwajalein), 3 submarines off Oahu.
     Akagi, Kaga, Soryu and Hiryu join Kido Butai only if the CTM ship pack is installed (the game has no other model of them).
   - British, German and Italian fleets are left out until there are models for them.
   - If a ship name doesn't match the game's list, the first free ship of that class is used (a `[STARTFLEET]` log line says so).
2. **Merchants no longer lead a task force away (S3).** When the enemy is spotted, merchants and oilers turn and run. If one was
   the leader, the first warship now takes the lead before that happens, so the warships stay and fight. When a leader is
   sunk, a merchant is never picked as the new leader while a warship is left. Log tag `[MERCHANTLEAD]`.
3. **Beaten bombers break off (S4).** In the air auto resolve window, a bomber group (dive, torpedo, medium, heavy) that lost
   a quarter of its planes in a lost fight, or half its planes in any fight, turns for home. Works for both sides. The result
   text says so, and the log says `[AUTORESOLVE] strike abort`.
4. **WIP tags.** The campaign list now reads "The Pacific War (WIP)", "Worlds at War: Allies (WIP)" and "Worlds at War: Axis (WIP)".
5. **Nebraska** is now locked out of both Worlds at War campaigns too (it was still buyable there).

## Install
1. Back up `WarOnTheSea_Data\Managed\Assembly-CSharp.dll`, then copy this folder's `Assembly-CSharp.dll` over it.
2. Copy this folder's `override\campaign` folder onto `WarOnTheSea_Data\StreamingAssets\override\campaign`
   (adds `startfleets.txt` to pacificwar, wawallies and wawaxis, and replaces the two Worlds at War `seaUnits.txt` files).
   - If you install the CTM pack too, install it AFTER this: its Worlds at War `seaUnits.txt` files include the Nebraska lock.
3. Campaign names (WIP tags). Open `StreamingAssets\override\language\english\campaign\campaigns.txt` in Notepad and change
   the name (the 2nd part of the line, between the first two `=` signs) of three lines:
   1. `pacificwar=Experimental. WIP might not work=...` becomes `pacificwar=The Pacific War (WIP)=...`
   2. `wawallies=Worlds at War: Allies=...` becomes `wawallies=Worlds at War: Allies (WIP)=...`
   3. `wawaxis=Worlds at War: Axis=...` becomes `wawaxis=Worlds at War: Axis (WIP)=...`
   Save. (Or copy this folder's `override\language\english\campaign\campaigns.txt` over yours: it is your 29 Oct file with
   only those three names changed. Only do that if you haven't edited the file since.)
4. Start a NEW campaign to get the start fleets. Saves from 0.32.15 and later still load.

## Testing
1. Start Worlds at War: Allies (WIP). On the map: Enterprise west of Oahu, Lexington towards Midway, a force at Reykjavik,
   two at Norfolk, one at Sydney. `output_log.txt` has `[STARTFLEET] startfleets.txt: 12 historical task forces, ... ships`.
2. Start Worlds at War: Axis (WIP). Kido Butai north of Hawaii sails for Kure on its own.
3. Find an enemy convoy whose first ship is a merchant (or set one up). When it sees you, look for `[MERCHANTLEAD]` in the log:
   the escorts should come at you while the merchants run.
4. Let an air fight go to auto resolve with your fighters against enemy bombers. If the bombers lose, the result text ends with
   "The enemy's ... broke off the attack and turned for home." and they fly back.

## dnSpy (if you'd rather edit your own DLL)
Add the classes `ModStartFleets` + `StartFleetLine`, `ModMerchantLead` (build_tools), replace `ModAirResolve` with
build_tools/ModAirResolve.cs, then these three one-line edits:
1. `CampaignAI.CreateStandingMissions`: add `ModStartFleets.Add(list, list2, list3, list4, list5, list6);` right above
   `ModShipPick.FixStart(list, list2);`
2. `EngagementAI.RetreatAllMerchants`: add `ModMerchantLead.BeforeRetreat(otherSea);` as the first line.
3. `EngagementAI.SwitchToNewLeader`: change `Unit unit = list2[0];` to `Unit unit = ModMerchantLead.Pick(list2);`

Build notes: compiled with Roslyn against net35 + Unity 2017.4 SDK refs and the 0.32.19 DLL, merged with the 0.32.19 Patcher
(NOHOOKS=1, STRINGS=strings20.txt), hooks added by Fix20 (Cecil). Full decompile diff vs 0.32.19 = only the items above;
assembly references unchanged; ilverify error list identical to 0.32.19.
