# 0.32.8 globe test 8 (phase 6: the battle square)

Built on 0.32.7 globe test 7. DLL md5: 492d80587a28e8e39f0027f990029474. Not tested in game yet.

## What is new
1. **Bigger battle square.** A battle's terrain was always a square about 234 km on a side, but only forces within 50 km joined, and any unit more than 50 km from the centre was parked. Both limits are now 110 km (knobs ModGeo.JoinRadiusMetres = 110000 and ModGeo.ZoneRadiusUnits = 11000, in battle units of 10 m). A task force up to 110 km from the attacked force is placed in the battle at its true position and can steam in. At 30 knots, 100 km takes about 1 h 50 min of battle time.
2. **Battle minimap shows the campaign map.** The minimap's background is now the campaign map's own picture of the same square (cut from the campaign map images, 240 pixels per degree), instead of the height-map shading. Knob ModBattleMap.On. Skirmishes keep the stock picture.

What it does not do: a force more than 110 km away stays out, and the campaign clock does not run during a battle, so a force cannot arrive from outside the square later.

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. The override file ModAssets/globe/earth.jpg is unchanged since 0.32.2. Keep the one you have.

## Test
1. Put two of your task forces about 80 to 100 km apart on the campaign map (the ruler helps), then get one of them into a battle. The log lines starting with [TFJOIN] say who joined and at what distance. The second force should appear in the battle far away, and you can sail it in.
2. In the battle, open the minimap: its background should be the campaign map picture of the area (log line [BMAP]).
3. Sail a unit out past 110 km from the centre: it gets the leaving-combat warning, then is parked, as before at 50 km.
4. Send output_log.txt plus a minimap screenshot if anything looks off.
