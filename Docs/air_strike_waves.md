# Air strikes arrive as one wave

**What was wrong (found in the code)**
- When an air group enters a battle, `EngagementData.BreakUpAirGroup` splits it into flights. The flight size is `defaultFlightNumber` in each aircraft's data file (4 for Dauntless, Val and so on).
- Each extra flight is pushed back behind the first: 50 units per flight for your aircraft and **3x that (150 per flight) for the AI**. With 24 aircraft (6 flights), the last AI flight starts 750 units behind the first, so the flights arrive one after another over a few minutes.

**What changes**
- Flights spread out **side by side**, 40 units apart and alternating left and right, with only a small step back (10 per flight). The whole strike arrives together as one wave, while each flight of 4 still flies and attacks as a unit.
- This applies to both sides, so your own strikes also arrive together.

(Making one giant 24-plane flight instead isn't a good idea: the air formations only have places for 12 aircraft, so the rest would stack on the leader.)

## Step 1 - EngagementData.BreakUpAirGroup
1. Right-click **BreakUpAirGroup** (class **EngagementData**) > **Edit Method (C#)...**
2. Near the bottom of the loop is a line that moves the new flight's leader. It calls `.transform.Translate(new Vector3(...` with the same number twice, for example:
```csharp
list[0].transform.Translate(new Vector3(num4, 0f, num4), Space.Self);
```
(dnSpy may use other names than `list`, `num4` and `i`.)
3. Replace that whole line with this, using dnSpy's name for the list (the one before `[0]`) and for the loop counter (the `int` that counts flights, normally `i`):
```csharp
list[0].transform.Translate(new Vector3((i % 2 == 0 ? -1f : 1f) * 40f * (float)((i + 1) / 2), 0f, -10f * (float)i), Space.Self);
```
4. **Compile**, then **File > Save Module**.

The lines just above it, which set the old distance (`-50` and `3f`), can stay. They are just no longer used.

## Testing
1. Let an AI carrier strike of 12-24 aircraft reach your force.
2. On the tactical map or with the camera, the flights should appear side by side and arrive within a few seconds of each other, not minutes apart.
3. Your own strikes should also arrive together.

## Tuning
- `40f`: sideways gap between flights. Bigger = wider wave.
- `-10f`: step back per flight. 0 = a perfectly flat line.

Note: dive bombers, torpedo bombers and fighters may still arrive at slightly different times because they fly at different speeds and attack differently. I could not compile or run this.
