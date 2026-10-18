# v0.26 Full Aircraft overhaul: full draft plan (draft 2, for Aaron to go over, nothing built)

**Status:** research and Stage 0 logging only. No flight code changes until this plan is agreed. Every item in "Proposed additions" is marked **Recommend** or **Optional**, so you can accept or cut each one.

## Goal
Replace the way aircraft fly in battle with a believable flight model, then rebuild the air AI to use it. Today planes slide along their nose; after the overhaul they bank to turn, trade speed for height, stall, and can really aim. Fighters come first.

## Decisions so far (Aaron)
1. Log first, so each change can be checked against measured numbers. Then the AI uses the new movement.
2. Fighters first.
3. No on/off switch: the new flight replaces the old flying outright (decided 18 Oct, replaces the earlier switch idea). The old movement is kept only as an automatic fallback if the new code throws an error.
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
5. **No switch.** The old movement is replaced. Restoring the DLL backup is the way back.

## Proposed additions (accept or cut each one)
**A. Idle flight mode (Recommend, your idea).** A real "Idle" state for planes with no task: they hold altitude and a steady speed, fly circuits or follow the leader, instead of reading as Level_Bomb. Implementation note: do not renumber the `AIAttack` enum (values could be stored in saves), so add `Idle` at the end or use a separate flag. The logger already treats non-attacking planes as Idle.
**B. Stall and minimum speed (Recommend).** Below stall speed a plane loses lift and its nose drops. Stops fighters hanging in the air in a hard climb.
**C. Dive speed limit and over-speed (Recommend).** Planes cannot dive past a per-type limit; heavy controls at high speed (the Zero idea from v0.20.4) become a rule for everyone.
**D. Damage affects flight (Recommend, later stage).** Engine hits lower top speed and acceleration; control hits lower turn rate; smoking planes limp home. Builds on the air damage rework (v0.20 air_damage_rework).
**E. Pilot skill gates the manoeuvres (Recommend, Aaron 18 Oct).** Green / Trained / Veteran / Elite pilots (from the planned v0.18.6 air crew experience) decide which manoeuvres a plane may use, how well it flies them, reaction time and gunnery. A pilot only picks a move from his own rank and below, so skilled pilots are visibly better to watch. Proposed ladder (fighters):
- **Green:** straight pursuit, simple break turn when shot at, basic gun run. Slow to react, sloppy aim, often overshoots.
- **Trained:** adds boom and zoom (US) or turn fight (Japanese), slashing passes on bombers, wingman pairs (loose deuce).
- **Veteran:** adds high and low yo-yos, scissors, defensive barrel roll, Thach Weave for US pairs, deflection shots.
- **Elite:** adds split-S escape, reversal at the top of a climb, lag pursuit to stay out of the enemy's guns, hammerhead and snap shots, and picks the right move for the enemy (a Zero's turn vs a Wildcat's dive).
Bombers get a ladder too: Green flies a straight run, Veteran jinks and varies approach height, Elite bombers choose their dive angle and release height more precisely. **Tied to the crew toggle (Aaron, 18 Oct):** when the Crew system is switched off in Mod Options (`ModOptions.Crew`), pilot skill is off too and every plane may use every manoeuvre at full quality (Elite behaviour). That makes the manoeuvres easy to test, and means a campaign without crews never locks planes into simple attacks.
Until crew experience is built, a plane's rank comes from its nation and year (like the v0.20.3 bomb aim table), then from real experience later.
**F. Visible manoeuvres (Optional).** Real rolls, loops and split-S as a result of pitch control, replacing the hand-made `PerformManeuvre` curves a few at a time (the old v0.20.10 idea).
**G. Real formation flying (Recommend).** Slot keeping by speed and heading instead of the pull in `UnitAIAir.FollowUnit`. Formations break and re-form around attacks.
**H. Altitude performance (Optional).** Top speed and climb change with height (thinner air). Makes high or low altitude matter.
**I. Per-aircraft flight file (Optional).** An Override file listing extra flight numbers for any plane (stall speed, dive limit, climb rate). Missing values fall back to defaults.
**J. Flight debug readout (Optional).** A key that shows the log values for the selected plane on screen, using the Stage 0 logger code.
**K. ~~Settings switch~~ (dropped by Aaron).** The new flight is not optional.
**L. Collision and ship avoidance (Optional, late).** Planes pull off before flying into ships or terrain, using the same raycasts as `CheckNavigation`.
**Not in this overhaul:** carrier launch and landing in battle, campaign-map range and timers (v0.25.3), weather and wind.

