# Large task forces (AI overhaul, part 1)

**What I found in the game code**
- The task force limit is a campaign setting, `maxShipsInTaskForce` (default 10). It isn't in `setup.txt`, so the game uses 10. Adding it to `setup.txt` raises the limit, with no DLL change. The task force panel already scrolls when there are more than 10 ships.
- AI task forces are built from the `units` lists in each campaign's `sea_missions.txt`. A bigger list gives a bigger AI task force. The AI uses its real named ships. If it has none of a type left, it swaps in the next type listed in `sea_alts.txt` (battleship > heavy cruiser > light cruiser > destroyer).
- **The formations had to be extended.** Most formations only had positions for 10 ships (Line Abreast and the column formations). In battle, ships past the last position are placed almost on top of the leader. The task force panel's formation preview would also read past the end of the list. All formations now have positions for 25 ships.
- New formations are added by appending a line to `formationsSea.txt` and a name to `seaFormationNames.txt`. AI missions choose a formation by its number (0 = Line Ahead ... 8 = Convoy Box).
- Skirmish mode has its own hard-coded limit of 10 (DLL, `SkirmishManager.AddSea`). It is not changed yet.

**What changes**
1. Task forces can hold up to **20 ships** (yours and the AI's).
2. The six existing formations are unchanged for the first 10 ships and now continue the same pattern up to 25 ships.
3. Three new formations (the number is what missions use):
   - **6 Battle Line + Screen:** ships 1-8 in line ahead, the rest in two destroyer columns on the flanks.
   - **7 Cruising Disposition:** ships 1-4 as a core diamond (carriers / battleships), ships 5-12 in an inner ring, ships 13+ in an outer screen ring.
   - **8 Convoy Box:** ship 1 leads, ships 2-10 in a 3x3 box (transports / oilers, then heavy escorts), ships 11+ round the outside.
4. AI fleets are larger. Patrols, small invasions, fast troop runs and submarines are unchanged.

| Mission | Before | After | Formation |
|---|---|---|---|
| Intercept / Bombard (surface) | 6-9 | 14-16 | Battle Line + Screen |
| Carrier groups (Intercept, Bombard, PrimaryLost, US carrier patrol) | 9-10 | 16-18 | Cruising Disposition |
| Battleship PrimaryLost groups | 9 | 16 | Battle Line + Screen |
| LargeInvasion / Convoy | 10 | 14-15 (same transports, more escorts) | Convoy Box |
| LargeFastTroop | 10 | 14 | 2 Column Left |

The rule used: +1 heavy cruiser, at least 2 light cruisers, destroyers doubled +2 (at least 8). The cap is 20 ships for Japan and 18 for the US. Ships are listed in formation order (carriers, battleships, cruisers, destroyers).

## Install
1. Back up the four files below and both `setup.txt` files.
2. Copy the contents of the `Override` folder in `large_task_forces.zip` over your game files:
   - `formationsSea.txt`
   - `language/english/dictionary/seaFormationNames.txt`
   - `campaign/campaign001/sea_missions.txt`
   - `campaign/campaign002/sea_missions.txt`
3. Open `campaign/campaign001/setup.txt` in Notepad. Ctrl+F `"taskForceSpeeds"`, click just before it, and type:
   `"maxShipsInTaskForce":20,`
   so it reads `..."maxShipsInTaskForce":20,"taskForceSpeeds":[8,12,16,20,25],...`. Save.
4. Do the same in `campaign/campaign002/setup.txt`.
5. Start a **new campaign** (AI task forces already on the map keep their old size).

## Testing
- Build a task force: you should be able to add up to 20 ships. Pick each formation in the dropdown and check the preview.
- Fight a battle with a big task force in Line Abreast or 3 Column: ships 11+ should start in formation, not stacked on the leader.
- AI: F9 (fog off) and hover enemy task forces. Intercept/Bombard groups should be about 14-18 ships. Check that a battle against one starts in formation.
- Performance: 20 v 20 ship battles are much heavier than 10 v 10. Note the frame rate.

## Tuning
- Limit: the number after `maxShipsInTaskForce` (25 is fine; the formations have 25 positions).
- Spacing is the in-game spacing setting (500 / 750 / 1000 m per unit).

Notes:
- With bigger fleets the AI fields fewer task forces at once, because it is using real ships.
- An AI task force that sets out short of ships, and falls below 60% of its listed size after a battle, heads home. That is vanilla behaviour.
- Ships keep their formation slot by their position in the task force, so use Swap Positions to put capital ships first.
