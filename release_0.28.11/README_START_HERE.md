# Release pack 0.28.11 (README, Change Log, in-game book and main menu version)

| File | Where it goes |
|---|---|
| README.md | Replaces the README in the mod upload (and the repo). |
| Change Log | Replaces the Change Log in the mod upload (and the repo). Statuses updated, 0.25 to 0.27 entries added, 0.28.11 on top. |
| ModGuide.cs.txt | In-game BOOK (What's New, Air and Keys pages updated to 0.28.11). dnSpy: right-click class `ModGuide` > Edit Class (C#), select all, paste, Compile. |
| ModVersion.cs.txt | Main menu changelog box and "Version 0.28.11" tag. dnSpy: class `ModVersion` > Edit Class (C#), select all, paste, Compile. If you never added ModVersion, follow /mnt/project-files/mainmenu_version/README.md first (Add Class + one line in ModOptions.BuildMainMenuButton). |

Then File > Save Module.

ModGuide.cs.txt is the class as decompiled from your 0.28.7 DLL with only the page text changed, so it should compile as is. If dnSpy shows a red line about `Object`, delete the line `using Object = UnityEngine.Object;` at the top and compile again.
