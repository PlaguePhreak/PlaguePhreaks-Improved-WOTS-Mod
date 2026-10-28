# Pacific War campaign tools (v0.29)

These scripts rebuild the `pacificwar` campaign files in Override.

- `render_map.py`: draws the 4 map pictures and the water mask from Natural Earth 10m land, minor islands and reefs (public domain). The current map is `python3 render_map.py 117 -8 136 <out>`, which covers 117E to 107W and 8S to 60N.
- `build_pacific.py`: locations (`mapLandLocations.txt`), names, and the sea route network (`seaWaypoints.txt`, a 5 degree grid plus helper points, with links checked against the water mask).
- `build_missions.py`: Japanese AI missions, nav aids, `setup.txt` map numbers, labels, objectives and the campaign list line.

Map numbers: the game's battle terrain grid is 240 pixels per degree, starting at 0 degrees longitude and 90S. `mapOriginXY` = (west lon * 240, (south lat + 90) * 240), `mapPixelWidth` = width in degrees * 240, and `mapWidthMetres` = `mapPixelWidth` * 488.28125. That last rule is the developer's own, as used for the Solomons and examplePacific.
