# v0.28.7 update (not run in the game yet)

You have 0.28.6 installed. This update edits 2 classes and has 1 one-word edit in the game's code. Save the module after every step.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModDogfight` | 1_ModDogfight.cs.txt |
| 2 | Edit Class `ModFlight` | 2_ModFlight.cs.txt |
| 3 | Edit Method `EngagementAI.CheckDefensiveConditions`: one word | 3_hook_lone_fighter.txt |

## What the 1v1 log (27 Oct, 0.28.6) showed
* 0.28.6 is in: no error lines, chase power came on, the Wildcat held 15.6 (above its 14.2 top speed) once boosted.
* **The Zero never fought because the stock game told it to retreat.** `EngagementAI.CheckDefensiveConditions` retreats any enemy air group that is a single fighter. The Zero attacked for 20 s, then flew to a waypoint 15 km away at full speed, the whole test. The same thing happened in the two earlier 1v1 logs. Step 3 fixes it.
* **The Wildcat could not catch it because it kept breaking off.** In boom-and-zoom mode every gun run ends after 30 s (`RunGiveUp`) with a zoom climb, then a climb "to get the energy to dive", then a dive: 37 s cycles in the log, each losing the distance the boost had won. Now a target that is running away (on a route, retreating, or busy with someone else, flying away from us, more than 300 m off) is chased straight in level flight at full power with no energy moves (`ModDogfight.Fleeing`, used in `Decide`, `Resume` and `Fly`).
* **Rudder wobble.** The rudder (0.26.5.8 yaw) was used at any range, 30 deg/s, up to 8 deg of slip, and the bank turn and the rudder both chased the same aim error, so the nose snapped left and right (the [YAW] lines alternate sign). It cost speed too (slip drag). Now the rudder is only used inside 600 m to line up a shot, at 12 deg/s, up to 4 deg, never while the plane is in a banked turn, with half the drag. `ModDogfight.GunRun`, `ModFlight` yaw constants and `Yaw`.

## How to tell it is installed (next log)
* 1v1: the enemy stays in `Attack_Unit`/`Dogfight` in the [STATUS] lines instead of `Follow_Nav_Points`/`Idle`, and there are gun bursts and hits.
* "[DOGFIGHT] ... is running away ... straight chase" lines when a target runs.
* Far fewer [YAW] lines, and only at short range.

## Not compiled
Same as 0.28.6: edits by exact text replacement, checked by diff, not compiled (no current DLL in the project folder). Paste any red line here.
