# v0.28.8 update (not run in the game yet)

You have 0.28.7 installed. This update edits 3 classes. No game code changes. Save the module after every step.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModDogfight` | 1_ModDogfight.cs.txt |
| 2 | Edit Class `ModFlight` | 2_ModFlight.cs.txt |
| 3 | Edit Class `ModAirCollide` | 3_ModAirCollide.cs.txt |

For each: in dnSpy right-click the class > Edit Class (C#), select all, paste the whole file, Compile. After step 3, File > Save Module. Step 3 may show yellow "unreachable code" warnings (the collision switch is a constant); warnings are fine, only red lines matter.

## What changed (from the 27 Oct review of the 0.28.7 DLL and log)
* **Zoom-climb loop (the critical one).** In the 4v4 log the Wildcats ended every gun pass with a zoom climb even at 190 km/h, under corner speed. The zoom was "spent" on its first tick, the plane dived back in slower than before, and the next pass started with even less speed. Now a pass only ends in a zoom when the plane is above 1.1 x corner speed; otherwise it extends level at full throttle until it has speed, then climbs (`ModDogfight.Attack`, both the overshoot branch and the boom-pass branch). A zoom gets 1.5 s before it can be called spent (`ModDogfight.Zoom`).
* **Air collisions off.** `ModAirCollide.On = false`. A quarter of the 4v4 losses were plane-to-plane collisions. Planes pass through each other as in the stock game again, avoidance never steers anyone, and the [BATTLE] line reads "collisions 0". The code stays in place: set `On = true` to turn it back on.
* **"fly failed" error log cap.** If `ModDogfight.Fly` throws, it is logged at most 20 times a session, now with a stack trace so the cause can be found. Before, a per-tick failure wrote one line every frame for every plane.
* **Collision look-ahead at time compression** (`ModFlight.End`, both calls to `ModAirCollide.Check`). Moot while collisions are off, harmless, in place for when they come back.
* **Less garbage per tick.** The energy sampler no longer allocates an array for every plane every tick (`ModFlight.AddSample`), and the collision builder reuses its Plane objects (`ModAirCollide.Build`). Only matters for stutter at x8-x10.

## How to tell it is installed (next log)
* "[DOGFIGHT] ... too slow to zoom: extending level to build speed" lines when a Wildcat ends a pass slow, followed by "extended to ... km/h, climbing away".
* No [COLLIDE] lines at all, and "collisions 0" in every [BATTLE] line.
* No zoom climbs starting under about 1.1 x corner speed (for the Wildcat: about 300 km/h in the [DOGFIGHT] lines).

## Not compiled
Same as before: edits by exact text replacement against the 0.28.7 source, checked by diff, not compiled. Paste any red line here.
