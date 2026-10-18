# v0.26 Full Aircraft overhaul: how aircraft fly today and a staged plan (research only, nothing built)

Class and method names are the ones to search for in dnSpy. All come from the decompiled `Assembly-CSharp.dll` in the repo.

## How aircraft fly today (battle)

**One loop drives every plane.** `Unit.Update` calls `UnitAir.UpdateMovementData` about every 0.021 s, and `UnitAir.ApplyUnitMovement` moves the plane. The AI (`UnitAI.UpdateUnitAI`, then `UnitAIAir.AttackUnit`, `FollowNavPoints`, `FollowUnit`, `RetreatUnit`) never moves a plane. It only writes three wishes on the unit: `wantedSpeed`, `wantedTurnRate` and `wantedHeight`.

**There is no flight model.**
- **Position:** `ApplyUnitMovement` does `transform.Translate(0, 0, dt * currentActualSpeed)`. The plane slides along its own nose. No lift, gravity, stall, energy or thrust.
- **Turning:** `currentTurnRate` moves toward `wantedTurnRate` at `unitData.turnRate`. Heading is changed directly (`eulerAngles.y += currentTurnRate * dt`). The AI gets its wish from `UnitAI.GetRequiredTurnRateFlat` (the angle to the target, clamped to `unitData.maxTurnRate`).
- **Banking is cosmetic:** `currentRoll` is just `currentTurnRate * -5`, smoothed. It does not change the path.
- **Climb and dive:** the pitch (`currentPitch`) is smoothed toward `altitudeDifference`, which is the plane's height minus `wantedHeight`, clamped to `maxDiveClimb` (`unitData.dive` and `unitData.climb`, in degrees). So the nose angle is "how far from the wanted height", and the plane then slides along the nose.
- **Speed:** `currentSpeed` moves toward `wantedSpeed` at `unitData.acceleration` times the `accelerationRate` curve. `CalculateSpeedPenalty` slows a plane in a hard turn (`speedPenaltyAtMaxTurn`). Diving does not speed a plane up and climbing does not slow it.
- **Special moves:** `UnitAir.PerformManeuvre` (the `Maneuvre` enum: Roll_Over, Dive_Bomb, Level_Out, Shot_Down, Break_Left, Break_Right, DiveBomb_Dive, Kamikaze) takes over the controls with hand-made curves (over 300 lines). Our `ModDogfight`, `ModAirRealism`, `ModTorpRun` and `ModFighterRules` sit on top and only change the wishes.
- **Limits:** altitude capped at 3,300 m (`UnitAIAir.SetAircraftWantedHeight`), terrain avoidance by raycasts (`UnitAIAir.CheckNavigation`), a plane crashes when its height reaches 0.
- **Attacks:** `UnitAIAir.InterceptTarget` picks one of Level_Bomb, Aerial_Torpedo, Dive_Bomb_Approach, Strafe, Dogfight, Rocket or Kamikaze, each its own `...Approach` method with numbers from `CustomAirAttack`. Formation flying is `UnitAIAir.FollowUnit`, which cheats by pulling the plane toward its slot (`followFudge`).
- Carriers cannot launch or recover in battle (vanilla). Groups are built once at battle start (`EngagementData.CreateUnitGroup`).

## How aircraft move on the campaign map

There is no flying there. A strike is an abstract moving map object. `CampaignManager.GetMobileEndurance` works out flight time from `UnitData.range`, speed and the `UnitAir.endurance` list. `CampaignManager.CheckAirEndurance` counts it down every 5 minutes. Launch, landing and rearm timers are in the v0.25.3 roadmap entry. The overhaul keeps this layer as it is.

## What went wrong before, and what that means

- v0.17 to v0.20.8 (dive heights, bomb aim, dogfight moves, torpedo setup, fighter spreading) all worked **around** the three wishes. They work.
- v0.20.9 failed because our aimed gun run had to steer the nose through the "height difference" pitch system. Any realistic manoeuvre (loops, split-S, aiming at a lead point) fights that system.
- So the root problem is the movement layer, not the AI. A new AI on top of the same movement layer hits the same wall.

