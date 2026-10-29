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
