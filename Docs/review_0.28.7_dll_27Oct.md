# Review of the 0.28.7 DLL and the 27 October log (1v1 then 4v4)

Sources: the uploaded `Assembly-CSharp.dll` (decompiled, 35 Mod classes), the log `c814a48c` (3,277 lines, 34 to 492 s, one 1v1 Wildcat against Zero at 1000 m and then a 4v4), and the earlier reviews. Nothing was run by me.

**Install check: the DLL is 0.28.7 complete.** `ModFlight` divides the time step in `End`, `Pitch`, `Roll`, `TurnRate`; `ModAirDamage.Tick` no longer divides; `ModAirCollide` has `CanGiveWay` and `FastClosing`; `ModDogfight` has `Fleeing` and `YawRange`; `ModPlayerOverride.IsManual` ends in `return false`; the three `CombatInterface` slider hooks, the `ModAAEvade` hook, the `DamageableAir` hook, the two auto-resolve hooks and the one-word `EngagementAI` edit (`otherAir.Count == 0`) are all in. No `__0` duplicate classes. The log has no error, exception or "failed and stopped" line.

## A. Critical issues (must fix)

**A1. Zoom climb loop when the plane is already slow.** `ModDogfight.Attack` ends a pass with `SetPhase(2)` (zoom) when it is about to fly past the target. `Zoom` ends at once when the speed is under 90% of corner speed (`spent`), calls `Decide` and `Resume`, which puts the plane back in phase 0, and `Attack` sends it straight back into the zoom in the same second. The log shows it: "passing Zero, zoom climb away" three times at 191 s (lines 889, 901, 921), and the pattern "passing Zero, zoom climb away" followed within 10 to 15 s by "slow for 4 s at 24x km/h ... unloading and accelerating" seven times in the 1v1. Every zoom from a low speed bleeds the Wildcat to 240 km/h (corner 324), the recover move spends 14 s getting it back, and the Zero shoots it in between: the Wildcat was below corner speed 70 to 100% of the time, took 10 hits, scored 0, and left with 80% wing damage. This is the single biggest reason the Wildcat loses every 1v1. Fix in F1.

## B. Important issues (should fix)

**B1. Two collisions in a 4v4 (25% of the losses).** A Zero-Zero "bad collision" at 59 m/s after three Zeros tangled for 10 s (seven [AVOID] lines between -23604, -22828 and -23216 from 1794 to 1930), and a Zero-Wildcat head-on at 193 m/s after both had broken at 1.3 s and again at 0.4 s. Both planes were already breaking when they hit: the break (0.9 s, 90% of the turn limit, 25 m of height) is too small to clear a head-on at 190 m/s in 0.4 s. See D for what to do about it.

**B2. `ModDogfight.Fly` has no cap on its error log.** The `catch` writes `[DOGFIGHT] fly failed: ...` every tick for every fighter with no `failed` flag or counter (every other class has one). A lasting exception (a game update that renames a field, another mod) would write thousands of lines a second and stall the game. Fix in F2.

**B3. Avoidance looks ahead in frames, not seconds, at time compression.** `ModAirCollide.Avoid` is called from `ModFlight.Begin` with no time step and uses `AvoidHorizon` (2 s) of real velocity, so it is right at any compression. But `Check` is called with `duration` from `End`, which is now battle seconds (0.28.6), so the collision look-ahead at x10 is one tenth of a frame of movement: a pair that crosses between two ticks can be missed, and one that is caught is caught late. Not seen in the log (both collisions were caught). Low risk; F3 has a one-line fix.

## C. Minor issues and code smells

