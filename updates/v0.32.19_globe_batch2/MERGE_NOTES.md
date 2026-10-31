# Merge notes 0.32.19 (vs 0.32.18 ship pick, md5 4580b19b)

Full decompile diff = exactly these:
- New classes **ModWorld**, **ModRoutes**, **ModScore**, **ConvoyRoute**, **ScoreRules** (build_tools/ModWorld.cs).
- **ModGlobe** replaced (build_tools/ModGlobe.cs): knobs Nations/NationKm/NationAlpha/Readout/SearchBox/ScorePanel; new methods
  Typing, HudText, BuildHud (called at the end of BuildBlocker), OnSearch, GoTo, ScoreUpdate (called at the end of Markers),
  ReadoutUpdate and NationTint/NationTexture (called at the end of Drive); Facing/ShadeBy also apply front triangles and
  day-night colours to the nation mesh; F10, N and the arrow keys skipped while the search box has focus.
- **CampaignData**: new field `public List<string> modWorld;` (saved with the campaign).
- **CampaignManager**: `ModWorld.Tick();` after `ModAllied.Tick();` in Check1Min; `ModWorld.Daily();` after `ModNews.Daily();`
  in CheckDaily; `ModWorld.Save(campaignData);` after `ModNotify.Save(campaignData);` in GetCampaignDataString.
- **ModVersion**: 0.32.19 strings and changelog entry (strings_globe19.txt).

ModOptions is NOT touched (the ship-pick thread's 23-option version stays; next free index is 23).

## Build
```
csc (Roslyn, net35 refs, game's UnityEngine + UnityEngine.UI, -r:sp18.dll) ModGeo ModGlobe ModBattleMap ModHistory ModNews ModWorld -> patch.dll
NOHOOKS=1 HOOKS_WORLD=1 STRINGS=strings_globe19.txt Patcher sp18.dll patch.dll <refs> out.dll
```
HooksWorld is new in Patcher_Program.cs (adds the field and the three calls). ilverify: identical error list to the base (24 pre-existing).

## Data
build_tools/build_world.py now writes convoys.txt, score.txt and the wconvoy_arrived / wconvoy_lost / wconvoy_sunk / wscore_warn
event frames (content is written by the mod at run time). Route table CONVOYS, weights SCORE_WEIGHTS.
