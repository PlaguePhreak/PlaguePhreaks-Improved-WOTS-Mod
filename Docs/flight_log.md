# v0.26 Stage 0: flight logging (flight_log.md)

**Status: written, not compiled, not tested.** Back up the DLL first.

**What it does:** nothing you can see in the game. About once a second per aircraft it writes one `[FLIGHT]` line to `output_log.txt`: speed (actual / wanted, and the plane's max), height in metres (actual / wanted), nose angle (pitch), bank (roll), turn rate (actual / wanted), the speed penalty from turning, the current manoeuvre and attack type. One bad line switches the logging off by itself instead of breaking the battle.

**Why:** the new flight model (Stage 1 onwards) needs real numbers from today's planes to be tuned against, and later to prove the new movement does what it should.

## Step 1 - add the class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Delete what is there and paste all of `Docs/flight_log_ModFlightLog.cs.txt`.
3. **Compile**. If an error appears, send me the exact text.

## Step 2 - hook it into UnitAir
1. Find class **UnitAir**, right-click the method **`UpdateMovementData`** > **Edit Method (C#)...**
2. Click just after the method's first `{`, press Enter and paste:
```csharp
ModFlightLog.Log(this);
```
3. **Compile**, then **File > Save Module**.

## Step 3 - the test battle
1. Start an air battle (a carrier strike with fighters and bombers is best, so we get every type).
2. Let it run for a few minutes, with some dogfights and bomb or torpedo runs.
3. Close the game and send me `output_log.txt` (search it for `[FLIGHT]`).

## To switch it off later
Change `Enabled = true` to `Enabled = false` in `ModFlightLog` (**Compile**, **Save Module**). Leave the hook in place.

## What I will do with it
Work out, per aircraft type: how fast it really turns, climbs and dives, how much speed a hard turn costs, and where today's numbers disagree with the aircraft data. That gives the starting numbers for Stage 1 (bank and speed in turns).
