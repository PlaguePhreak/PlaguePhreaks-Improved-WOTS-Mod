# Coordinated torpedo attacks (AI surface ships)

**What was wrong (found in the code)**
- Each AI destroyer or cruiser fired its torpedoes the moment it was in range of its own target, on its own, so attacks came in one ship at a time.
- After its first salvo, an AI surface ship never fired torpedoes again for the rest of the battle (the "already fired" flag was never cleared), even if its tubes reloaded.

**What changes**
1. **Wait for the group:** an AI ship in torpedo range holds fire while other AI torpedo ships within 3 km are still closing in on their targets.
2. **Launch together:** as soon as 2 other ships are also in range, every ship that is ready fires at the same moment, each at its own best target. The result is a spread arriving together.
3. **No endless waiting:** a ship fires anyway after holding for 40 seconds, or if its target comes within 60% of torpedo range. A ship with no torpedo ships nearby fires straight away, as before.
4. **Second salvo:** once a ship has fired and its tubes are at least half reloaded (and the usual 50-60 s turn-away is over), it can attack with torpedoes again, coordinating with its group again.
5. Player ships and submarines are not affected.

Back up the DLL first. Do the steps in order. Everything is in class **UnitAISea**.

## Step 1 - new fields
1. In dnSpy right-click class **UnitAISea** > **Edit Class (C#)...**
2. Find the line `public float subFireTime;` (added for the submarines). Click at the end of it, press Enter, and paste:
```csharp
public float torpHoldStart;
public int torpLoadedAtFire;
public int torpLowWater;
```
3. **Compile**, **File > Save Module**, then **close and reopen dnSpy** and the DLL.

## Step 2 - helper methods
1. Right-click class **UnitAISea** > **Edit Class (C#)...**
2. Find the `TorpedoTargetRank` method (added for the submarines). Click just after its closing `}`, press Enter, and paste:
```csharp
private int LoadedTorpedoes()
{
    int idx = Utilities.GetWeaponSystemIndex(this.parentUnit.weapons, WeaponType.Torpedo);
    if (idx == -1)
    {
        return 0;
    }
    WeaponMount mount = this.parentUnit.weapons[idx].GetComponent<WeaponMount>();
    if (mount == null || mount.ammoRemaining == null)
    {
        return 0;
    }
    int total = 0;
    for (int i = 0; i < mount.ammoRemaining.GetLength(0); i++)
    {
        total += mount.ammoRemaining[i, 0];
    }
    return total;
}

private void LaunchCoordinatedTorpedoes()
{
    this.torpHoldStart = 0f;
    this.torpLoadedAtFire = this.LoadedTorpedoes();
    this.torpLowWater = this.torpLoadedAtFire;
    this.firingTorpedoes = true;
    this.navPoints.Clear();
    this.FireTorpedoes();
}

private void CoordinateTorpedoes(float targetDistance)
{
    if (this.LoadedTorpedoes() <= 0)
    {
        return;
    }
    UnitAISea[] readyMates = new UnitAISea[EngagementAI.instance.otherSea.Count];
    int readyCount = 0;
    int closingCount = 0;
    for (int i = 0; i < EngagementAI.instance.otherSea.Count; i++)
    {
        Unit mate = EngagementAI.instance.otherSea[i];
        if (mate == null || mate == this.parentUnit || mate.isDestroyed || mate.unitAISea == null)
        {
            continue;
        }
        if (mate.unitData.unitSubtype == UnitSubType.Submarine)
        {
            continue;
        }
        if (Vector3.Distance(base.transform.position, mate.transform.position) > 3000f)
        {
            continue;
        }
        UnitAISea mateAI = mate.unitAISea;
        if (mateAI.firingTorpedoes || mateAI.currentAIAction != AIAction.Attack_Unit || mateAI.focusedUnit == null || mateAI.focusedUnit.isDestroyed)
        {
            continue;
        }
        if (mateAI.LoadedTorpedoes() <= 0)
        {
            continue;
        }
        float mateDistance = Vector3.Distance(mate.transform.position, mateAI.focusedUnit.transform.position);
        if (mateDistance < mateAI.torpedoEngageDistance && mateDistance > 50f && mateAI.focusedUnit.unitData.unitSubtype != UnitSubType.Submarine)
        {
            readyMates[readyCount] = mateAI;
            readyCount++;
        }
        else
        {
            closingCount++;
        }
    }
    bool waitedLongEnough = this.torpHoldStart > 0f && Time.time - this.torpHoldStart > 40f;
    bool targetClose = targetDistance < this.torpedoEngageDistance * 0.6f;
    if (closingCount > 0 && readyCount < 2 && !waitedLongEnough && !targetClose)
    {
        if (this.torpHoldStart <= 0f)
        {
            this.torpHoldStart = Time.time;
        }
        return;
    }
    this.LaunchCoordinatedTorpedoes();
    for (int j = 0; j < readyCount; j++)
    {
        readyMates[j].LaunchCoordinatedTorpedoes();
    }
}
```
3. **Compile.**

## Step 3 - AttackUnit
1. Right-click **AttackUnit** (class **UnitAISea**) > **Edit Method (C#)...**
2. Click in the code, press **Ctrl+A**, and paste this over everything:
```csharp
using System;
using UnityEngine;

public partial class UnitAISea : UnitAI
{
	public override void AttackUnit()
	{
		float num = Vector3.Distance(base.transform.position, this.focusedUnit.transform.position);
		if (this.parentUnit.faction != Faction.Player && this.navPoints.Count > 0)
		{
			this.FollowNavPoints();
		}
		else
		{
			this.InterceptTarget(num, false);
		}
		if (this.focusedUnit.isDestroyed || !this.focusedUnit.detected)
		{
			this.CeaseFiringAllWeapons();
			return;
		}
		if (Utilities.isUnitSubmerged(this.focusedUnit, -0.2f))
		{
			if (this.parentUnit.unitData.activeSonarStrength == 0f)
			{
				this.parentUnit.usingActiveSonar = false;
				return;
			}
			if (this.focusedUnit.currentSpeed <= Utilities.FiveKnotsEquivalent && num < 200f)
			{
				this.parentUnit.usingActiveSonar = true;
				return;
			}
			this.parentUnit.usingActiveSonar = false;
			return;
		}
		if (num >= this.primaryEngageDistance)
		{
			return;
		}
		if (!Utilities.isUnitSubmerged(this.parentUnit, -0.1f))
		{
			if (!this.firingPrimary)
			{
				this.FirePrimaryGuns(true);
			}
			if (num < this.secondaryEngageDistance && !this.firingSecondary)
			{
				this.FireSecondaryGuns(true);
			}
		}
		bool coordinated = this.parentUnit.faction != Faction.Player && this.parentUnit.unitData.unitSubtype != UnitSubType.Submarine && Utilities.GetWeaponSystemIndex(this.parentUnit.weapons, WeaponType.Torpedo) != -1;
		if (coordinated && this.firingTorpedoes && this.torpLoadedAtFire > 0)
		{
			int loadedNow = this.LoadedTorpedoes();
			if (loadedNow < this.torpLowWater)
			{
				this.torpLowWater = loadedNow;
			}
			if (this.torpLowWater < this.torpLoadedAtFire && loadedNow >= Mathf.Max(1, this.torpLoadedAtFire / 2) && this.ignoreTimer <= 0f)
			{
				this.firingTorpedoes = false;
				this.torpLoadedAtFire = 0;
				this.torpLowWater = 0;
			}
		}
		if (this.focusedUnit.unitData.unitSubtype != UnitSubType.Submarine && num < this.torpedoEngageDistance && num > 50f && !this.firingTorpedoes)
		{
			if (coordinated)
			{
				this.CoordinateTorpedoes(num);
				return;
			}
			this.firingTorpedoes = true;
			this.navPoints.Clear();
			this.FireTorpedoes();
		}
	}
}
```
3. **Compile**, then **File > Save Module**.

## Testing
- Use a battle where you face a group of AI destroyers or cruisers with torpedoes (for example a night action off Guadalcanal). F10 shows what each AI ship is doing.
- You should see AI ships in range keep shooting guns but not launch at first, then several switch to `Torpedo_Run` at about the same moment. In the dev view this shows as several ships changing action together.
- A lone AI destroyer should still fire as soon as it is in range.
- Later in a long battle, a ship whose tubes have reloaded may come back for a second torpedo attack.

## Tuning
- `3000f`: how far apart (metres) ships can be and still count as one group.
- `readyCount < 2`: how many *other* ships must be in range before the group fires. `1` = pairs, `2` = groups of 3.
- `40f`: longest a ship will hold fire (seconds).
- `0.6f`: fire anyway once the target is within this fraction of torpedo range.
- `this.torpLoadedAtFire / 2`: how reloaded the tubes must be before a second attack (half).

Note: I could not run this. If dnSpy shows a compile error, send me a screenshot.

**Units note (v0.17.1):** the `3000f` group distance in CoordinateTorpedoes was in game units (30 km). It was fixed to `3000f * 0.1f` (3,000 m). See units.md.
