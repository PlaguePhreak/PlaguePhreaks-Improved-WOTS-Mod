# Plague's Better WOTS mod 0.30 "Mega Patch 01": tester release

Built on 0.31.14, the newest build, so it has everything up to there. Only text changed in the DLL: the version label, the main menu Change Log and the in-game logbook. All the code is the same as 0.31.14.
The main menu says **Version 0.30 Mega Patch 01**. Built for War on the Sea v1.09a.

The tester keys are still in (F9, F4, F3). The CTM ship pack is not included.

## What is in this folder

- `Assembly-CSharp.dll`: the mod.
- `override/`: everything the mod needs in the game's override folder:
  - `mod_wreck`: break pieces for every ship, fire animation and smoke images
  - `mod_debris`: floating wreckage and oil slicks
  - `ModAssets`: parachutes, airmen and plane wreck parts
  - `unit/sea/allUnitsList.txt` and `campaign/campaign001`, `campaign002` ship lists: Nebraska (1944) removed
  - `campaign/pacificwar`, `maps/pacificwar`, `language/.../pacificwar`: the Pacific War campaign (experimental)
  - `language/english/campaign/campaigns.txt`: the campaign list, with the Pacific War named "Experimental. WIP might not work"
- `CHANGELOG_0.30_for_chat.txt`: the short changelog for the tester chat.

## Install (fresh or over an older version)

The game folder below is `...\steamapps\common\War on the Sea\WarOnTheSea_Data`.

1. Close the game.
2. In `WarOnTheSea_Data\Managed\`, rename `Assembly-CSharp.dll` to `Assembly-CSharp_backup.dll`.
3. Copy `Assembly-CSharp.dll` from this folder into `Managed\`.
4. Copy the `override` folder from this folder into `WarOnTheSea_Data\StreamingAssets\`. Say **yes** to merging folders and replacing files.
5. For the Pacific War only: copy `rules.txt` from `StreamingAssets\language\english\campaign\campaign001\` into `StreamingAssets\override\language\english\campaign\pacificwar\`.
6. Start the game. The main menu should say **Version 0.30 Mega Patch 01**. Click **CHANGE LOG** at the top right to see what's new.

If you had the old `War on the Sea\ModAssets` folder from 0.29.4 or older, you can delete it after step 4.

## Aaron: only for your own PC

You already have most of the art. What is new for you:

1. Put the DLL in `Managed\` (step 2 and 3 above).
2. Copy `override\unit` and `override\campaign\campaign001`, `campaign002` from this folder into your override folder (the Nebraska removal). Also copy `pacificwar\seaUnits.txt` from the `nebraska_removal` pack if you haven't installed it.
3. Rename the Pacific campaign. Open your `campaigns.txt` (the one in `override\language\english\campaign\`, or the game's own one if you have no override copy). Find the line that starts with `pacificwar=The Pacific War=` and change `The Pacific War` to `Experimental. WIP might not work`. Leave the rest of the line as it is. Save.
   Don't copy this pack's `campaigns.txt` over yours if your campaign descriptions are newer than 0.26. This pack's file uses the 0.26 descriptions.

## Notes

- The logbook (BOOK button on the campaign map) has the new features on 8 pages. Page 12 is now called ENEMY AND ALLIED AI.
- Nothing in this release was changed in the code since 0.31.14, which is not tested in game yet. Please send `output_log.txt` after a test.
