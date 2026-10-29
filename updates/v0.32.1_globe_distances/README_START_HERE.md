# 0.32.1 globe test 1: true distances (globe phase 1)

Built on the released 0.30 Mega Patch 01 DLL (md5 eb5ffe6b). DLL md5: dfaf539e8878e1c0728003f32bdc6b58. Not tested in game yet.

This is phase 1 of the globe plan. Nothing on screen looks new yet, except the base circles in the far north and south. The change is underneath: the campaign now measures distance on a round Earth.

## Install

1. Close the game.
2. In `WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp.dll.030`.
3. Copy `Assembly-CSharp.dll` from this folder into `WarOnTheSea_Data\Managed\`.
4. Start the game. The main menu should say **Version 0.32.1 globe test 1**.

No other files change. To go back, delete the new DLL and rename `Assembly-CSharp.dll.030` back to `Assembly-CSharp.dll`.

## What changed

- **Distances are measured on a round Earth.** The stock game measured straight across the flat map, so a degree east-west counted as equator size everywhere. Now east-west distances shrink to the real value the further you are from the equator.
- Everything that uses campaign distance follows: travel times, fuel, detection, strike, escort and supply ranges, and which forces join a battle.
- **On the equator nothing changes.** The game's own map scale is kept, so the Solomons plays almost the same (its distances shrink by about 1%).
- **Battles place far forces at their real distance.** A force joining from the east or west in the north now starts at its true gap.
- **Base spotting circles stay round in real distance.** On the flat map they become wider ovals in the far north and south, because the flat map stretches east-west there.
- **Battle coastline at 0 degrees longitude.** A battle near the Greenwich line now loads the land on both sides (stock left that tile blank). This matters for maps that cross 0 degrees, like a future world map.

## Pacific War examples (game scale)

| Route | Before | Now |
| --- | --- | --- |
| Pearl Harbor to Midway | 2,414 km | 2,214 km |
| Pearl Harbor to San Francisco | 4,590 km | 4,069 km |
| Kure to Truk | 3,869 km | 3,768 km |
| 10 degrees east-west at 52N (Aleutians) | 1,172 km | 721 km |
| 10 degrees east-west on the equator | 1,172 km | 1,172 km |

The game's map scale is about 5% bigger than the real Earth (that was already so in the stock game), so these are about 5% longer than an atlas gives.

## Please test

1. Main menu says **Version 0.32.1 globe test 1**.
2. **Solomons (either side):** play a few days. Travel, spotting and battles should feel the same as 0.30.
3. **Pacific War:** send a task force from Pearl Harbor toward San Francisco and note the arrival time. It should be about 11% shorter than in 0.30.
4. **Pacific War, far north:** look at a base circle in Japan or the Aleutians. It should be an oval, wider east-west than north-south.
5. **Battle:** fight a battle where a second task force joins from the east or west. Check it starts at a sensible distance and nothing looks wrong.
6. Send me `output_log.txt`. Look for lines starting with `[GEO]`: they list the map's corners and a few distances, before and after. Also look for any red errors.

## Switch

ModGeo.On (dnSpy, class `ModGeo`, top of the class): `true` uses round-Earth distances, `false` goes back to the stock flat ones.
