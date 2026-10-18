# Fighter manoeuvres in the game now (0.26.4), what triggers them, chances and cooldowns

Distances are in metres (the code uses game units of 10 m). "Elite" means rank 3. With the Crew system off, every pilot is Elite. Numbers marked (const) can be changed at the top of `ModDogfight` or `ModFlight`.

## Pilot rank (ModFlight.Rank)
Chosen once per plane (fixed by its id), from nation and campaign year (1942 if no campaign date).
| | Green | Trained | Veteran | Elite |
|---|---|---|---|---|
| Japan 1942 | 5% | 25% | 45% | 25% |
| Japan 1943 | 15% | 40% | 35% | 10% |
| Japan 1944+ | 40% | 40% | 17% | 3% |
| US/others 1942 | 15% | 45% | 30% | 10% |
| US 1943 | 10% | 35% | 40% | 15% |
| US 1944+ | 5% | 25% | 45% | 25% |

Rank effects: notices a plane on its tail after 2 s (Green), 0.8 s (Trained), instantly (Veteran, Elite). Gun lead 60% / 85% / 100% / 100%. Green never climbs to set up a pass. Trained and above go to the rank-gated moves below.

## The attack cycle (phases)
| Phase | What the pilot does | When it starts | How long / how it ends |
|---|---|---|---|
| 0 Attack (gun run) | Points the nose at the lead point (where the target will be when the bullets arrive), left/right and up/down. Pulls the nose at 40 deg/s. Fires when the lead point is within 5 degrees of the nose and in range (the plane's attack range, else 400 m). | A new target, or after any other phase. | Ends at: overshoot, pass done, 30 s without getting the target ahead, or a target switch (below). |
| 1 Position | Climbs to 500 m above a fighter target (400 m above a bomber) and 800 m out to one side. | On a new target if the pilot is Trained or better, is a US pilot against fighters (or anyone against bombers), has less than 60% of that height advantage and is more than 1000 m away. Japanese pilots do not climb against fighters. Also after a US pilot's defence or roll-over. | Dives in when 80% of the height is gained and the target is within 2000 m, or after 25 s. |
| 2 Zoom | Zoom climb away: gentle 25% turn, climb up to 500 m but never more than 1000 m above the target. | After a gun run when: about to overshoot a bomber or (US, or Japanese Trained or lower) any target; a US pass on a fighter or any pass on a bomber is done. | 7 s, then picks the best target again (5 s minimum between picks). Japanese against fighters, and Green pilots, turn straight back in (phase 0). Others set up another pass (phase 1). |
| 3 High yo-yo | Pulls up 150 m, eases the turn to half, slows to 85% speed so as not to overshoot, then drops in behind. | Japanese Veteran or Elite pilot in a gun run on a fighter, within 120 m and with the target within 60 degrees of the nose. | 3 s, then phase 0. |
| 4 Defend | Breaks at full turn rate toward the plane on its tail. Japanese climb 60 m; US dive 400 m. The Zero's controls stiffen (turn rate x0.55) above 105% of top speed. | An enemy fighter within 400 m, on the pilot's tail (within 70 degrees behind) and pointing at him (within 25 degrees), that is targeting him. Checked every 0.5 s. | 4 to 6 s. Then 8 s before another defence can start. Japanese go back to the attack, US climb back (phase 1). If a friend was being covered (below) he goes straight at that enemy instead. |
| 5 Roll-over / split-S | See below, flown by `ModFlight.Acro`. | | |

## Gun run end conditions (phase 0)
- **Overshoot:** closer than 120 m and the target within 60 degrees of the nose. Japanese Veteran or better against a fighter: yo-yo. Everyone else: zoom.
- **Pass done:** the pilot got within 600 m and the range is now more than 150 m past his closest point, and the target was ahead of him (within 45 degrees) at some point. Ends the run against bombers, and against fighters for US pilots.
- **Gave up:** 30 s in one run without finishing.
- **Switching targets:** after 12 s in a run, if the target is farther than 300 m, the pilot asks the game's target choice (the v0.17 fighter AI that spreads fighters out) for the best target. At most once every 5 s per pilot. Also done at the end of every zoom.

## Defensive extras (added to Defend)
- **Thach Weave** (US, Veteran or Elite): at the start of a defence, turns toward the nearest friendly fighter within 1500 m that is in a dogfight, is not already after this threat and is not itself defending; that friend is told to turn in on the attacker.
- **Barrel roll** (Veteran or Elite): every defence starts a 3.5 s full roll round the nose while the break turn goes on. Only if no other acrobatic move is running.
- **Split-S escape** (US only, Elite only): at the start of a defence, if the pilot is above 1100 m, the enemy is within 450 m, the move is off cooldown, and a 40% roll succeeds: half roll (about 2.6 s at 70 deg/s), pulls through at 30 deg/s into a dive away, finishing level on the opposite heading. About 6 to 9 s in all. 40 s cooldown. Not used by Japanese pilots.

## Roll-over attack (Veteran 35%, Elite 80% chance per check)
Checked every 3 s during a gun run. All must be true: the chased plane was less than 100 m below the pilot at the last check and is now between 150 m and 900 m below, 300 to 1100 m away, off to the side or behind (more than 75 degrees from the nose); the pilot is above 1000 m; the 30 s cooldown has passed. (Chance 50% for Veteran and 80% for Elite per check.) Flight: half roll at 70 deg/s, pull through at 30 deg/s (upright again past 90 degrees), follow the target down, fire when lined up within 5 degrees, hold up to 4 s, then pull out level (also ends if the plane gets below 450 m, the target is lost, the target is within 120 m, or 14 s pass). Safety: anything running over 30 s is cut off and the plane handed back level. Cooldown 30 s.

## Wingman cover (Trained or better)
Every 1 s: looks for a friendly fighter within 1500 m that has an enemy fighter on its tail within 400 m (the same test as above). If the enemy is within 1500 m of the pilot and fewer than two of our fighters are already after it: he targets that enemy ("covering a wingman"), going straight into a gun run unless he is defending. While defending himself he keeps the break, fires if that enemy crosses his nose within 5 degrees and 400 m, and goes at it when the break ends. Support lasts 8 s per sighting.

## Cooldowns at a glance
| What | Cooldown |
|---|---|
| Threat check | every 0.5 s |
| Reaction delay (Green / Trained / better) | 2 s / 0.8 s / 0 |
| After a defence, split-S or roll-over | 8 s before the next defence |
| Split-S | 40 s |
| Roll-over attack | 30 s (checked every 3 s) |
| Target re-pick | 5 s minimum; tried after 12 s in a run and after each zoom |
| Wingman cover check | every 1 s, lasts 8 s |
| Position climb | gives up after 25 s |
| Zoom / yo-yo / defend | 7 s / 3 s / 4 to 6 s |

## Flight limits underneath (ModFlight)
Dive speed cap: 125% of top speed for fighters, 105% dive bombers, 115% others. Stall: a fighter below 35% of top speed (others 45%) cannot hold a climb and drops its nose. Turn rate is limited by speed and by bank (a fighter rolls at 90 deg/s, others 45), with the AI's turn wish eased over 0.35 s. Pitch while aiming: 40 deg/s up to 60 degrees nose down and 50 up (20 deg/s for non-fighters). The old v0.20 energy code is switched off.

## What the 10:12 battle showed (24 Wildcats against 72 Japanese fighters, Crew off)
Wildcats lost 7, the Japanese lost 6 (3 A6M2 and 3 A8K1), so the Wildcats now score kills. Wingman cover fired 463 times and carried on out of the break 139 times. The yo-yo fired 657 times, so the Japanese pilots yo-yo constantly, which you may want less often. The Wildcats lined up shots on 44% of their attack lines against 97% (A6M2) and 94% (A8K1) for the Japanese.
