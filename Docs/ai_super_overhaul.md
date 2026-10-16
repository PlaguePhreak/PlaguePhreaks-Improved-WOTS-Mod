# AI super overhaul (v0.20 and onwards)

AI work goes under v0.20, then v0.20.1, v0.20.2 and so on.

| Version | Part | Status |
|---|---|---|
| v0.20 | Stuck attackers steer straight at their target `[AIMOVE]` | Tested |

---

## v0.20 - AI ships that "attack" but sail in circles

**What was wrong (from the code and the 13 Oct log):** when an AI ship is ordered to attack, the game plans a short path towards an intercept point and the ship follows it as waypoints (`UnitAI.MoveSeaToPosition`, `FollowNavPoints`). A new path is only planned once the old waypoints are used up. A ship only "reaches" a waypoint when it comes within a small distance of it (`tacMapNavThreshold`). The most likely cause: a slow ship with a wide turning circle, like a carrier at 12 knots, misses the point and then keeps turning round it. It never uses up the waypoint, so it never gets a new path, and the F3 view still says `Attack_Unit`. Her escorts keep station on her, so the whole task force circles. The log couldn't confirm it, because no mod log covered AI movement, so the new `[AIMOVE]` line also records what the ship was doing.

**What changes**
- Once a minute, every AI ship that is attacking and isn't keeping station in a formation (so the leader, or a ship on her own) is checked. If she closed less than a quarter of the distance she could have covered at her speed, she counts as stuck.
- A stuck ship drops her waypoints and steers straight for her target (the game's own direct-steering mode, which leads a moving target) for 3 minutes, then goes back to normal path-finding. If she's still stuck at the next check, it happens again.
- It stops as soon as she's within gun range (or 1.5 km), or within torpedo range, so close-range fighting and torpedo runs are unchanged.
- Formation followers aren't touched. They keep following the leader, so the whole group straightens out with her.
- Your ships and submarines are not affected.
- A `[AIMOVE]` line in `output_log.txt` each time a ship is caught: her name, the target, the distance a minute ago and now, her speed, waypoints and AI action.

- **Land check:** before and while steering straight, the line ahead towards the target is checked every 200 m out to 2 km (every 2 seconds). If there's land or shallow water on it, the ship doesn't steer straight. Instead her stuck waypoint is dropped, so the game plans a fresh path round the island. That alone breaks the circling.

**Install (dnSpy).** Back up the DLL first.

### Step 1 - new class ModAIMove
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Delete everything in the window and paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20: AI ships that are ordered to attack but don't close in (for example circling round a waypoint they
// can't reach) are noticed after a minute and steered straight at their target for a while.
// Land check: they never steer straight into land or shallows. If the way is blocked, the waypoint is dropped so the game plans a new path round it.
public class ModAIMove
{
	public class State
	{
		public float checkTime;
		public float distAtCheck;
		public float directUntil;
		public int stuckCount;
		public float landCheckTime;
		public bool landAhead;
	}

	// How often progress is checked (seconds of battle time)
	public const float CheckSeconds = 60f;
	// A ship must close at least this share of the distance it could cover in that time, or it counts as stuck
	public const float MinProgressShare = 0.25f;
	// How long a stuck ship steers straight at its target before going back to normal pathing (seconds)
	public const float DirectSeconds = 180f;
	// Below this distance (10 m units, 1,500 m) the normal close-range fighting takes over
	public const float CloseRange = 1500f * 0.1f;

	// Land check: how far ahead to look (10 m units, 2,000 m), the spacing of the checks (200 m),
	// and the depth that counts as safe water (the same -2.5 the game's submarine placement uses)
	public const float LandLookAhead = 2000f * 0.1f;
	public const float LandStep = 200f * 0.1f;
	public const float SafeDepth = -2.5f;
	public const float LandCheckSeconds = 2f;

	public static Dictionary<int, ModAIMove.State> states = new Dictionary<int, ModAIMove.State>();

	// First thing in UnitAISea.AttackUnit. Returns true when this method has done the steering this tick.
	public static bool Steer(UnitAISea ai, float dist)
	{
		try
		{
			Unit u = ai.parentUnit;
			Unit target = ai.focusedUnit;
			if (u == null || target == null || (int)u.faction == 0 || u.unitData == null || u.unitData.unitSubtype == UnitSubType.Submarine || u.isDestroyed || ai.retreating)
			{
				return false;
			}
			// ships keeping station in a formation follow their leader; only the leader (or a ship on its own) is checked
			Unit leader = ai.followingUnit;
			if (leader != null && leader != u && !leader.isDestroyed && leader.unitAI != null && !leader.unitAI.retreating)
			{
				return false;
			}
			int id = u.GetInstanceID();
			ModAIMove.State s;
			if (!ModAIMove.states.TryGetValue(id, out s))
			{
				s = new ModAIMove.State();
				s.checkTime = Time.time;
				s.distAtCheck = dist;
				ModAIMove.states[id] = s;
			}
			float closeRange = Mathf.Max(ModAIMove.CloseRange, ai.primaryEngageDistance);
			if (Time.time < s.directUntil)
			{
				if (dist <= closeRange)
				{
					// close enough: back to the normal fight
					s.directUntil = 0f;
					s.checkTime = Time.time;
					s.distAtCheck = dist;
					UnityEngine.Debug.Log("[AIMOVE] " + u.unitInstanceName + " is within " + (dist * 10f).ToString("F0") + " m of " + target.unitInstanceName + ", back to normal manoeuvring");
					return false;
				}
				// land or shallows on the way: stop steering straight and let the game plan a path round it
				if (ModAIMove.LandAhead(u, target, s, dist))
				{
					s.directUntil = 0f;
					s.checkTime = Time.time;
					s.distAtCheck = dist;
					ai.navPoints.Clear();
					UnityEngine.Debug.Log("[AIMOVE] " + u.unitInstanceName + " has land or shallows ahead, stops steering straight and plans a new path");
					return false;
				}
				ai.navPoints.Clear();
				ai.InterceptTarget(dist, true);
				return true;
			}
			if (Time.time - s.checkTime < ModAIMove.CheckSeconds)
			{
				return false;
			}
			float elapsed = Time.time - s.checkTime;
			float closed = s.distAtCheck - dist;
			float couldClose = Mathf.Max(u.currentSpeed, Utilities.ConvertKnotToMetrePerSecond(5f)) * elapsed;
			float before = s.distAtCheck;
			s.checkTime = Time.time;
			s.distAtCheck = dist;
			if (dist <= closeRange || ai.torpedoEngageDistance > 0f && dist <= ai.torpedoEngageDistance)
			{
				return false;
			}
			if (closed >= couldClose * ModAIMove.MinProgressShare)
			{
				s.stuckCount = 0;
				return false;
			}
			s.stuckCount++;
			s.landCheckTime = -100f;
			if (ModAIMove.LandAhead(u, target, s, dist))
			{
				// can't steer straight: dropping the waypoint she was circling still makes the game plan a fresh path
				UnityEngine.Debug.Log("[AIMOVE] " + u.unitInstanceName + " is not closing on " + target.unitInstanceName + ": " + (before * 10f / 1000f).ToString("F1") + " km -> " + (dist * 10f / 1000f).ToString("F1") + " km in " + elapsed.ToString("F0") + " s, " + ai.navPoints.Count + " waypoints, action " + ai.currentAIAction + " -> land or shallows in the way, waypoints cleared for a new path (time " + s.stuckCount + ")");
				ai.navPoints.Clear();
				return false;
			}
			s.directUntil = Time.time + ModAIMove.DirectSeconds;
			UnityEngine.Debug.Log("[AIMOVE] " + u.unitInstanceName + " is not closing on " + target.unitInstanceName + ": " + (before * 10f / 1000f).ToString("F1") + " km -> " + (dist * 10f / 1000f).ToString("F1") + " km in " + elapsed.ToString("F0") + " s, speed " + (u.currentSpeed * 10f * 1.943844f).ToString("F0") + " kn, " + ai.navPoints.Count + " waypoints, action " + ai.currentAIAction + " -> steering straight at it for " + ModAIMove.DirectSeconds.ToString("F0") + " s (time " + s.stuckCount + ")");
			ai.navPoints.Clear();
			ai.InterceptTarget(dist, true);
			return true;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[AIMOVE] steer failed: " + ex.Message);
			return false;
		}
	}

	// True if there is land or shallow water on the straight line towards the target (checked every 2 s per ship)
	public static bool LandAhead(Unit u, Unit target, ModAIMove.State s, float dist)
	{
		if (Time.time - s.landCheckTime < ModAIMove.LandCheckSeconds)
		{
			return s.landAhead;
		}
		s.landCheckTime = Time.time;
		s.landAhead = false;
		if (TerrainTiles.instance == null || TerrainTiles.instance.disableTerrain)
		{
			return false;
		}
		Vector3 from = u.transform.position;
		Vector3 dir = target.transform.position - from;
		dir.y = 0f;
		if (dir.sqrMagnitude < 0.01f)
		{
			return false;
		}
		dir.Normalize();
		float reach = Mathf.Min(ModAIMove.LandLookAhead, dist);
		for (float d = ModAIMove.LandStep; d <= reach; d += ModAIMove.LandStep)
		{
			Vector3 p = from + dir * d;
			p.y = -1f;
			if (TerrainTiles.instance.GetRaycastTerrainHeight(p) > ModAIMove.SafeDepth)
			{
				s.landAhead = true;
				return true;
			}
		}
		return false;
	}
}
```

### Step 2 - UnitAISea.AttackUnit (one line)
1. Right-click method **AttackUnit** (class **UnitAISea**) > **Edit Method (C#)...**
2. Near the top, find this line (it's the first `if` after the line that works out `num`):
```csharp
if (this.parentUnit.faction != Faction.Player && this.navPoints.Count > 0)
```
3. Replace that one line with these three lines (the rest stays the same):
```csharp
if (ModAIMove.Steer(this, num))
{
}
else if (this.parentUnit.faction != Faction.Player && this.navPoints.Count > 0)
```
If dnSpy uses another name than `num` for the distance, use that name.
4. **Compile**, then **File > Save Module**.

**Testing**
1. Fight an AI task force that starts far away, like the Shokaku group did.
2. If it circles, within a minute or two an `[AIMOVE]` line should appear in `output_log.txt` and the leader should turn towards you, with the group following.
3. Near islands, a stuck ship should say `land or shallows in the way` and turn onto a new path instead of heading for the beach.
4. Normal fights shouldn't change: no `[AIMOVE]` lines for ships that are closing normally.
5. Send the `output_log.txt` either way.
