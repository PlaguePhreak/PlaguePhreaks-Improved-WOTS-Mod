# Realistic air attack heights and bomb aim (v0.20.3, AI super overhaul)

## What was wrong (found in the code)
- **Bombs had no aim error at all.** A bomb leaves the aircraft exactly along its flight path (`AmmunitionMoveBallistic.InitialiseBallistics`), and the aim point allows for the ship's speed. In the second test about 90% of the 24 dive bombers hit.
- **Heights:** every aircraft in a campaign battle starts at 1,000 m (`CampaignManager.GenerateUnitGroupData`), except dive bombers (2,000-2,200 m, our v0.17 change in `EngagementData.CreateUnitGroup`), and start heights are capped at 3,300 m. Level bombers bomb from whatever height they are flying at, so B-17s were bombing from about 1,000 m.

## What changes
**1. Historical start heights** (campaign battles):

| Type | Start height | Notes |
|---|---|---|
| Fighters | 4,500-5,500 m | top cover over the strike |
| Dive bombers | 4,000-4,500 m | push over about 2.6 km out, release 600-700 m |
| Torpedo bombers | 800-1,200 m | let down to the water for the run, drop at 40 m as before |
| Medium bombers (Betty, Nell) | 4,000-5,000 m | level bombing from that height |
| Heavy bombers (B-17) | 6,000-7,000 m | level bombing from that height |
| Scouts | 1,000-1,500 m | |

The start height cap goes from 3,300 m to 8,000 m, and so does the top of the altitude slider for your aircraft.

**2. Bomb aim error.** Every bomb now leaves the aircraft slightly off the aim, a normal spread with this size (one standard deviation):

| How it was dropped | Spread |
|---|---|
| Dive, US crews | 3.5° in 1942, 3.0° in 1943, 2.6° from 1944 |
| Dive, Japanese crews | 2.4° in 1942 (the elite carrier crews), 3.6° in 1943, 4.5° from 1944 |
| High level | 0.9° (from 6,500 m that is about 150 m) |
| Low level (under 300 m) | 1.5° (only a few metres at that height, so low-level attacks stay deadly, as they were) |
| Target ship turning hard | +1.5° on top |

Roughly what to expect against a ship evading at full speed: US 1942 dive bombers hit a carrier about 1 time in 4 and a destroyer about 1 time in 12. The 1942 Japanese crews do better. High level bombers rarely hit a moving ship, as in real life. Damaged ships that can't turn are easier to hit.

The year comes from the campaign date. Outside a campaign it counts as 1942.

**3. Ships see dive bombers earlier:** the warning range in `ModAAEvade` goes from 3 km to 4.5 km, because the bombers now push over further out.

## Install
Back up the DLL and the Override folder first.

