# Damage control priorities (v0.17.6)

**What was wrong (found in the code)**
- Auto damage control (`DamageableSea.GetCoordsToRepair`) worked through fixed groups in this order:
  1. Fires, with a magazine fire first.
  2. Flooding.
  3. Knocked-out equipment.
  4. Structural damage.
  5. Rebuilding destroyed compartments.
- Inside each group it picked a job **at random**. A party could fight a fire in an empty storeroom while the engine room or the compartment next to a magazine burned.
- Flooding always waited behind every fire, even when the ship was close to sinking.

**What changes**

Every job now gets a priority, and each free party takes the most urgent one.

| Priority | Job |
|---|---|
| 1000 | Fire in a magazine |
| 750-840 | Flooding when the ship is in danger of sinking (more than 60% of the sinking limit) |
| 700 | Fire in a compartment next to a magazine |
| 600 | Fire by the torpedoes (torpedo room or tubes) |
| 500 | Fire in the hangar (aircraft and fuel) |
| 300 | Fire in machinery (engines, propellers, rudder) |
| 260 | Fire in the bridge, control room, conning tower or director |
| 230 | Fire by the guns |
| 200 | Any other fire |
| 150-240 | Flooding (more water = sooner, engine rooms a bit sooner) |
| 140 | Knocked-out machinery (speed and steering) |
| 120 | Knocked-out main guns or fire control |
| 100 | Other knocked-out weapons |
| 80 | Other knocked-out equipment |
| 40-60 | Structural damage (worst first) |
| last | Rebuilding destroyed compartments |

- The game's own settings still apply: if `repairKnockedOut` or `repairIntegrityTo` are switched off for a side in `config.txt`, those jobs are skipped as before.
- Equipment that needs a port repair is still skipped.
- Each dispatch writes a `[DC]` line to `output_log.txt`, with the ship, the compartment, the reason and how flooded the ship is.
- Parties you send by hand aren't affected. This only changes where Auto damage control sends them.

Back up the DLL first.

