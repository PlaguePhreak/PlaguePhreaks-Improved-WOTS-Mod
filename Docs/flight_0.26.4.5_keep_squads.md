# 0.26.4.5 - Keep fighter squads together (2 small edits, no new class)

## Why squads fall apart (found in the decompiled game code)
1. **Roster**: `EngagementAI.AttackUnit` - when the target is an aircraft it calls
   `RosterInterface.instance.DropFromGroup(...)`. That is what un-groups the 1-24 list as soon as an
   enemy is picked. (The squad link itself, `followingUnit`, is NOT cleared there.)
2. **Behaviour**: `EngagementAI.AIRvsAIR` loops over the squad and gives EVERY plane its own
   `GetBestDogfightTarget` (nearest enemy for each one) and a 20% chance per plane per call to
   `BreakAwayFromUnit()`. So 4 planes scatter onto 4 different enemies.

## Edit A - EngagementAI.AttackUnit (Edit Method)
Find:
```
DogfightTarget(attackingUnit);
if (attackingUnit.faction == Faction.Player)
{
    RosterInterface.instance.DropFromGroup(EngagementManager.instance.playerUnits.IndexOf(attackingUnit));
}
return;
```
Delete the `if (attackingUnit.faction == Faction.Player) { ... DropFromGroup ... }` part so it is just:
```
DogfightTarget(attackingUnit);
return;
```

## Edit B - EngagementAI.AIRvsAIR (Edit Method), the fighter loop
Replace the loop `for (int i = 0; i < meAndMyFollowers.Count; i++) { ... }` with:
```
Unit flightTarget = null;
for (int i = 0; i < meAndMyFollowers.Count; i++)
{
    Unit u = meAndMyFollowers[i];
    if (Random.value < 0.05f)
    {
        if (u.unitAI.focusedUnit != null)
        {
            u.unitAIAir.BreakAwayFromUnit();
        }
        continue;
    }
    Unit best = null;
    if (flightTarget != null && !flightTarget.isDestroyed && !flightTarget.isParked)
    {
        // wingmen: same enemy as the leader, unless 2 of us are already on it,
        // then an enemy within 400 m (40 units) of the leader's target
        int onIt = 0;
        for (int m = 0; m < i; m++)
        {
            if (meAndMyFollowers[m].unitAI.focusedUnit == flightTarget) onIt++;
        }
        if (onIt < 2)
        {
            best = flightTarget;
        }
        else
        {
            float bestD = 40f;
            for (int e = 0; e < list.Count; e++)
            {
                Unit en = list[e];
                if (en == null || en.isDestroyed || en.isParked || !en.detected || en == flightTarget) continue;
                float d = Vector3.Distance(flightTarget.transform.position, en.transform.position);
                if (d < bestD) { bestD = d; best = en; }
            }
        }
    }
    if (best == null)
    {
        best = GetBestDogfightTarget(u, list);
    }
    if (best != null)
    {
        u.unitAI.focusedUnit = best;
        if (flightTarget == null) flightTarget = best;
        AttackUnit(u);
    }
}
```
(`list` is the enemy list already defined above the loop in that method. The 20% break-away
is dropped to 5%, since the dogfight class already does its own breaks/defence.)

## What you should see
A flight of 4 picks the same enemy (max 2 on one plane), the other two take a neighbour,
and the roster keeps the squad grouped. ModDogfight's wingman cover (0.26.4) then works
within the flight.
