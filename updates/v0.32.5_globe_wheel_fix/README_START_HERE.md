# 0.32.5 globe test 5 (wheel direction fix)

Built on 0.32.4 globe test 4. DLL md5: 5ab16fc2d29fa11583cc9c1022bd4d05. Not tested in game yet.

## What this fixes (Aaron's report 29 Oct)
1. Scrolling out on the flat map did not open the globe, and a fast zoom-in on the globe bounced back to the globe. Both came from one bug: the mod read the mouse wheel backwards (the game's map has the zoom direction inverted, and the mod did not follow it). The wheel is now read the same way the flat map reads it.
2. Zooming in on the globe landed on the flat map fully zoomed out. It now lands at a middle zoom (knob ModGlobe.DropZoom = 0.4; 0 = closest, 1 = farthest).
3. A short cooldown (ModGlobe.SwitchCooldown = 0.8 s) so a fast wheel cannot flip between the two views in one go.

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. The override file ModAssets/globe/earth.jpg is unchanged since 0.32.2. Keep the one you have.

## Test
1. Start a campaign. Scroll out to the farthest zoom and give one more notch out. The globe should open where you were looking.
2. On the globe, zoom in fast. It should drop to the flat map at a middle zoom and stay there.
3. Scroll out again: the globe comes back only once you are at the farthest zoom.
4. The 3D button and F10 still toggle the globe.
5. Send output_log.txt plus a screenshot if anything looks off.
