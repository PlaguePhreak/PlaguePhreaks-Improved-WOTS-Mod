# 0.32.11 globe test 11 (the globe in the main menu)

Built on 0.32.10 globe test 10. DLL md5: 7e73045231eb9937277f09ec29eb4ce0. Not tested in game yet.

## What is new
The main menu's video picture (the right-hand part of the screen) now shows the spinning Earth instead of the film,
with the day/night line from the real clock (UTC). The still menu image is hidden too. It uses the same
override/ModAssets/globe/earth.jpg as the campaign globe.

Knobs in ModGlobe (dnSpy, top of the class): MenuGlobe (on/off), MenuSpin (1.5 degrees per second), MenuLat (18),
MenuZoom (2.4 radii).

Everything from 0.32.1 to 0.32.10 is included.

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. Keep override/ModAssets/globe/earth.jpg where it is (it has been there since 0.32.2).

## Test
1. Start the game: the main menu shows the slowly turning Earth on the right, dark on the night side.
2. Open Campaign, Skirmish, Options and come back: the globe keeps turning, the menu buttons still work.
3. Start a campaign and quit back to the menu: the globe is back; the campaign globe (3D button) still works.
4. Send output_log.txt if the menu looks wrong (lines starting with [GLOBE]).
