# v0.26 Full Aircraft overhaul: full draft plan (draft 2, for Aaron to go over, nothing built)

**Status:** research and Stage 0 logging only. No flight code changes until this plan is agreed. Every item in "Proposed additions" is marked **Recommend** or **Optional**, so you can accept or cut each one.

## Goal
Replace the way aircraft fly in battle with a believable flight model, then rebuild the air AI to use it. Today planes slide along their nose; after the overhaul they bank to turn, trade speed for height, stall, and can really aim. Fighters come first.

## Decisions so far (Aaron)
1. Log first, so each change can be checked against measured numbers. Then the AI uses the new movement.
2. Fighters first.
3. The on/off switch for new flight tied to the pause menu / Mod Options rework (v0.27).
4. Full draft agreed before any code changes.
5. Idea from the first log: aircraft with nothing to do should be in an "idle flight" mode (see addition A).

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

## How aircraft move on the campaign map
There is no flying there. A strike is an abstract moving map object. `CampaignManager.GetMobileEndurance` works out flight time from `UnitData.range`, speed and the `UnitAir.endurance` list, and `CampaignManager.CheckAirEndurance` counts it down every 5 minutes. The overhaul keeps this layer as it is. Launch, landing and rearm timers belong to v0.25.3.

## What the first test log showed (about 50 aircraft, two battles, 8,522 lines)
- Speed never exceeded the aircraft's max. Planes start from 0 speed at 45 s and accelerate.
- Turn rate peaks: Dauntless 6.5, Avenger 5.2, Wildcat 12.9, P-39 about 16, A6M2 20 degrees per second. A hard turn costs speed (penalty factor down to 0.75 Wildcat, 0.84 Dauntless, 0.85 Avenger).
- Bank is always turn rate x about -5, so it is for show only.
- Nose pitch follows the height gap exactly (a Dauntless 1,000 m above its wanted height dives at 17 degrees; the Wildcat reaches its 23.5 degree dive limit).
- The "Level_Bomb" shown for planes doing nothing is only the default value of the attack type. Fixed in the logger (it now says Idle).
- To look into: 37 lines on live planes with a speed penalty of exactly 0.00, and the A6M2 showing up to 100 degrees of bank in 64 lines.
- Missing: no bombing, torpedo or dive-bomb runs yet. A second test is coming.

## Design: what the new flight model is
Replace only the movement layer (`UnitAir.UpdateMovementData`, `ApplyFlightControls`, `ApplyUnitMovement`, `CalculateSpeedPenalty`). The AI keeps writing wishes (speed, turn, height) at first, then gains a direct pitch wish.
1. **Bank decides turn rate.** The plane rolls to a bank angle, and turn rate follows bank and speed, limited by a g-limit and stall speed.
2. **Energy.** Diving gains speed, climbing loses it. Thrust, drag and a per-aircraft dive speed limit.
3. **Pitch control.** The AI can ask for a nose angle or a target point, so aiming works (fixes the v0.20.9 failure).
4. **Uses the numbers planes already have** (`maxSpeed`, `acceleration`, `turnRate`, `maxTurnRate`, `dive`, `climb`, `speedPenaltyAtMaxTurn`), so all 115 added aircraft work from day one. Extra per-aircraft numbers (stall speed, dive limit) are optional later.
5. **Old movement stays as a fallback** behind a switch until the new one is proven.

