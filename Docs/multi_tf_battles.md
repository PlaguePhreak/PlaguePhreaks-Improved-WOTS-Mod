# Multi task force battles (pincers)

**What was wrong (found in the code)**
- When a battle starts, `CampaignManager.GetValidNeighbouringMobiles` pulls in other task forces within 50 km of the battle. Each one keeps its real direction from the battle.
- But for **surface** task forces it only allows **one per side**. It checks a flag ("this side already has ships here") and skips every other surface force. Air groups have no such limit, which is why several air groups can join.

**What changes**
1. Any number of surface task forces from each side within 50 km join the same battle, up to **30 ships per side** in total.
2. Each force starts in its real direction from the battle, so a second force coming from another side arrives on that side (a pincer).
3. The cap keeps performance sane. A force that would take its side over 30 ships stays out of this battle.
4. It works for the AI too.

Back up the DLL first.

## Step 1 - CampaignManager.GetValidNeighbouringMobiles
1. In dnSpy open class **CampaignManager**, right-click **GetValidNeighbouringMobiles** > **Edit Method (C#)...**
2. Leave the `using` lines and the `public partial class CampaignManager ...` line at the top exactly as dnSpy shows them.
3. Select the whole method, from its first line (`private void GetValidNeighbouringMobiles(...)`) down to its closing `}`, and paste this over it:
```csharp
private void GetValidNeighbouringMobiles(List<GameObjectAnimator> nearbyMobiles, GameObjectAnimator battleMobile)
{
    for (int i = 0; i < nearbyMobiles.Count; i++)
    {
        GameObjectAnimator goa = nearbyMobiles[i];
        if (goa == null || goa.mobileMapObject == null)
        {
            continue;
        }
        MobileMapObject mmo = goa.mobileMapObject;
        if (mmo.type == 0 && nearbyMobiles == this.otherMobile)
        {
            continue;
        }
        if (this.GetDistanceInMetresBetweenMapObjects(battleMobile.currentMap2DLocation, goa.currentMap2DLocation) >= 50000f)
        {
            continue;
        }
        if (this.goasInBattle.Contains(goa))
        {
            continue;
        }
        if (mmo.postEngagementTimer > 0f && mmo.currentFaction != 0)
        {
            continue;
        }
        int side = (int)mmo.currentFaction;
        if (mmo.type == 0)
        {
            int shipsOnSide = 0;
            for (int g = 0; g < this.goasInBattle.Count; g++)
            {
                GameObjectAnimator inBattle = this.goasInBattle[g];
                if (inBattle != null && inBattle.mobileMapObject != null && inBattle.mobileMapObject.type == 0 && (int)inBattle.mobileMapObject.currentFaction == side)
                {
                    shipsOnSide += inBattle.mobileMapObject.unitPrefabs.Count;
                }
            }
            if (shipsOnSide + mmo.unitPrefabs.Count > 30)
            {
                continue;
            }
        }
        else if (this.airNumbers[side] + mmo.unitPrefabs.Count > Config.instance.maxAirPerSide)
        {
            continue;
        }
        Vector2 offset = (goa.currentMap2DLocation - battleMobile.currentMap2DLocation) * this.campaignData.mapWidthMetres * 0.1f;
        EngagementManager.instance.engagementData.unitGroups.Add(this.GenerateUnitGroupData(goa, new Vector3(offset.x, 0f, offset.y / 2f), this.GetHeadingFromObj(goa), mmo.speed / 0.514444f, mmo.currentFaction));
        if (mmo.type == 0)
        {
            this.seaPresent[side] = true;
        }
        else
        {
            this.airNumbers[side] += mmo.unitPrefabs.Count;
        }
        this.goasInBattle.Add(goa);
    }
}
```
4. **Compile**, then **File > Save Module**.

If Compile shows an error, send me a screenshot of the error list. The most likely one is a different name for the first line's types, which is quick to fix.

## Testing
1. Put two of your task forces (for example 10 ships and 6 ships) within about 50 km of one enemy force, ideally on different sides of it.
2. When the battle starts, both of your forces should be in it. In the roster both groups' ships appear, and on the battle map the second group starts in the direction it really came from.
3. Also try it the other way round: two AI forces near one of yours.

## Tuning
- `50000f`: how close (metres on the campaign map) a force must be to join.
- `30`: most surface ships per side in one battle.
- Distances on the campaign map are shrunk to one tenth in battle (the game's own rule), so a force 30 km away starts about 3 km from the fight.

**Fix (v2):** the game runs a second pass over the enemy list near the end of the battle setup (mainly for air groups), and just before it, it removes one enemy force from the 'in battle' list. Without the check above that force was added twice, the battle setup stopped and no enemy ships appeared. Surface forces now only join on the first pass.

Note: I could not compile or run this.

## Cooldown removed (user choice)
In both campaigns' `setup.txt`, set `"postEngageSeaCooldown":0` (was 1800 seconds). Without it, a force that has just fought can join the next battle straight away. Watch for back-to-back battles when forces stay next to each other after a fight. The air (`postEngageAirCooldown` 900) and submarine (`postEngageSubCooldown` 14400) cooldowns are unchanged.

## Final version (tested)
The working version is the logging version: every `Debug.Log` is written as `UnityEngine.Debug.Log` (plain `Debug` is ambiguous in dnSpy and won't compile). It has no cooldown check, a 40 ships per side limit, and writes `[TFJOIN]` lines to `WarOnTheSea_Data/output_log.txt` showing why each nearby force joined or was skipped. Tested: two enemy forces (6 and 8 ships) both joined a battle against one player force.
