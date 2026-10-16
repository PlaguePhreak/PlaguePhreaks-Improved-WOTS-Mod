# Damaged ships slow their task force

**What was wrong (found in the code)**
- On the campaign map a task force always moves at the cruising speed of its slowest ship *class*, from the ship data. Battle damage is never taken into account.
- The damage itself is kept: each ship's wrecked compartments are saved with the task force after a battle, and in the next battle a ship with wrecked propellers or engine rooms is slower. Only the map ignores it.
- After a battle the game automatically patches up knocked-out equipment, fires and flooding. Only compartments that were **destroyed** stay broken until the ship is repaired at a port.

**What changes**
1. A ship's map speed is reduced by its destroyed propeller and engine-room compartments, using the same rule the battle uses: losing half the propellers costs half the speed; losing half the engine rooms costs half the speed; both add up. It never drops below 25% (the ship is crawling, not stopped).
2. The task force moves at the speed of its slowest ship *after* damage, so one crippled ship slows the whole force.
3. The speed is recalculated right after every battle, and whenever ships join or leave a force (split, merge, add a ship), so detaching a cripple lets the rest speed up again.
4. Ships repaired at a port come back at full speed.
5. It works for the AI too: damaged enemy forces limp home.
6. It works with the fuel system: a force that is out of fuel still crawls, and when refuelled it returns to its (possibly damaged) speed.

Back up the DLL first. Do the steps in order.

## Step 1 - helper method (MobileMapObject)
1. Right-click class **MobileMapObject** > **Edit Class (C#)...**
2. Press **Ctrl+End**. Click at the end of the second-to-last `}` (the end of the last method), press Enter, and paste:
```csharp
public static float GetDamageSpeedFactor(MobileMapObject mmo, int index)
{
    try
    {
        if (mmo.cellVariables == null || index < 0 || index >= mmo.cellVariables.Count || index >= mmo.unitPrefabs.Count)
        {
            return 1f;
        }
        string cellData = mmo.cellVariables[index];
        if (string.IsNullOrEmpty(cellData) || cellData == "DESTROYED")
        {
            return 1f;
        }
        if (!EngagementManager.instance.unitDataDictionary.ContainsKey(mmo.unitPrefabs[index]))
        {
            return 1f;
        }
        UnitData shipData = EngagementManager.instance.unitDataDictionary[mmo.unitPrefabs[index]];
        if (shipData == null || shipData.cellDictionary == null)
        {
            return 1f;
        }
        int props = 0;
        int engines = 0;
        foreach (var pair in shipData.cellDictionary)
        {
            int cellKind = (int)pair.Value.cellType;
            if (cellKind == 16 || cellKind == 17 || cellKind == 19)
            {
                props++;
            }
            else if (cellKind == 14)
            {
                engines++;
            }
        }
        int propsLost = 0;
        int enginesLost = 0;
        string[] parts = cellData.Split(new char[] { '|' });
        for (int i = 0; i + 1 < parts.Length; i += 2)
        {
            if (!parts[i + 1].Contains("\"isDestroyed\":true") && !parts[i + 1].Contains("\"isOffline\":true"))
            {
                continue;
            }
            if (!shipData.cellDictionary.ContainsKey(parts[i]))
            {
                continue;
            }
            int lostKind = (int)shipData.cellDictionary[parts[i]].cellType;
            if (lostKind == 16 || lostKind == 17 || lostKind == 19)
            {
                propsLost++;
            }
            else if (lostKind == 14)
            {
                enginesLost++;
            }
        }
        float factor = 1f;
        if (props > 0)
        {
            factor -= Config.instance.speedPenaltyNoPropellers * (float)propsLost / (float)props;
        }
        if (engines > 0)
        {
            factor -= Config.instance.speedPenaltyNoEngineering * (float)enginesLost / (float)engines;
        }
        return Mathf.Clamp(factor, 0.25f, 1f);
    }
    catch
    {
        return 1f;
    }
}
```
3. **Compile.**

(16, 17 and 19 are the game's propeller compartment types, 14 is engine rooms.)

## Step 2 - task-force speed uses damaged speed (CampaignManager.GetMobileMapObjectSpeed)
1. Right-click **GetMobileMapObjectSpeed** (class **CampaignManager**) > **Edit Method (C#)...**
2. Near the top is a short loop that collects every ship's `maxKnots`. The line inside it looks like this (dnSpy may use different names for `list` and `i`):
```csharp
list.Add(EngagementManager.instance.unitDataDictionary[mmo.unitPrefabs[i]].maxKnots);
```
3. Change it so it reads (use the same names dnSpy shows):
```csharp
list.Add(EngagementManager.instance.unitDataDictionary[mmo.unitPrefabs[i]].maxKnots * MobileMapObject.GetDamageSpeedFactor(mmo, i));
```
In other words, add ` * MobileMapObject.GetDamageSpeedFactor(mmo, i)` straight after `.maxKnots`, where `i` is whatever name is inside `unitPrefabs[...]`.
4. **Compile.**

## Step 3 - recalculate after battle (CampaignManager.ProcessMobileObjectPostCombat)
1. Right-click **ProcessMobileObjectPostCombat** (class **CampaignManager**) > **Edit Method (C#)...**
2. This method contains `DestroyMapMobileObject` twice. Find the **second** one. It is in a block that also contains `recreateMissions.Add(...)` and ends with `return;`:
```csharp
    CampaignInterface.instance.DestroyMapMobileObject(mmo.gameObjectAnimator);
    return;
}
```
3. Click at the end of the `}` that closes that block, press Enter, and paste:
```csharp
if (mmo.type == 0)
{
    float damagedSpeed = this.GetMobileMapObjectSpeed(mmo);
    if (mmo.fuelSavedSpeed > 0f)
    {
        mmo.fuelSavedSpeed = damagedSpeed;
    }
    else
    {
        mmo.speed = damagedSpeed;
    }
}
```
4. **Compile**, then **File > Save Module**.

## Testing
1. Fight a battle in which one of your ships takes propeller or engine-room damage that is still red (destroyed) at the end.
2. Back on the map, hover the task force: its speed label (e.g. "Very Fast (22+kn)") should drop if the damaged ship is now its slowest.
3. Split the damaged ship into its own task force: the rest should go back to their normal speed, the cripple keeps the low speed.
4. Release it for repair at a port and recruit it again: full speed.

Note: funnel damage (a small extra penalty in battle) is not counted on the map. I could not run this; if dnSpy shows a compile error, send me a screenshot.
