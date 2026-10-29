# 0.30: Allied AI (RAN task forces) and the self-sailing supply convoy

Built on 0.29.11 (auto rescue, which already has the 0.29.10 bail-outs). You don't need anything in between.
The main menu says **Version 0.30**. DLL md5 `88d60029...`. **Not tested in game yet.**

## Install
1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.11.dll`.
3. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Start the game and start a NEW Allied campaign (or load one). Allied AI only runs in the Allied campaign; in the Japanese campaign it stays off.

## What you should see
- **RAN groups in yellow.** 3 to 7 days in, a yellow RAN group sails from Cooktown (or Port Moresby / Milne Bay if Cooktown isn't yours). Names: `RAN CRUISER FORCE 1`, `RAN DESTROYER FORCE 2`, and from 3 months after the campaign start sometimes `RAN CARRIER FORCE n` (Colossus). At most 2 fighting groups at once; a new one comes 15 to 25 days after one is lost.
- **They do their own jobs**, checked every game hour: go home to refit when damaged or after 12 days at sea, escort the supply convoy / RAN merchants / your own merchant groups that look exposed, attack spotted enemy ships within 250 km they can beat, carrier groups send air strikes at enemy ships within 250 km, otherwise patrol.
- **RAN merchants.** Every 10 to 15 days, when one of your ports is short of supplies or fuel, `RAN MERCHANTS n` (borrowed US transports/oilers you don't own, with a RAN destroyer) loads cargo from Cooktown's stock, sails to that port and unloads, then goes home and disappears. They never carry troops and never take a port.
- **Click a yellow group** (or the supply convoy): an info window shows its ships, types, damage, what it is doing, days at sea, carrier planes and cargo. You can't give it orders.
- **Battles:** when a yellow group meets the enemy you get the normal encounter panel. ENGAGE plays the battle as usual. AUTO RESOLVE opens the new sea resolve window (same look as the air one): chance bar, RESOLVE or FIGHT IT OUT. Battles a yellow group fights give **no command points**.
- **Supply convoy:** now sails by itself to the port's sea point (that's why it used to sit still: it was aimed at a land point), is shown in yellow, re-sends itself if it stops, unloads when it arrives and then disappears. You can't move it.
- Messages for all of this appear in the Admiralty tab.

## What to check first
1. Wait for the first supply convoy: does it move now and arrive?
2. Wait 3 to 7 days: does a yellow RAN group appear and move?
3. Click it: does the info window open?
4. If something is wrong, send `output_log.txt`. Look for lines starting `[ALLIED]` and `[CONVOY]`.

## For dnSpy (not needed if you use the DLL above)
1. Add Class: `01_NEW_ModAllied.cs.txt`, then `02_NEW_ModSeaResolve.cs.txt`, then `03_NEW_ModAllyWindow.cs.txt`.
2. Edit Class ModConvoy: paste the whole of `04_ModConvoy_whole_class.cs.txt`.
3. The six one-line hooks in `05_six_hooks.txt` (CampaignManager.CheckDaily, CampaignManager.Check1Min, CampaignInterface.SelectMapObject, CampaignManager.CheckMobileEncounters, EngagementPanel.AutoResolve, ActionReport.CreateActionReport).
4. ModVersion: change `0.29.11` to `0.30` in the 2 places in `06_ModVersion_strings.txt`.
5. Save Module.

## Settings (top of ModAllied, edit with dnSpy)
`On` true, `MaxGroups` 2, `MaxMerchants` 1, `FirstDaysMin/Max` 3/7, `RespawnDaysMin/Max` 15/25, `MerchantDaysMin/Max` 10/15,
`CarrierAfterDays` 90, `CarrierChance` 0.3, `CruiserChance` 0.5, `PatrolKm` 600, `AttackKm` 250, `StrikeKm` 250, `EscortKm` 400,
`ThreatKm` 300, `PatrolDays` 12, `RefitDays` 5, `CargoSupplies` 1000, `CargoFuel` 50, `KeepSupplies` 2000 (Cooktown keeps at least this), `NeedSupplies` 3000.

## Known limits
- Compiled against Unity reference files from the internet, not the files on your PC (same way as 0.29.6 to 0.29.11).
- Yellow groups belong to your side in the game's lists, so they can show up in your task force lists and their ships can pick up airmen.
- If you choose ENGAGE, you command the RAN ships in that battle.
- The logbook doesn't have a page for 0.30 yet.
