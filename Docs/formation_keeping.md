# AI fleets hold formation in battle (AI overhaul, part 2)

**What was wrong (found in the code)**
- AI ships start a battle in formation: every ship follows its group leader at its formation offset (F10 shows `Follow_Unit`).
- As soon as any AI ship spots you, `EngagementAI.OnDetectUnit` orders **every** AI ship to attack. Each ship then steers straight at its own target (`InterceptTarget`), so the formation falls apart into a swarm.
- The ships still remember their leader and formation place (`followingUnit` / `followOffset`) during the attack. They just stop using them.

**What changes**
1. While attacking, an AI ship that has a formation leader keeps its formation place. It steers with the game's own follow-the-leader code, while its guns and torpedoes keep firing as normal.
2. The leader (ship 1 of the group) still manoeuvres towards the enemy as before, so the whole formation moves as one. A Battle Line keeps its line, a Cruising Disposition keeps its rings, and a Convoy Box keeps its box.
3. Destroyers still make torpedo runs (the coordinated torpedo attack). When the run is over they rejoin their place.
4. A ship breaks formation and fights on its own when:
   - an enemy is within **1,200 m** (close-quarters melee), or
   - its leader is sunk or retreating.
5. If the leader is sunk, the game already hands the group to a new leader (vanilla `SwitchToNewLeader`), and the ships form up on it.
6. Your ships and submarines are not affected.

Back up the DLL first. Everything is in class **UnitAISea**.

## Step 1 - helper method
1. Right-click class **UnitAISea** > **Edit Class (C#)...**
2. Find the `CoordinateTorpedoes` method (added for torpedo coordination). Click just after its closing `}`, press Enter, and paste:
```csharp
private bool KeepStationInBattle(float targetDistance)
{
    if (this.parentUnit.faction == Faction.Player || this.parentUnit.unitData.unitSubtype == UnitSubType.Submarine)
    {
        return false;
    }
    Unit leader = this.followingUnit;
    if (leader == null || leader == this.parentUnit || leader.isDestroyed || leader.unitAI == null || leader.unitAI.retreating)
    {
        return false;
    }
    if (targetDistance < 1200f)
    {
        return false;
    }
    this.FollowUnit(leader);
    return true;
}
```
3. **Compile.**

## Step 2 - AttackUnit
1. Right-click **AttackUnit** (class **UnitAISea**) > **Edit Method (C#)...**
2. At the top of the method are these lines (from the torpedo coordination version):
```csharp
if (this.parentUnit.faction != Faction.Player && this.navPoints.Count > 0)
{
    this.FollowNavPoints();
}
else
{
    this.InterceptTarget(num, false);
}
```
3. Replace them with:
```csharp
if (this.parentUnit.faction != Faction.Player && this.navPoints.Count > 0)
{
    this.FollowNavPoints();
}
else if (!this.KeepStationInBattle(num))
{
    this.InterceptTarget(num, false);
}
```
(If dnSpy shows a different name than `num` for the distance on the first line of the method, use that name.)
4. **Compile**, then **File > Save Module**.

## Testing
1. Fight an AI group of 8 or more ships (F9 helps find one). Watch it from the camera or the tactical map once it spots you.
2. The ships should stay in their formation while they close and open fire, instead of spreading out towards separate targets. F10 shows them as `Attack_Unit` while they hold their place.
3. Destroyers should still break off for torpedo attacks, then come back.
4. Get within about 1 km and the formation should break up into a close-range brawl.
5. Sink the AI leader: the group should form up on a new leader.

## Tuning
- `1200f` in **KeepStationInBattle**: the distance (metres) at which ships break formation and fight on their own. Bigger = formations break earlier.

Note: I could not compile or run this. If dnSpy shows a compile error, send me a screenshot of the error list.

**Units note (v0.17.1):** the `1200f` in KeepStationInBattle was in game units (12 km). It was fixed to `1200f * 0.1f` (1,200 m). See units.md.
