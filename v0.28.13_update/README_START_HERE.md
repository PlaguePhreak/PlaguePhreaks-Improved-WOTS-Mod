# v0.28.13 update: auto resolve pulls in nearby air groups

One file. Paste it over the existing class in dnSpy (Edit Class on ModAirResolve), Compile, then File > Save Module.

1. **ModAirResolve** (1_ModAirResolve.cs.txt): replaces the whole class.

ModAirResolveWindow from 0.28.12 is unchanged.

## What changed

- The window now gathers the fight the way a real engagement does. Every other air group within 50 km of our engaged group joins, on both sides, nearest first, up to the game's air limit per side.
- An enemy group we have not spotted shows as "+ N unknown aircraft". Its planes still count in the points and the dice, so the chance of victory is honest.
- When more than one group is on a side the window adds "(2 groups, 36 aircraft)".
- Losses are rolled across all planes on a side and written back to every group that took part. The game then removes the dead planes group by group as before.
- The log says which groups joined: "[AUTORESOLVE] enemy air group of 12 at 27 km joins the fight as unknown aircraft".

Yesterday's case would now read: "24 x Wildcat" against "24 x A7M2 Sam + 12 unknown aircraft (2 groups)".

- The shot-down die has a floor of 1 for any armed side, and the winner always loses at least one plane when anything was shot down against it. Your 0/36 roll with "the enemy lost nothing" cannot happen now.

## Knobs

- `ShotDownMin = 1`. Raise it to make every fight bloodier.

- `JoinRange = 50000f` metres. Lower it to make the auto resolve narrower than a real engagement.