## Step 1 - DamageableSea.GetCoordsToRepair
1. Right-click **GetCoordsToRepair** (class **DamageableSea**) > **Edit Method (C#)...**
2. Select the whole method, from `public string GetCoordsToRepair()` down to its closing `}`, and paste this over it:
```csharp
public string GetCoordsToRepair()
{
    string bestId = string.Empty;
    float bestScore = 0f;
    string bestReason = string.Empty;
    float flooded = this.GetPercentageFlooded();
    bool sinkingDanger = flooded >= Config.instance.sinkFloodThreshold * 0.6f;
    for (int i = 0; i < this.cellsBurning.Count; i++)
    {
        string id = this.cellsBurning[i];
        if (!this.cellVariables.ContainsKey(id))
        {
            continue;
        }
        CellVariable cv = this.cellVariables[id];
        if (!cv.isBurning || cv.isUnderRepair || cv.parentCell == null)
        {
            continue;
        }
        float score = 200f;
        string reason = "fire";
        CellType ct = cv.parentCell.cellType;
        if (ct == CellType.Magazine)
        {
            score = 1000f;
            reason = "fire in magazine";
        }
        else if (ct == CellType.Torpedo_Room || ct == CellType.Torpedo)
        {
            score = 600f;
            reason = "fire by torpedoes";
        }
        else if (ct == CellType.Aircraft)
        {
            score = 500f;
            reason = "fire in hangar";
        }
        else if (ct == CellType.Engineering || ct == CellType.ElectricEngine || ct == CellType.Propeller || ct == CellType.DoublePropeller || ct == CellType.Rudder || ct == CellType.PropellersRudder)
        {
            score = 300f;
            reason = "fire in machinery";
        }
        else if (ct == CellType.Bridge || ct == CellType.ControlRoom || ct == CellType.Conning || ct == CellType.Director)
        {
            score = 260f;
            reason = "fire in command";
        }
        else if (ct == CellType.Primary || ct == CellType.Secondary)
        {
            score = 230f;
            reason = "fire by guns";
        }
        if (score < 700f && this.magazineCoords != null && id.Contains(","))
        {
            string[] a = id.Split(',');
            int ax;
            int ay;
            int az;
            if (a.Length == 3 && int.TryParse(a[0], out ax) && int.TryParse(a[1], out ay) && int.TryParse(a[2], out az))
            {
                for (int m = 0; m < this.magazineCoords.Count; m++)
                {
                    string[] b = this.magazineCoords[m].Split(',');
                    int bx;
                    int by;
                    int bz;
                    if (b.Length == 3 && int.TryParse(b[0], out bx) && int.TryParse(b[1], out by) && int.TryParse(b[2], out bz))
                    {
                        if (Mathf.Abs(ax - bx) + Mathf.Abs(ay - by) + Mathf.Abs(az - bz) <= 1)
                        {
                            score = 700f;
                            reason = "fire next to magazine";
                            break;
                        }
                    }
                }
            }
        }
        score += UnityEngine.Random.value * 5f;
        if (score > bestScore)
        {
            bestScore = score;
            bestId = id;
            bestReason = reason;
        }
    }
    for (int i = 0; i < this.cellsFlooded.Count; i++)
    {
        string id = this.cellsFlooded[i];
        if (!this.cellVariables.ContainsKey(id))
        {
            continue;
        }
        CellVariable cv = this.cellVariables[id];
        if (cv.isFlooded == 0f || cv.isUnderRepair || cv.isDestroyed || cv.parentCell == null)
        {
            continue;
        }
        float score = 150f + Mathf.Clamp01(cv.isFlooded) * 50f;
        string reason = "flooding";
        CellType ct = cv.parentCell.cellType;
        if (ct == CellType.Engineering || ct == CellType.ElectricEngine)
        {
            score += 40f;
            reason = "flooding in machinery";
        }
        if (sinkingDanger)
        {
            score += 600f;
            reason = "flooding, ship in danger of sinking";
        }
        score += UnityEngine.Random.value * 5f;
        if (score > bestScore)
        {
            bestScore = score;
            bestId = id;
            bestReason = reason;
        }
    }
    if (Config.instance.repairKnockedOut[(int)this.parentUnit.faction])
    {
        for (int i = 0; i < this.cellsOffline.Count; i++)
        {
            string id = this.cellsOffline[i];
            if (!this.cellVariables.ContainsKey(id))
            {
                continue;
            }
            CellVariable cv = this.cellVariables[id];
            if (!cv.isOffline || cv.isUnderRepair || cv.isDestroyed || cv.needsPortRepair || cv.parentCell == null)
            {
                continue;
            }
            float score = 80f;
            string reason = "knocked out";
            CellType ct = cv.parentCell.cellType;
            if (ct == CellType.Engineering || ct == CellType.ElectricEngine || ct == CellType.Propeller || ct == CellType.DoublePropeller || ct == CellType.Rudder || ct == CellType.PropellersRudder)
            {
                score = 140f;
                reason = "knocked-out machinery";
            }
            else if (ct == CellType.Primary || ct == CellType.Director || ct == CellType.ControlRoom || ct == CellType.Bridge || ct == CellType.Conning)
            {
                score = 120f;
                reason = "knocked-out main guns or fire control";
            }
            else if (ct == CellType.Secondary || ct == CellType.Torpedo || ct == CellType.Aircraft)
            {
                score = 100f;
                reason = "knocked-out weapons";
            }
            score += UnityEngine.Random.value * 5f;
            if (score > bestScore)
            {
                bestScore = score;
                bestId = id;
                bestReason = reason;
            }
        }
    }
    if (Config.instance.repairIntegrityTo[(int)this.parentUnit.faction] > 0f)
    {
        for (int i = 0; i < this.cellsDamaged.Count; i++)
        {
            string id = this.cellsDamaged[i];
            if (!this.cellVariables.ContainsKey(id))
            {
                continue;
            }
            CellVariable cv = this.cellVariables[id];
            if (cv.isDestroyed || cv.isUnderRepair || cv.integrity == cv.maxIntegrity || cv.maxIntegrity <= 0f)
            {
                continue;
            }
            float score = 40f + (1f - cv.integrity / cv.maxIntegrity) * 20f + UnityEngine.Random.value * 5f;
            if (score > bestScore)
            {
                bestScore = score;
                bestId = id;
                bestReason = "structural damage";
            }
        }
    }
    if (bestId == string.Empty)
    {
        for (int r = 0; r < this.cellsDestroyed.Count; r++)
        {
            string rebuildId = this.cellsDestroyed[r];
            if (!rebuildId.Contains(",") || !this.cellVariables.ContainsKey(rebuildId))
            {
                continue;
            }
            CellVariable rebuildCell = this.cellVariables[rebuildId];
            if (rebuildCell.parentCell != null && !rebuildCell.parentCell.isUpper && !rebuildCell.isUnderRepair && !rebuildCell.isBurning)
            {
                bestId = rebuildId;
                bestReason = "rebuild destroyed compartment";
                break;
            }
        }
    }
    if (bestId != string.Empty)
    {
        UnityEngine.Debug.Log("[DC] " + (string.IsNullOrEmpty(this.parentUnit.unitInstanceName) ? this.parentUnit.unitData.unitName : this.parentUnit.unitInstanceName) + " sends a party to " + bestId + ": " + bestReason + " (flooded " + (flooded * 100f).ToString("F0") + "%)");
    }
    return bestId;
}
```
3. **Compile**, then **File > Save Module**.

This replaces the earlier version from lasting damage and the combat damage package. Everything those added (skipping port-repair equipment, rebuilding destroyed compartments last) is kept.

## Testing
1. Turn on Auto damage control on one of your ships and let it take a beating, with fires in several places.
2. The parties should go to magazine fires, fires next to magazines and machinery first, and to general fires after that.
3. Get a ship heavily flooded: once it's near the sinking point, parties should switch to pumping before fighting ordinary fires.
4. In `output_log.txt`, each `[DC]` line shows what the party was sent to and why.

## Tuning (all in GetCoordsToRepair)
- The `score =` numbers are the priorities in the table. Higher = sooner.
- `0.6f` in `sinkFloodThreshold * 0.6f`: how close to sinking before flooding jumps the queue.
- `600f` in the flooding section: how far it jumps.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.
