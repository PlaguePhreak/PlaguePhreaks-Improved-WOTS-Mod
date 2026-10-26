# v0.28.6 update (not run in the game yet)

You have 0.28.5 installed. This update edits 5 existing classes and adds NO hooks. Do it in this order and save the module after every step (File > Save Module).

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModFlight` | 1_ModFlight.cs.txt |
| 2 | Edit Class `ModAirDamage` | 2_ModAirDamage.cs.txt |
| 3 | Edit Class `ModAirCollide` | 3_ModAirCollide.cs.txt |
| 4 | Edit Class `ModDogfight` | 4_ModDogfight.cs.txt |
| 5 | Edit Class `ModPlayerOverride` | 5_ModPlayerOverride.cs.txt |

Edit Class: right-click the class with the plain name > Edit Class, select all, delete, paste the whole file, Compile (yellow warnings are fine), OK, File > Save Module.

Steps 1 and 2 belong together: step 1 divides the time step once for everything, step 2 removes the fuel-only division from 0.28.4. If you do only one of them, fuel will run 10 times too slow or too fast at time compression.

## What changed (from Docs/full_review_0.28.5_23Oct.md)
1. **Time compression no longer speeds up the flight physics.** The game hands the mod a time step multiplied by the compression twice. Speed, pitch, roll, turn rate and the collision look-ahead now run on battle seconds at x2, x5 and x10 (fuel already did since 0.28.4). Nothing changes at x1. `ModFlight.End`, `Pitch`, `Roll`, `TurnRate`; `ModAirDamage.Tick`.
2. **Friends on a collision course.** The plane that holds its course now checks that the other one can actually give way (not hand-flown, not in an acrobatic or scripted move, not already dodging a third plane, not near the sea). Two friends closing faster than 100 m/s both break, as before 0.28.5. `ModAirCollide.Avoid`, new `CanGiveWay`, constant `FastClosing`.
3. **The selected fighter stops firing again.** `ModDogfight.StopGuns` no longer skips the plane you have selected; its AI bursts used to run until the ammunition was gone.
4. **Scissors.** A scissors is no longer cut short by a new defence move at 4 s, and the turn is reversed every 2.8 to 3.6 s (was 1.4 to 2.2, less than the roll from one bank to the other). `ModDogfight.Fly`, `Move`, `StartDefend`.
5. **Chase power** only switches on when the target is flying away (within 60 degrees of straight away) and the chaser is already at 90% of its top speed. `ModDogfight.GunRun`.
6. **Hand-flown check.** Merely having a plane selected no longer counts as flying it by hand (the avoidance never steered the plane you were looking at). `ModPlayerOverride.IsManual`.

## How to tell it is installed (next log)
* Run the same 1v1 once at x1 and once at x10: the [ENERGY] and [FLIGHT] speeds should look alike now.
* Fewer friendly [COLLIDE] lines; `[AVOID]` pairs again when two friends close fast.
* Far fewer `[CHASE]` lines and a small "chase boosts" count.
* "scissors worked" in a [DOGFIGHT] line, if a Zero gets one.

## What I checked, and what I did not
Each file is the 0.28.5 file with the edits above applied by exact text replacement and checked by diff. I could NOT compile them this time (the DLL in the project folder is the 0.28.4 one, without ModPlayerOverride). If a Compile fails, paste the red line here.
