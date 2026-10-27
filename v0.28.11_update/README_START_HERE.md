# v0.28.11 update (not run in the game yet)

You have 0.28.10 installed (if not, install 0.28.10 first: this ModDogfight builds on it). This update edits 3 classes. Save the module after step 3.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModDogfight` | 1_ModDogfight.cs.txt |
| 2 | Edit Class `ModAirFlight` | 2_ModAirFlight.cs.txt |
| 3 | Edit Class `ModAirDamage` | 3_ModAirDamage.cs.txt |

For each: right-click the class > Edit Class (C#), select all, paste the whole file, Compile. Then File > Save Module.

## What changed
* **Realistic fuel.** Every aircraft row now carries its real endurance at full power from the internal tanks (no drop tank), in minutes (`fuelMinutes`, set by `Alt` or the new `Fuel` line under each row). Before, every fighter had 26 minutes. Cruise burns about a third of full power, so a 100-minute fighter cruises for about 5 hours. Examples: A6M2 Zero 140, A6M5 Zero 130, F4F-4 Wildcat 100, FM-2 90, F6F Hellcat 100, F4U Corsair 95, P-38J 110, P-47D 100, P-51D 160, P-39 60, Ki-84 Frank 90, Ki-43 Oscar 150, SBD 180, TBF 240, Val 180, Kate 200. Planes not in the table: fighters 100, bombers 180, heavies 240. The figures are from tank capacity and engine consumption at military power, rounded; tell me any you want changed.
* **Bingo fuel is 10%** (was 15%). A plane at bingo leaves the battle at once, as before (`ModAirDamage.BingoFuel`), and since 0.28.10 it cruises to the edge of the area.
* **Fighters let a leaver go.** A target that has left the battle (damaged, out of ammunition, bingo fuel) is dropped within 2 s for the best enemy plane still in the fight. When only leavers are left they are chased as before. Logged as "[DOGFIGHT] ... has left the battle, letting it go for ..." and counted in the [BATTLE] line ("leavers let go"). The 15 s target re-pick also skips leavers (`ModDogfight.Candidates`, `Repick`).

## How to tell it is installed (next log)
* [FLIGHT] lines: fuel % barely moves over a 20-minute fight (before: about 5% a minute).
* "has left the battle, letting it go for" lines when a damaged plane runs with others still fighting.
* [FUEL] bingo lines say "10% left".

## Not compiled
Edits by exact text replacement, checked by diff, not compiled. Paste any red line here.
