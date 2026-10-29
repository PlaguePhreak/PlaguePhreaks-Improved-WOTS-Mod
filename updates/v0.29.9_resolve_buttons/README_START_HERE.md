# 0.29.9: auto resolve buttons sized like the game's

Built on 0.29.8. The only changes are the auto resolve buttons and the menu version (0.29.9).
The buttons are now sized to their text, like BEGIN and AUTO, with less space between them.
They used to be a fixed 170 wide.

## Install
1. Close the game.
2. In `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`, rename the current `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.8.dll` as a backup.
3. Copy the `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Start the game. The main menu should say **Version 0.29.9**.

## For dnSpy (not needed)
Class `ModAirResolveWindow`, method `Button`: the width is the label width + 40, minimum 76, and the height is 32.
The full class is in `dnspy_reference\01_ModAirResolveWindow.cs.txt` (Edit Class, paste, Compile, Save Module).
