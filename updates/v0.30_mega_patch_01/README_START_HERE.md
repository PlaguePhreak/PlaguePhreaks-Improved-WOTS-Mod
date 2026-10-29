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
  - `language/english/campaign/campaigns.txt`: the campaign list (Aaron's own, 29 Oct), with the Pacific War named "Experimental. WIP might not work"
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

1. Put the DLL in `Managed\` (steps 2 and 3 above). That's the only step left for you.
2. Already done on your PC: Nebraska removed from your override `unit\sea\allUnitsList.txt` and the 3 campaign `seaUnits.txt` files. Your old files are in `backup_before_nebraska_removal\` in this folder.
3. Already done on your PC: the Pacific campaign is renamed in your `override\language\english\campaign\campaigns.txt`, only that one line changed. Your old file is `campaigns_before_0.30.txt` in this folder.
4. You already have all the art from 0.29 to 0.31.14, so you don't need to copy the `override` folder yourself. The full pack for testers is the `v0.30_mega_patch_01.7z.001` ... set next to this folder: open `.001` with 7-Zip and it unpacks the whole release.

## Notes

- The logbook (BOOK button on the campaign map) has the new features on 8 pages. Page 12 is now called ENEMY AND ALLIED AI.
- Nothing in this release was changed in the code since 0.31.14, which is not tested in game yet. Please send `output_log.txt` after a test.