## Proposed additions (accept or cut each one)
**A. Idle flight mode (Recommend, your idea).** A real "Idle" state for planes with no task: they hold altitude and a steady speed, fly circuits or follow the leader, instead of reading as Level_Bomb. Implementation note: do not renumber the `AIAttack` enum (values could be stored in saves), so add `Idle` at the end or use a separate flag. The logger already treats non-attacking planes as Idle.
**B. Stall and minimum speed (Recommend).** Below stall speed a plane loses lift and its nose drops. Stops fighters hanging in the air in a hard climb.
**C. Dive speed limit and over-speed (Recommend).** Planes cannot dive past a per-type limit; heavy controls at high speed (the Zero idea from v0.20.4) become a rule for everyone.
**D. Damage affects flight (Recommend, later stage).** Engine hits lower top speed and acceleration; control hits lower turn rate; smoking planes limp home. Builds on the air damage rework (v0.20 air_damage_rework).
**E. Pilot skill (Optional, ties to the planned v0.18.6 air crew experience).** Green/Trained/Veteran/Elite change reaction time, how hard they pull and gunnery.
**F. Visible manoeuvres (Optional).** Real rolls, loops and split-S as a result of pitch control, replacing the hand-made `PerformManeuvre` curves a few at a time (the old v0.20.10 idea).
**G. Real formation flying (Recommend).** Slot keeping by speed and heading instead of the pull in `UnitAIAir.FollowUnit`. Formations break and re-form around attacks.
**H. Altitude performance (Optional).** Top speed and climb change with height (thinner air). Makes high or low altitude matter.
**I. Per-aircraft flight file (Optional).** An Override file listing extra flight numbers for any plane (stall speed, dive limit, climb rate). Missing values fall back to defaults.
**J. Flight debug readout (Optional).** A key that shows the log values for the selected plane on screen, using the Stage 0 logger code.
**K. Settings switch (Recommend).** A Mod Options entry "New aircraft flight" (on/off), plus fine switches while testing. Stage 0 uses a plain `Enabled` flag until Mod Options is tested.
**L. Collision and ship avoidance (Optional, late).** Planes pull off before flying into ships or terrain, using the same raycasts as `CheckNavigation`.
**Not in this overhaul:** carrier launch and landing in battle, campaign-map range and timers (v0.25.3), weather and wind.

## Stages with how we know each one works
Rules for every stage: new behaviour is behind a switch (default off until tested), writes `[FLIGHT]` lines, and is compared against the Stage 0 log.
- **Stage 0, Measure (written, being tested).** `ModFlightLog`. Done when we have logs with fighter, dive bomber, torpedo bomber and level bomber runs, and a table of real numbers per aircraft type.
- **Stage 1, Bank, speed and idle state.** Turn rate from bank and speed, speed lost in turns, plus the Idle flight state (A). Done when logged turn rates sit within about 20% of today's per-type values and planes visibly bank into turns.
- **Stage 2, Energy and limits (B, C).** Pitch changes speed, stall speed, dive limit. Done when a dive gains speed and a climb loses it in the log, and no plane exceeds its limit.
- **Stage 3, Pitch control for fighters.** `wantedPitch`, and the gun run (`ModDogfight`, `DogfightApproach`, `IsInFiringCone`) uses it. Done when a diving Wildcat gets shots on a Zero (the v0.20.9 failure) and kill counts stay sane.
- **Stage 4, Bombers and torpedo planes.** Dive, level, torpedo and rocket approaches re-tuned; `Maneuvre` special cases replaced one at a time (Roll_Over and Level_Out first, Kamikaze last).
- **Stage 5, Formation flying (G).**
- **Stage 6, Damage, skill, data and balance (D, E, I, H as accepted).** Balance pass over all aircraft.
- **Stage 7, Switch and cleanup (K).** Mod Options entry, then remove the old movement only after a long clean test period.

## Risks
- I cannot compile or run anything, so every stage needs your dnSpy build, a test battle and the log back.
- `PerformManeuvre`, `CustomAirAttack` and aircraft data were tuned for the old movement, so each stage changes the feel. Hence the switch.
- v0.20.9 is the warning: small stages, one switch each.

## Questions for you
1. Which of A to L do you accept, cut or want changed?
2. Should the stage order stay (fighters at Stage 3), or should Idle (A) and bank (Stage 1) wait until fighters work?
3. Anything missing you want in the overhaul (for example scouts, floatplanes or kamikazes getting their own handling)?

