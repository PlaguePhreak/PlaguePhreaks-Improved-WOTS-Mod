# Torpedo bomber runs (v0.20.5, AI super overhaul)

## What the test showed (14 Oct, Kates against Hull and Farragut)
- The Kates spawned 9-10 km astern of Farragut running at 30 kn, so they chased her from behind the whole way (130-175 degrees off her bow in the `[TORP]` lines).
- Our hammer and anvil set-up (`UnitAIAir.ModTorpedoSetup`) lets a flight go straight in once it is inside 2.5 km and pointed at the ship, at any angle, and always hands over to the game's run inside 1.2 km. So a flight stuck astern never tries to get ahead.
- The game's drop point (`UnitAIAir.TorpedoApproach`) is "where the ship will be in 28 s, minus about 600 m back along the plane's path". From dead astern that is about 180 m *behind* a 30 kn ship, so the torpedo lands on top of her or right next to her.

## What changes
1. **Fly round to get ahead:** a torpedo flight more than 120 degrees off the ship's bow, inside 4 km, doesn't go in. It keeps flying the set-up (out to the side and ahead) until it is ahead of her beam, then turns in. The planes are 5-6 times faster than a destroyer, so they can overtake her.
2. **Stern attack as a last resort:** if a flight still can't get ahead after 2 minutes, it attacks from astern.
3. **Never drop closer than 600 m:** if the drop point is closer than 600 m to the ship, it is moved out to 600 m on the side the plane is coming from. Real aerial torpedoes needed a few hundred metres to dive, settle and arm, so a drop on top of a ship would not have worked anyway. This also applies to your torpedo planes under manual orders.

Note: a stern attack on a fast ship will often miss, because a 42 kn Type 91 only gains about 12 kn on a 30 kn destroyer. That is historically right; stern attacks were a poor option.

## Install (3 steps)
Back up the DLL first.