### Step 1 - add the class
1. Right-click `Assembly-CSharp` > **Add Class (C#)**, delete what is there and paste all of `ModAirRealism.cs` below.
2. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 2 - AmmunitionMoveBallistic.InitialiseBallistics
1. Find class **AmmunitionMoveBallistic**, right-click the method **`InitialiseBallistics`** > **Edit Method (C#)**.
2. Click just after the method's first `{`, press Enter and paste:
```csharp
ModAirRealism.Scatter(this);
```
3. **Compile**, then **File > Save Module**.

### Step 3 - EngagementData.CreateUnitGroup
1. Find class **EngagementData**, right-click the method **`CreateUnitGroup`** > **Edit Method (C#)**.
2. Near the top is this block (our v0.17 dive bomber height):
```csharp
if (this.isCampaignEngagement && EngagementManager.instance.unitDataDictionary[unitGroupData.unitPrefabs[0]].unitSubtype == UnitSubType.Dive_Bomber)
{
    unitGroupData.startPosition.y = Random.Range(200f, 220f);
}
```
3. Replace the whole block with:
```csharp
if (this.isCampaignEngagement && EngagementManager.instance.unitDataDictionary[unitGroupData.unitPrefabs[0]].unitSubtype >= UnitSubType.Scout)
{
    unitGroupData.startPosition.y = ModAirRealism.SpawnHeight(EngagementManager.instance.unitDataDictionary[unitGroupData.unitPrefabs[0]].unitSubtype, unitGroupData.startPosition.y);
}
```
4. A few lines below, find `Mathf.Clamp(unitGroupData.startPosition.y, 2f, 330f)` and change **330f** to **800f**.
5. **Compile**, then **File > Save Module**.
(If the block looks different, send a screenshot.)

### Step 4 - ModAAEvade
1. Right-click class **ModAAEvade** > **Edit Class (C#)**.
2. Find `public const float DiveRange = 3000f * 0.1f;` and change **3000f** to **4500f**.
3. **Compile**, then **File > Save Module**.

### Step 5 - dive bomber data files
In each of these four files in `Override/unit/air/`: `dauntless/dauntless_data.txt`, `helldiver/helldiver_data.txt`, `val/val_data.txt`, `judy/judy_data.txt` (not judy_kamikaze), change (each appears once):

| Find | Change to | Meaning |
|---|---|---|
| `"attackHeight":[205,215]` | `"attackHeight":[400,450]` | dive from 4,000-4,500 m |
| `"attackRange":[110,120]` | `"attackRange":[250,270]` | push over 2,500-2,700 m out (keeps the same 70-75° dive) |
| `"diveDropHeight":[45,55]` | `"diveDropHeight":[60,70]` | release at 600-700 m |

Save each file.

### Step 6 - the altitude slider (added after the first look)
The aircraft altitude slider stopped at 3,330 m (10,000 ft in imperial), below the new heights.
1. Find class **CombatInterface**, right-click the method **`SetUnitNavigationPanel`** > **Edit Method (C#)**.
2. Find `this.heightChange.maxValue = 333f;` and change **333f** to **800f** (8,000 m).
3. Just below it, find `this.heightChange.maxValue = 1000f;` and change **1000f** to **2625f** (26,250 ft, the same 8,000 m; this one is used when the game is set to feet).
4. **Compile**, then **File > Save Module**.

### ModAirRealism.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.3: realistic air attack heights and bomb aim.
// 1. Aircraft arrive at historical heights for their type (EngagementData.CreateUnitGroup), so fighters fly top cover,
//    dive bombers dive from about 4 km and level bombers bomb from where real ones did.
// 2. Every bomb leaves the aircraft with a small aim error (AmmunitionMoveBallistic.InitialiseBallistics). The game's own
//    aim is near perfect; real crews were not. The error depends on how the bomb was dropped (dive, high level, low level),
//    how good the crews were for their nation and year, and whether the target ship was turning hard.
public class ModAirRealism
{
	// ---------- spawn heights (game units: metres x 0.1) ----------
	public static float SpawnHeight(UnitSubType type, float current)
	{
		switch (type)
		{
		case UnitSubType.Fighter:
			return Random.Range(4500f, 5500f) * 0.1f;   // top cover over the strike
		case UnitSubType.Dive_Bomber:
			return Random.Range(4000f, 4500f) * 0.1f;   // SBD / Val approach height before pushing over
		case UnitSubType.Torpedo_Bomber:
			return Random.Range(800f, 1200f) * 0.1f;    // let down to the water for the run
		case UnitSubType.Medium_Bomber:
			return Random.Range(4000f, 5000f) * 0.1f;   // Betty / Nell level bombing
		case UnitSubType.Heavy_Bomber:
			return Random.Range(6000f, 7000f) * 0.1f;   // B-17 at sea
		case UnitSubType.Scout:
			return Random.Range(1000f, 1500f) * 0.1f;
		default:
			return current;
		}
	}

	// ---------- bomb aim error ----------
	// Typical aim error (degrees, one standard deviation) for a dive bombing attack, by nation and year.
	// US: improving from 1942. Japan: the elite carrier crews of 1942, then much worse once they were lost.
	public static float DiveError(int nation, int year)
	{
		if (nation == 3)
		{
			if (year <= 1942)
			{
				return 2.4f;
			}
			if (year == 1943)
			{
				return 3.6f;
			}
			return 4.5f;
		}
		if (year <= 1942)
		{
			return 3.5f;
		}
		if (year == 1943)
		{
			return 3.0f;
		}
		return 2.6f;
	}

	// Extra error when the target ship is turning hard (at full rudder), and for high and low level bombing
	public const float TurningExtra = 1.5f;
	public const float HighLevelError = 0.9f;
	public const float LowLevelError = 1.5f;
	public const float LowLevelAltitude = 300f * 0.1f;

	// First line of AmmunitionMoveBallistic.InitialiseBallistics: turn the bomb a little off the aircraft's aim
	public static void Scatter(AmmunitionMoveBallistic amb)
	{
		try
		{
			if (amb == null || amb.parentAmmunition == null || amb.parentAmmunition.ammoType != AmmoType.Bomb || EngagementManager.instance == null || EngagementManager.instance.allAirUnits == null)
			{
				return;
			}
			Unit plane = ModAirRealism.Dropper(amb.transform.position);
			if (plane == null || plane.unitData == null)
			{
				return;
			}
			int year = 1942;
			if (CampaignInterface.instance != null && CampaignInterface.instance.dateTime.Year > 1900)
			{
				year = CampaignInterface.instance.dateTime.Year;
			}
			int nation = plane.unitData.nationIndex;
			float alt = plane.transform.position.y;
			bool dive = plane.transform.forward.y < -0.5f;
			string how;
			float sigma;
			if (dive)
			{
				sigma = ModAirRealism.DiveError(nation, year);
				how = "dive";
			}
			else if (alt < ModAirRealism.LowLevelAltitude)
			{
				sigma = ModAirRealism.LowLevelError;
				how = "low level";
			}
			else
			{
				sigma = ModAirRealism.HighLevelError;
				how = "high level";
			}
			Unit target = (plane.unitAI != null) ? plane.unitAI.focusedUnit : null;
			float turning = 0f;
			if (target != null && target.unitData != null && target.unitData.maxTurnRate > 0f)
			{
				turning = Mathf.Clamp01(Mathf.Abs(target.currentTurnRate) / target.unitData.maxTurnRate);
				sigma += ModAirRealism.TurningExtra * turning;
			}
			float ex = ModAirRealism.Gauss() * sigma;
			float ey = ModAirRealism.Gauss() * sigma;
			Transform t = amb.transform;
			t.rotation = Quaternion.AngleAxis(ex, Vector3.up) * Quaternion.AngleAxis(ey, t.right) * t.rotation;
			// rough distance off on the water: aim error x the bomb's path length (along the dive, or about 1.5 x height for level bombing)
			float path = dive ? alt * 10f / Mathf.Max(0.5f, -plane.transform.forward.y) : alt * 10f * 1.5f;
			float off = Mathf.Sqrt(ex * ex + ey * ey) * Mathf.Deg2Rad * path;
			UnityEngine.Debug.Log("[BOMBAIM] " + plane.unitData.unitName + " (" + ModAirRealism.NationName(nation) + " " + year + ") " + how + " release at " + (alt * 10f).ToString("F0") + " m" + (target != null ? " on " + target.unitInstanceName + (turning > 0.5f ? " (turning hard)" : "") : "") + ": aim error " + Mathf.Sqrt(ex * ex + ey * ey).ToString("F1") + " deg (spread " + sigma.ToString("F1") + "), about " + off.ToString("F0") + " m off");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[BOMBAIM] scatter failed: " + ex.Message);
		}
	}

	// The aircraft a bomb has just left: the nearest aircraft to it (bombs appear on their aircraft)
	public static Unit Dropper(Vector3 pos)
	{
		List<Unit> air = EngagementManager.instance.allAirUnits;
		Unit best = null;
		float bestDist = 300f * 0.1f;
		for (int i = 0; i < air.Count; i++)
		{
			Unit p = air[i];
			if (p == null || p.isDestroyed)
			{
				continue;
			}
			float d = Vector3.Distance(p.transform.position, pos);
			if (d < bestDist)
			{
				bestDist = d;
				best = p;
			}
		}
		return best;
	}

	// A normally distributed random number (mean 0, standard deviation 1)
	public static float Gauss()
	{
		float u1 = Mathf.Max(Random.value, 0.0001f);
		float u2 = Random.value;
		return Mathf.Sqrt(-2f * Mathf.Log(u1)) * Mathf.Cos(2f * Mathf.PI * u2);
	}

	public static string NationName(int nation)
	{
		switch (nation)
		{
		case 0:
			return "US";
		case 1:
			return "British";
		case 2:
			return "Australian";
		case 3:
			return "Japanese";
		default:
			return "nation " + nation;
		}
	}
}
```

## Testing
1. Start a new battle with an air strike (the heights are set when the aircraft enter the battle).
2. Click an aircraft of each type: fighters about 5 km up, dive bombers 4-4.5 km, torpedo bombers about 1 km, B-17s 6-7 km.
3. Dive bombers should push over further out and dive for longer, steep as before.
4. Count hits: far fewer than 90%. Ships that are turning hard should be hit less.
5. In `output_log.txt`, one line per bomb, for example:
   `[BOMBAIM] Dauntless (US 1942) dive release at 650 m on Shokaku (turning hard): aim error 5.3 deg (spread 5.0), about 64 m off`

## Tuning (top of ModAirRealism)
- `SpawnHeight`: the start height range for each type (metres x 0.1).
- `DiveError`: the dive bombing spread for each nation and year.
- `TurningExtra` 1.5°, `HighLevelError` 0.9°, `LowLevelError` 1.5°.
- Bigger numbers mean fewer hits.

## Notes
- Torpedoes are not affected (they have their own dud and aim rules).
- Tags: `[BOMBAIM]`. I could not compile or run this.
