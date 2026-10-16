# Smarter AI part 1: the AI weighs the odds before chasing

**Found in the code**
- When the AI spots one of your task forces, every aggressive AI surface force within 200 km chases it (`CampaignManager.CheckAISeaIntercept` -> `CampaignAI.GetNewSpottedWaypoint`). Each force goes at 1.25x speed, no matter how strong your force is.
- So a 3-destroyer patrol happily charges a battleship group and gets wiped out, one force at a time.
- The AI already sends badly damaged forces home after a battle (vanilla `taskForceRetreat...` settings), so that part needs no change.

**What changes**
1. Before chasing, an AI force compares strengths: warship tonnage, with carriers counted x1.5 and damaged ships counted less.
2. It adds up its own strength plus every other aggressive AI force within 200 km of your force (they all converge, and with the pincer change they join the same battle).
3. It only chases if that combined strength is at least **75% of yours**. Otherwise it ignores you and carries on with its mission.
4. Merchants, oilers and submarines don't count as strength, so the AI still hunts lone supply ships. Air groups are not affected.

## Step 1 - CampaignAI: helper methods (Edit Class)
After the `IsSeaGroupAggressive` method's closing `}`, paste:
```csharp
private float WarshipTonnage(MobileMapObject m)
{
    float total = 0f;
    if (m == null || m.unitPrefabs == null)
    {
        return 0f;
    }
    for (int i = 0; i < m.unitPrefabs.Count; i++)
    {
        if (!EngagementManager.instance.unitDataDictionary.ContainsKey(m.unitPrefabs[i]))
        {
            continue;
        }
        UnitData d = EngagementManager.instance.unitDataDictionary[m.unitPrefabs[i]];
        UnitSubType st = d.unitSubtype;
        if (st == UnitSubType.Submarine || st == UnitSubType.Merchant || st == UnitSubType.Oiler)
        {
            continue;
        }
        float weight = (float)d.displacement_weight;
        if (st == UnitSubType.Aircraft_Carrier || st == UnitSubType.Light_Carrier)
        {
            weight *= 1.5f;
        }
        total += weight * MobileMapObject.GetDamageSpeedFactor(m, i);
    }
    return total;
}

private bool ShouldChaseSpotted(GameObjectAnimator goa, float range)
{
    if (goa == null || goa.type != 0 || goa.mobileMapObject == null)
    {
        return true;
    }
    int index = CampaignManager.instance.GetClosestPlayerSpottedIndex(goa, range);
    if (index == -1)
    {
        return true;
    }
    MobileMapObject target = CampaignManager.instance.spottedContacts[index];
    if (target == null || target.type != 0 || target.gameObjectAnimator == null)
    {
        return true;
    }
    float targetStrength = this.WarshipTonnage(target);
    if (targetStrength <= 0f)
    {
        return true;
    }
    float mine = this.WarshipTonnage(goa.mobileMapObject);
    if (mine <= 0f)
    {
        return false;
    }
    float group = mine;
    for (int i = 0; i < CampaignManager.instance.otherMobile.Count; i++)
    {
        GameObjectAnimator other = CampaignManager.instance.otherMobile[i];
        if (other == null || other == goa || other.type != 0 || other.mobileMapObject == null)
        {
            continue;
        }
        if (!this.IsSeaGroupAggressive(other.mobileMapObject))
        {
            continue;
        }
        if (CampaignManager.instance.GetDistanceInMetresBetweenMapObjects(other.currentMap2DLocation, target.gameObjectAnimator.currentMap2DLocation) > range)
        {
            continue;
        }
        group += this.WarshipTonnage(other.mobileMapObject);
    }
    return group >= targetStrength * 0.75f;
}
```
Compile.

## Step 2 - CampaignAI.GetNewSpottedWaypoint
At the very top of the method (just after its opening `{`), paste, using the method's own names for its two inputs (the GameObjectAnimator and the float):
```csharp
if (!this.ShouldChaseSpotted(goa, range))
{
    return -1;
}
```
Compile, File > Save Module.

## Testing
- Park a strong force (battleships) where the AI patrols. Small AI patrols should no longer charge it. Larger AI fleets, or several together, still come.
- A lone oiler or merchant should still be hunted.

## Tuning
`0.75f` in ShouldChaseSpotted: how much of your strength the AI needs before attacking (higher = more cautious).
