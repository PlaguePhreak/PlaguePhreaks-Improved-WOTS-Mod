# v0.26.1 Flight core: energy, dive limit, stall, turn limit (flight_0.26.1.md)

**Status: written, not compiled, not tested.** Back up the DLL first. Do the steps in order. If a compile error appears, send me the exact text.

**What you will see**
- Dives build speed and climbs lose it, so boom and zoom now works with real physics.
- Planes cannot dive past a speed limit (fighters 125% of top speed, dive bombers 105%, other bombers 115%).
- A plane that gets too slow stalls: the nose drops until it has flying speed again. A `[FLIGHT] ... stalling` line is written.
- Turns get slower at high speed (heavy controls) and when nearly stalled. This replaces the Zero-only heavy controls rule.
- No switch: this is how planes fly from now on. (If the code ever throws an error it stops itself and logs `[FLIGHT] flight core failed`, so one bug cannot break a battle.)

**Why these numbers (from your two logs):** the game gave no speed change with pitch; the dive bombers reached only 9 of 12.6 speed in their dives, with pitch up to about 50 degrees. With this, a Val in a long dive should get close to 105% of top speed.

## Step 1 - replace the logger class
1. Find class **ModFlightLog**, right-click > **Edit Class (C#)...**, select all and paste `Docs/flight_log_ModFlightLog.cs.txt` (new version: stops logging wrecks, shows if the core is on). Do not compile yet (it needs Step 2).

## Step 2 - add the flight core class
1. Right-click **Assembly-CSharp** > **Add Class...** and paste all of `Docs/flight_model_ModFlight.cs.txt`.
2. **Compile** (both classes now compile).

## Step 3 - the two hook lines in UnitAir.UpdateMovementData
1. Right-click method **`UpdateMovementData`** in class **UnitAir** > **Edit Method (C#)...**.
2. The first line of the method body should be `ModFlightLog.Log(this);` (from Stage 0). Right under it add:
```csharp
ModFlight.Begin(this);
```
3. At the very end of the method, just before its closing `}`, add:
```csharp
ModFlight.End(this, duration);
```
4. **Compile**.

## Step 4 - stop the old fighter energy rule from fighting the new one
1. Class **ModDogfight**, method **`Energy`** > **Edit Method (C#)...**.
2. As the first line inside the method add:
```csharp
return;
```
(The old fighter speed and heavy-controls rule is now done by the flight core. If the compiler warns about unreachable code, that is fine.)
3. **Compile**, then **File > Save Module**.

## Test
1. Fly an air battle with fighters (a Wildcat vs Zero fight) and bombers (dive bombers and torpedo bombers).
2. Send `output_log.txt`. I will check: speed in dives vs top speed, stall lines, and that the turn rates changed as expected.
3. If anything looks wrong, send me the log. To go back to the old flying, restore your DLL backup.

## Next versions (each one only after the previous passes a test)
- 0.26.2 Idle flight mode and bank-based turning
- 0.26.3 Pitch control for fighters (gun run that really aims)
- 0.26.4 Fighter manoeuvres (rolls, yo-yos, loops, split-S, weave)
- 0.26.5 Bombers and torpedo planes on the new model
- 0.26.6 Formation flying
- 0.26.7 Damage affects flight, pilot skill, altitude performance, per-aircraft flight file, flight readout, avoidance
