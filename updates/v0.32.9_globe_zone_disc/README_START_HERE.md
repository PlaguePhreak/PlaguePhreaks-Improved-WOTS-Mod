# 0.32.9 globe test 9 (phase 6 follow-up: the battle-zone disc)

Built on 0.32.8 globe test 8. DLL md5: 831b6169dc1979fc175105e8199bdd0d. Not tested in game yet.

## What changed since 0.32.8
1. The grey disc on the tactical map (the battle zone) was still drawn at the stock 50 km radius while the real limit was already 110 km. It now follows ModGeo.ZoneRadiusUnits, so it shows the 110 km zone.
2. The minimap picture code now says in output_log.txt why it did nothing, if it did nothing (lines starting with [BMAP]).

Everything from 0.32.7 and 0.32.8 is included.

## Install
1. Back up your current Assembly-CSharp.dll.
2. Copy this folder's Assembly-CSharp.dll over War on the Sea/WarOnTheSea_Data/Managed/Assembly-CSharp.dll.
3. The override file ModAssets/globe/earth.jpg is unchanged since 0.32.2. Keep the one you have.

## Test
1. Start a campaign battle: the grey disc on the tactical map should be much larger (110 km radius).
2. Send output_log.txt after the battle so the [BMAP] and [TFJOIN] lines can be checked.
