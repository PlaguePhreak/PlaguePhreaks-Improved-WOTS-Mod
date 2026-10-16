# Smarter AI submarines

**What was wrong (found in the code)**
- Enemy subs were placed only 150-250 m ahead of your fleet, with almost no warning.
- After firing, an AI sub switched on "silent running" and never switched it off. Torpedo tubes (and repairs) do not reload while silent, and the sub stayed in "retreat" for the rest of the battle, so it could never reload or attack again.

**What changes**
1. **Ambush from further away:** subs now start 1,000-1,600 m ahead of your fleet and 400-800 m to the side (before: 150-250 m and 75-150 m). That is data only: the new `config.txt`.
2. **Hit, run and reload:** after a salvo the sub escapes quietly for 2 minutes, then runs normally so its tubes can reload. After at least 4 minutes, with tubes reloaded, torpedoes left, no serious damage, and no player ship within 600 m, it comes back for another attack on your best target.
3. **Split salvos:** a sub with 2 or more tubes ready now splits them between up to 3 different targets (for 6 tubes: 3 / 2 / 1) instead of putting the whole salvo into one ship.
4. **Ambush trigger:** a waiting sub now starts its attack when one of your surface ships comes within 2,500 m, instead of waiting until its sensors detect you (at the longer distance it often never did, so it just sat there at 1 knot).
5. A sub that has been hurt (any destroyed or flooded compartment) never comes back. It keeps running.

Back up the DLL first. Do the steps in order.

## Step 1 - config.txt
Replace `StreamingAssets/default/config.txt` with the attached `config.txt`. This one includes the earlier AI tuning plus the new sub ambush distance. (Back up the old one.)
Tuning: `enemySubAmbushOffset` is [ahead min, ahead max, side min, side max], each divided by 10 in game metres. Bigger numbers = further away.

