# v0.28.18 update: tester fixes (torpedo attacks, AA in mid air, fighters vs ships, planes that blow up, wings off = spin) + planes arrive like a real strike + torpedo strikes get ahead and split

All five tester reports in one update. Builds on 0.28.17 (install that first; you did on 27 Oct).
Not compiled or run by me: back up `Assembly-CSharp.dll` first.

In dnSpy, for a whole class: right-click the class > **Edit Class (C#)...**, select all, delete, paste the whole file, **Compile**.
For one method: right-click the method > **Edit Method (C#)...**, change it, **Compile**.
When everything is in: **File > Save Module**.

## Do them in this order

1. **ModAirDamage**: paste all of `1_ModAirDamage.cs.txt` (whole class).
2. **ModFlight**: paste all of `2_ModFlight.cs.txt` (whole class). Only one change: 6 lines near the top of `End`. ModAirDamage must be in first.
3. **ModAALoadout**: paste all of `3_ModAALoadout.cs.txt` (whole class).
4. **ModFighterShips** (NEW class): in the tree, right-click the `-` (empty) namespace under Assembly-CSharp > **Add Class (C#)...**, select all, delete, paste all of `4_NEW_ModFighterShips.cs.txt`, **Compile**.
5. **UnitAIAir.ModAnvilSide**: Edit Method, select the whole method (from `private float ModAnvilSide` to its last `}`), paste `5_UnitAIAir_ModAnvilSide.cs.txt` over it, **Compile**.
6. **UnitAIAir.ModAllTorpFlightsReady**: same way, paste `6_UnitAIAir_ModAllTorpFlightsReady.cs.txt`, **Compile**.
7. Four one-line edits, all in `7_small_stock_edits.txt`:
   - A) `UnitAIAir.StrafeApproach`
   - B) `EngagementAI.ModPickStrikeTarget`
   - C) `EngagementAI.GetBestSeaTarget`
   - D) `EngagementAI.AttackUnit`
