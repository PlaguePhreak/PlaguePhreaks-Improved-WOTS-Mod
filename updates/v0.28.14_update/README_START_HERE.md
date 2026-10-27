# v0.28.14 update: aircraft control panel + own-bomb blast fix

One new class and four small edits. In dnSpy, after each edit: **Compile**. When all are done: **File > Save Module**.

## 1. Add the new class ModAirPanel
1. In dnSpy, right-click the `-` (empty namespace) folder of Assembly-CSharp > **Add Class (C#)**.
2. Delete everything in the window and paste all of `1_ModAirPanel.cs.txt`. **Compile**.

## 2. CombatInterface.SetUnitNavigationPanel (slider ranges)
1. Open `CombatInterface`, find the method `SetUnitNavigationPanel`, right-click > **Edit Method (C#)**.
2. Find this line (about two thirds down):
   `heightChange.value = currentUnit.wantedHeight;`
3. Add this new line **just above** it:
   `ModAirPanel.Limits(this);`
4. **Compile**.

## 3. CombatInterface.SetSpeedText (speed slider text)
1. Find the method `SetSpeedText`, **Edit Method (C#)**.
2. Add these lines as the **first lines** inside the method (right after the opening `{`):
   `if (ModAirPanel.SpeedText(this)) { return; }`
3. **Compile**.

## 4. CombatInterface.UpdateSelfInterface (the SPD number)
1. Find the method `UpdateSelfInterface`, **Edit Method (C#)**.
2. Find this line:
   `currentUnitTexts[2].text = Utilities.ConvertMetrePerSecondToKnots(currentUnit.currentSpeed).ToString("F0");`
3. Add this new line **just below** it:
   `ModAirPanel.CurrentSpeed(this);`
4. **Compile**.

## 5. Stock bug: a plane is killed by its own bomb's blast (skip bombing)
1. Open `AmmunitionDamage`, find the method `OnCollisionEnter`, **Edit Method (C#)**.
2. Find this line:
   `else if ((Object)(object)component.unitAir != (Object)null)`
3. Replace it with:
   `else if ((Object)(object)component.unitAir != (Object)null && component.unitID != firedByUnitID)`
4. **Compile**.

Then **File > Save Module**.

## What changes in game (aircraft only, ships untouched)
- Speed reads in **km/h** (metric option) or **mph** (imperial option), the same numbers as the logs and the F8 readout. Before it was knots, so 350 on the panel was about 650 km/h.
- The speed slider runs from just above the plane's stall speed (x1.15) to its real top speed in the mod (F4U-4 Corsair 702 km/h). Before it ran from 100 knots to the data file's top speed.
- The height slider goes up to the plane's ceiling instead of 3330 m for everyone: Wildcat about 10500 m, F4U-4 Corsair 12000 m (the cap). Planes without a hand-set row keep 3330 m. The engine still loses power above its critical altitude, so a plane climbs slowly up there.
- The plane that drops a bomb is no longer hurt by that bomb's blast. Other planes near the blast still are.
- The log shows `[PANEL] F4U-4 Corsair: speed slider ... to 702 km/h, height slider up to 12000 m` when you select a plane.

## Knobs (top of ModAirPanel)
- `CeilingMax = 12000f` metres. Lower it if planes flying very high spoil the game (AI fighters only fight up to 6500 m).
- `MinSpeedOverStall = 1.15f`. The slowest speed the slider allows, as a multiple of the stall speed.
- `On = false` turns the whole panel change off.

## Check
Select a plane in a battle. The SPD number should now be about the same as `speed` x 36 in the `[FLIGHT]` log line, and the speed slider's right end should read the plane's top speed in km/h.
