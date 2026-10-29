# 0.32.5 merge notes

- **Base:** 0.32.4 globe test 4 (md5 41a9a1a3bfd455bb8554becba020476d).
- **Output:** md5 5ab16fc2d29fa11583cc9c1022bd4d05.
- **Changed:** class ModGlobe only. No new hooks. Version strings (ModVersion) 0.32.4 -> 0.32.5 and a changelog entry.

## ModGlobe changes
- New fields: lastSwitch (float), SwitchCooldown (0.8 s), DropZoom (0.4).
- New method Outward(WMSK map): returns the wheel axis in the flat map's sense (positive = zoom out), flipping it when map.invertZoomDirection is true. Used by ScrollOut and Drive.
- ScrollOut: opens the globe on a positive (outward) notch at zoom level >= zoomMaxDistance - 0.02, not inside the cooldown. Sets lastSwitch.
- Drive: wheel negative = zoom in (drops to the map at the closest globe zoom, outside the cooldown), positive = zoom out.
- DropToMap: flat-map zoom level = Lerp(zoomMinDistance, zoomMaxDistance, DropZoom) instead of min(max, min*6) which was the farthest zoom. Sets lastSwitch.

## dnSpy
Replace the whole ModGlobe class with dnspy_reference/ModGlobe.cs.txt, or edit the four spots above. Verified: CampaignManager decompile identical to 0.32.2/0.32.3/0.32.4; ilverify list identical to 0.32.4.
