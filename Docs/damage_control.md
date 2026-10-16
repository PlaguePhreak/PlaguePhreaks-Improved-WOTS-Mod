# Damage control realism: fire, flooding, list, capsize, counter-flooding

**What the game does now (found in the code)**
- A ship floats on 6 buoyancy points: port and starboard, each fore, midships and aft. Flooded hull compartments take away buoyancy from the points they sit over. A ship sinks when it has lost about 1.2 points' worth of buoyancy (more for big ships).
- Flooding one side more than the other only tilts the model a little; it never capsizes a ship. (Every sinking already plays a roll-over animation.)
- Fire can start in a compartment even while it is full of water.
- The game already has **manual** counter-flooding: the first toggle on the damage-control panel. With it on, clicking a hull compartment floods it on purpose. There is no automatic version and no safety check.

**What changes**
1. **Water and fire:** a flooded compartment cannot catch fire, and flooding a compartment that is burning puts that fire out.
2. **List and capsize:** the ship's list is measured as port flooding minus starboard flooding. If it reaches **60%** of what would sink the ship, the ship capsizes and sinks. Uneven flooding is now much deadlier than even flooding.
3. **Automatic counter-flooding:** when the list passes **25%** of the sinking limit, the crew floods one intact compartment on the high side to level the ship (every 2 seconds, one compartment at a time, never more than the list itself).
4. **Safety net:** counter-flooding is skipped if it would bring total flooding above **80%** of the sinking limit. If the ship cannot be levelled safely it is left listing; if the list keeps growing it capsizes.
5. **Pumping back out:** if the list swings the other way (for example after damage control pumps out the original flooding), the crew pumps out its own counter-flooded compartments first, so a ship does not end up flooding both sides.
6. **Who does it:** AI ships always. Your ships only when **Auto damage control** is on for that ship; with it off, you still have the game's manual counter-flood toggle.
7. **Harder fires and flooding (config):** fires and flooding take 50% longer to fight, and spread a bit more easily.

Back up the DLL first. Do the steps in order.

## Step 1 - new fields and methods (UnitSea)
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
3. **Compile**, **File > Save Module**, then **close and reopen dnSpy** and the DLL.

## Step 2 - run the check (UnitSea.CheckFlooding)
1. Right-click **CheckFlooding** (class **UnitSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
this.CheckListAndCounterflood(fixedDuration);
```
(If dnSpy shows the method's number argument with a different name than `fixedDuration`, use that name.)
3. **Compile.**

## Step 3 - water puts out fire (DamageableSea)
**3a - no fire in a flooded compartment.**
1. Right-click **SetFire** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (isOn && cv.isFlooded > 0f)
{
    return;
}
```
3. **Compile.**

**3b - flooding a burning compartment puts it out.**
1. Right-click **FloodCompartment** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (cv.isBurning && amount > 0f)
{
    this.ExtinguishCell(cv);
}
```
3. **Compile**, then **File > Save Module**.

## Step 4 - harder fires and flooding (config.txt)
Open `StreamingAssets/default/config.txt` in Notepad and change these four values (Ctrl+F for each name):

| Setting | Old | New |
|---|---|---|
| `extinguishFireTime` | `{"x":120.0,"y":120.0}` | `{"x":180.0,"y":180.0}` |
| `repairFloodTime` | `{"x":120.0,"y":120.0}` | `{"x":180.0,"y":180.0}` |
| `fireSpreadBaseProbability` | `0.02` | `0.03` |
| `floodBaseSpreadProbability` | `0.05` | `0.06` |

(`x` is your ships, `y` is the enemy's: seconds a damage party needs per fire or flooded compartment.)

## Testing
- Torpedo a ship on one side (or use the manual counter-flood toggle on a ship of yours to flood several compartments on one side).
- With Auto damage control on, compartments on the other side should flood by themselves a few seconds later, and the hull display should show them flooded.
- Keep flooding one side: once counter-flooding is no longer safe, the ship should keep listing and then capsize and sink before it would have sunk from even flooding.
- Start a fire in a compartment, then flood it with the manual toggle: the fire should go out. A flooded compartment should not catch fire when hit.

## Tuning (all in CheckListAndCounterflood)
- `0.6f`: capsize point, as a share of the sinking limit. Higher = ships tolerate more list.
- `0.25f`: list at which the crew starts counter-flooding.
- `0.8f`: the safety net. Counter-flooding never takes total flooding above this share of the sinking limit.
- `2f`: seconds between checks (one compartment per check).

Note: if Auto damage control pumps out a counter-flooded compartment, the list returns and the crew floods it again a moment later. That is harmless, but it can keep one damage party busy. I could not run this; if dnSpy shows a compile error, send me a screenshot.
