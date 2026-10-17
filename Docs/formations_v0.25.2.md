# v0.25.2 New formations (draft, untested)

Status: files written, not tested in game (the game cannot be run here). Data only, except the Supply Event convoy which needs one dnSpy edit.

## How a formation works
- One line per formation in `Override/formationsSea.txt` (24 offsets, x sideways, z forward = +, astern = -). Names are in `Override/language/english/dictionary/seaFormationNames.txt`, same line order.
- Ship 1 in the task force list is the leader at (0,0). Ship 2 takes offset 1, ship 3 offset 2 and so on. The ship order in the task force decides who goes where.
- The existing nine (0-8) are unchanged. Line Ahead (0) uses the game's own follow-the-ship-in-front code and Convoy Box (8) is kept as it was.

## Template for the new formations (9-17)
Position 1 leader, 2-5 big ships (carriers, battleships, heavy cruisers) in the middle, 6-8 destroyers at the front, 9-10 destroyers on the flanks, 11-20 anywhere that suits the shape, 21-25 spare astern.

| No. | Name | Shape |
|---|---|---|
| 9 | Escorted Wedge | V-shape, big ships close behind the leader |
| 10 | Escorted Box | square of big ships around the leader |
| 11 | Escorted Diamond | diamond of big ships around the leader |
| 12 | Escorted Ring | cross of big ships, ring of ships behind and around |
| 13 | Escorted Echelon | big ships on a diagonal through the leader |
| 14 | Escorted Double Column | two columns of big ships |
| 15 | Kido Butai (2 Carriers) | carrier pair (carriers listed first), ring of escorts |
| 16 | Kido Butai (4 Carriers) | 4 carriers in a box (list them first) with a battleship or cruiser in the middle, escorts outside |
| 17 | Surface Action Line | big ships in a column, destroyers ahead and on the flanks |
| 18 | Supply Event | see below |

The smallest distance between any two ships in each shape is 1.3 spacing units or more (checked by script). Spacing values are estimates; if ships look too close or too far, the numbers are easy to scale.

## Supply Event (18)
- Slot 1 is always a light cruiser (a heavy cruiser only if no light cruiser exists). A merchant or oiler is never in slot 1, because they retreat when a fight starts and take the whole task force with them.
- Slots 2-4: the escorts (front, port, starboard). Slots 5-16: a grid of cargo ships. Slots 17-20: extras, so players can use it with up to 20 ships.
- Limit: with fewer than 3 destroyers the first cargo ships fill the free escort slots (front or flank spots).

## dnSpy step (convoy event only)
1. Open **ModConvoy** > **Spawn** > right-click > **Edit Method (C#)...**
2. Select the whole method and paste the contents of `spawn_supply_event.cs.txt` over it.
3. **Compile**, then **File > Save Module**.

The new Spawn builds: 1 light cruiser, 1-3 destroyers, 6-12 cargo ships (at least one each of troops, supplies, engineering and an oiler, the rest random), formation 18. The minimum total cargo stays 2,000 troops, 2,000 supplies, 100 engineering, 100 fuel, split over the ships of each type. It already includes the v0.22.6 sailing fix, so it replaces the earlier Spawn edits.

## Rule for all task forces (from Aaron)
Never put a merchant or oiler in first position. No starting force or mission list does today (checked both campaigns' `sea_missions.txt`).
