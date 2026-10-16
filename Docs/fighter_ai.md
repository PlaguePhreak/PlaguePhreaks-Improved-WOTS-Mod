# Fighter AI: escorts and CAP (v0.17.2)

**What was wrong (found in the code)**
- **Every escort chases the first plane it sees:** when an AI escort fighter spots one of your planes, every AI fighter in the battle is sent at that one plane (`EngagementAI.OnDetectUnit`). The whole escort leaves its bombers to gang up on a single target, often a fighter, and your other fighters get a free run at the bombers.
- **Target choice ignores the job:** fighters pick their next target with `EngagementAI.GetBestDogfightTarget`. It takes the closest enemy plane with fewer than 2 attackers. It doesn't know whether the fighter is escorting or defending, and doesn't care whether the target is a fighter, a torpedo bomber still carrying its torpedo, or a bomber that has already dropped.

**What changes**
1. **Escorts protect their bombers.** A fighter whose side still has bombers carrying their payload counts as an escort.
   - It goes for enemy fighters first, and above all for fighters that are attacking one of its bombers.
   - It mostly leaves enemy bombers alone.
   - Enemy planes more than 5 km from the nearest bomber it protects become less and less interesting, so escorts don't wander off.
2. **Defending fighters (CAP) go for the bombers.** A fighter whose side has no loaded bombers counts as CAP.
   - It goes for enemy bombers that still carry their payload: torpedo bombers first, then dive bombers, then level bombers.
   - Enemy planes within 10 km of its own ships are preferred.
   - It fights enemy fighters normally, and largely ignores bombers that have already dropped.
3. **Self-defence:** any fighter strongly prefers a plane that is attacking it.
4. **Spreading out:** each fighter already attacking a plane makes that plane less attractive to the next one, so fighters split up instead of piling on.
5. **Stability:** a fighter slightly prefers its current target, so it doesn't flip between targets.
6. **When escorts spot an enemy,** each AI fighter now picks its own target with the rules above, instead of all of them diving on the one plane that was spotted.
7. This applies to both sides. Your fighters on auto (dogfight mode) use the same choices.
8. Each choice writes a `[FIGHTER]` line to `output_log.txt`.

Back up the DLL first. Both steps are in class **EngagementAI**.

