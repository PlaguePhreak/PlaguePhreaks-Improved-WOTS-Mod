## 0.32.13 (base change!)
Built on the tester hotfix 2 DLL 091a6546 (= 0.30 Mega Patch 01 + fuel hotfix + hotfix 2 14 fixes + 0.30.1 low flight), NOT on 0.32.12. All globe hooks re-applied with the Cecil patcher (HOOKS_GEO, HOOKS_GLOBE, HOOKS_BATTLE, HOOKS_BATTLE2; the fuel hook is already in that base). ModGlobe changes: OnDestroy() destroys root/blocker/button and clears inst (fixes blank icons when a second campaign is opened in one sitting); AddEntry forces icon alpha 1. Decompile diff vs 0.32.12 = only the hotfix 2 / low-flight changes; vs hotfix 2 = only the globe hooks and classes.

## 0.32.12
- No new hooks. ModGlobe.BuildRibbon returns early when mapPixelWidth/240 > 359 degrees or Theatre is false. MenuGlobe default false; the MenuSystem.Start hook from 0.32.11 is NOT in this DLL (built on 0.32.10).

# 0.32.11 merge notes

- **Base:** 0.32.10 globe test 10 (md5 89192094a7a60b704430cb2073af189a).
- **Output:** md5 7e73045231eb9937277f09ec29eb4ce0.
- **Changed:** ModGlobe (menu mode), one hook, version strings 0.32.10 -> 0.32.11 and a changelog entry.

## Hook (dnSpy)
- MenuSystem.Start: last line `ModGlobe.Menu(this);`.

## ModGlobe changes
- New knobs MenuGlobe, MenuSpin, MenuLat, MenuZoom; fields menuPending (static), menu, menuRt, menuRaw, menuSys.
- Awake: a copy added while menuPending is set becomes the menu copy and does not replace the campaign `inst`.
- Menu(MenuSystem): adds the menu copy to the MenuSystem object. OnDisable/OnEnable hide and show it with the menu.
- DriveMenu(): builds the globe without ribbon or blocker (Build(null)), draws its camera into a RenderTexture
  (60% of the screen width by its height), puts that texture on the menu's video RawImage (parent of
  MenuSystem.menuStaticBackground), hides the VideoPlayer object and the still image, spins MenuSpin degrees per second,
  shades from DateTime.UtcNow every 2 s.
- centre is x = 80000 for the menu copy so the two globes never overlap.
- SunDir/Shade split into SunDir(DateTime, offset) and ShadeBy(Vector3).
- UI stub: RawImage.texture.

Verified: MenuSystem decompile differs only by the one call; CampaignManager, EngagementAI, EngagementManager,
TerrainTiles, ModGeo, ModBattleMap identical to 0.32.10; ilverify list identical apart from one expected line for
ModGlobe.DriveMenu (UI RawImage).
