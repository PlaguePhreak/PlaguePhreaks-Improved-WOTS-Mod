# 0.32.9 merge notes

- **Base:** 0.32.8 globe test 8 (md5 492d80587a28e8e39f0027f990029474).
- **Output:** md5 831b6169dc1979fc175105e8199bdd0d.
- **Changed:** ModGeo (new method), ModBattleMap (log lines), one hook, version strings 0.32.8 -> 0.32.9 and a changelog entry.

## Hook (dnSpy)
- EngagementManager.StartCombat: `float num2 = instance.engagementSize / 0.1f;` -> `float num2 = ModGeo.EngagementSize() / 0.1f;`. (sizeDelta of Map.engagementBorders = size / 0.1 / 0.1; stock engagementSize is 100 = 10,000 units across = 50 km radius.)

## ModGeo
- `public static float EngagementSize() { return On ? ZoneRadiusUnits * 0.02f : 100f; }` (11000 -> 220 -> 22,000 units across = 110 km radius).

## ModBattleMap
- Each early return now logs a [BMAP] reason.

Verified: EngagementManager decompile differs only in that line; CampaignManager, EngagementAI, TerrainTiles, ModGlobe identical to 0.32.8; ilverify list identical to 0.32.8.
