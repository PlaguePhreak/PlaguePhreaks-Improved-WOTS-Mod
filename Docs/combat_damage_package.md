# Combat damage package (one install)

This one guide replaces `damaged_speed.md` and `damage_control.md`: do this instead of those two. Back up `Assembly-CSharp.dll` and `config.txt` first, then do the steps in order.

**What you get**
- **Damaged ships slow their task force** on the campaign map (destroyed propellers or engine rooms; never below 25% speed). Recalculated after every battle and whenever ships join or leave a force.
- **List and capsize:** uneven flooding makes a ship list; at 60% of its sinking limit it capsizes and sinks.
- **Automatic counter-flooding with a safety net:** at 25% of the sinking limit the crew floods one intact compartment on the high side every 2 s, but never takes total flooding above 80% of the sinking limit, and pumps its own water back out if the list swings the other way. AI ships always; your ships when Auto damage control is on (the game's manual counter-flood toggle still works).
- **Water and fire:** a flooded compartment can't catch fire; flooding a burning compartment puts it out (so flooding a burning magazine saves the ship).
- **Fire no longer floods** the compartment it is burning in (needed for the rule above).
- **Bigger fires spread faster:** each fire already burning on the ship adds 10% to the chance of fire spreading, up to triple.
- **Destroyed compartments can be rebuilt at sea, slowly:** a damage party can rebuild a destroyed hull compartment (engine rooms, propellers, magazines and so on). It takes 10 minutes on a destroyer up to 30 minutes on a battleship, faster with a veteran crew and slower with a battered one. The rebuilt compartment then still needs pumping out, its equipment bringing back online and its structure patching up. Destroyed deck items (guns, AA, bridge, funnels) stay destroyed until port repair (a deliberate balance choice).
- **Harder damage control (config):** fires burn hotter (15 per tick instead of 10), fires and flooding take 180 s instead of 120 s to fight, and both spread a little more easily.

> **If Compile shows `CS1612: Cannot modify the return value of ... because it is not a variable`** on a line you did not paste, it is a dnSpy quirk in the game's own particle-effect code. Split that line in two. For example
> `this.fires[shipFireIndex].main.startSize = new ParticleSystem.MinMaxCurve(vector.x, vector.y);`
> becomes
> `var fireMain = this.fires[shipFireIndex].main;`
> `fireMain.startSize = new ParticleSystem.MinMaxCurve(vector.x, vector.y);`
> (Known spots: UnitSea line with `bowwave.velocityOverLifetime.x`, DamageableSea.SetFire line with `.main.startSize`.) For an Edit Class step you can also use **Add Class Members (C#)...** instead, which only compiles the new code.

---

## Step 1 - UnitSea: new fields and methods
1. Right-click class **UnitSea** > **Edit Class (C#)...**
2. Press **Ctrl+End**. Click at the end of the second-to-last `}` (the end of the last method), press Enter, and paste:
```csharp
public float listCheckTimer;

public System.Collections.Generic.List<string> counterFloodCells = new System.Collections.Generic.List<string>();

private int FloodSideOfCell(int[] regions)
{
    if (regions == null || regions.Length == 0)
    {
        return 0;
    }
    bool port = false;
    bool starboard = false;
    for (int i = 0; i < regions.Length; i++)
    {
        if (regions[i] < 3)
        {
            port = true;
        }
        else
        {
            starboard = true;
        }
    }
    if (port && !starboard)
    {
        return -1;
    }
    if (starboard && !port)
    {
        return 1;
    }
    return 0;
}

public void CheckListAndCounterflood(float duration)
{
    if (this.isDestroyed || this.damageableSea == null || this.compartments == null || this.compartments.Length < 6)
    {
        return;
    }
    if (this.unitData.unitSubtype == UnitSubType.Submarine)
    {
        return;
    }
    this.listCheckTimer += duration;
    if (this.listCheckTimer < 2f)
    {
        return;
    }
    this.listCheckTimer = 0f;
    float portFlood = this.compartments[0].currentFlooding + this.compartments[1].currentFlooding + this.compartments[2].currentFlooding;
    float starboardFlood = this.compartments[3].currentFlooding + this.compartments[4].currentFlooding + this.compartments[5].currentFlooding;
    float totalFlood = portFlood + starboardFlood;
    float sinkLimit = Config.instance.sinkAtThreshold + this.GetBonus();
    float list = portFlood - starboardFlood;
    float listSize = Mathf.Abs(list);
    if (listSize > sinkLimit * 0.6f)
    {
        this.damageableSea.SinkShip();
        return;
    }
    if (this.counterFloodCells == null)
    {
        this.counterFloodCells = new System.Collections.Generic.List<string>();
    }
    if (listSize > sinkLimit * 0.1f && this.counterFloodCells.Count > 0)
    {
        for (int i = this.counterFloodCells.Count - 1; i >= 0; i--)
        {
            string pumpId = this.counterFloodCells[i];
            if (!this.damageableSea.cellVariables.ContainsKey(pumpId))
            {
                this.counterFloodCells.RemoveAt(i);
                continue;
            }
            int pumpSide = this.FloodSideOfCell(this.damageableSea.cellVariables[pumpId].parentCell.regionIndex);
            if ((list > 0f && pumpSide == -1) || (list < 0f && pumpSide == 1))
            {
                this.damageableSea.UnfloodCompartment(pumpId);
                this.damageableSea.ModifyCellIDInStatusList(pumpId, this.damageableSea.cellsFlooded, false);
                this.counterFloodCells.RemoveAt(i);
                return;
            }
        }
    }
    if (this.faction == Faction.Player && !this.damageableSea.autoDC)
    {
        return;
    }
    if (listSize < sinkLimit * 0.25f)
    {
        return;
    }
    int floodSide = (list > 0f) ? 1 : -1;
    string bestId = null;
    float bestAmount = 0f;
    foreach (var pair in this.damageableSea.cellVariables)
    {
        var cell = pair.Value;
        if (cell == null || cell.parentCell == null || !cell.parentCell.canFlood || cell.isDestroyed || cell.isBurning || cell.isFlooded > 0f)
        {
            continue;
        }
        if (this.FloodSideOfCell(cell.parentCell.regionIndex) != floodSide)
        {
            continue;
        }
        float amount = cell.parentCell.floodCapacity / 1000f;
        if (amount <= 0f || amount > listSize)
        {
            continue;
        }
        if (amount > bestAmount)
        {
            bestAmount = amount;
            bestId = pair.Key;
        }
    }
    if (bestId == null)
    {
        return;
    }
    if (totalFlood + bestAmount > sinkLimit * 0.8f)
    {
        return;
    }
    this.damageableSea.FloodCompartment(this.damageableSea.cellVariables[bestId], 1f);
    this.counterFloodCells.Add(bestId);
}
```
3. **Compile.**

## Step 2 - MobileMapObject: damaged-speed helper
1. Right-click class **MobileMapObject** > **Edit Class (C#)...**
2. Press **Ctrl+End**. Click at the end of the second-to-last `}`, press Enter, and paste:
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
3. **Compile**, **File > Save Module**, then **close and reopen dnSpy** and the DLL.

## Step 3 - CampaignManager.GetMobileMapObjectSpeed
1. Right-click **GetMobileMapObjectSpeed** (class **CampaignManager**) > **Edit Method (C#)...**
2. Near the top is a short loop collecting each ship's `maxKnots`. Its line looks like this (dnSpy may use other names for `list` and `i`):
```csharp
list.Add(EngagementManager.instance.unitDataDictionary[mmo.unitPrefabs[i]].maxKnots);
```
3. Add ` * MobileMapObject.GetDamageSpeedFactor(mmo, i)` straight after `.maxKnots`, using the same name that is inside `unitPrefabs[...]`:
```csharp
list.Add(EngagementManager.instance.unitDataDictionary[mmo.unitPrefabs[i]].maxKnots * MobileMapObject.GetDamageSpeedFactor(mmo, i));
```
4. **Compile.**

## Step 4 - CampaignManager.ProcessMobileObjectPostCombat
1. Right-click **ProcessMobileObjectPostCombat** (class **CampaignManager**) > **Edit Method (C#)...**
2. `DestroyMapMobileObject` appears twice. Find the **second** one, in the block that also contains `recreateMissions.Add(...)`:
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
4. **Compile.**

## Step 5 - UnitSea.CheckFlooding
1. Right-click **CheckFlooding** (class **UnitSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
this.CheckListAndCounterflood(fixedDuration);
```
(If dnSpy shows the method's number argument with a different name than `fixedDuration`, use that name.)
3. **Compile.**

## Step 6 - DamageableSea.SetFire
1. Right-click **SetFire** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (isOn && cv.isFlooded > 0f)
{
    return;
}
```
3. **Compile.**

## Step 7 - DamageableSea.FloodCompartment
1. Right-click **FloodCompartment** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (cv.isBurning && amount > 0f)
{
    this.ExtinguishCell(cv);
}
```
3. **Compile.**

## Step 8 - DamageableSea.SpreadFires (fire no longer floods)
1. Right-click **SpreadFires** (class **DamageableSea**) > **Edit Method (C#)...**
2. Near the top there is exactly one line that calls `ApplyDamageToCell`. It looks like:
```csharp
this.ApplyDamageToCell(cellVariable, num, 0f, true, true, true);
```
3. Change the **first** `true` to `false` (that one means "may flood"):
```csharp
this.ApplyDamageToCell(cellVariable, num, 0f, false, true, true);
```
4. **Compile.**

## Step 9 - DamageableSea.GetBurnProbability (big fires spread faster)
1. Right-click **GetBurnProbability** (class **DamageableSea**) > **Edit Method (C#)...**
2. Press **Ctrl+A** and paste this over everything:
```csharp
using System;
using UnityEngine;

public partial class DamageableSea : MonoBehaviour
{
	private float GetBurnProbability()
	{
		float num = EngagementData.instance.baseFireSpreadP + Mathf.Abs(this.parentUnit.percentMaxSpeed) * Config.instance.fireSpreadSpeedFactor;
		num *= Mathf.Min(1f + 0.1f * (float)this.cellsBurning.Count, 3f);
		return num * this.vulnerable;
	}
}
```
3. **Compile.**

## Step 10 - DamageableSea.GetRepairTime (time to rebuild)
1. Right-click **GetRepairTime** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (cv.isDestroyed && !cv.isBurning && cv.parentCell != null && !cv.parentCell.isUpper && cv.parentCell.cellID.Contains(","))
{
    float rebuildTime = Mathf.Clamp(600f + (float)this.parentUnit.unitData.displacement_weight * 0.035f, 600f, 1800f);
    return rebuildTime * this.vulnerable / Mathf.Max(0.25f, this.parentUnit.efficiency);
}
```
3. **Compile.**

## Step 11 - DamageableSea.RepairCompartment (finish a rebuild)
1. Right-click **RepairCompartment** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
var rebuilt = this.cellVariables[id];
if (rebuilt.isDestroyed && !rebuilt.isBurning && rebuilt.parentCell != null && !rebuilt.parentCell.isUpper && id.Contains(","))
{
    rebuilt.isDestroyed = false;
    rebuilt.integrity = 25f;
    this.ModifyCellIDInStatusList(id, this.cellsDestroyed, false);
    this.ModifyCellIDInStatusList(id, this.cellsDamaged, true);
    if ((int)rebuilt.parentCell.cellType != 0)
    {
        rebuilt.isOffline = true;
        this.ModifyCellIDInStatusList(id, this.cellsOffline, true);
    }
    rebuilt.repairTime = this.GetRepairTime(rebuilt);
    if (rebuilt.repairTime <= 0f)
    {
        this.MovePartyToCell(id, false);
    }
    this.speedPenalty = this.GetSpeedPenalty();
    this.turnPenalty = this.GetTurnPenalty();
    this.CheckUpdateCellIcons(rebuilt);
    return;
}
```
3. **Compile.**

## Step 12 - DamageableSea.GetCoordsToRepair (auto damage control rebuilds too)
1. Right-click **GetCoordsToRepair** (class **DamageableSea**) > **Edit Method (C#)...**
2. Scroll to the very bottom. The last line before the method's closing `}` is:
```csharp
return string.Empty;
```
3. Click at the **start** of that line, press Enter (so it moves down one line), click on the new empty line above it, and paste:
```csharp
for (int r = 0; r < this.cellsDestroyed.Count; r++)
{
    string rebuildId = this.cellsDestroyed[r];
    if (!rebuildId.Contains(",") || !this.cellVariables.ContainsKey(rebuildId))
    {
        continue;
    }
    var rebuildCell = this.cellVariables[rebuildId];
    if (rebuildCell.parentCell != null && !rebuildCell.parentCell.isUpper && !rebuildCell.isUnderRepair && !rebuildCell.isBurning)
    {
        return rebuildId;
    }
}
```
(Auto damage control still deals with fires, flooding, knocked-out equipment and damage first; rebuilding is its last job.)
4. **Compile.**

## Step 13 - save
**File > Save Module**, then close dnSpy.

## Step 14 - config.txt
Open `StreamingAssets/default/config.txt` in Notepad. For each setting, Ctrl+F the name and change the value:

| Setting | Old | New |
|---|---|---|
| `burnPerTick` | `10` | `15` |
| `extinguishFireTime` | `{"x":120.0,"y":120.0}` | `{"x":180.0,"y":180.0}` |
| `repairFloodTime` | `{"x":120.0,"y":120.0}` | `{"x":180.0,"y":180.0}` |
| `fireSpreadBaseProbability` | `0.02` | `0.03` |
| `floodBaseSpreadProbability` | `0.05` | `0.06` |

Save the file.

---

## Testing
1. **Counter-flooding and capsize:** in a battle, open one of your ships' damage control, turn on Auto damage control, then use the manual counter-flood toggle to flood 3-4 compartments on one side. Within a few seconds the crew should flood a compartment on the other side. Keep flooding one side: once more counter-flooding is no longer safe, the ship keeps listing and then capsizes.
2. **Water and fire:** when a compartment is burning, flood it with the manual toggle: the fire goes out. A flooded compartment hit by a shell should not catch fire.
3. **Fires:** an unattended fire should burn a compartment out in about 3 minutes, and spread more readily on a ship with several fires.
4. **Rebuilding:** when a hull compartment is destroyed (black), click it once with a free damage party: the party count drops and the timer in the detail panel shows 600-1800 seconds depending on the ship. When it finishes, the compartment comes back damaged (and flooded, if it is in the hull), and the party carries on pumping and repairing. Destroyed deck items cannot be rebuilt. With Auto damage control on, idle parties start rebuilds by themselves. If a party is pulled off a rebuild, the timer starts again from the beginning next time, so leave it on the job.
5. **Map speed:** after a battle in which a ship's propellers or engine rooms are destroyed (red), the task force's speed label on the map should drop. Split that ship off and the others speed up again.

## Tuning
- Capsize / counter-flood / safety net: `0.6f`, `0.25f`, `0.8f` in **CheckListAndCounterflood** (UnitSea); `2f` is seconds between checks.
- Fire spread growth: `0.1f` (per fire) and `3f` (maximum) in **GetBurnProbability**.
- Rebuild time: `600f` (minimum seconds), `0.035f` (extra seconds per ton of displacement) and `1800f` (maximum) in **GetRepairTime**.
- Minimum damaged speed: `0.25f` in **GetDamageSpeedFactor** (MobileMapObject).

Notes: funnel damage is not counted for map speed. If Auto damage control pumps out a counter-flooded compartment, the crew refloods it a moment later (harmless, but it can keep one damage party busy). I could not compile or run this; if dnSpy shows a compile error, send me a screenshot of the error list and the code window.