### Step 1 - add the class
1. Right-click `Assembly-CSharp` > **Add Class (C#)**, delete what is there and paste all of `ModTorpRun.cs` below.
2. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 2 - UnitAIAir.ModTorpedoSetup (2 small changes)
1. Find class **UnitAIAir**, right-click the method **`ModTorpedoSetup`** > **Edit Method (C#)**.
2. Find these lines:
```csharp
if (dist < 120f)
{
	return false;
}
```
(dnSpy shows `1200f * 0.1f` as `120f`.) Replace them with:
```csharp
if (dist < 120f && !ModTorpRun.Astern(this, target, Vector3.Angle(tFwd, toMe), dist))
{
	return false;
}
```
3. Further down, find the line that starts `if (sideNow == side && dist < 250f && pointedIn)` and change it to:
```csharp
if (sideNow == side && dist < 250f && pointedIn && !ModTorpRun.Astern(this, target, angle, dist))
```
(Keep the `{`, `this.modTorpWaitStart = 0f;`, `return false;` and `}` lines below it as they are.)
4. **Compile**, then **File > Save Module**.
(If dnSpy names any of `dist`, `tFwd`, `toMe`, `angle`, `side`, `sideNow` or `pointedIn` differently, use the names it shows, or send a screenshot.)

### Step 3 - UnitAIAir.TorpedoApproach
1. In class **UnitAIAir**, right-click the method **`TorpedoApproach`** > **Edit Method (C#)**.
2. The first lines are:
```csharp
if (this.ModTorpedoSetup())
{
	return;
}
```
Click just after that closing `}`, press Enter and paste:
```csharp
ModTorpRun.KeepDropOut(this);
```
3. **Compile**, then **File > Save Module**.

### ModTorpRun.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.5 / v0.20.7: torpedo bomber runs.
// 1. Torpedo planes that find themselves astern of their target fly round to get ahead of her before going in,
//    instead of chasing her from behind. Only if they still can't get ahead after 2 minutes do they attack from astern.
// 2. A torpedo is never dropped closer than 600 m from the ship (the game's aim could put the drop point right on top
//    of a fast ship being chased from behind). Real torpedoes needed a few hundred metres to arm and settle.
public class ModTorpRun
{
	// distances in battle code are metres x 0.1
	public const float MinDrop = 600f * 0.1f;
	// "astern" = more than this many degrees off the ship's bow
	public const float SternAngle = 120f;
	// only counts as stuck astern inside this range
	public const float SternRange = 4000f * 0.1f;
	// seconds of trying to get ahead before attacking from astern anyway
	public const float SternGiveUp = 120f;
	// v0.20.7: only check the drop point on the run in (further out the set-up code moves the aim point around),
	// and count as "ahead" only once 15 degrees inside the astern line, so it doesn't flicker at the edge
	public const float DropCheckRange = 2500f * 0.1f;
	public const float AheadMargin = 15f;

	public static Dictionary<int, float> sternSince = new Dictionary<int, float>();
	public static HashSet<int> gaveUp = new HashSet<int>();

	// From UnitAIAir.ModTorpedoSetup: true = this flight is astern and should keep flying round to get ahead (don't commit yet)
	public static bool Astern(UnitAIAir ai, Unit target, float angleOffBow, float dist)
	{
		try
		{
			int id = ai.GetInstanceID();
			bool wasAstern = ModTorpRun.sternSince.ContainsKey(id);
			float line = wasAstern ? ModTorpRun.SternAngle - ModTorpRun.AheadMargin : ModTorpRun.SternAngle;
			if (angleOffBow < line || dist > ModTorpRun.SternRange)
			{
				if (angleOffBow < line && wasAstern)
				{
					ModTorpRun.sternSince.Remove(id);
					UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " is ahead of " + target.unitInstanceName + "'s beam now (" + angleOffBow.ToString("F0") + " deg off her bow, " + (dist * 10f).ToString("F0") + " m), turning in");
				}
				return false;
			}
			if (ModTorpRun.gaveUp.Contains(id))
			{
				return false;
			}
			float t0;
			if (!ModTorpRun.sternSince.TryGetValue(id, out t0))
			{
				ModTorpRun.sternSince[id] = Time.time;
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " is astern of " + target.unitInstanceName + " (" + angleOffBow.ToString("F0") + " deg off her bow, " + (dist * 10f).ToString("F0") + " m), flying round to get ahead before attacking");
				return true;
			}
			if (Time.time - t0 > ModTorpRun.SternGiveUp)
			{
				ModTorpRun.gaveUp.Add(id);
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " couldn't get ahead of " + target.unitInstanceName + " in " + ModTorpRun.SternGiveUp.ToString("F0") + " s, attacking from astern");
				return false;
			}
			return true;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[TORPRUN] astern check failed: " + ex.Message);
			return false;
		}
	}

	// Second line of UnitAIAir.TorpedoApproach: move the drop point out if it is too close to the ship
	public static void KeepDropOut(UnitAIAir ai)
	{
		try
		{
			Unit target = ai.focusedUnit;
			if (target == null || target.isDestroyed || target.unitSea == null || ai.parentUnit == null)
			{
				return;
			}
			Vector3 tPos = target.transform.position;
			if (Utilities.GetXZDistance(ai.parentUnit.transform.position, tPos) > ModTorpRun.DropCheckRange)
			{
				return;
			}
			Vector3 ap = ai.attackPosition;
			Vector3 v = ap - tPos;
			v.y = 0f;
			if (v.magnitude >= ModTorpRun.MinDrop)
			{
				return;
			}
			// push it out towards the side the plane is coming from
			Vector3 dir = ai.parentUnit.transform.position - tPos;
			dir.y = 0f;
			if (dir.sqrMagnitude < 0.01f)
			{
				return;
			}
			dir.Normalize();
			Vector3 moved = tPos + dir * ModTorpRun.MinDrop;
			moved.y = ap.y;
			ai.attackPosition = moved;
			int id = ai.GetInstanceID();
			if (!ModTorpRun.logged.Contains(id))
			{
				ModTorpRun.logged.Add(id);
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + ": drop point was " + (v.magnitude * 10f).ToString("F0") + " m from " + target.unitInstanceName + ", moved out to " + (ModTorpRun.MinDrop * 10f).ToString("F0") + " m");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[TORPRUN] drop check failed: " + ex.Message);
		}
	}

	public static HashSet<int> logged = new HashSet<int>();

	public static string Name(Unit u)
	{
		return (u != null && u.unitData != null) ? u.unitData.unitName : "torpedo plane";
	}
}
```

## Testing
1. Torpedo planes attacking a ship that is running away from them (or start them astern of a destroyer at full speed).
2. They should swing out to one side and overtake her, then turn in from ahead of her beam.
3. No more drops on top of the ship: every torpedo should go in at least 600 m out.
4. In `output_log.txt`:
   - `[TORPRUN] Kate is astern of Farragut (165 deg off her bow, 3100 m), flying round to get ahead before attacking`
   - `[TORPRUN] Kate is ahead of Farragut's beam now (80 deg off her bow, 2400 m), turning in`
   - `[TORPRUN] Kate couldn't get ahead of Farragut in 120 s, attacking from astern`
   - `[TORPRUN] Kate: drop point was 180 m from Farragut, moved out to 600 m`

## Tuning (top of ModTorpRun)
- `MinDrop` 600 m, `SternAngle` 120 degrees, `SternRange` 4,000 m, `SternGiveUp` 120 s.

## Notes
- Tag: `[TORPRUN]`. I could not compile or run this.
- The old `[TORP]` lines from the hammer and anvil code are written many times a second (7,637 in this short test). They could be cut down to one line every few seconds later.


## dnSpy names (14 Oct)
dnSpy shows ModTorpedoSetup with its own variable names: `dist` = `magnitude`, `tFwd` = `forward`, `toMe` = `vector`, `target` = `focusedUnit`, `angle` = `num3`, `side` = `num`, `sideNow` = `num2`, `pointedIn` = `flag`. In that version the two changes are:
```csharp
if (magnitude < 120f && !ModTorpRun.Astern(this, focusedUnit, Vector3.Angle(forward, vector), magnitude))
```
```csharp
if (num2 == num && magnitude < 250f && flag && !ModTorpRun.Astern(this, focusedUnit, num3, magnitude))
```
Optional: the unconditional `Debug.Log` with `" side "`, `" now "`, `" angle "` (about 20,000 lines per battle) can be deleted; the 5-second `[TORP]` line above it stays. **Done 14 Oct: deleted in the user's DLL.**


## v0.20.7
See fixes_v0.20.7.md. The code above is the v0.20.7 version.
