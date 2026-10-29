# 0.30.1 low flight: aircraft can fly down to 20 m

Built on the **0.30 Mega Patch 01** DLL (md5 eb5ffe6b...). New DLL md5 **f3c92a38f5a174a4b9263d753ce115a2**.
Only 11 numbers changed. No new code, no hooks, no version text change (menu still says "Version 0.30 Mega Patch 01").

## Install
1. Back up `War on the Sea\WarOnTheSea_Data\Managed\Assembly-CSharp.dll`.
2. Copy this folder's `Assembly-CSharp.dll` over it.

## Why planes stayed at about 120 m
- `ModFlight.Pitch`: while a fighter aims its guns it was not allowed to point the nose down below about 100 m, and was forced nose-up below 120 m.
- `ModDogfight`: every dogfight height order was clamped to at least 200 m (300 m when extending away).
- `ModDogfight.NeedsPullOut`: any dive of 12 degrees or more pulled out with 100 m to spare.
- Stock `UnitAI.BreakAwayFromUnit`: break-away height never below 40 m.

## Or do it yourself in dnSpy (same result)
In dnSpy each line is: open the class, find the method, right-click it > **Edit Method (C#)**, change the number, click **Compile**. Game units are 10 m, so `2f` = 20 m.

1. `ModFlight` > `Pitch`: change `num3 = Mathf.Clamp((y - 10f) * 1.5f, 0f, 60f);` to `(y - 2.5f)`.
2. Same method: change `if (y < 12f)` to `if (y < 2f)`.
3. `ModDogfight` > `SetHeight`: `Mathf.Clamp(h + num, 20f, Ceiling(u))` -> `2f`.
4. `ModDogfight` > `GunRun`: `Mathf.Clamp(position.y - num3, 20f, Ceiling(u))` -> `2f`.
5. `ModDogfight` > `Fly`: `Mathf.Clamp(position.y, 20f, 650f)` -> `2f`.
6. `ModDogfight` > `Move` (the one with 6 parameters): two lines `Mathf.Max(30f, y - ...)` -> `4f`, and `Mathf.Max(20f, position.y - 8f)` -> `2f`.
7. `ModDogfight` > `NeedsPullOut`: last line `num3 * 1.2f + 100f` -> `30f`.
8. `UnitAI` > `BreakAwayFromUnit`: `wantedHeight < 4f` and `wantedHeight = 4f` -> `2f` both.
9. File > Save Module.

Tip: if dnSpy's C# compile complains in a big class like ModDogfight, use **Edit IL Instructions** instead and change the `ldc.r4` number at the same spot.

## Not changed
- Aerobatics still need room (Immelmann 600 m, others 1000 m).
- A fighter flying waypoints that is more than 150 m under the height it cruised at climbs back (`ModFlight.IdleClimb`, only above 400 m). Say if player orders to go low should override this.
- Terrain/island avoidance is unchanged.
