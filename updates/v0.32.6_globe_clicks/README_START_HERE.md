# 0.32.6 globe test 6 (phase 4: clicks and orders on the globe)

Built on 0.32.5 globe test 5. DLL md5: 60c18f7a5faa26a4b0da79ac2f984f95. Not tested in game yet.

## What is new
1. Clicking on the globe now does what clicking on the flat map does. Click a task force or base icon to select it. Hovering an icon shows the game's own tooltip. The selected icon and the hovered icon draw a little larger.
2. Plot Course works on the globe. Select a task force, press the game's Plot Course button, click waypoints on the Earth, right-click to finish. The ruler tool works the same way.
3. The route lines the game draws (plotted course, the selected force's current route, the ruler line) are drawn on the globe too. They follow the flat map's own path, so they bend the same way the game's route finder does.
4. Dragging still spins the globe. A press and release that moves less than 6 pixels counts as a click.

Knobs in ModGlobe (dnSpy, top of the class): Clicks (on/off), PickPx (click radius in pixels, 16), RouteWidth (line width, 0.005).

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. The override file ModAssets/globe/earth.jpg is unchanged since 0.32.2. Keep the one you have.

## Test
1. Open the globe, click one of your task forces. Its panel should open as on the flat map, and the icon grows a little.
2. Hover a base: its tooltip appears.
3. With a task force selected, press Plot Course, click three points on the sea, right-click. The route should draw on the globe and the force should sail it (check on the flat map too).
4. Try the ruler.
5. Zoom in to drop to the flat map: the same route should be there.
6. Send output_log.txt plus a screenshot if anything looks off.

Not yet: range circles and markers on the globe (phase 5), and the battle square (phase 6).
