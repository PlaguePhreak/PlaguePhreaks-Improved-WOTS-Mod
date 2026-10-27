# Main menu text: Changelog box and Version tag (0.28.9)

**Status: written, not compiled, not tested.** Back up the DLL first. Touches no flight class.

- Top right (under the compass): a CHANGELOG box showing what 0.28 introduces.
- Bottom left: "Plague's Better WOTS mod" and "Version 0.28.9".
Both are plain text, no buttons. They sit on the main menu and hide with it.

## Steps (dnSpy)
1. Right-click **Assembly-CSharp** > **Add Class...**, paste all of `ModVersion.cs.txt`, **Compile**.
   (If you installed the earlier button version of ModVersion, instead right-click that class > Edit Class (C#)..., select all, paste this, Compile.)
2. Class **ModOptions** > method **BuildMainMenuButton** > Edit Method (C#)..., select all, paste all of `BuildMainMenuButton.cs.txt`, **Compile**. (It is the old method plus one last line, `ModVersion.Build();`.)
3. **File > Save Module**.

## Each new release
Edit class **ModVersion**: change `Current`. For a new minor version also rewrite `ChangelogBody`.
