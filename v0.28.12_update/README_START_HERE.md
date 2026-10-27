# v0.28.12 update: air auto resolve, points and dice (not run in the game yet)

Edits 2 classes. Save the module after step 2.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModAirResolve` | 1_ModAirResolve.cs.txt |
| 2 | Edit Class `ModAirResolveWindow` | 2_ModAirResolveWindow.cs.txt |

Right-click the class > Edit Class (C#), select all, paste the whole file, Compile. Then File > Save Module.

## The bug
"No fight: nobody is armed" for two fighter groups: the planes were only marked alive inside the fight roll, and the armed check ran before it, so every plane counted as dead. Fixed (planes are alive from the start).

## The new model (your design)
* **Points.** For every plane: gun damage + toughness x armour (+ 3 x gunner value for planes with gunners), from the aircraft stats table. Summed over the group and divided by 6. A Wildcat group of 24 = 103 points, 24 Sams = 74, 24 Zeros = 76. Multiplier = 1 + points / 1000 (103 points = 1.103x).
* **Dice**, rolled for each side when you press Resolve:
  * Attacked! 1 to 6
  * Defended 1 to 6
  * Shot down: 0 up to the side's own number of planes (never more than the enemy has), pulled toward the side with more points (103 against 74 points makes the better side roll high about 40% more often)
* **Score** = (attacked + defended + shot down) x multiplier. The higher score wins. A side whose planes are all shot down loses at once.
* **Losses.** The loser loses the planes shot down against it. The winner loses 1/2 to 3/4 of the planes shot down against it.
* **Window.** Enemy aircraft and our aircraft side by side with their points and multiplier, the chance of victory (1000 dice rehearsals) and expected losses, then after Resolve the three rolls, the scores and the result. Everything is also in the log as [AUTORESOLVE].

## Knobs (top of ModAirResolve)
`PointDivisor` 6, `GunnerWeight` 3, `WinnerLossMin` 0.5 and `WinnerLossMax` 0.75, `ShotDownShare` 1 (the shot-down die runs up to this share of the side's planes; 0.5 would halve the losses).

What the dice give, by my rehearsal outside the game: 24 Wildcats v 24 Sams about 67% for the Wildcats, 8 Wildcats and 13 Sams lost on average; 8 Wildcats v 6 Zeros 72%; 6 Wildcats v 8 Zeros 53%; 12 v 24 Zeros 31%; 1 v 1 63%. The Wildcat scores high because it has armour and the Japanese planes have none, so if that feels too strong, PointDivisor or the armour weight is the place to tune. The losses are heavy because the shot-down die can reach the whole group; ShotDownShare = 0.5 halves them.

## Not compiled
Written against the class names used in the current DLL (ModAirStats.RowFor, EngagementPanel, CampaignManager.ProcessMobileObjectPostCombat), checked by eye, not compiled. Paste any red line here.
