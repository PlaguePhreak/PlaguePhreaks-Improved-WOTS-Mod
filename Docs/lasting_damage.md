# Lasting damage between battles

**Found in the code:** `EngagementData.GetCellVariables` saves each ship's damage when a battle ends. With `repairKnockedOut` on, it switches every knocked-out (offline) compartment back on, so only destroyed compartments carried over.

**What changes**
- Knocked-out equipment stays offline after battle and is marked `needsPortRepair`.
- Damage parties can't repair `needsPortRepair` equipment at sea. Equipment knocked out in the new battle can still be repaired as normal.
- Releasing the ship for repair at a port clears it (the ship comes back fresh).
- Offline engine rooms and propellers also slow the task force on the map (`GetDamageSpeedFactor` already counts offline).
- Applies to the AI too.

## Step 1 - CellVariable (Edit Class)
After `public bool isOffline;` add `public bool needsPortRepair;`. Compile, Save Module, reopen dnSpy.

## Step 2 - EngagementData.GetCellVariables (replace the method)
```csharp
public string GetCellVariables(DamageableSea ds, bool inBattleSave)
{
    string text = string.Empty;
    if (ds != null)
    {
        int side = (int)ds.parentUnit.faction;
        foreach (KeyValuePair<string, CellVariable> pair in ds.cellVariables)
        {
            CellVariable cv = pair.Value;
            if (!inBattleSave)
            {
                if (Config.instance.repairIntegrityTo[side] > 0f)
                {
                    Utilities.RepairCompartmentToIntegrity(cv, side);
                }
                bool keepOffline = cv.isOffline && !cv.isDestroyed;
                if (keepOffline)
                {
                    cv.needsPortRepair = true;
                }
                if (cv.isDestroyed || cv.tdsHit || keepOffline || (Config.instance.repairIntegrityTo[side] < 1f && cv.integrity != 100f))
                {
                    cv.isBurning = false;
                    cv.isFlooded = 0f;
                    cv.isUnderRepair = false;
                    cv.repairTime = 0f;
                    text = text + pair.Key + "|" + JsonUtility.ToJson(cv) + "|";
                }
            }
            else if (cv.integrity != cv.maxIntegrity || cv.isFlooded != 0f || cv.isBurning || cv.tdsHit || cv.isOffline)
            {
                text = text + pair.Key + "|" + JsonUtility.ToJson(cv) + "|";
            }
        }
    }
    if (text.Length > 0)
    {
        text = text.Substring(0, text.Length - 1);
    }
    return text;
}
```

## Step 3 - block repair at sea
- **DamageableSea.RepairCompartment:** the `if` with `isOffline` and `repairKnockedOut` gets ` && !this.cellVariables[id].needsPortRepair`.
- **DamageableSea.GetRepairTime:** the `if` with `cv.isOffline` and `repairKnockedOut` gets ` && !cv.needsPortRepair`.
Compile, Save Module.

## Testing
1. End a battle with a knocked-out (red) gun or engine room.
2. Next battle: still red, and a party can't repair it.
3. Release at port and recruit again: all working.

Note: auto damage control may briefly send a party to such a compartment; it finishes instantly and moves on. I could not compile or run this.

## Fix - auto damage control (DamageableSea.GetCoordsToRepair)
The knocked-out list now skips `needsPortRepair` compartments, so Auto DC doesn't keep sending parties to equipment it can't fix. The method was replaced in full; it also restores the auto-rebuild of destroyed hull compartments (combat damage package Step 12, which was missing). Order: fires (magazine first) > flooding > knocked-out (not needing port) > structure > rebuild.