8. **ModAirSpawn** (NEW class, added 28 Oct after the first five): Add Class (C#) like step 4, paste all of `8_NEW_ModAirSpawn.cs.txt`, **Compile**. Then one line in **EngagementData.CreateUnitGroup**, see `9_EngagementData_CreateUnitGroup.txt`. If you already did steps 1 to 7, just do this step and Save Module.
9. **ModTorpStrike** (NEW class, added 28 Oct): Add Class (C#), paste all of `10_NEW_ModTorpStrike.cs.txt`, **Compile**. Then one block in **UnitAIAir.ModTorpedoSetup**, see `11_UnitAIAir_ModTorpedoSetup.txt`. Needs steps 5 and 6 (ModAnvilSide) in.
10. Optional: in **ModVersion** change `Current` to `"0.28.18"`.
11. **File > Save Module**.

No new hooks besides the one-line edits above. The panel, stick and chase cam (0.28.14 to 0.28.16) are not touched.

## What changed

**1. Hammer and anvil only when planes really are on both sides (UnitAIAir).** The torpedo flights going for one ship were split left and right by their number in a list, not by where they were. So when every flight came in from the same side, half of them flew round the ship to the far side, through its AA, and the attack fell apart. Now every flight attacks from the side of the ship it is already on. If there are flights on both sides, that is a hammer and anvil. If they are all on one side, they make a **wave attack** from that side: they still wait for each other in position (up to 5 minutes, as before) and go in together. The side is fixed when the flight is 8 km out, so a ship that turns before then is still handled. Log: `[TORP] Kate id ... attacks Yorktown from its port side: wave attack, all 3 flight(s) on this side` or `... hammer and anvil, 2 flight(s) this side and 1 on the other`.

**2. Small AA guns firing from mid air: a mod bug, now fixed (ModAALoadout).** This was not a game bug. It came from the mod's historical AA loadout (v0.27.1). Many ship models (Fletcher42, Kagero43, Fuso44, Benson42, Kitakami, Hakuryu45, Sekiryu45 and others) keep their AA as tiny positions inside an AA object that is scaled up 10 to 110 times. The loadout worked out the guns on the hull but wrote them in the AA object's units, so on those ships every light AA gun sat 10 to 110 times too far out: tens to hundreds of metres beside, above or ahead of the ship. The guns are now converted to the AA object's scale and position. Ships where the AA object is not scaled (Farragut, Mahan, Gleaves, Brooklyn...) were right before and are unchanged. Log: `[AALOAD] fletcher42 historical AA loadout applied: 12 guns (was 5), listed, AA object scale 10.0 ...: positions converted (v0.28.18)`.

**3. Fighters only attack small ships (new ModFighterShips + 3 one-line edits).** A fighter may now only go for a merchant, an oiler, a destroyer, a destroyer escort or a surfaced submarine. The target picker never gives a fighter a cruiser, battleship or carrier, and a fighter already on its way to one switches to a small ship, or, if there is none, breaks off and climbs away to do something else (enemy aircraft, its escort job, or circling). This is for the enemy AI and your auto strikes. If you order your own fighters at a battleship yourself, they still go (knob `PlayerOrdersToo` in ModFighterShips). Log: `[FIGHTSHIP] Zero id ... was sent at North Carolina (Battleship): fighters only attack small ships, going for Fletcher instead`.

**4. Shot-down planes can blow up (ModAirDamage).** When a plane is shot down it has a chance to explode in the air: 10%, plus up to 60% for a heavy killing hit (a flak burst or a cannon shell, not a last rifle-calibre round), plus 30% if it was on fire, plus 20% if it still had its bombs or torpedo, at most 65%. Armour and self-sealing tanks cut it by up to half, so Zeros and Bettys go up far more often than Hellcats or B-17s. A plane that blows up throws up to 8 pieces out and the rest disappears in the blast (fighters use the game's `explosionSecondary`, bombers `explosionLarge`). Log: `[EXPLODE] ... BLOWS UP at 1200 m (chance was 48%: ...)`. Knobs: `ExplodeBase`, `ExplodePerRel`, `ExplodeFire`, `ExplodeLoad`, `ExplodeArmourCut`, `ExplodeMax`, `DebrisMax`, `ExplodeFx`, `ExplodeFxBig`.

**5. A plane that loses a wing rolls over and spins down (ModAirDamage + ModFlight).** When a wing spar breaks (0.28.17) or the wings come off at overspeed, the plane now rolls towards the missing wing and spins down out of control: it keeps rolling, the nose drops to 50 to 75 degrees and swings round faster and faster, and it falls at about 1.6 x its stall speed instead of diving. A plane shot down with a wing already shot to pieces spins half the time. Planes that spin do not also explode. Log: `[SPIN] Wildcat id ... lost its left wing: rolls over and spins down from 900 m`. Knobs: `SpinWrecked`, `SpinRollRate`, `SpinYawRate`, `SpinNoseMin`, `SpinNoseMax`, `SpinSpeedOverStall`.

**6. Planes arrive like a real strike (new ModAirSpawn + 1 line).** Before, every air group popped into the battle standing still, pointing whichever way the map gave it, and fighter groups appeared on their own map spot, often in the middle of the bombers or far from them. Now as each group is put in: an enemy group with a route turns, as one formation, to fly towards its target; every plane starts at cruise speed (65% of its top speed, never below 1.5 x its stall speed); each flight after the first sits 150 m further back and 50 m higher or lower, so they are not all on one line; and a fighter group of the same side that starts within 4 km of a bomber group is moved to fly top cover over it, 800 m higher, 1 km behind and 400 m out to one side (a second escort group takes the other side). Your own groups keep the heading the game gives them. Log: `[SPAWN] B5N2 Kate x9 (enemy) enters at 1000 m, 230 km/h, heading 75 (towards its route), 3 flight(s), A6M2 Zero x6 fly top cover over B5N2 Kate x9 at 1800 m`. Knobs at the top of ModAirSpawn; `Enabled = false` switches it off.

**7. Torpedo strikes get ahead of the formation, then split and swing in together (new ModTorpStrike + 1 block).** Every torpedo flight going for a ship now drops to attack height and runs up its side of the enemy formation 4.5 km out (outside light AA), to a gathering point 3.5 km ahead of the formation's leading ship. It circles there until every flight has arrived (at most 4 minutes after the first). Then the flights split, the left half to port and the right half to starboard, and swing in from the bows with the normal run-in: they wait in the drop window for each other and drop together, a hammer and anvil. A single flight comes in from the side it is on. A flight already within 3 km of the ship when its attack starts goes straight in. This is the planned version of item 1: from ahead the split is short, so nobody flies round the ship through its AA. Log: `[TORPSTRIKE] ... is in place 3500 m ahead of ...` and `[TORPSTRIKE] 4 flight(s) ahead of Yorktown split and swing in: hammer and anvil, 2 to port, 2 to starboard`. Knobs at the top of ModTorpStrike (`AheadDistance`, `WideOffset`, `GatherTimeout`...); `Enabled = false` gives the item 1 behaviour.

## What to test

1. A torpedo strike with 2+ flights on one ship, coming from one direction: they should all attack from that side together (`wave attack` in the log), not split.
2. Send flights at a ship from two sides: `hammer and anvil`.
3. Put a Fletcher42 or Kagero43 under air attack and watch the light AA tracers: they should start on the ship.
4. Enemy strikes with fighters against a fleet with battleships: the fighters should only strafe destroyers or merchants, or stay up and fight. Search the log for `[FIGHTSHIP]`.
5. Watch planes being shot down: some should blow up (`[EXPLODE]`), wing losses should spin (`[SPIN]`).
6. Start a battle with an enemy strike and escorts: the bombers should come in at speed heading for you, with the fighters above and behind (`[SPAWN]` lines).
7. An enemy torpedo strike on your fleet: the Kates should run up a side of the formation, gather ahead, then come at the bows from both sides (`[TORPSTRIKE]`).
8. Send me `output_log.txt`. If the explosion looks too big or too small, say which plane, and I will swap the effect.

## Switch off
- Explosions: set `ExplodeMax` to `0f` in ModAirDamage.
- Spins: set `SpinWrecked` to `0f` and remove `s.spin = true;` in `Breakup` and `WingFails` (or ask me).
- Fighters vs ships: change `return SmallShip(ship);` in `ModFighterShips.MayAttack` to `return true;` and make `Check` return `false` first.

## Change Log entry (already added to the project Change Log file, together with the missing 0.28.14 to 0.28.17 entries)

v0.28.18 - Tester fixes: torpedo attacks, AA in mid air, fighters vs big ships, planes that blow up or spin
---------------------------------------------------------------------------------------------------------
* Torpedo flights only make a hammer and anvil when they are on both sides of the ship. Flights all on one side make a wave attack from that side together, instead of half of them flying round the ship through its AA.
* Fix: light AA guns on many custom ship models (Fletcher42, Kagero43, Fuso44, Kitakami and others) fired from mid air beside the ship. A mod bug in the historical AA loadout (scaled AA objects), now fixed.
* Fighters only attack small ships (merchants, oilers, destroyers, destroyer escorts, surfaced submarines), never cruisers, battleships or carriers. Your own direct orders are still obeyed.
* Shot-down planes can blow up in the air. More likely after a heavy hit, when burning or still carrying bombs or a torpedo, less likely with armour and self-sealing tanks.
* A plane that loses a wing rolls over towards it and spins down out of control.
* Torpedo strikes run up the side of the enemy formation, gather 3.5 km ahead of it, then split to both bows and swing in together.
* Planes arrive like a real strike: at cruise speed, enemy groups heading for their target, flights staggered, escort fighters flying top cover above and behind their bombers.
