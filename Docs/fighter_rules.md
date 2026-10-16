# v0.20.8 Fighter rules: aircraft before ships, at most 4 on one plane

## What the test showed (14 Oct)
- **The v0.20.7 fix worked:** Wildcat gun runs now last about 8 s (for example id -96526: diving at 154 s, pass done at 162 s). 3 Zeros were shot down and many more left smoking, for no Wildcats lost.
- **Still piling on:** 281 of the 338 Wildcat target picks went to one Zero (id -111716). Our v0.17 target choice (`EngagementAI.GetBestDogfightTarget`) only makes a plane a little less attractive for each fighter already on it (x1.75 for one, x8.5 for ten, on a distance score), so a near Zero with 10 Wildcats on it still beat a free Zero a few km further away.
- **Zeros strafing ships:** only 3 Zeros ever joined the dogfight; the rest went for your ships. When the game gives a fighter a ship as its target (`EngagementAI.AttackUnit`), it strafes it, whatever enemy planes are around.

## What changes (both sides)
1. **Aircraft before ships:** a fighter sent at a ship goes for enemy aircraft instead, as long as there are any it can see within 20 km. Fighters already strafing look again every 5 s and switch to an air target if one turns up. Once the sky is clear they go back to strafing.
   - Your own orders win: the fighter you have selected and are commanding still strafes when you tell it to.
2. **At most 4 fighters on one enemy plane** (one division). If the best target already has 4 attackers, the fighter takes the nearest other enemy plane (within 20 km) that has fewer.

## Install (4 steps)
Back up the DLL first.

