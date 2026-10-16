# Repair rework (v0.17.11)

**What changes**
- **New colours on the damage control grid** (hull and deck):

| Colour | Meaning |
|---|---|
| Yellow | Lightly damaged, 60% health or more, still working |
| Orange | Badly damaged, under 60% health, still working |
| Red | Knocked out. Damage control can fix it at sea |
| Black | Destroyed, or knocked out and needs a port (can't be fixed at sea) |
| Grey | Patched up as far as damage control can go: working, but needs a port to be fully fixed |

- Destroyed hull compartments can still be rebuilt at sea, as before (combat damage package). They show black until rebuilt.
- **Engine rooms can always be repaired at sea,** even when they were knocked out in an earlier battle. Before, those were port-only (lasting damage). Other carried-over equipment (guns, propellers, rudders and so on) still needs a port.
- **A repaired engine room only comes back to 50% health,** and gives **half its power** until a port repair. With 4 engine rooms, one patched room costs about 1/8 of the ship's speed instead of 1/4. A patched engine room shows grey, and at 50% health it breaks again more easily.
- This applies to both sides, including AI auto damage control.
- `[REPAIR]` lines in `output_log.txt` when an engine room comes back online at 50%, and when a carried-over engine room becomes repairable at sea.

**Fix (grey):** after each repair the game lowers a compartment's maximum health, so a compartment repaired in an earlier battle can't be repaired any further at sea. These showed yellow but couldn't be fixed. They now show grey.

**Install (dnSpy).** Back up the DLL first.

### Step 1 - new class ModRepair
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Delete everything in the window and paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// v0.17.11: damage control colours and engine repairs
// Colours on the damage control grid:
//   yellow = lightly damaged (60% or more), orange = badly damaged (under 60%) but working,
//   red = knocked out, damage control can fix it at sea, black = destroyed, or knocked out and needs a port,
//   grey = patched up as far as damage control can go (working, needs a port to be fully fixed)
// Engine rooms can always be repaired at sea (even when the damage was carried over from an earlier battle),
// but a repaired engine room only comes back at 50% health and gives half its power until a port repair.
public class ModRepair
{
	// Health a repaired engine room comes back to (out of 100), and the share of its power it then gives
	public const float EngineRepairCap = 50f;
	public const float PatchedPower = 0.5f;
	// At or above this health (out of 100) damage counts as light (yellow), below it as heavy (orange)
	public const float LightDamage = 60f;

	public static Color Yellow = new Color(1f, 0.82f, 0.24f, 1f);
	public static Color Orange = new Color(1f, 0.55f, 0.1f, 1f);
	public static Color Red = new Color(0.88f, 0.16f, 0.16f, 1f);
	public static Color Black = new Color(0.04f, 0.04f, 0.04f, 1f);
	public static Color Grey = new Color(0.55f, 0.55f, 0.58f, 1f);

	// engine rooms that were knocked out or destroyed when a repair started
	public static HashSet<CellVariable> broken = new HashSet<CellVariable>();
	public static float scanTimer;

	public static bool IsEngine(CellVariable cv)
	{
		return cv != null && cv.parentCell != null && (cv.parentCell.cellType == CellType.Engineering || cv.parentCell.cellType == CellType.ElectricEngine);
	}

	// A working engine room that has been patched up at sea (health capped by an earlier repair)
	public static bool IsPatched(CellVariable cv)
	{
		return ModRepair.IsEngine(cv) && !cv.isOffline && !cv.isDestroyed && cv.maxIntegrity <= ModRepair.EngineRepairCap + 0.5f;
	}

	// ---------- damage control grid colours ----------

	// Replaces the end of DamageControlInterface.UpdateCellIcons: colours the status overlay of one compartment
	public static void SetStatus(DamageControlInterface dci, CellButton hb, CellVariable cv)
	{
		if (hb == null || hb.destroyedIcon == null)
		{
			return;
		}
		Color c;
		bool show = true;
		if (cv.isDestroyed)
		{
			c = ModRepair.Black;
		}
		else if (cv.isOffline)
		{
			c = ModRepair.CanFixAtSea(dci, cv) ? ModRepair.Red : ModRepair.Black;
		}
		else if (cv.integrity < cv.maxIntegrity - 0.01f)
		{
			// damaged, damage control can still repair it
			c = (cv.integrity >= ModRepair.LightDamage) ? ModRepair.Yellow : ModRepair.Orange;
		}
		else if (cv.maxIntegrity < 100f)
		{
			// patched up as far as damage control can go: working, needs a port to be fully fixed
			c = ModRepair.Grey;
		}
		else
		{
			c = Color.clear;
			show = false;
		}
		hb.destroyedIcon.gameObject.SetActive(show);
		if (show)
		{
			hb.destroyedIcon.color = c;
		}
	}

	public static bool CanFixAtSea(DamageControlInterface dci, CellVariable cv)
	{
		if (cv.needsPortRepair && !ModRepair.IsEngine(cv))
		{
			return false;
		}
		try
		{
			int side = (dci != null && dci.currentUnit != null) ? (int)dci.currentUnit.faction : 0;
			return Config.instance.repairKnockedOut[side];
		}
		catch
		{
			return true;
		}
	}

	// ---------- engine repairs ----------

	// First line of DamageableSea.RepairCompartment: remember engine rooms that are being brought back
	public static void BeforeRepair(DamageableSea ds, string id)
	{
		try
		{
			CellVariable cv;
			if (ds != null && ds.cellVariables.TryGetValue(id, out cv) && ModRepair.IsEngine(cv) && (cv.isOffline || cv.isDestroyed))
			{
				ModRepair.broken.Add(cv);
			}
		}
		catch
		{
		}
	}

	// First line of DamageableSea.CheckUpdateCellIcons (runs at the end of every repair): cap an engine room that just came back
	public static void AfterChange(DamageableSea ds, CellVariable cv)
	{
		try
		{
			if (cv == null || !ModRepair.broken.Contains(cv) || cv.isOffline || cv.isDestroyed)
			{
				return;
			}
			ModRepair.broken.Remove(cv);
			cv.maxIntegrity = Mathf.Min(cv.maxIntegrity, ModRepair.EngineRepairCap);
			cv.integrity = Mathf.Min(cv.integrity, cv.maxIntegrity);
			ds.speedPenalty = ds.GetSpeedPenalty();
			UnityEngine.Debug.Log("[REPAIR] " + ds.parentUnit.unitInstanceName + ": engine room " + cv.parentCell.cellID + " back online at " + Mathf.RoundToInt(cv.maxIntegrity) + "% (half power until a port repair), speed penalty now " + (ds.speedPenalty * 100f).ToString("F0") + "%");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[REPAIR] engine cap failed: " + ex.Message);
		}
	}

	// Every frame from ModRescue.Update: engine rooms knocked out in an earlier battle can be repaired at sea
	public static void Tick()
	{
		ModRepair.scanTimer -= Time.unscaledDeltaTime;
		if (ModRepair.scanTimer > 0f)
		{
			return;
		}
		ModRepair.scanTimer = 2f;
		try
		{
			if (EngagementManager.instance == null)
			{
				return;
			}
			List<Unit>[] lists = new List<Unit>[] { EngagementManager.instance.playerUnits, EngagementManager.instance.otherUnits };
			for (int l = 0; l < lists.Length; l++)
			{
				if (lists[l] == null)
				{
					continue;
				}
				for (int i = 0; i < lists[l].Count; i++)
				{
					Unit u = lists[l][i];
					if (u == null || u.isDestroyed || u.damageableSea == null || u.damageableSea.engineCoords == null)
					{
						continue;
					}
					for (int e = 0; e < u.damageableSea.engineCoords.Count; e++)
					{
						CellVariable cv;
						if (u.damageableSea.cellVariables.TryGetValue(u.damageableSea.engineCoords[e], out cv) && cv.needsPortRepair && ModRepair.IsEngine(cv))
						{
							cv.needsPortRepair = false;
							UnityEngine.Debug.Log("[REPAIR] " + u.unitInstanceName + ": engine room " + cv.parentCell.cellID + " from an earlier battle can be repaired at sea (it will come back at " + ModRepair.EngineRepairCap.ToString("F0") + "%)");
						}
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[REPAIR] scan failed: " + ex.Message);
		}
	}
}
```

### Step 2 - DamageControlInterface.UpdateCellIcons (replace the method)
1. Right-click method **UpdateCellIcons** (class **DamageControlInterface**) > **Edit Method (C#)...**
2. Replace the whole method (from `public void UpdateCellIcons` to its last `}`) with:
```csharp
public void UpdateCellIcons(CellButton hb, CellVariable cv, bool allOff)
{
	if (allOff)
	{
		hb.repairIcon.gameObject.SetActive(false);
		hb.fireIcon.gameObject.SetActive(false);
		hb.destroyedIcon.gameObject.SetActive(false);
		if (hb.fillOverlay != null)
		{
			hb.fillOverlay.gameObject.SetActive(false);
		}
		return;
	}
	hb.repairIcon.gameObject.SetActive(cv.isUnderRepair);
	hb.fireIcon.gameObject.SetActive(cv.isBurning);
	if (hb.fillOverlay != null)
	{
		hb.fillOverlay.gameObject.SetActive(cv.isFlooded != 0f);
	}
	ModRepair.SetStatus(this, hb, cv);
}
```
3. **Compile**.

### Steps 3-4 - one line at the start of each method
For each method below, right-click it > **Edit Method (C#)...**, click just after the opening `{`, press Enter, paste the line and click **Compile**.

| Step | Class | Method | Line to paste |
|---|---|---|---|
| 3 | DamageableSea | **RepairCompartment** | `ModRepair.BeforeRepair(this, id);` |
| 4 | DamageableSea | **CheckUpdateCellIcons** | `ModRepair.AfterChange(this, cv);` |

If dnSpy uses other names than `id` or `cv` for the method's input, use those.

### Step 5 - DamageableSea.GetSpeedPenalty (half power for patched engine rooms)
1. Right-click method **GetSpeedPenalty** (class **DamageableSea**) > **Edit Method (C#)...**
2. Press Ctrl+F and find `engineCoords`. You'll find a `for` loop that looks like this (dnSpy's letters may differ):
```csharp
for (int k = 0; k < this.engineCoords.Count; k++)
{
	if (this.cellVariables[this.engineCoords[k]].isOffline || this.cellVariables[this.engineCoords[k]].isDestroyed)
	{
		num -= num2;
	}
}
```
3. Directly after the `}` that closes the `if` (still inside the loop), add:
```csharp
	else if (ModRepair.IsPatched(this.cellVariables[this.engineCoords[k]]))
	{
		num -= num2 * (1f - ModRepair.PatchedPower);
	}
```
Use the same letters as your `if` line (`k`, `num`, `num2`). If the loop looks different, send me a screenshot of it.
4. **Compile**, then **File > Save Module**.

### Step 6 - ModRescue (replace the class)
1. Right-click class **ModRescue** > **Edit Class (C#)...** (check the title says *ModRescue*)
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

```csharp
using UnityEngine;

public class ModRescue : MonoBehaviour
{
	private void Update()
	{
		try
		{
			ModHitLog.Tick();
		}
		catch
		{
		}
		try
		{
			ModGroups.Tick();
		}
		catch
		{
		}
		try
		{
			ModMinimap.Tick();
		}
		catch
		{
		}
		try
		{
			ModRepair.Tick();
		}
		catch
		{
		}
		this.timer += Time.deltaTime;
		if (this.timer < 1f)
		{
			return;
		}
		float dt = this.timer;
		this.timer = 0f;
		try
		{
			if (EngagementData.instance != null && EngagementData.instance.isCampaignEngagement)
			{
				ModCrew.RescueTick(dt);
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] tick failed: " + ex.Message);
		}
	}

	private void OnGUI()
	{
		try
		{
			ModHitLog.Draw();
		}
		catch
		{
		}
	}

	private float timer;
}
```

**Testing**
1. In battle, open damage control on a damaged ship. Lightly hit compartments should be yellow, badly hit ones orange, knocked-out ones red, and destroyed ones black.
2. A gun or other equipment carried over knocked out from an earlier battle should be black (needs a port).
3. Repair a knocked-out engine room. It should come back online and show grey (50%, patched). The ship should get some speed back, but not all of it. The log should say `[REPAIR] ... back online at 50%`.
4. Start a battle with an engine room carried over knocked out. The log should say it can be repaired at sea, and a party should be able to fix it.
5. If something looks wrong, send a screenshot of the damage control panel and the `[REPAIR]` lines.

**Tuning (top of ModRepair):** `EngineRepairCap` (50), `PatchedPower` (0.5), `LightDamage` (60), and the four colours.
