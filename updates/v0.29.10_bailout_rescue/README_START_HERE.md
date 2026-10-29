# 0.29.10: downed airmen and PBY rescues

Built on 0.29.9 (the one you approved). The menu says **Version 0.29.10**.
I can't run the game, so keep your 0.29.9 DLL as a backup. I compiled it against the DLLs from your own Managed folder and checked it: only the classes listed below changed.

## Install
1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.9.dll`.
3. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Start the game. The main menu should say **Version 0.29.10**.

## What it does
**In battle (any battle)**
- Airmen who bail out and land in the sea now count as survivors.
- Stop one of your ships (5 knots or less) within about 300 m of an airman and he is picked up. Your own airmen are saved. Enemy airmen are taken prisoner. The Crew tab says so.

**After a campaign battle**
- Airmen still in the water go on the campaign map, like the ship survivors do: an orange marker for ours, a red one for the enemy's. It reads e.g. "About 3 men of B-25J and Wildcat aircrew".
- A message says how many are there. They last 36 hours (ship survivors last 24), and a few are lost every hour.
- If your ships picked up airmen in the battle, you get command points for them: 1 for every 4 of ours, 1 for every 10 prisoners.

**PBY rescues on the campaign map**
1. Launch a flying boat from an airfield in the normal way: PBY, PBM, H6K, H8K (Emily) or Sunderland.
2. Plot its course to the orange marker.
3. When it gets there, it lands, picks up as many airmen as it can carry and flies home by itself. Each flying boat carries 10, so one PBY is enough for a bomber crew.
4. You get command points: 1 for every 4 airmen, at least 1. If there are more airmen than seats, the rest stay on the marker.

- A cruiser's floatplane (Kingfisher, SOC, Walrus, Duck, Jake, Pete and others) also works, but it carries only 1 man.
- A task force that sails to the marker also picks them up.
- Red markers (enemy airmen): only a task force can take them prisoner, the same as ship survivors.
- A flying boat on a patrol route that happens to fly over the marker also picks them up and turns for home.

## In the log (output_log.txt)
- `[BAILOUT] 3 of our airmen still in the water after the battle: map marker 'B-25J aircrew'`
- `[BAILOUT] PBY ... landed on the sea and picked up 3 airmen of the B-25J aircrew. They are flying home (+1 command points).`
- `[BAILOUT] ... picked up an airman of Wildcat (ours)` (a ship in battle)

## For dnSpy (not needed if you use the DLL above)
1. **ModAirRescue** (NEW): right-click the `-` namespace > **Add Class (C#)...**, paste all of `dnspy_reference\01_NEW_ModAirRescue.cs.txt`, **Compile**.
2. **ModParachute**: right-click > **Edit Class (C#)...**, select all, paste `02_ModParachute.cs.txt`, **Compile**.
3. **ModCampaignRescue.Update**: add one line, see `03_ModCampaignRescue_Update.txt`.
4. **ModVersion**: change `0.29.9` to `0.29.10` in the two places listed in `04_ModVersion_strings.txt`.
5. **File > Save Module**.

## Settings (top of ModAirRescue)
`MarkerHours` 36, `BoatSeats` 10, `FloatSeats` 1, `AirmanPoints` 0.25, and the plane lists `FlyingBoats` / `Floatplanes`.
It uses the mod's Rescue option: turn that off and none of this happens.

## Not in this pack
- The enemy's own flying boats don't rescue their airmen yet.
- Bad weather doesn't stop a flying boat from landing yet.
- The logbook doesn't have a page about this yet.