* **C1. Allocation per tick.** `ModFlight.Sample` allocates a two-element array every tick per fighter; `ModAirCollide.Build` allocates a `Plane` object per plane per frame (with 72 a side, about 150 objects per frame). Both feed the garbage collector and can cause small hitches in big battles. Fix in F4 (pooling), cosmetic in small fights.
* **C2. `FindAttackerOfFriend` is O(n cubed)** (once a second per fighter, for every friend it scans all planes twice). Fine at 12 v 12; at the config limit of 72 a side it is roughly 3 million distance checks a second. Only matters if you see stutter in big battles.
* **C3. Log caps and [BATTLE] counters are per game session**, not per battle (the 4v4 in this log inherited the 1v1's counts: "kills ours 1" was the collision). Testing only.
* **C4. `ModAirCollide.On` and the other `const bool` switches are folded into the compiled code**, so flipping one needs an Edit Class and recompile, not just a value change. Worth knowing; not a bug.
* **C5. All hooks are edits inside `Assembly-CSharp.dll`.** A game update replaces that file and removes the whole mod; any other DLL mod must be merged by hand in dnSpy. Inherent to this modding method; keep the per-version folders (you do).
* **C6. `[FIGHTER] ... CAP -> ...` logs twice for the same pair** (lines 1786 and 1790): harmless duplicate from `ModFighterRules.PreferAir`.
* Fine: no race conditions (Unity single thread); null checks on `unitAI`, `unitData`, `weaponParticle` are consistent; each class has a `failed` latch except `ModDogfight.Fly` (B2); the hit path (`DamageableAir` hook) has the `dead` guard against recursion.

## D. Air collision analysis and recommendation

**What the game itself does.** Stock War on the Sea has no plane-to-plane contact at all; aircraft pass through each other. Bullet hits are particle collisions (`AAAParticleCollisions` to `DamageableAir`) and have nothing to do with the mod's collision system. So everything about mid-air collisions lives in one mod class, `ModAirCollide`, called from two places in `ModFlight` (`Begin` calls `Avoid`, `End` calls `Check`) and reporting into `ModAirDamage.CollisionHit` and `ModAirFormation.Yield`.

**Removing it is safe and clean.** Set `public const bool On = false;` at the top of `ModAirCollide` and recompile the class (Edit Class). `Check` and `Avoid` return at their first line; nothing else in the game or the mod depends on them. Side effects: none on hit detection, AI targeting, physics or visuals. What you lose: the "collisions ... avoided" counts go to zero in the [BATTLE] line (cosmetic), the formation yield (`ModAirFormation.Yield`) is never called because only `Avoid` calls it, and planes can again fly through each other, which looks odd in a head-on pass at close zoom.

**Should you?** The numbers so far: 7 collisions in the 12 v 12 multi log, 2 in this 4v4, 2 in the 24 v 36. About 20 to 30% of all losses in the tests have been collisions, which is far above the real rate (a few percent of losses, mostly in formation or in head-on passes). The cause is the game's own dogfight geometry: both AIs aim lead pursuit straight at each other, so a head-on pass at 190 m/s closing is the normal case, and a 0.9 s break cannot clear it. Avoidance also costs the fight: 38 [AVOID] lines here, each a 0.9 s break that throws the plane off its gun run.

**Recommendation: keep the system, but make it rare.** Three changes in `ModAirCollide`, F5 below:
1. A collision is only lethal in a true head-on above `CrashSpeed` for both sides (raise `CrashSpeed` from 90 to 200 m/s, like `FriendlyCrashSpeed`); below that it is damage and a lost part (`baseKill` 0.5 becomes 0.15). Planes that touch still pay; they rarely die.
2. Avoidance starts earlier for a fast closing: `AvoidHorizon` 2.0 to 3.0 s, and the break lasts 1.5 s instead of 0.9 with a 40 m height change, so one break clears a head-on.
3. Halve the collision radius (`RadiusScale` 0.42 to 0.25): the planes' boxes are generous now (a Zero counts as 4 m; a real hit needs the fuselages or wings to overlap).
If after that collisions are still above about 5% of losses, switch it off with `On = false`; nothing else needs to change.

## E. Log findings

| Line(s) | Finding | Severity | Action |
|---|---|---|---|
| whole log | No exception, error or "failed and stopped" | - | none |
| 181 to 1561 | The lone enemy Zero fought for the whole 1v1 (`Attack_Unit` throughout): the 0.28.7 one-word edit works | - | none |
| 889, 901, 921 | "passing Zero, zoom climb away" three times in one second | critical | F1 |
| 577, 777, 965, 1117, 1293 (7 in all) | "slow for 4 s at 24x km/h ... unloading" after each zoom; Wildcat below corner speed 70 to 100% | critical | F1 (same cause) |
| 661 to 1561 | 10 hits on the Wildcat, 0 on the Zero; Wildcat leaves with 80% wing damage at 1513 | important | follows from A1; also tactics (the Wildcat should not boom-and-zoom from level energy) |
| 1958 | Zero-Zero collision at 59 m/s after a 10 s tangle of three Zeros (1794 to 1930) | important | D / F5 |
| 2366 | Zero-Wildcat head-on at 193 m/s, both had broken at 1.3 and 0.4 s | important | D / F5 |
| 333 to 1473 | [AVOID] pairs between the two 1v1 planes (both break: correct for enemies) | harmless | none |
| 1786, 1790 | duplicate [FIGHTER] line | harmless | none |
| no [YAW] lines at all | the 0.28.7 rudder change is in; the rudder was never needed inside 600 m in this log | - | none |
| no [CHASE] lines | the 0.28.6 chase condition is in; no straight chase happened here | - | none |
| [BATTLE] 401 "kills ours 1" | that kill is the Zero-Zero collision, not a gun kill | unclear/cosmetic | C3 |
| no [PLAYER] lines | the player did not move a slider; override not exercised | - | none |

## F. Suggested fixes

**F1 (A1). No zoom from a low speed; a zoom lasts at least 1.5 s.** Class `ModDogfight`:
1. Method `Attack`, the overshoot branch: find the last `else` of that chain:
```
			else
			{
				ModDogfight.SetPhase(u, s, 2, now, 7f, "passing " + ModDogfight.Name(target) + ", zoom climb away");
			}
```
   and replace it with
```
			else if (ModDogfight.FastEnough(u, 1.1f))
			{
				ModDogfight.SetPhase(u, s, 2, now, 7f, "passing " + ModDogfight.Name(target) + ", zoom climb away");
			}
			else
			{
				// v0.28.8: too slow to zoom (a zoom from under corner speed stalled the Wildcat every pass): extend level and accelerate instead
				s.move = 4;
				ModDogfight.SetPhase(u, s, 6, now, ModDogfight.ExtendMax, "passing " + ModDogfight.Name(target) + " at " + (u.currentSpeed * 36f).ToString("F0") + " km/h, too slow to zoom: extending level to build speed");
			}
```
2. Same method, the fighter branch `if (targetIsFighter && (passed || inRun > ModDogfight.RunGiveUp))`: change `if (s.mode == ModDogfight.ModeBoom)` to `if (s.mode == ModDogfight.ModeBoom && ModDogfight.FastEnough(u, 1.1f))`.
3. Method `Zoom`: change `bool spent = zr != null && u.currentSpeed < zr.cornerSpeed * 0.9f;` to `bool spent = zr != null && u.currentSpeed < zr.cornerSpeed * 0.9f && now - s.phaseStart > 1.5f;`.

**F2 (B2). Cap the Fly error log.** Class `ModDogfight`, method `Fly`, the `catch`: replace `UnityEngine.Debug.LogError("[DOGFIGHT] fly failed: " + ex.Message);` with
```
			if (ModDogfight.flyFailLogged < 20)
			{
				ModDogfight.flyFailLogged++;
				UnityEngine.Debug.LogError("[DOGFIGHT] fly failed: " + ex.Message + " " + ex.StackTrace);
			}
```
and add `public static int flyFailLogged;` next to the other counters at the top of the class.

**F3 (B3). Collision look-ahead in real seconds.** Class `ModFlight`, method `End`: change both `ModAirCollide.Check(ua, duration);` lines to `ModAirCollide.Check(ua, duration * Mathf.Max(1f, Time.timeScale));`.

**F4 (C1). Less garbage.** Class `ModFlight`, method `Sample`: replace `Acc[] targets = new Acc[] { battle[side], recentA[side] };` and its loop with two direct calls (`AddAcc(battle[side], ...)`, `AddAcc(recentA[side], ...)`) to a small private method that does the five additions. Class `ModAirCollide`, method `Build`: keep a `static List<Plane> planePool` and reuse `Plane` objects instead of `new Plane()` (take from the pool, set the fields, put all back at the next `Build`). Both are optional; I can write the exact code if you want them.

**F5 (D). Rare collisions.** Class `ModAirCollide`, constants at the top: `RadiusScale` 0.42 to 0.25, `CrashSpeed` 90 to 200, `AvoidHorizon` 2.0 to 3.0, `AvoidHold` 0.9 to 1.5. In `Collide`, change `baseKill = 0.5f;` to `baseKill = 0.15f;`. In `Avoid`, change `avoidHeight[id] = ((Component)ua).transform.position.y + hAway * 2.5f;` to `... + hAway * 4f;`.

Ready-to-paste files: F1, F2, F3 and F5 together as `v0.28.8_update` (Edit Class `ModDogfight`, `ModFlight`, `ModAirCollide`) on request.

## G. Overall assessment

The 0.28.7 build is stable: no errors in 492 s, every hook present, every class latched against its own failures except `Fly` (B2). The 1v1 now works as a test. The mod's remaining problems are behaviour, not crashes: the zoom loop (A1) makes the Wildcat lose every fight against a Zero regardless of the other fixes, and the collision tuning (D) takes a quarter of the losses. With F1 and F5 in, run the same 1v1 and 4v4 again; if the Wildcat still cannot score, the next step is tactics (mutual cover, no boom-and-zoom from level energy), not code fixes.
