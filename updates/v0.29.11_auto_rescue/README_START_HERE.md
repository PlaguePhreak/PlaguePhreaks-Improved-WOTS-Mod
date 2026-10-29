# 0.29.11: auto rescue button

This build has everything from 0.29.10 (downed airmen, PBY rescues) plus an **auto rescue** button. Build it on 0.29.9, which you approved. You don't need to install 0.29.10 first.
The main menu says **Version 0.29.11**.

## Install
1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.9.dll`.
3. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Start the game and load a campaign.

## The button
On the campaign map, the column of buttons at the top left (BOOK, BELL, FUEL) has a new 4th button with the survivors icon. Hover over it to see "Auto rescue by flying boat".
- Click it to switch auto rescue on or off. When it's on, the button is lit orange. The game remembers your choice. It starts **off**.
- When it's on, the mod checks the map every couple of seconds. It looks for each orange "aircrew" marker that no rescue plane is heading for yet. Then it picks the **nearest** of your airfields that:
  - has a flying boat free (PBY, PBM, H6K, H8K Emily or Sunderland),
  - is not on launch cooldown,
  - and is close enough that the plane can fly there and back.
- It launches one flying boat, or two for a big crew of more than 10 men. The airfield gets its normal launch cooldown and the plane counts as "in the air", the same as when you launch one yourself. Scout planes go one at a time, as the game normally does.
- A message says what was sent, for example: "Auto rescue: 1 PBY is flying from Espiritu Santo to pick up 4 airmen of the B-25J aircrew (420 km)."
- The plane flies to the marker, picks up the airmen and flies home. You get command points the same as in 0.29.10.
- Auto rescue only launches during air operation hours. At night it waits until morning.
- It won't change which unit you have selected.

## Not covered by the button
- Floatplanes on cruisers are never launched automatically. You can still send them yourself.
- Ship survivors and enemy airmen still need a task force.

## Log lines (output_log.txt)
`[BAILOUT] auto rescue button added (off)`, `[BAILOUT] auto rescue on`, `[BAILOUT] Auto rescue: 1 PBY is flying from ...`

## For dnSpy (not needed if you use the DLL above)
1. Add Class: `01_NEW_ModAirRescue.cs.txt`, then `02_NEW_ModAutoRescue.cs.txt`.
2. Edit Class ModParachute: paste `03_ModParachute.cs.txt`.
3. ModCampaignRescue: the two small changes in `04_ModCampaignRescue_two_changes.txt`.
4. ModVersion: change `0.29.9` to `0.29.11` in the 2 places listed in `05_ModVersion_strings.txt`.
5. Save Module.

## Settings (top of ModAutoRescue)
- `MaxPlanes` 2
- `RangeMargin` 0.9 (it keeps 10% of the range in reserve)
- `CheckSeconds` 2