## Step 2 - new field (UnitAISea)
1. In dnSpy open class **UnitAISea** > right-click > **Edit Class (C#)...**
2. Add this line next to the other fields (e.g. just above `public bool firingPrimary;`):
```csharp
public float subFireTime;
```
3. Compile, **File > Save Module**, then **close and reopen dnSpy** and the DLL.

## Step 3 - split salvos and note the firing time (UnitAISea.FireTorpedoes)
This step does two things: the sub now splits its ready torpedoes between up to 3 targets, and it records when it fired.

**3a - helper method.** Right-click class **UnitAISea** > **Edit Class (C#)...** and add this method anywhere inside the class:
```csharp
private int TorpedoTargetRank(Unit u)
{
    UnitSubType st = u.unitData.unitSubtype;
    if (st == UnitSubType.Aircraft_Carrier || st == UnitSubType.Light_Carrier)
    {
        return 4;
    }
    if (st == UnitSubType.Battleship || st == UnitSubType.Battlecruiser)
    {
        return 3;
    }
    if (st == UnitSubType.Heavy_Cruiser)
    {
        return 2;
    }
    return 1;
}
```
Compile.

**3b - FireTorpedoes.** Right-click **FireTorpedoes** > **Edit Method (C#)...** and replace the whole method with:
```csharp
private void FireTorpedoes()
{
    int weaponSystemIndex = Utilities.GetWeaponSystemIndex(this.parentUnit.weapons, WeaponType.Torpedo);
    if (weaponSystemIndex != -1)
    {
        Unit bestTorpedoTarget = EngagementAI.instance.GetBestTorpedoTarget(this.parentUnit, 60f);
        if (bestTorpedoTarget != null)
        {
            WeaponMount component = this.parentUnit.weapons[weaponSystemIndex].GetComponent<WeaponMount>();
            component.salvoSpread = 10f;
            component.currentSalvoSize = component.ammoRemaining[0, 0] * component.baseTransforms.Length;
            this.parentUnit.weapons[weaponSystemIndex].GetComponent<WeaponMount>().SetWeaponMountToMode(0, null, 0, false, bestTorpedoTarget, false, Vector3.zero, 1);
            EngagementAI.instance.ChangeAIAction(this.parentUnit, AIAction.Torpedo_Run);
            this.ignoreTimer = (float)UnityEngine.Random.Range(50, 60);
            this.torpedoDir = Utilities.GetSignedAngleToPosition(base.transform.forward, base.transform.position, component.interceptPoints[0]);
            if (this.torpedoDir < 0f)
            {
                this.torpedoDir = 1f;
            }
            else
            {
                this.torpedoDir = -1f;
            }
        }
        return;
    }
    weaponSystemIndex = Utilities.GetWeaponSystemIndex(this.parentUnit.weapons, WeaponType.Torpedo_Room);
    if (weaponSystemIndex == -1)
    {
        return;
    }
    Unit bestTorpedoTarget2 = EngagementAI.instance.GetBestTorpedoTarget(this.parentUnit, 60f);
    if (bestTorpedoTarget2 == null)
    {
        return;
    }
    WeaponTorpedoTube component2 = this.parentUnit.weapons[weaponSystemIndex].GetComponent<WeaponTorpedoTube>();
    int readyTubes = component2.numberTubesReady;
    Unit[] splitTargets = new Unit[3];
    splitTargets[0] = bestTorpedoTarget2;
    int splitCount = 1;
    if (this.parentUnit.faction != Faction.Player && readyTubes >= 2)
    {
        for (int slot = 1; slot < 3; slot++)
        {
            Unit pick = null;
            int pickRank = 0;
            float pickDistance = 999999f;
            for (int s = 0; s < EngagementAI.instance.playerSea.Count; s++)
            {
                Unit candidate = EngagementAI.instance.playerSea[s];
                if (candidate == null || candidate.isDestroyed || !candidate.detected || candidate.unitData.unitSubtype == UnitSubType.Submarine)
                {
                    continue;
                }
                bool alreadyChosen = false;
                for (int c = 0; c < splitCount; c++)
                {
                    if (splitTargets[c] == candidate)
                    {
                        alreadyChosen = true;
                    }
                }
                if (alreadyChosen)
                {
                    continue;
                }
                float candidateDistance = Vector3.Distance(base.transform.position, candidate.transform.position);
                if (candidateDistance < 150f || candidateDistance > this.torpedoEngageDistance)
                {
                    continue;
                }
                int candidateRank = this.TorpedoTargetRank(candidate);
                if (candidateRank > pickRank || (candidateRank == pickRank && candidateDistance < pickDistance))
                {
                    pick = candidate;
                    pickRank = candidateRank;
                    pickDistance = candidateDistance;
                }
            }
            if (pick == null)
            {
                break;
            }
            splitTargets[splitCount] = pick;
            splitCount++;
        }
    }
    int targetsToHit = Mathf.Min(splitCount, readyTubes);
    if (targetsToHit < 1)
    {
        targetsToHit = 1;
    }
    Unit originalFocus = this.focusedUnit;
    int remaining = readyTubes;
    for (int t = 0; t < targetsToHit; t++)
    {
        int share;
        if (t == targetsToHit - 1)
        {
            share = remaining;
        }
        else
        {
            float weight = 0.5f;
            if (targetsToHit == 2)
            {
                weight = 0.6f;
            }
            else if (t == 1)
            {
                weight = 0.33f;
            }
            share = Mathf.Clamp(Mathf.RoundToInt((float)readyTubes * weight), 1, remaining - (targetsToHit - 1 - t));
        }
        component2.targetUnit = splitTargets[t];
        this.focusedUnit = splitTargets[t];
        component2.salvoSpread = 10f;
        component2.salvoSize = share;
        component2.FireWeapon();
        remaining -= share;
    }
    if (originalFocus != null)
    {
        this.focusedUnit = originalFocus;
    }
    if (this.parentUnit.faction != Faction.Player)
    {
        this.RetreatUnit(bestTorpedoTarget2);
        this.parentUnit.unitSea.runningSilent = true;
        this.subFireTime = Time.time;
    }
}
```
Compile.

How the split works: the most valuable target (the same one the sub chose before) gets the biggest share; other targets are picked by value (carrier, battleship, heavy cruiser, then anything else) among detected, non-submarine ships within torpedo range. With 6 ready tubes and 3 targets it fires 3 / 2 / 1; with 2 targets it fires 4 / 2 (6 tubes), and with 2 ready tubes it fires 1 / 1. If only one target is in range, nothing changes from before. Player-controlled subs are not affected. (A target that cannot be hit from the sub's firing arc falls back to the best target, the same way the game's own code already did.)

## Step 4a - ambush trigger (UnitAISea.CheckNavigation)
**Why:** an AI sub in ambush sits at about 1 knot with the action `Nothing` until its own sensors detect one of your ships. At the new, longer ambush distance it often never does, so it just waits. This trigger makes it spring the ambush once any of your surface ships comes within 2,500 m. It calls the game's own "I have detected a ship" routine, so the sub (and any escorts in its group) react exactly as they would after a normal detection.

1. Right-click **CheckNavigation** (class UnitAISea) > **Edit Method (C#)...** (you edit this same method in Step 4).
2. At the top of the method are two `if ... return;` checks (`noNavEvade`, and `this.parentUnit == CombatInterface.instance.currentUnit`). Directly **after** them, and before the `if (...retreating && ... Submarine)` block, paste:
```csharp
if (this.parentUnit.faction != Faction.Player && this.parentUnit.unitData.unitSubtype == UnitSubType.Submarine && !this.retreating && this.currentAIAction == AIAction.Nothing && this.focusedUnit == null)
{
    Unit ambushTarget = null;
    float ambushDistance = 2500f;
    for (int a = 0; a < EngagementAI.instance.playerSea.Count; a++)
    {
        Unit ambushShip = EngagementAI.instance.playerSea[a];
        if (ambushShip == null || ambushShip.isDestroyed || ambushShip.unitData.unitSubtype == UnitSubType.Submarine)
        {
            continue;
        }
        float ambushShipDistance = Vector3.Distance(base.transform.position, ambushShip.transform.position);
        if (ambushShipDistance < ambushDistance)
        {
            ambushDistance = ambushShipDistance;
            ambushTarget = ambushShip;
        }
    }
    if (ambushTarget != null)
    {
        EngagementAI.instance.OnDetectUnit(this.parentUnit, ambushTarget);
        this.parentUnit.wantedSpeed = this.parentUnit.unitData.maxSpeed * 0.85f;
    }
}
```
3. Compile. (You can do this together with Step 4 in the same edit window: it is the same method.)

Tuning: the `2500f` (= 2,500 m) is how close your ships must come before the sub springs the ambush. Make it smaller for a later ambush.

## Step 4 - the reload-and-return logic (UnitAISea.CheckNavigation)
1. Right-click **CheckNavigation** (class UnitAISea) > **Edit Method (C#)...**
2. Near the top find this block:
```csharp
if (this.parentUnit.faction != Faction.Player && this.retreating && this.parentUnit.unitData.unitSubtype == UnitSubType.Submarine)
{
    EngagementAI.instance.SetSubmarineDepth(this.parentUnit, (float)(-(float)this.parentUnit.unitSea.unitData.testDepth_ceiling) * 0.75f * 0.1f);
    return;
}
```
3. Change only what is inside the braces. Keep the `SetSubmarineDepth(...)` line as it is, and put the new code between it and the `return;`:
```csharp
if (this.parentUnit.faction != Faction.Player && this.retreating && this.parentUnit.unitData.unitSubtype == UnitSubType.Submarine)
{
    EngagementAI.instance.SetSubmarineDepth(this.parentUnit, (float)(-(float)this.parentUnit.unitSea.unitData.testDepth_ceiling) * 0.75f * 0.1f);
    if (this.subFireTime > 0f)
    {
        float sinceFire = Time.time - this.subFireTime;
        if (this.parentUnit.unitSea.runningSilent)
        {
            this.parentUnit.wantedSpeed = this.parentUnit.unitData.maxSpeed * 0.5f;
            if (sinceFire > 120f)
            {
                this.parentUnit.unitSea.runningSilent = false;
            }
        }
        else
        {
            this.parentUnit.wantedSpeed = this.parentUnit.unitData.maxSpeed;
        }
        int tubeIndex = Utilities.GetWeaponSystemIndex(this.parentUnit.weapons, WeaponType.Torpedo_Room);
        if (tubeIndex != -1 && sinceFire > 240f && this.parentUnit.damageableSea.cellsDestroyed.Count == 0 && this.parentUnit.damageableSea.cellsFlooded.Count == 0)
        {
            WeaponTorpedoTube tubes = this.parentUnit.weapons[tubeIndex].GetComponent<WeaponTorpedoTube>();
            if (tubes != null && tubes.maxTorps > 0 && tubes.numberTubesReady >= Mathf.Min(2, tubes.maxTorps))
            {
                float nearestPlayer = 999999f;
                for (int p = 0; p < EngagementAI.instance.playerSea.Count; p++)
                {
                    Unit nearShip = EngagementAI.instance.playerSea[p];
                    if (nearShip == null || nearShip.isDestroyed)
                    {
                        continue;
                    }
                    float playerDistance = Vector3.Distance(base.transform.position, nearShip.transform.position);
                    if (playerDistance < nearestPlayer)
                    {
                        nearestPlayer = playerDistance;
                    }
                }
                Unit returnTarget = EngagementAI.instance.GetBestSeaTarget(this.parentUnit, EngagementAI.instance.playerSea);
                if (returnTarget == null)
                {
                    float returnDistance = 999999f;
                    for (int r = 0; r < EngagementAI.instance.playerSea.Count; r++)
                    {
                        Unit returnShip = EngagementAI.instance.playerSea[r];
                        if (returnShip == null || returnShip.isDestroyed || returnShip.unitData.unitSubtype == UnitSubType.Submarine)
                        {
                            continue;
                        }
                        float returnShipDistance = Vector3.Distance(base.transform.position, returnShip.transform.position);
                        if (returnShipDistance < returnDistance)
                        {
                            returnDistance = returnShipDistance;
                            returnTarget = returnShip;
                        }
                    }
                }
                if (returnTarget != null && nearestPlayer > 600f)
                {
                    this.retreating = false;
                    this.firingTorpedoes = false;
                    this.subFireTime = 0f;
                    this.parentUnit.unitSea.runningSilent = false;
                    this.focusedUnit = returnTarget;
                    this.navPoints.Clear();
                    EngagementAI.instance.SetSubmarineDepth(this.parentUnit, -3f);
                    EngagementAI.instance.ChangeAIAction(this.parentUnit, AIAction.Attack_Unit);
                    this.parentUnit.wantedSpeed = this.parentUnit.unitData.maxSpeed * 0.85f;
                }
            }
        }
    }
    return;
}
```
4. Compile, then **File > Save Module**.

## Testing
- Make a campaign encounter between your fleet and an enemy submarine group (or use skirmish if it lets you pick enemy subs). You should see the sub first appear about 1 km ahead and to the side.
- After the first salvo the sub should slip away, and a few minutes later (game time) come back for a second attack. Use time compression to see this faster.
- If it comes back too eagerly or too rarely, the numbers to change are 120f (when it stops running silent, in seconds), 240f (earliest return, in seconds), 600f (how far your ships must be, in metres) and `Mathf.Min(2, ...)` (tubes needed).

**Fix (v2):** the sub now gets a proper speed when it springs the ambush, while escaping (half speed while silent, full after), and when it returns; sunk ships no longer count in the 600 m check. If the sub has lost contact with your ships while deep (the game's own target picker only accepts ships it has currently detected), it now heads back towards your nearest surface ship instead of waiting forever. Distances in the battle code are in metres (the config file values are divided by 10).

Note: I could not run this. If dnSpy shows a compile error, send me a screenshot.

**Units note (v0.17.1):** battle distances are really in 10 m game units, not metres (see units.md). The 2,500 m ambush trigger, 600 m return check and 150 m minimum torpedo distance were written as 2500f, 600f and 150f, so they worked at 10 times the distance. They were fixed to 2500f * 0.1f, 600f * 0.1f and 150f * 0.1f.

---

## Fix v0.17.7 - subs spawning right next to the fleet

**What was wrong (found in the code):** `EngagementData.PutSubsIntoPosition` picks one spot ahead of and to the side of your fleet, and checks whether it is open, deep water. If it isn't, because the spot is on land, in shallow water or past the edge of the battle area, the sub is **not moved at all**. It stays at its normal battle start point, about 1-1.5 km from your ships. Every other sub in the group then tries the same spot, so the whole group ends up close. With the config distances of 10-16 km ahead, the spot is often past the edge of the battle area or on an island.

**What changes**
- If the first spot fails, the code tries the other side, then moves a little closer each time (16 tries, down to a quarter of the distance). The sub only stays at its start point if every try fails.
- New `[SUBAMBUSH]` log lines show where each sub was placed and how far it is from your ship.
- **Config change:** `"enemySubAmbushOffset":[5000,8000,1000,2500]` puts enemy subs 5-8 km ahead and 1-2.5 km to the side (the old values were 10-16 km ahead and 4-8 km to the side). Your fleet then passes within the 2.5 km ambush trigger. At 4-8 km to the side, it could sail straight past without the sub ever reacting.

**Install**
1. In class **EngagementData**, right-click method **PutSubsIntoPosition** > **Edit Method (C#)...**
2. Select all of it and replace it with:
```csharp
private void PutSubsIntoPosition(List<Unit> subs, Unit target)
{
	bool isPlayer = true;
	if ((int)subs[0].faction != 0)
	{
		isPlayer = false;
	}
	float[] offset = Config.instance.playerSubAmbushOffset;
	if ((int)subs[0].faction != 0)
	{
		offset = Config.instance.enemySubAmbushOffset;
	}
	Vector3 targetPos = target.transform.position;
	Vector3 targetForward = target.transform.forward;
	Vector3 targetRight = target.transform.right;
	float ahead = UnityEngine.Random.Range(offset[0] * 0.1f, offset[1] * 0.1f);
	float side = UnityEngine.Random.Range(offset[2] * 0.1f, offset[3] * 0.1f);
	if (UnityEngine.Random.value < 0.5f)
	{
		side *= -1f;
	}
	float spacing = (float)UnityEngine.Random.Range(50, 100);
	if (UnityEngine.Random.value < 0.5f)
	{
		spacing *= -1f;
	}
	Unit firstSub = null;
	for (int i = 0; i < subs.Count; i++)
	{
		bool placed = false;
		Vector3 pos = subs[i].transform.position;
		if (firstSub == null)
		{
			// Try the chosen spot first. If it is land or shallow water, try the other side,
			// then move a little closer each time (down to a quarter of the distance).
			for (int attempt = 0; attempt < 16 && !placed; attempt++)
			{
				float scale = 1f - 0.05f * (float)attempt;
				float trySide = (attempt % 2 == 0) ? side : -side;
				pos = targetPos + targetForward * ahead * scale + targetRight * trySide * scale;
				pos.y = -1f;
				pos.x += (float)i * 10f;
				pos.z += (float)i * 10f;
				if (TerrainTiles.instance.GetRaycastTerrainHeight(pos) < -2.5f)
				{
					placed = true;
					if (attempt > 0)
					{
						UnityEngine.Debug.Log("[SUBAMBUSH] first spot was land or shallow, moved after " + attempt + " tries");
					}
				}
			}
		}
		else
		{
			pos = firstSub.transform.position + firstSub.transform.forward * (float)i * -spacing + firstSub.transform.right * (float)i * -spacing;
			pos.y = -1f;
			if (TerrainTiles.instance.GetRaycastTerrainHeight(pos) < -2.5f)
			{
				placed = true;
			}
		}
		if (placed)
		{
			subs[i].transform.position = pos;
			if (firstSub == null)
			{
				firstSub = subs[i];
			}
			if (isPlayer)
			{
				subs[i].transform.LookAt(target.transform.position);
			}
			UnityEngine.Debug.Log("[SUBAMBUSH] " + subs[i].unitInstanceName + " (side " + (int)subs[i].faction + ") placed " + (Vector3.Distance(pos, targetPos) * 10f).ToString("F0") + " m from " + target.unitInstanceName);
		}
		else
		{
			UnityEngine.Debug.Log("[SUBAMBUSH] " + subs[i].unitInstanceName + " (side " + (int)subs[i].faction + ") could not find open water, left at its start point " + (Vector3.Distance(subs[i].transform.position, targetPos) * 10f).ToString("F0") + " m from " + target.unitInstanceName);
		}
		subs[i].unitAI.navPoints.Clear();
	}
}
```
3. Click **Compile**, then **File > Save Module**.
4. In `config.txt`, change `enemySubAmbushOffset` to `[5000,8000,1000,2500]`.

**Testing:** start a battle against enemy subs. The log should show `[SUBAMBUSH] <sub> (side 1) placed 6200 m from <your ship>` or similar. If it says `could not find open water`, send me the log.
