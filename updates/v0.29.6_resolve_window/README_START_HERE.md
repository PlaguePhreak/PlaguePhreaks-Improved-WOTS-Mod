# 0.29.6: the air auto resolve window gets the game's look

Built on your 0.29.5 DLL. The only changes: the auto resolve window (the one that opens when you press
Auto resolve on an air engagement in the campaign) is redrawn with the game's own panel, header bar,
buttons, fonts and text colours, and the menu says 0.29.6. Nothing about how the fight is worked out has changed.

## What it looks like now
- The game's dark container panel with its header bar, titled "Auto resolve: air engagement".
- Our aircraft on the left, enemy on the right (it was the other way round), with their points.
- "Chance of victory" in the game's highlight colour with a bar under it.
- Resolve and Fight it out are the game's own campaign buttons (they light up when you hover).
- The result screen shows Victory or Defeat as a heading and the dice in a tidy Ours / Enemy table.

## Install
1. Close the game.
2. Go to `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`.
3. Rename the old `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.5.dll` as a backup.
4. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
5. Start the game. The main menu should say **Version 0.29.6**.

## How to check it worked
Open an air engagement in the campaign and press Auto resolve. In `output_log.txt` you should see
`[AUTORESOLVE] window style: game look`.
If it says `plain look (N/6 game styles found)`, the game's style entries were not found, so the window
uses a plain dark look in the same layout. Send me the log if that happens.

## For dnSpy (not needed for the install)
1. Open `Assembly-CSharp.dll` in dnSpy and find the class `ModAirResolveWindow`.
2. Right-click it, pick **Edit Class (C#)**, select all, and paste `dnspy_reference\01_ModAirResolveWindow.cs.txt`.
3. Click **Compile**, then **File > Save Module**.
4. `02_ModVersion_strings.txt` lists the 0.29.5 to 0.29.6 text changes in `ModVersion`.
