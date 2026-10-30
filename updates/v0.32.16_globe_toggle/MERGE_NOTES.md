# Merge notes 0.32.16 (vs 0.32.15)

## ModOptions
- `Count` 21 -> 22, new `IGlobe = 21`, new `public static bool Globe => Get(21);`
- `keys`/`names`/`values` arrays grow to 22: key `globe`, name "3D world map (3D button, F10, scroll out on the campaign map)", default true.
- `BuildPanel`: after the Interface features loop (6..10) add `row = AddSetting(row, 21);`
- An old options file without the `globe` line loads fine (missing key keeps the default true).

## ModGlobe.Update
After the `Enabled` check:
```
if (!ModOptions.Globe)
{
    if (on) Off();
    if (buttonObject != null && buttonObject.activeSelf) buttonObject.SetActive(false);
    if (sunButton != null && sunButton.activeSelf) sunButton.SetActive(false);
    return;
}
if (buttonObject == null) BuildButton(ci);
else if (!buttonObject.activeSelf) buttonObject.SetActive(true);
```

## ModVersion
Version text "Version 0.32.16 globe test 16"; changelog entry for 0.32.16 added (strings_globe16.txt).

## Build
Same pipeline as 0.32.15: compile the six build_tools sources against the game's own UnityEngine.dll + UnityEngine.UI.dll and the hotfix 2 DLL, then
`NOHOOKS=1 HOOKS_GEO=1 HOOKS_GLOBE=1 HOOKS_BATTLE=1 HOOKS_BATTLE2=1 HOOKS_HISTORY=1 HOOKS_NEWS=1 STRINGS=strings_globe16.txt Patcher hotfix2b.dll patch_globe16.dll mref_real out.dll`.
ilverify: identical error list to the base DLL (24 pre-existing).
