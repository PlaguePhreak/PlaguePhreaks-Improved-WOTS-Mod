# Main menu: Version button and Changelog window (0.28.9)

**Status: written, not compiled, not tested.** Back up the DLL first. It touches no flight class, so it does not collide with the air combat updates.

## What you get
- A **VERSION 0.28.9** button on the main menu, right under MOD OPTIONS.
- Click it: a scrolling window titled VERSION 0.28.9 with one block per minor version (Changelog 0.28, 0.27, 0.26 ... down to 0.19, then one line for 0.1 to 0.18). Patch versions like 0.28.x are folded into their minor version.

## Steps (dnSpy)
1. Right-click **Assembly-CSharp** > **Add Class...**. Paste all of `ModVersion.cs.txt`. Click **Compile**. (If dnSpy complains, send me the error text.)
2. Open class **ModOptions**, method **BuildMainMenuButton**. Right-click > **Edit Method (C#)...**.
3. Select all, delete, paste all of `BuildMainMenuButton.cs.txt`. Click **Compile**.
4. **File > Save Module**.
5. Start the game. The main menu shows MOD OPTIONS and below it VERSION 0.28.9. Click it to read the changelog, Close to leave.

## Each new release
Open class **ModVersion** > **Edit Class (C#)...**. Change `Current = "0.28.9"` to the new number. If the release is a new minor version, add a new `H + "Changelog 0.29" + E + ...` block at the top of the `changelog` text. For a patch (0.28.10) only the number changes unless you want to add a line to the 0.28 block.

## My reading of the numbering (tell me if wrong)
0.26 = flight model and pilots; 0.27 = energy flight, Mod Options and pause menu, ship AA; 0.28 = the big air update. 0.24 and 0.25 follow the in-game logbook.
