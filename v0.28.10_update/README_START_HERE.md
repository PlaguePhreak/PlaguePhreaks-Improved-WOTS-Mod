# v0.28.10 update (not run in the game yet)

You have 0.28.9 installed. This update edits 1 class. Save the module after.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModDogfight` | 1_ModDogfight.cs.txt |

In dnSpy right-click `ModDogfight` > Edit Class (C#), select all, paste the whole file, Compile, File > Save Module.

## What the 0.28.9 log (27 Oct, 1v1 + 4v4) showed
0.28.9 is in and clean: no errors, threats now seen out to 400 m, "flaps in, building speed" lines, the fire key gives a burst.

The 4v4 was won: two Zeros shot down, the other two driven off damaged, no Wildcat lost (0.28.8: two Wildcats lost, one Zero). Bursts ours 42 against enemy 49 (0.28.8: 8 against 38).

Two small behaviour fixes here, both about the end of the fight:
* **A plane leaving the battle flew at full throttle away from its target and never reached the edge.** A Wildcat that left on bingo fuel (15%) flew straight for 280 s at top speed and ditched with an empty tank, still inside the battle area. A leaver now heads straight away from the middle of the area once it is 1 km clear of its enemy (the shortest way to the edge, where the game takes the plane off the map), at cruise throttle when it is short of fuel or clear of the enemy. Cruise burns about a third of what full power does.
* **No emergency power below 40% fuel.** Four Wildcats chased the two damaged, leaving Zeros for five minutes on emergency power (1.8 x the burn) and all four reached bingo fuel.

## Not fixed, for discussion
* Fighters still chase a plane that has left the battle as long as the game keeps it as a target. Letting a leaver go needs a change in the game's own target choice (EngagementAI.GetBestDogfightTarget), the same kind of one-line hook as the lone-fighter edit. Say the word and I will write it.
* The 1v1 is a Wildcat against a Zero at the same height and energy, and the Wildcat lost it without firing a shot. That is the historical outcome of that fight; the Wildcat's answer was height and the Thach weave, not a 1v1.

## Not compiled
Edits by exact text replacement against the 0.28.9 source, checked by diff, not compiled. Paste any red line here.
