# v0.29 "The Pacific War" (Mega Patch 01): install

## Part A: Override files

1. If you installed a Pacific War test build before, delete these 3 folders first:
   - `Override/campaign/pacificwar/`
   - `Override/maps/pacificwar/`
   - `Override/language/english/campaign/pacificwar/`
2. Copy the `Override` folder from this pack over your game's `StreamingAssets/Override`.
3. Skip this step if you already did it for a test build. Otherwise, open `language/english/campaign/campaigns.txt` and add the line from `campaigns_line.txt` under the `campaign002=...` line. Do not replace the whole file.
4. Skip this step if you already did it. Otherwise, copy `rules.txt` from `StreamingAssets/language/english/campaign/campaign001/` into `Override/language/english/campaign/pacificwar/`.

## Part B: DLL (historical events)

Start from your current 0.28.18 Assembly-CSharp.dll and keep a backup copy first.

1. **New class ModHistory.** In dnSpy, right-click the `-` namespace under Assembly-CSharp and choose Add Class (C#). Delete everything in the editor, paste the whole of `DLL/1_NEW_ModHistory.cs.txt`, then click Compile.
2. **One line in CampaignManager.CheckDaily.** Follow `DLL/2_CampaignManager_CheckDaily.txt`.
3. **Version text.** Follow `DLL/3_ModVersion_edit.txt`.
4. Choose File > Save Module.

Start a **new** Pacific War campaign. If anything goes wrong, send `output_log.txt`. Lines starting with `[HISTORY]` show each event and why it passed or failed.

## Historical events

These are in `campaign/pacificwar/history.txt`. You can edit the dates, ranges and rewards there without touching the DLL.

| Date | Event | You change history if... |
|---|---|---|
| 10 Dec 1941 | Guam invaded | 3+ of your warships are within 300 km of Guam |
| 10 Dec 1941 | Makin occupied | 3+ warships are within 300 km of Makin |
| 23 Dec 1941 | Wake falls | 4+ warships are within 500 km of Wake (+100 CP) |
| 18 Apr 1942 | Doolittle Raid | a carrier is within 1,500 km of Yokosuka (+100 CP) |
| 4 Jun 1942 | Battle of Midway | 2+ carriers are within 800 km of Midway (+200 CP). Otherwise Midway falls (-50 CP) |
| 6-7 Jun 1942 | Kiska and Attu occupied | 3+ warships are within 400 km |
| 26 Aug 1942 | Nauru occupied | 3+ warships are within 300 km |
| Sep 1942 | Tarawa fortified | 3+ warships are within 300 km |

An event is skipped if the place has already changed hands. For example, if the AI already took Midway, there is no Midway event.