## Stages with how we know each one works
Rules for every stage: new behaviour writes `[FLIGHT]` lines, and is compared against the Stage 0 log.
- **Stage 0, Measure (written, being tested).** `ModFlightLog`. Done when we have logs with fighter, dive bomber, torpedo bomber and level bomber runs, and a table of real numbers per aircraft type.
- **Stage 1, Bank, speed and idle state.** Turn rate from bank and speed, speed lost in turns, plus the Idle flight state (A). Done when logged turn rates sit within about 20% of today's per-type values and planes visibly bank into turns.
- **Stage 2, Energy and limits (B, C).** Pitch changes speed, stall speed, dive limit. Done when a dive gains speed and a climb loses it in the log, and no plane exceeds its limit.
- **Stage 3, Pitch control for fighters.** `wantedPitch`, and the gun run (`ModDogfight`, `DogfightApproach`, `IsInFiringCone`) uses it. Done when a diving Wildcat gets shots on a Zero (the v0.20.9 failure) and kill counts stay sane.
- **Stage 4, Bombers and torpedo planes.** Dive, level, torpedo and rocket approaches re-tuned; `Maneuvre` special cases replaced one at a time (Roll_Over and Level_Out first, Kamikaze last).
- **Stage 5, Formation flying (G).**
- **Stage 4b (0.26.4), Fighter manoeuvres by skill (E, F).** The ladder above, one rung per test. Aaron (18 Oct) asked for a full roll to inverted and a 90 degree dive onto a plane below (split-S / roll-over attack). The game already has this for dive bombers (`Maneuvre.Roll_Over` rolls to 180 degrees, then `Dive_Bomb` flips the nose down while inverted, `UnitAir.ManeuverUpdate` around line 523), so fighters can reuse it for a Veteran/Elite rung: roll over when the target is below and close, then pull through and fire.
- **Stage 6, Damage, data and balance (D, I, H as accepted).** Balance pass over all aircraft.
- **0.26.7.1 AA hits, fires and ablaze planes (Aaron, 18 Oct; idea inspired by Kiko's "Fuel fires"): AAA or a normal AA round can set a plane on fire; it may go ablaze and be shot down, or a skilled pilot cuts the engine or seals the fuel tanks to put the fire out. All new (the game has no fire, engine-off or fuel tank model). To be worked out later.**
- **0.26.8 Remove speed limit and break-up (see its section).**
- **0.26.9 Air auto resolve (see its section).**
- **Stage 7, Cleanup.** Remove dead old-movement code once everything has had a long clean test period.


## 0.26.8 Remove speed limit: overspeed break-up and shed wings (requested by Aaron, 18 Oct; research done, nothing built)
**What Aaron wants:** planes may dive past the 125 to 130% speed they can handle. Past that point the wings get a chance to break off, and the plane can snap apart. Also: could the models be changed live (a wing shot off falls away, a wing snaps off in a fast dive)?

**Why it is number 8:** it needs the 0.26.1 energy model (tested) and the damage work in 0.26.7 (damage that changes how a plane flies), and the mesh work below needs a short test first. It replaces the hard 125% dive cap (and the 105% and 115% caps) from 0.26.1.

**Overspeed design**
- Each aircraft gets a safe speed (a share of top speed: fighters 125%, dive bombers 105% with dive brakes, other bombers 115%, as today) and a structural limit (about 130 to 150%, set by toughness, see `DamageableAir.ModAirToughness`).
- Between safe and structural limit nothing breaks, the plane just buffets (log line, small shake).
- Above the structural limit a break chance per second rises with how far over it is and with pull-up load (turn rate x speed). Wings go first, then the tail or the whole airframe.
- When a wing goes the plane rolls hard toward the missing wing, turn rate and speed collapse, and it enters the existing shot-down fall (`UnitAir.HitAirUnit`, `Maneuvre.Shot_Down`). Log tag `[BREAKUP]`, message "wings ripped off".
- Mostly a change in the 0.26.1 `ModFlight.End` plus a small break-up routine. The first version has no visible mesh change, only the roll, smoke and fall. The visible wing comes from the mutation work below.

**Can the models be mutated? (checked in the code and in your aircraft files)**
- Every aircraft is one solid mesh for the whole airframe (for example `D3A1_Val`, `SBD-5`), plus separate guns, hub, blades and blur, and one collider. The wings are not separate objects, so there is nothing to simply detach.
- There is no damage model for parts. `DamageableAir` keeps one damage total against a toughness number, with smoke at one third and two thirds, then shot down. No wing, tail or engine zones exist yet.
- The game already shows destruction by switching things off or on and by gravity and fall (`HitAirUnit`), not by changing the mesh.
- **What is possible:** cutting the mesh while the game runs. At the moment a wing breaks, the game splits the airframe mesh along a plane through the wing root into a wing piece and a fuselage piece. The wing piece becomes its own falling object (rigid body, tumbling, smoke), and the fuselage keeps flying with the wing triangles removed. This works for every aircraft with no new 3D work. The cut edge is open (no cap), which will look rough up close.
- **What we do not know yet:** whether the game's meshes can be read at run time (Unity needs "read/write" on them, which depends on how the models were built). A short test finds out: the first step of 0.26.8 is a probe that only logs, for every aircraft model, whether the mesh is readable, its size and its wing span. If it is not readable, the fallback is a fake break: hide the whole wing area with a shader trick or swap in a simple stand-in wing piece that falls, while the real mesh stays.
- **Per-part hits:** to shoot a wing off, hits need a zone. `DamageableAir.ApplySmallCalibreDamageToAir` is given the hit point, so a hit can be mapped to the left wing, right wing, tail or fuselage by its position on the plane, with a damage total per zone. A wing zone past its limit makes the wing fail. Same cut routine as the overspeed break.
- **Effect on flying:** missing left wing means roll left, big turn rate and speed loss, plane spins down.

**0.26.8 steps**
1. Probe (logging only): mesh readability, bounds and wing span per aircraft. One class and one added line.
2. Overspeed wear and break chance with roll, smoke and fall, no mesh change.
3. Per-zone damage (wings, tail, fuselage) from hit points.
4. Real wing cutting and falling wing pieces, if step 1 says the meshes are readable.
5. Tune per aircraft (a wing coming off a Zero in a dive should happen sooner than on a Dauntless).

## Risks
- I cannot compile or run anything, so every stage needs your dnSpy build, a test battle and the log back.
- `PerformManeuvre`, `CustomAirAttack` and aircraft data were tuned for the old movement, so each stage changes the feel. Hence small stages with a test after each.
- v0.20.9 is the warning: small stages, a test after each.

## Questions for you
1. Which of A to L do you accept, cut or want changed?
2. Should the stage order stay (fighters at Stage 3), or should Idle (A) and bank (Stage 1) wait until fighters work?
3. Anything missing you want in the overhaul (for example scouts, floatplanes or kamikazes getting their own handling)?

## 0.26.9 Air auto resolve (requested by Aaron, 18 Oct; research only, to be discussed when we get there)

**What the game does today** (`CampaignManager` around line 1297, `EngagementPanel.AutoResolve`):
- The Auto resolve button only appears when one side is a Scout group and the other is a Fighter group (checked on the first aircraft of each group). Nothing else can be auto resolved.
- The result is a fixed rule, not a fight: if the fighter group has more than 3 more aircraft than the scout group, the scouts are destroyed; otherwise nobody is hurt and both sides just get the post-engagement cooldown. There are no odds, no losses for the fighters, and no use of aircraft type, pilot skill or ammo.

**What Aaron wants:** auto resolve for every kind of air meeting (fighter vs fighter, fighters vs bombers, bombers vs scouts and so on), with a new window titled "Auto resolve" that lists the aircraft on both sides and shows a % chance of victory.

**Rough design (to be agreed later):**
- Open the button for any air vs air meeting, not just scout vs fighter.
- Score each aircraft from its data file: speed, gun damage and rate of fire, toughness, armour, and for bombers the defensive guns. Pilot skill counts when crews are on, the same as in the real fight. Fighters score on attack, bombers and scouts mostly on toughness and defence.
- Chance of victory comes from comparing the two side totals, with a spread so a weaker side can still win sometimes. The window shows each side's aircraft by name and count, plus the % for the player.
- On the player pressing Resolve, roll the result, then remove destroyed aircraft from each group (a proportion, not all or nothing), keep survivors, apply the post-engagement cooldown, and show a short result line (for example "lost 3 Wildcats, shot down 5 Vals").
- The player can still choose to fight it out by hand; the window just offers the quick option with honest odds.

**Open questions:** should odds be shown exactly or as a band (Likely, Even, Unlikely)? Should bombers carrying a strike lose their attack if beaten? Should it also work for the AI side meeting AI side?

**Needs:** a new UI panel built in the game's UI system (the hardest part, we will look at how `EngagementPanel` is wired to its prefab first), plus a reworked `EngagementPanel.AutoResolve` and the check in `CampaignManager`.
