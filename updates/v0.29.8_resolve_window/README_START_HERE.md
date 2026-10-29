# 0.29.8: auto resolve window, second pass

Built on your 0.29.7 (fireball) DLL, so it keeps everything in 0.29.7. Only the auto resolve window
and the menu version (0.29.8) change.

## What changed after your screenshot
- The panel corners are now drawn at the same size as the game's own panels, so no more big cut-off octagon.
- The gold-bracket header bar is gone. The title is now in the same style as the Encounter panel: white "AIR AUTO RESOLVE" with a gold line under it.
- Buttons are the game's normal small buttons (RESOLVE, FIGHT IT OUT, OK), centred, the same size as BEGIN / AUTO.
- The panel fits its content, so there is no empty space at the bottom.
- The chance line is a little smaller and the bar thinner.

## Install
1. Close the game.
2. Go to `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`.
3. Rename the current `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.7.dll` as a backup.
4. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
5. Start the game. The main menu should say **Version 0.29.8**.

The log should still say `[AUTORESOLVE] window style: game look`.

## For dnSpy (not needed for the install)
1. Open `Assembly-CSharp.dll` in dnSpy and find the class `ModAirResolveWindow`.
2. Right-click it, pick **Edit Class (C#)**, select all, and paste `dnspy_reference\01_ModAirResolveWindow.cs.txt`.
3. Click **Compile**, then **File > Save Module**.