## What a replacement could look like

Replace only the movement layer (`UnitAir.UpdateMovementData`, `ApplyFlightControls`, `ApplyUnitMovement`, `CalculateSpeedPenalty`). Keep the AI's "wishes" at first, then widen them.

1. **Real attitude control.** The AI asks for a heading and a pitch (or a target point), and the plane rolls into the turn and pulls the nose. Turn rate comes from bank angle and speed, limited by a g-limit and stall speed.
2. **Energy.** Speed changes with pitch: diving gains speed, climbing loses it, throttle sets thrust, drag grows with speed and bank. This gives real boom-and-zoom against turn-fighter differences from a few numbers per plane.
3. **Per-aircraft numbers** from the existing `UnitData` (`maxSpeed`, `acceleration`, `turnRate`, `maxTurnRate`, `dive`, `climb`, `speedPenaltyAtMaxTurn`) so the 115 new aircraft work from day one, with optional extra columns (stall speed, climb rate, dive-speed limit) in the aircraft data files later.
4. **Aiming that matches.** With the nose steerable at a point, the gun run, rocket run and strafing become "point the nose at the lead point", and `IsInFiringCone` works.
5. **Formation flying** with real slot keeping instead of the pull in `FollowUnit`.
6. **Later, not movement:** carrier launch and landing in battle, better targeting.

## Staged plan (each stage is one dnSpy edit session, testable alone)

Rule for all stages: every new behaviour sits behind a switch in `config.txt` (off until tested), so a failed stage can be turned off without undoing the edit, and writes `[FLIGHT]` log lines.

- **Stage 0, Measure (no gameplay change).** A new class `ModFlightLog` writes every second per plane to `output_log.txt`: speed, height, pitch, bank, turn rate. Aaron flies one test battle, and we know the real numbers of each plane type before changing anything. One new class plus one added line in `UnitAir.UpdateMovementData`. Low risk.
- **Stage 1, Bank and speed in turns.** Change `ApplyFlightControls` and `CalculateSpeedPenalty` only: turn rate follows bank and speed, and a hard turn bleeds speed (fighters keep more than bombers). Same wishes, same AI. Planes stop turning on rails. Low-medium risk.
- **Stage 2, Energy.** Pitch affects speed: dive gains, climb loses, with a floor (stall) and a ceiling (dive limit per aircraft). `ApplyUnitMovement` moves along the real nose. Medium risk, needs balance numbers.
- **Stage 3, Pitch control instead of the height wish.** The AI can ask for a pitch angle directly (new field `wantedPitch`, used when set). `ModDogfight` gun runs and `UnitAIAir.DogfightApproach` use it, so the v0.20.9 aimed run finally works. Medium-high risk, fighters only.
- **Stage 4, Bombers and torpedo planes on the new model.** `DiveBombApproach`, `LevelBombApproach`, `TorpedoApproach` and `RocketApproach` re-tuned, and the `Maneuvre` special cases replaced one at a time (Roll_Over and Level_Out first, Kamikaze last).
- **Stage 5, Formation flying.** Replace the pull in `FollowUnit` with slot keeping by speed and heading.
- **Stage 6, Data and balance.** Per-aircraft columns, a balance pass over all aircraft, then look at carriers launching and landing in battle as a separate job.

## Risks

- I can read and write the code but cannot compile or run it. Every stage needs Aaron to build in dnSpy, fly a test battle and send back the `output_log.txt` lines.
- `PerformManeuvre` and the game's own attack numbers (`CustomAirAttack`, aircraft data files) were tuned for the old movement, so each stage changes how they feel.
- v0.20.9 is the warning: small stages, one switch each.

## Questions for Aaron before any code

1. Is the stage order OK, starting with Stage 0 (logging only)?
2. Keep the old movement behind a switch until the new one is proven? (Recommended: yes.)
3. Fighters first (Stage 3) or bombers first?
