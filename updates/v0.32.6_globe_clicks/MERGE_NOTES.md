# 0.32.6 merge notes

- **Base:** 0.32.5 globe test 5 (md5 5ab16fc2d29fa11583cc9c1022bd4d05).
- **Output:** md5 60c18f7a5faa26a4b0da79ac2f984f95.
- **Changed:** class ModGlobe only. No new hooks. Version strings (ModVersion) 0.32.5 -> 0.32.6 and a changelog entry. Four unused ModGlobe fields from 0.32.2 (markerRoot, markers, markerDirs, markerMats) and the old 5-argument AddEntry were pruned.

## ModGlobe changes
- Entry now carries the flat map's GameObjectAnimator (goa), its screen position and whether it is shown.
- New knobs Clicks, PickPx, RouteWidth; new fields downButton, downPos, hover, routeObj, routeMesh, routeSig, lastRouteMouse, miRoute.
- Drive: records mouse down; a release within 6 px is a click -> Click(ci, button). Each frame: Hover, RouteMouse, RouteLines.
- MouseMapPoint: ray from the globe camera against the sphere -> lat/lon -> map point via MapPoint.
- Click: right button ends Plot Course exactly like the game's map.OnClick handler (enablePlotCourse = false, SetCampaignCursor, ClearToolTip, PlotMobileCourse). Left button on an icon (not plotting) calls map.OnVGOPointerDown(goa), the same delegate the flat map uses (merge / multiple selection / SelectMapObject). Left button while plotting calls MoveMobileToDestination(currentMapObject, point).
- Hover/SetHover: calls map.OnVGOPointerEnter / OnVGOPointerExit for tooltips.
- RouteMouse: while plotting or using the ruler, calls the private CampaignInterface.UpdateRoutePathLine(x, y) by reflection whenever the mouse's map point changes.
- RouteLines: mirrors CampaignInterface.pathlines (LineMarkerAnimator.path, color) as a ribbon mesh on the sphere (render queue 3004), subdividing long legs, hiding the far side by vertex alpha. Rebuilt only when the lines or the view change (signature).
- PlaceEntries: hovered or selected icon drawn 1.3x.

Verified: CampaignManager decompile identical to 0.32.2 through 0.32.5; ilverify list identical to 0.32.4 apart from the AddEntry signature line.