## Step 1 - EngagementAI.GetBestDogfightTarget
1. Right-click **GetBestDogfightTarget** (class **EngagementAI**) > **Edit Method (C#)...**
2. Select the whole method, from `public Unit GetBestDogfightTarget(` down to its closing `}`, and paste this over it:
```csharp
public Unit GetBestDogfightTarget(Unit unit, List<Unit> units)
{
    if (unit == null || units == null || unit.unitData == null)
    {
        return null;
    }
    List<Unit> friends = (unit.faction == Faction.Player) ? this.playerAir : this.otherAir;
    List<Unit> ownShips = (unit.faction == Faction.Player) ? this.playerSea : this.otherSea;
    List<Unit> myBombers = new List<Unit>();
    for (int i = 0; i < friends.Count; i++)
    {
        Unit f = friends[i];
        if (f == null || f.isDestroyed || f.isParked || f.unitAir == null || f.unitData == null)
        {
            continue;
        }
        UnitSubType fst = f.unitData.unitSubtype;
        if (fst == UnitSubType.Fighter || fst == UnitSubType.Scout || f.unitAir.hasDroppedPayload)
        {
            continue;
        }
        myBombers.Add(f);
    }
    bool escort = myBombers.Count > 0;
    Unit best = null;
    float bestScore = float.MaxValue;
    for (int j = 0; j < units.Count; j++)
    {
        Unit e = units[j];
        if (e == null || e.isDestroyed || e.isParked || !e.detected || e.unitAir == null || e.unitData == null || e.unitAir.shootDown)
        {
            continue;
        }
        float score = Vector3.Distance(unit.transform.position, e.transform.position);
        UnitSubType est = e.unitData.unitSubtype;
        bool eFighter = est == UnitSubType.Fighter;
        bool eLoaded = !eFighter && est != UnitSubType.Scout && !e.unitAir.hasDroppedPayload;
        Unit eTarget = (e.unitAI != null) ? e.unitAI.focusedUnit : null;
        bool eOnMe = eTarget == unit;
        bool eOnMyBomber = eTarget != null && myBombers.Contains(eTarget);
        if (escort)
        {
            if (eFighter)
            {
                score *= eOnMyBomber ? 0.3f : 0.6f;
            }
            else
            {
                score *= 2.5f;
            }
            float nearBomber = float.MaxValue;
            for (int b = 0; b < myBombers.Count; b++)
            {
                float d = Vector3.Distance(myBombers[b].transform.position, e.transform.position);
                if (d < nearBomber)
                {
                    nearBomber = d;
                }
            }
            if (nearBomber > 5000f * 0.1f)
            {
                score *= 1f + (nearBomber - 5000f * 0.1f) / (5000f * 0.1f);
            }
        }
        else
        {
            if (eLoaded)
            {
                if (est == UnitSubType.Torpedo_Bomber)
                {
                    score *= 0.35f;
                }
                else if (est == UnitSubType.Dive_Bomber)
                {
                    score *= 0.45f;
                }
                else
                {
                    score *= 0.6f;
                }
            }
            else if (!eFighter)
            {
                score *= 1.8f;
            }
            for (int s = 0; s < ownShips.Count; s++)
            {
                Unit ship = ownShips[s];
                if (ship != null && !ship.isDestroyed && Vector3.Distance(ship.transform.position, e.transform.position) < 10000f * 0.1f)
                {
                    score *= 0.7f;
                    break;
                }
            }
        }
        if (eOnMe)
        {
            score *= 0.5f;
        }
        int attackers = this.GetNumberAttacking(e);
        if (unit.unitAI != null && unit.unitAI.focusedUnit == e)
        {
            attackers--;
            score *= 0.8f;
        }
        if (attackers < 0)
        {
            attackers = 0;
        }
        score *= 1f + 0.75f * (float)attackers;
        if (score < bestScore)
        {
            bestScore = score;
            best = e;
        }
    }
    if (best == null)
    {
        best = this.GetClosestUnit(unit, units, false);
    }
    if (best != null && best.unitData != null)
    {
        UnityEngine.Debug.Log("[FIGHTER] " + unit.unitData.unitName + " id " + unit.GetInstanceID() + " side " + unit.faction + (escort ? " escort" : " CAP") + " -> " + best.unitData.unitName + " id " + best.GetInstanceID());
    }
    return best;
}
```
3. **Compile.**

## Step 2 - EngagementAI.OnDetectUnit
1. Right-click **OnDetectUnit** (class **EngagementAI**) > **Edit Method (C#)...**
2. Near the top is a loop over `this.otherAir` that only runs when `this.fightersAreEscorts` is on. Inside it is this line:
```csharp
this.otherAir[i].unitAI.focusedUnit = detectedUnit;
```
(dnSpy may use a different letter than `i`. Use whatever it shows.)
3. Replace that one line with:
```csharp
Unit modPick = this.GetBestDogfightTarget(this.otherAir[i], this.playerAir);
this.otherAir[i].unitAI.focusedUnit = (modPick != null) ? modPick : detectedUnit;
```
4. **Compile**, then **File > Save Module**.

If you can't find the line, send me a screenshot of the top part of OnDetectUnit.

## Testing
1. **AI escorts:** let an escorted AI strike (fighters plus bombers) reach your fleet while your fighters are on CAP. The AI fighters should split up and go for your fighters, mostly those attacking their bombers, instead of all chasing one plane. Their bombers should get through more often.
2. **AI CAP:** send an escorted strike of yours at an AI fleet that has fighters overhead. The AI fighters should go for your torpedo and dive bombers first, before your fighters.
3. **Your fighters on auto:** your escorts should stick with your bombers, and your CAP should go for incoming bombers.
4. `output_log.txt` shows a `[FIGHTER]` line for every pick: the fighter, its side, whether it's an escort or CAP, and its target.

## Tuning (all in GetBestDogfightTarget, lower score = more wanted)
- **Escorts:**
  - `0.3f`: enemy fighters attacking our bombers.
  - `0.6f`: other enemy fighters.
  - `2.5f`: enemy bombers (bigger means escorts ignore them more).
  - `5000f`: how far from our bombers, in metres, before a target loses interest.
- **CAP:**
  - `0.35f` / `0.45f` / `0.6f`: loaded torpedo / dive / level bombers.
  - `1.8f`: bombers that already dropped.
  - `10000f` and `0.7f`: the "near our ships" bonus.
- **Everyone:**
  - `0.5f`: a plane attacking me.
  - `0.75f`: penalty per fighter already on a target.
  - `0.8f`: stick with the current target.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.
