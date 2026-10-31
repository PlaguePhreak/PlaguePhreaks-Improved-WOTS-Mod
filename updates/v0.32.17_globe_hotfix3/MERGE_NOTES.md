# Merge notes 0.32.17

Rebase, not a code change: the globe line now sits on the hotfix 3 DLL (6b0de454) instead of hotfix 2 (091a6546).

- Hotfix 3 classes ModAirListFix and ModOilOrder, and its IL edits (38 `Dictionary<string,UnitListData>.get_Item`
  sites -> `ModAirListFix.Get`, 3 `ModSinking.OilQueue` reads -> `ModOilOrder.Queue()`), come from the base DLL untouched.
- Globe-line classes (ModGeo, ModGlobe, ModBattleMap, ModHistory, ModNews, ModOptions) decompile identical to 0.32.16.
- Hooks re-applied by the patcher: HOOKS_GEO, HOOKS_GLOBE, HOOKS_BATTLE, HOOKS_BATTLE2, HOOKS_HISTORY, HOOKS_NEWS
  (CampaignManager, EngagementManager, EngagementAI, TerrainTiles, MapRadii, CampaignData).
- ModVersion: version text "Version 0.32.17 globe test 17", changelog entry 0.32.17 on top (strings_globe17.txt;
  the first STRINGS block now targets "hotfix 3" instead of "hotfix 2").

## Build
```
csc (Roslyn, net35 refs, game's UnityEngine.dll + UnityEngine.UI.dll, hotfix3.dll) the six sources -> patch_globe17.dll
NOHOOKS=1 HOOKS_GEO=1 HOOKS_GLOBE=1 HOOKS_BATTLE=1 HOOKS_BATTLE2=1 HOOKS_HISTORY=1 HOOKS_NEWS=1 STRINGS=strings_globe17.txt \
  dotnet Patcher.dll hotfix3.dll patch_globe17.dll <refs dir> out.dll
```
ilverify: identical error list to the hotfix 3 DLL (24 pre-existing).

## For other threads on this DLL line
Any further 0.30.x hotfix: rebuild this way on the new hotfix DLL, nothing in the globe sources needs to change.
The 3D world map switch is ModOptions index 21 (key `globe`); next free index is 22.