### Step 1 - add the class
1. Right-click `Assembly-CSharp` > **Add Class (C#)**, delete what is there and paste all of `ModFighterRules.cs` below.
2. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 2 - EngagementAI.AttackUnit
1. Find class **EngagementAI**, right-click the method **`AttackUnit`** > **Edit Method (C#)** (the one with one parameter, `attackingUnit`).
2. Click just after the method's first `{`, press Enter and paste:
```csharp
ModFighterRules.PreferAir(attackingUnit);
```
3. **Compile**, then **File > Save Module**.

### Step 3 - UnitAIAir.StrafeApproach
1. Find class **UnitAIAir**, right-click the method **`StrafeApproach`** > **Edit Method (C#)**.
2. Click just after the method's first `{`, press Enter and paste:
```csharp
if (ModFighterRules.CheckStrafe(this))
{
	return;
}
```
3. **Compile**, then **File > Save Module**.

### Step 4 - EngagementAI.GetBestDogfightTarget
1. In class **EngagementAI**, right-click the method **`GetBestDogfightTarget`** > **Edit Method (C#)** (our v0.17 version).
2. Go to the **very last** `return` line of the method, just above the final `}`. It looks like `return unit2;` (dnSpy may use another name than `unit2`).
3. Change it to (use the same name dnSpy shows instead of `unit2`):
```csharp
return ModFighterRules.Spread(unit, unit2, units);
```
4. Leave the `return null;` near the top of the method alone.
5. **Compile**, then **File > Save Module**.
(If the parameters aren't called `unit` and `units`, send a screenshot.)

### ModFighterRules.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.8 / v0.20.9: fighter rules.
// 1. Fighters fight enemy aircraft before ships. A fighter sent to strafe a ship goes for enemy planes instead while
//    there are any it can see within 20 km. Your own fighters still strafe when you order the selected one to.
// 2. No more than 4 fighters on one enemy plane (a division). If the best target already has 4 attackers, the fighter
//    takes the nearest other enemy plane that has fewer.
public class ModFighterRules
{
	// distances in battle code are metres x 0.1
	public const float AirSearchRange = 20000f * 0.1f;
	public const int MaxPerTarget = 4;
	public const float StrafeCheckSeconds = 5f;

	public static Dictionary<int, float> nextStrafeCheck = new Dictionary<int, float>();
	// v0.20.9: only log a spread decision when it changes (it was 1,861 lines in one battle)
	public static Dictionary<int, int> lastSpreadLog = new Dictionary<int, int>();

	public static bool IsFighter(Unit u)
	{
		return u != null && u.unitData != null && u.unitData.unitSubtype == UnitSubType.Fighter && u.unitAir != null;
	}

	public static List<Unit> Enemies(Unit u)
	{
		if (EngagementAI.instance == null)
		{
			return null;
		}
		return (u.faction == Faction.Player) ? EngagementAI.instance.otherAir : EngagementAI.instance.playerAir;
	}

	public static List<Unit> Friends(Unit u)
	{
		if (EngagementAI.instance == null)
		{
			return null;
		}
		return (u.faction == Faction.Player) ? EngagementAI.instance.playerAir : EngagementAI.instance.otherAir;
	}

	public static bool ValidAir(Unit e)
	{
		return e != null && !e.isDestroyed && !e.isParked && e.unitAir != null && !e.unitAir.shootDown && e.unitData != null;
	}

	// First line of EngagementAI.AttackUnit: a fighter given a ship as its target goes for enemy aircraft instead
	public static void PreferAir(Unit attacker)
	{
		try
		{
			if (!ModFighterRules.IsFighter(attacker) || attacker.unitAI == null)
			{
				return;
			}
			Unit target = attacker.unitAI.focusedUnit;
			if (target == null || target.unitSea == null)
			{
				return;
			}
			// your own orders win: the fighter you have selected and are commanding is left alone
			if (attacker.faction == Faction.Player && CombatInterface.instance != null && CombatInterface.instance.currentUnit == attacker)
			{
				return;
			}
			Unit air = ModFighterRules.FindAir(attacker);
			if (air != null)
			{
				attacker.unitAI.focusedUnit = air;
				UnityEngine.Debug.Log("[FIGHTRULE] " + attacker.unitData.unitName + " id " + attacker.GetInstanceID() + " (" + (attacker.faction == Faction.Player ? "ours" : "enemy") + ") was sent at " + target.unitInstanceName + ", enemy aircraft about: going for " + air.unitData.unitName + " id " + air.GetInstanceID() + " instead");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] prefer air failed: " + ex.Message);
		}
	}

	// First line of UnitAIAir.StrafeApproach: a fighter already strafing a ship looks up every 5 s for enemy aircraft.
	// Returns true if it has been switched to an air target (skip the strafing this tick).
	public static bool CheckStrafe(UnitAIAir ai)
	{
		try
		{
			Unit u = ai.parentUnit;
			if (!ModFighterRules.IsFighter(u) || ai.focusedUnit == null || ai.focusedUnit.unitSea == null)
			{
				return false;
			}
			if (u.faction == Faction.Player && CombatInterface.instance != null && CombatInterface.instance.currentUnit == u)
			{
				return false;
			}
			int id = u.GetInstanceID();
			float next;
			if (ModFighterRules.nextStrafeCheck.TryGetValue(id, out next) && Time.time < next)
			{
				return false;
			}
			ModFighterRules.nextStrafeCheck[id] = Time.time + ModFighterRules.StrafeCheckSeconds;
			Unit air = ModFighterRules.FindAir(u);
			if (air == null)
			{
				return false;
			}
			Unit ship = ai.focusedUnit;
			ai.focusedUnit = air;
			EngagementAI.instance.AttackUnit(u);
			UnityEngine.Debug.Log("[FIGHTRULE] " + u.unitData.unitName + " id " + id + " (" + (u.faction == Faction.Player ? "ours" : "enemy") + ") stops strafing " + ship.unitInstanceName + ": enemy aircraft about, going for " + air.unitData.unitName + " id " + air.GetInstanceID());
			return true;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] strafe check failed: " + ex.Message);
			return false;
		}
	}

	// The best enemy aircraft for this fighter within 20 km, or null if there is none it can see
	public static Unit FindAir(Unit u)
	{
		List<Unit> enemies = ModFighterRules.Enemies(u);
		if (enemies == null)
		{
			return null;
		}
		bool any = false;
		for (int i = 0; i < enemies.Count; i++)
		{
			Unit e = enemies[i];
			if (ModFighterRules.ValidAir(e) && e.detected && Vector3.Distance(e.transform.position, u.transform.position) < ModFighterRules.AirSearchRange)
			{
				any = true;
				break;
			}
		}
		if (!any)
		{
			return null;
		}
		Unit pick = EngagementAI.instance.GetBestDogfightTarget(u, enemies);
		if (!ModFighterRules.ValidAir(pick) || Vector3.Distance(pick.transform.position, u.transform.position) > ModFighterRules.AirSearchRange)
		{
			return null;
		}
		return pick;
	}

	// Last line of EngagementAI.GetBestDogfightTarget: if the chosen plane already has 4 attackers, take the nearest
	// other enemy plane with fewer
	public static Unit Spread(Unit unit, Unit best, List<Unit> units)
	{
		try
		{
			if (unit == null || best == null || units == null || !ModFighterRules.IsFighter(unit))
			{
				return best;
			}
			if (ModFighterRules.Attackers(unit, best) < ModFighterRules.MaxPerTarget)
			{
				return best;
			}
			Unit alt = null;
			float altDist = float.MaxValue;
			for (int i = 0; i < units.Count; i++)
			{
				Unit e = units[i];
				if (e == best || !ModFighterRules.ValidAir(e) || !e.detected)
				{
					continue;
				}
				float d = Vector3.Distance(e.transform.position, unit.transform.position);
				if (d < altDist && d < ModFighterRules.AirSearchRange && ModFighterRules.Attackers(unit, e) < ModFighterRules.MaxPerTarget)
				{
					altDist = d;
					alt = e;
				}
			}
			if (alt == null)
			{
				return best;
			}
			int uid = unit.GetInstanceID();
			int last;
			if (!ModFighterRules.lastSpreadLog.TryGetValue(uid, out last) || last != alt.GetInstanceID())
			{
				ModFighterRules.lastSpreadLog[uid] = alt.GetInstanceID();
				UnityEngine.Debug.Log("[FIGHTRULE] " + unit.unitData.unitName + " id " + uid + ": " + best.unitData.unitName + " id " + best.GetInstanceID() + " already has " + ModFighterRules.MaxPerTarget + " attackers, taking " + alt.unitData.unitName + " id " + alt.GetInstanceID() + " instead");
			}
			return alt;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] spread failed: " + ex.Message);
			return best;
		}
	}

	// How many of this fighter's side are attacking that plane (not counting this fighter)
	public static int Attackers(Unit unit, Unit target)
	{
		List<Unit> friends = ModFighterRules.Friends(unit);
		if (friends == null)
		{
			return 0;
		}
		int n = 0;
		for (int i = 0; i < friends.Count; i++)
		{
			Unit f = friends[i];
			if (f != null && f != unit && !f.isDestroyed && f.unitAI != null && f.unitAI.focusedUnit == target)
			{
				n++;
			}
		}
		return n;
	}
}
```

## Testing
1. Wildcat CAP against an incoming strike with Zero escort: no more than 4 Wildcats on any one plane; they should spread over the Zeros and bombers.
2. Zeros should go for your fighters and bombers while any are about, and only strafe ships once the sky is clear.
3. In `output_log.txt`:
   - `[FIGHTRULE] Zero id ... (enemy) was sent at Benham, enemy aircraft about: going for Wildcat id ... instead`
   - `[FIGHTRULE] Zero id ... stops strafing Enterprise: enemy aircraft about, going for Wildcat id ...`
   - `[FIGHTRULE] Wildcat id ...: Zero id ... already has 4 attackers, taking Zero id ... instead`

## Tuning (top of ModFighterRules)
- `AirSearchRange` 20 km, `MaxPerTarget` 4, `StrafeCheckSeconds` 5.

Tag: `[FIGHTRULE]`. I could not compile or run this.


## v0.20.9
See fixes_v0.20.9.md. The code above is the v0.20.9 version.
