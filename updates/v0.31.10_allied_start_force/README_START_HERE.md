# 0.31.10: the RAN start force goes to the Allied AI

Built on 0.31.9 + changelog button (md5 5f7cf51e). DLL md5 `2acf8a88d5a5331f8cf54defeeb68cc0`. The main menu says **Version 0.31.10**.
**Not tested in game yet.**

## What you will see
- Start a NEW Allied (US) campaign. The "Australia Surface Force" the game gives you at Coral6 is no longer yours.
  As soon as the clock runs, it is renamed **RAN CRUISER FORCE 1**, turns yellow and sails under RAN command
  (patrol, escort, attack, refit at Cooktown, the same as every Allied AI group). It is the AI's first group.
- An Admiralty message says so. Clicking it opens the allied info window, not your orders.
- With this group out, the AI sends its next own group 15 to 25 days later (not 3 to 7), and still keeps at most 2.
- Saves older than 2 days of game time are left alone, so a campaign you are already playing keeps its Australian ships.
- Japanese campaign: nothing changes.

## Install
1. Close the game.
2. In `...\WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp.dll.03109` (backup).
3. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Start a new Allied campaign and unpause.
5. If it doesn't happen, look in output_log.txt for `[ALLIED] start force handed to the Allied AI`.

## For merging (other builds on 0.31.9)
- Classes changed: **ModAllied** and **ModVersion** only. No stock method, no new hooks.
- `ModAllied`: new fields `StartForceName` ("Australia Surface Force"), `StartForceDays` (2), private `startChecked`;
  new method `TakeStartForce()`; `Tick()` calls `TakeStartForce();` right after `Sync();`; `Sync()` resets
  `startChecked = false;` when a new campaign is loaded. The exact lines are in `dnspy_reference/ModAllied_changes.diff.txt`.
- `ModVersion`: `Current` = "0.31.10", one new changelog entry on top of `ChangelogBody`. Nothing else.
- The ships stay in the player-owned ship lists, so you can't buy a second Australia, Canberra or Hobart.

## dnSpy instead
1. Open the 0.31.9 changelog-button `Assembly-CSharp.dll` in dnSpy.
2. Right-click the class `ModAllied`, choose **Edit Class (C#)**, replace everything with `dnspy_reference\ModAllied.cs`, then **Compile**.
3. Do the same for `ModVersion` with `dnspy_reference\ModVersion.cs`.
4. **File > Save Module**.
