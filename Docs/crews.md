# Crews (v0.18 and onwards)

All crew and veterancy work goes under v0.18, then v0.18.1, v0.18.2 and so on. It builds on veteran crews (veteran_crews.md).

## The plan
| Version | Part | Status |
|---|---|---|
| v0.18 | Veterancy only from real fights `[VET]` | Tested |
| v0.18.1 | Crew numbers and losses `[CREW]` | Tested |
| v0.18.2 | Short-crew effects | Tested |
| v0.18.3 | Rescue survivors in battle `[RESCUE]` | Tested |
| v0.18.4 | Rescue missions on the campaign map `[RESCUE]` | Tested |

**Decisions**
- **Crew:** each ship has its historical crew (`UnitData.crew`, already in every ship's data file), saved per ship in the campaign. Crew is lost from destroyed compartments, fires and flooding.
- **Experience:** veterancy becomes experience points, with the same ranks (Green, Trained, Veteran, Elite). Losing crew takes away progress towards the next rank.
- **Port top-up:** recruits from port always reset progress towards the next rank to 0. If progress is already 0, the ship drops one rank.
- **Short crew:** below 80% crew (90% before v0.18.5), reloads and repairs get slower. Damage control parties = normal parties x crew left, with a minimum of 1.
- **Rescue, both places:**
  - In battle: a ship that sinks leaves survivors in the water. Get close and slow down to pick them up.
  - On the campaign map: events like "a merchant ship was ambushed and sunk at X, send someone to check for survivors". A task force that reaches the spot in time picks them up.
- **Whose survivors count:**
  - Your own survivors top up crew without hurting experience.
  - Enemy survivors become prisoners and give a reward, such as supply or command points.

---

## v0.18 - Veterancy only from real fights

**What was wrong:** every surviving ship gained a battle of veterancy whenever a battle ended, even if no enemy was there.

**What changes:** a task force only gains veterancy if:
- at least one enemy ship or aircraft was in the battle, **and**
- at least one enemy was sunk or shot down.

Enemy aircraft that landed back on their carrier don't count as losses. Each player task force writes a `[VET]` line to `output_log.txt` saying whether it gained veterancy and why.

**Install (dnSpy)**
1. In class **MobileMapObject**, right-click method **AwardVeterancy** > **Edit Method (C#)...**
2. Select everything and replace it with:
```csharp
public static void AwardVeterancy(MobileMapObject mmo)
{
    if (mmo.currentFaction != 0 || mmo.type != 0)
    {
        return;
    }
    int enemyUnits = 0;
    int enemyLosses = 0;
    try
    {
        List<Unit> enemyList = EngagementManager.instance.otherUnits;
        for (int e = 0; e < enemyList.Count; e++)
        {
            Unit enemy = enemyList[e];
            if ((object)enemy == null)
            {
                continue;
            }
            enemyUnits++;
            if (enemy.isDestroyed && !enemy.isParked)
            {
                enemyLosses++;
            }
            else if ((object)enemy.unitAir != null && enemy.unitAir.shootDown)
            {
                enemyLosses++;
            }
        }
    }
    catch (System.Exception ex)
    {
        UnityEngine.Debug.LogError("[VET] could not read the enemy list: " + ex.Message);
    }
    if (enemyUnits == 0 || enemyLosses == 0)
    {
        UnityEngine.Debug.Log("[VET] " + mmo.mobileName + " gets no veterancy: " + enemyUnits + " enemy units in the battle, " + enemyLosses + " lost");
        return;
    }
    UnityEngine.Debug.Log("[VET] " + mmo.mobileName + " gains veterancy: " + enemyUnits + " enemy units in the battle, " + enemyLosses + " lost");
    CampaignData cd = CampaignManager.instance.campaignData;
    if (cd.vetNames == null)
    {
        cd.vetNames = new List<string>();
    }
    if (cd.vetBattles == null)
    {
        cd.vetBattles = new List<int>();
    }
    string promoted = string.Empty;
    for (int i = 0; i < mmo.unitPrefabs.Count; i++)
    {
        if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
        {
            continue;
        }
        string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
        int idx = cd.vetNames.IndexOf(shipName);
        int before = 0;
        if (idx == -1)
        {
            cd.vetNames.Add(shipName);
            cd.vetBattles.Add(0);
            idx = cd.vetNames.Count - 1;
        }
        else
        {
            before = cd.vetBattles[idx];
        }
        cd.vetBattles[idx] = before + 1;
        string oldRank = MobileMapObject.GetVeteranRank(before);
        string newRank = MobileMapObject.GetVeteranRank(before + 1);
        if (oldRank != newRank)
        {
            if (promoted != string.Empty)
            {
                promoted = promoted + ", ";
            }
            promoted = promoted + shipName + " (" + newRank + ")";
        }
    }
    if (promoted != string.Empty)
    {
        try
        {
            ErrorPanel.instance.SetErrorMessage("CrewPromoted", promoted, string.Empty, string.Empty);
        }
        catch
        {
        }
    }
}
```
3. Click **Compile**, then **File > Save Module**.

**Testing**
1. Sail a task force into a battle with no enemy, or leave a battle before anything is sunk or shot down. The log should say `[VET] <task force> gets no veterancy: ...`.
2. Fight a battle where you sink a ship or shoot down a plane. The log should say `[VET] <task force> gains veterancy: X enemy units in the battle, Y lost`.

**Note:** an attack on a port or airfield with no enemy ships or aircraft in the battle doesn't count, because the game doesn't list those as enemy units.

---

## v0.18.1 - Crew numbers and losses

**What changes**
- **Every ship has a crew count:** its historical crew from its data file, e.g. Enterprise 2,217 or a Fletcher about 330. The hover panel shows it as a new **Men** line, e.g. `1,840 / 2,217`. It turns orange below 90% and red below 50%.
- **Ships lose men in battle:**
  - Each destroyed compartment kills about half of that compartment's share of the crew.
  - Each new fire kills a little, and each compartment that starts flooding kills a little.
  - Some compartments cost more: magazine x4, bridge / control room / conning tower x2.5, engine rooms and gun turrets x2, hangar and torpedoes x1.5. Propellers, rudder, funnel and director cost x0.5.
  - A ship that stays afloat never drops below 15% of its crew.
- **Experience points:** veterancy now counts in experience points instead of whole battles. Each real fight still gives +1, and the ranks are the same: Green 0-1.9, Trained 2-4.9, Veteran 5-8.9, Elite 9+. The hover panel shows the points, e.g. `Trained (4.6)`.
- **Losses cost progress:** losing a share of the crew takes the same share of the progress towards the next rank, but never drops a rank. For example, a ship on 4.6 (Trained, 2.6 into the rank) that loses 15% of its men goes to 4.21.
- **Port top-up:**
  - Using **Rearm** at a port refills the crew with recruits.
  - That resets progress towards the next rank to 0. If the progress was already 0, the ship drops one rank.
  - Top-ups of 3% or less of the crew are free (wounded returning to duty).
- **Old saves:** existing ships keep their battles as experience points and start at full crew.
- **Log lines** (`[CREW]`): crew at the start of each battle, each loss with the compartment, the total after the battle, and port top-ups. `[VET]` lines now show each ship's experience change.

**Install (dnSpy).** Back up the DLL first, then do the steps in order.

### Step 1 - save-file fields (CampaignData)
1. Right-click class **CampaignData** > **Edit Class (C#)...**
2. Find the line `public List<int> vetBattles = new List<int>();` and add these two lines directly under it:
```csharp
public List<float> vetXP = new List<float>();
public List<int> vetCrew = new List<int>();
```
3. Click **Compile**, then **File > Save Module**.
4. **Close dnSpy, reopen it and reopen the DLL.**

### Step 2 - new class ModCrew
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Select everything in the window and paste this over it:
```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModCrew
{
	public class Entry
	{
		public string name;
		public int full;
		public int start;
		public float lost;
		public int cells;
		public bool applied;
	}

	// Share of one compartment's worth of crew lost when that compartment is destroyed / catches fire / starts flooding
	public const float DestroyShare = 0.5f;
	public const float FireShare = 0.15f;
	public const float FloodShare = 0.1f;
	// A ship afloat never drops below this share of its full crew
	public const float MinCrew = 0.15f;
	// Port top-ups this small (wounded returning to duty) cost no experience
	public const float FreeTopUp = 0.03f;

	public static Dictionary<int, ModCrew.Entry> battle = new Dictionary<int, ModCrew.Entry>();

	// ---------------- campaign data ----------------

	public static int Index(string name, bool create)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.vetNames == null)
		{
			cd.vetNames = new List<string>();
		}
		if (cd.vetBattles == null)
		{
			cd.vetBattles = new List<int>();
		}
		if (cd.vetXP == null)
		{
			cd.vetXP = new List<float>();
		}
		if (cd.vetCrew == null)
		{
			cd.vetCrew = new List<int>();
		}
		while (cd.vetBattles.Count < cd.vetNames.Count)
		{
			cd.vetBattles.Add(0);
		}
		while (cd.vetXP.Count < cd.vetNames.Count)
		{
			cd.vetXP.Add((float)cd.vetBattles[cd.vetXP.Count]);
		}
		while (cd.vetCrew.Count < cd.vetNames.Count)
		{
			cd.vetCrew.Add(-1);
		}
		int idx = cd.vetNames.IndexOf(name);
		if (idx == -1 && create)
		{
			cd.vetNames.Add(name);
			cd.vetBattles.Add(0);
			cd.vetXP.Add(0f);
			cd.vetCrew.Add(-1);
			idx = cd.vetNames.Count - 1;
		}
		return idx;
	}

	public static float GetXP(string name)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return 0f;
		}
		return CampaignManager.instance.campaignData.vetXP[idx];
	}

	public static void SetXP(int idx, float xp)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (xp < 0f)
		{
			xp = 0f;
		}
		cd.vetXP[idx] = xp;
		cd.vetBattles[idx] = Mathf.FloorToInt(xp + 0.001f);
	}

	public static float RankFloor(float xp)
	{
		int b = Mathf.FloorToInt(xp + 0.001f);
		if (b >= 9)
		{
			return 9f;
		}
		if (b >= 5)
		{
			return 5f;
		}
		if (b >= 2)
		{
			return 2f;
		}
		return 0f;
	}

	public static float PreviousRankFloor(float floor)
	{
		if (floor >= 9f)
		{
			return 5f;
		}
		if (floor >= 5f)
		{
			return 2f;
		}
		return 0f;
	}

	public static string RankName(float xp)
	{
		return MobileMapObject.GetVeteranRank(Mathf.FloorToInt(xp + 0.001f));
	}

	public static int FullCrew(string prefab)
	{
		try
		{
			if (EngagementManager.instance != null && EngagementManager.instance.unitDataDictionary.ContainsKey(prefab))
			{
				return EngagementManager.instance.unitDataDictionary[prefab].crew;
			}
		}
		catch
		{
		}
		return 0;
	}

	public static int GetCrew(string name, int full)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return full;
		}
		int crew = CampaignManager.instance.campaignData.vetCrew[idx];
		if (crew < 0 || crew > full)
		{
			return full;
		}
		return crew;
	}

	// Losing a share of the crew takes the same share of the progress towards the next rank. Never drops a rank.
	public static void LoseProgress(int idx, float share)
	{
		float xp = CampaignManager.instance.campaignData.vetXP[idx];
		float floor = ModCrew.RankFloor(xp);
		ModCrew.SetXP(idx, floor + (xp - floor) * (1f - Mathf.Clamp01(share)));
	}

	// ---------------- battle ----------------

	public static void OnBattleStart()
	{
		try
		{
			if (EngagementData.instance == null || !EngagementData.instance.isCampaignEngagement || EngagementManager.instance == null)
			{
				return;
			}
			Dictionary<int, ModCrew.Entry> fresh = new Dictionary<int, ModCrew.Entry>();
			List<Unit> units = EngagementManager.instance.playerUnits;
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u == null || u.unitSea == null || u.damageableSea == null || u.unitData == null || u.unitData.crew <= 0)
				{
					continue;
				}
				int id = u.damageableSea.GetInstanceID();
				if (ModCrew.battle.ContainsKey(id))
				{
					fresh[id] = ModCrew.battle[id];
					continue;
				}
				ModCrew.Entry e = new ModCrew.Entry();
				e.name = u.unitInstanceName;
				e.full = u.unitData.crew;
				e.start = ModCrew.GetCrew(e.name, e.full);
				e.lost = 0f;
				e.cells = Mathf.Max(1, u.damageableSea.cellVariables.Count);
				e.applied = false;
				fresh[id] = e;
				UnityEngine.Debug.Log("[CREW] " + e.name + " enters battle with " + e.start.ToString("#,##0") + " / " + e.full.ToString("#,##0") + " men, " + ModCrew.RankName(ModCrew.GetXP(e.name)) + " (" + ModCrew.GetXP(e.name).ToString("F2") + ")");
			}
			ModCrew.battle = fresh;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] battle start failed: " + ex.ToString());
		}
	}

	public static float CellFactor(CellVariable cv)
	{
		if (cv == null || cv.parentCell == null)
		{
			return 1f;
		}
		switch (cv.parentCell.cellType)
		{
		case CellType.Magazine:
			return 4f;
		case CellType.Bridge:
		case CellType.ControlRoom:
		case CellType.Conning:
			return 2.5f;
		case CellType.Engineering:
		case CellType.ElectricEngine:
		case CellType.Primary:
		case CellType.Secondary:
			return 2f;
		case CellType.Aircraft:
		case CellType.Torpedo:
		case CellType.Torpedo_Room:
			return 1.5f;
		case CellType.Propeller:
		case CellType.DoublePropeller:
		case CellType.Rudder:
		case CellType.PropellersRudder:
		case CellType.Funnel:
		case CellType.Director:
			return 0.5f;
		}
		return 1f;
	}

	public static void AddLoss(DamageableSea ds, CellVariable cv, float share, string what)
	{
		try
		{
			if (ds == null || ModCrew.battle.Count == 0)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.applied)
			{
				return;
			}
			float men = (float)e.start / (float)e.cells * share * ModCrew.CellFactor(cv);
			float maxLoss = (float)e.start - (float)e.full * ModCrew.MinCrew;
			if (maxLoss <= 0f)
			{
				return;
			}
			if (e.lost + men > maxLoss)
			{
				men = maxLoss - e.lost;
			}
			if (men <= 0f)
			{
				return;
			}
			e.lost += men;
			string cellName = (cv != null && cv.parentCell != null) ? (cv.parentCell.cellType.ToString() + " " + cv.parentCell.cellID) : "?";
			UnityEngine.Debug.Log("[CREW] " + e.name + ": " + cellName + " " + what + ", " + men.ToString("F1") + " men lost (battle total " + Mathf.RoundToInt(e.lost) + " of " + e.start + ")");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] loss failed: " + ex.Message);
		}
	}

	public static void OnCellDestroyed(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.DestroyShare, "destroyed");
	}

	public static void OnFire(DamageableSea ds, CellVariable cv, bool isOn)
	{
		if (!isOn || cv == null || cv.isBurning || cv.isDestroyed || cv.parentCell == null || !cv.parentCell.canBurn)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FireShare, "on fire");
	}

	public static void OnFlood(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isFlooded > 0f || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FloodShare, "flooding");
	}

	// ---------------- after battle ----------------

	public static void ApplyBattleLosses(MobileMapObject mmo)
	{
		try
		{
			if (mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
				{
					continue;
				}
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				ModCrew.Entry e = null;
				foreach (ModCrew.Entry candidate in ModCrew.battle.Values)
				{
					if (!candidate.applied && candidate.name == shipName)
					{
						e = candidate;
						break;
					}
				}
				if (e == null)
				{
					continue;
				}
				e.applied = true;
				int lostMen = Mathf.RoundToInt(e.lost);
				if (lostMen <= 0)
				{
					continue;
				}
				int idx = ModCrew.Index(shipName, true);
				int crewNow = Mathf.Max(0, e.start - lostMen);
				cd.vetCrew[idx] = crewNow;
				float xpBefore = cd.vetXP[idx];
				ModCrew.LoseProgress(idx, (float)lostMen / (float)e.full);
				UnityEngine.Debug.Log("[CREW] " + shipName + " lost " + lostMen + " men in the battle: crew " + crewNow.ToString("#,##0") + " / " + e.full.ToString("#,##0") + ", experience " + xpBefore.ToString("F2") + " -> " + cd.vetXP[idx].ToString("F2"));
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] applying losses failed: " + ex.ToString());
		}
	}

	// ---------------- port ----------------

	public static void PortTopUp(MobileMapObject mmo)
	{
		try
		{
			if (mmo == null || mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0)
				{
					continue;
				}
				int missing = full - cd.vetCrew[idx];
				cd.vetCrew[idx] = -1;
				if (missing <= 0)
				{
					continue;
				}
				if ((float)missing <= (float)full * ModCrew.FreeTopUp)
				{
					UnityEngine.Debug.Log("[CREW] " + shipName + " topped up " + missing + " men in port (wounded back on duty, no experience lost)");
					continue;
				}
				float xp = cd.vetXP[idx];
				float floor = ModCrew.RankFloor(xp);
				float newXP;
				if (xp - floor > 0.01f)
				{
					newXP = floor;
				}
				else
				{
					newXP = ModCrew.PreviousRankFloor(floor);
				}
				ModCrew.SetXP(idx, newXP);
				UnityEngine.Debug.Log("[CREW] " + shipName + " took on " + missing + " new recruits in port: experience " + xp.ToString("F2") + " -> " + newXP.ToString("F2") + " (" + ModCrew.RankName(xp) + " -> " + ModCrew.RankName(newXP) + ")");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] port top-up failed: " + ex.ToString());
		}
	}
}
```
3. Click **Compile**, then **File > Save Module**.
4. **Close dnSpy, reopen it and reopen the DLL.**

### Step 3 - MobileMapObject.AwardVeterancy
1. In class **MobileMapObject**, right-click method **AwardVeterancy** > **Edit Method (C#)...**
2. Select all of it and replace it with:
```csharp
public static void AwardVeterancy(MobileMapObject mmo)
{
    if (mmo.currentFaction != 0 || mmo.type != 0)
    {
        return;
    }
    ModCrew.ApplyBattleLosses(mmo);
    int enemyUnits = 0;
    int enemyLosses = 0;
    try
    {
        List<Unit> enemyList = EngagementManager.instance.otherUnits;
        for (int e = 0; e < enemyList.Count; e++)
        {
            Unit enemy = enemyList[e];
            if ((object)enemy == null)
            {
                continue;
            }
            enemyUnits++;
            if (enemy.isDestroyed && !enemy.isParked)
            {
                enemyLosses++;
            }
            else if ((object)enemy.unitAir != null && enemy.unitAir.shootDown)
            {
                enemyLosses++;
            }
        }
    }
    catch (System.Exception ex)
    {
        UnityEngine.Debug.LogError("[VET] could not read the enemy list: " + ex.Message);
    }
    if (enemyUnits == 0 || enemyLosses == 0)
    {
        UnityEngine.Debug.Log("[VET] " + mmo.mobileName + " gets no veterancy: " + enemyUnits + " enemy units in the battle, " + enemyLosses + " lost");
        return;
    }
    UnityEngine.Debug.Log("[VET] " + mmo.mobileName + " gains veterancy: " + enemyUnits + " enemy units in the battle, " + enemyLosses + " lost");
    CampaignData cd = CampaignManager.instance.campaignData;
    string promoted = string.Empty;
    for (int i = 0; i < mmo.unitPrefabs.Count; i++)
    {
        if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
        {
            continue;
        }
        string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
        int idx = ModCrew.Index(shipName, true);
        float before = cd.vetXP[idx];
        ModCrew.SetXP(idx, before + 1f);
        string oldRank = ModCrew.RankName(before);
        string newRank = ModCrew.RankName(before + 1f);
        UnityEngine.Debug.Log("[VET] " + shipName + " experience " + before.ToString("F2") + " -> " + (before + 1f).ToString("F2") + " (" + newRank + ")");
        if (oldRank != newRank)
        {
            if (promoted != string.Empty)
            {
                promoted = promoted + ", ";
            }
            promoted = promoted + shipName + " (" + newRank + ")";
        }
    }
    if (promoted != string.Empty)
    {
        try
        {
            ErrorPanel.instance.SetErrorMessage("CrewPromoted", promoted, string.Empty, string.Empty);
        }
        catch
        {
        }
    }
}
```
3. Click **Compile**.

### Step 4 - MobileMapObject.AppendShipInfoFromKey (hover panel)
1. In class **MobileMapObject**, right-click method **AppendShipInfoFromKey** > **Edit Method (C#)...**
2. Select all of it and replace it with:
```csharp
public static void AppendShipInfoFromKey(string shipData, Text labels, Text values)
{
	try
	{
		string[] parts = shipData.Split(new char[] { ',' });
		int shipIndex = int.Parse(parts[1]);
		MobileMapObject mmo;
		if (int.Parse(parts[0]) == -1)
		{
			mmo = CampaignInterface.instance.currentMapObject.mobileMapObject;
		}
		else
		{
			mmo = CampaignManager.instance.playerMobile[int.Parse(parts[0])].mobileMapObject;
		}
		if (mmo.currentFaction != 0 || mmo.type != 0 || shipIndex < 0 || shipIndex >= mmo.unitPrefabs.Count)
		{
			return;
		}
		if (labels.text != string.Empty && !labels.text.EndsWith("\n"))
		{
			labels.text = labels.text + "\n";
		}
		if (values.text != string.Empty && !values.text.EndsWith("\n"))
		{
			values.text = values.text + "\n";
		}
		string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[shipIndex], string.Empty, mmo.unitInstances[shipIndex]);
		float xp = ModCrew.GetXP(shipName);
		labels.text = labels.text + "Crew\n";
		values.text = values.text + ModCrew.RankName(xp) + " (" + xp.ToString("F1") + ")\n";
		int full = ModCrew.FullCrew(mmo.unitPrefabs[shipIndex]);
		if (full > 0)
		{
			int crew = ModCrew.GetCrew(shipName, full);
			string crewText = crew.ToString("#,##0") + " / " + full.ToString("#,##0");
			if ((float)crew < (float)full * 0.5f)
			{
				crewText = "<color=#ff5050>" + crewText + "</color>";
			}
			else if ((float)crew < (float)full * 0.9f)
			{
				crewText = "<color=#ff9020>" + crewText + "</color>";
			}
			labels.text = labels.text + "Men\n";
			values.text = values.text + crewText + "\n";
		}
		labels.text = labels.text + "Fuel\n";
		float fuelLeft = Mathf.Max(0f, 10f - mmo.fuelUsedDays);
		string fuelTag = string.Empty;
		if (fuelLeft <= 0f)
		{
			fuelTag = " <color=#ff5050>EMPTY</color>";
		}
		else if (fuelLeft <= 3f)
		{
			fuelTag = " <color=#ff9020>LOW</color>";
		}
		values.text = values.text + fuelLeft.ToString("F1") + " days" + fuelTag + "\n";
	}
	catch
	{
	}
}
```
3. Click **Compile**.

### Steps 5-9 - one line at the start of each method
For each method below:
1. Right-click the method > **Edit Method (C#)...**
2. Click just after the opening `{` of the method and press Enter.
3. Paste the line.
4. Click **Compile**.

| Step | Class | Method | Line to paste |
|---|---|---|---|
| 5 | EngagementManager | **StartCombat** | `ModCrew.OnBattleStart();` |
| 6 | DamageableSea | **DestroyCell** | `ModCrew.OnCellDestroyed(this, cv);` |
| 7 | DamageableSea | **FloodCompartment** | `ModCrew.OnFlood(this, cv);` |
| 8 | DamageableSea | **SetFire** | `ModCrew.OnFire(this, cv, isOn);` |
| 9 | ResupplyShips | **ResetAircraft** | `ModCrew.PortTopUp(mmo);` |

Then **File > Save Module**. If any step shows red errors, send me a screenshot.

**Testing**
1. Hover over a ship on the campaign map. You should see `Crew  Green (0.0)` (or its rank) and `Men  2,217 / 2,217`.
2. Fight a battle and take some damage. In `output_log.txt`, look for:
   - `[CREW] <ship> enters battle with ...` at the start.
   - `[CREW] <ship>: Engineering 1,0,3 destroyed, 8.5 men lost ...` as hits land.
   - `[CREW] <ship> lost N men in the battle ...` after the battle.
3. Hover over the damaged ship. Its **Men** should be lower, and its experience points may have dropped a little.
4. Sail to a port and use **Rearm**. The log should show `[CREW] <ship> took on N new recruits ...`, and the hover panel should show a full crew again.

**Tuning:** the numbers at the top of ModCrew (`DestroyShare`, `FireShare`, `FloodShare`, `MinCrew`, `FreeTopUp`) set how many men are lost and how big a top-up is free. Send me a log after a few battles if the losses feel too high or too low.

**Not in this part:**
- The crew count doesn't change anything in battle yet. That comes in v0.18.2.
- Survivors from sunk ships come in v0.18.3.


---

## v0.18.2 - Short-crew effects

**What changes**
- **Slower reloads and repairs:** below 90% of its crew, a ship loses efficiency, 7.5% for every 10% of crew under 90%. Lower efficiency means slower gun and torpedo reloads and slower damage control (the same number veterancy raises).

  | Crew left | Efficiency | Reloads and repairs take |
  |---|---|---|
  | 90% or more | no change | normal time |
  | 75% | -11% | about 11% longer |
  | 50% | -30% | about 30% longer |
  | 25% | -49% | about 49% longer (until the game's minimum efficiency stops it) |

- **Fewer damage control parties:** a ship gets its normal number of parties x the share of crew left, rounded, with a minimum of 1. For example, a cruiser with 4 parties at 60% crew has 2, and a destroyer with 3 at 60% has 2. Parties already at work finish their job.
- **It happens live in battle:** as men are lost, the ship gets slower and loses parties during the fight, not just in the next battle.
- **Enemy ships too:** enemy crews start full each battle, but they lose men in the same way and suffer the same effects. Their losses aren't saved.
- **Log lines** (`[CREW]`):
  - Battle start: `... is short-handed: 2 of 4 damage control parties, efficiency -23%`
  - In battle: `... now has 3 of 4 damage control parties (68% crew)`

**Install (dnSpy).** Back up the DLL first.

### Step 1 - ModCrew (replace the class)
1. Right-click class **ModCrew** > **Edit Class (C#)...**
2. Select everything and paste this over it:
```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModCrew
{
	public class Entry
	{
		public string name;
		public int full;
		public int start;
		public float lost;
		public int cells;
		public bool applied;
		public int faction;
		public int lastParties = -1;
	}

	// Share of one compartment's worth of crew lost when that compartment is destroyed / catches fire / starts flooding
	public const float DestroyShare = 0.5f;
	public const float FireShare = 0.15f;
	public const float FloodShare = 0.1f;
	// A ship afloat never drops below this share of its full crew
	public const float MinCrew = 0.15f;
	// Port top-ups this small (wounded returning to duty) cost no experience
	public const float FreeTopUp = 0.03f;
	// Below this share of the crew, reloads and repairs slow down
	public const float ShortCrewStart = 0.9f;
	// Efficiency lost per share of crew below ShortCrewStart (0.75 = -30% efficiency at half crew)
	public const float ShortCrewFactor = 0.75f;

	public static Dictionary<int, ModCrew.Entry> battle = new Dictionary<int, ModCrew.Entry>();

	// ---------------- campaign data ----------------

	public static int Index(string name, bool create)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.vetNames == null)
		{
			cd.vetNames = new List<string>();
		}
		if (cd.vetBattles == null)
		{
			cd.vetBattles = new List<int>();
		}
		if (cd.vetXP == null)
		{
			cd.vetXP = new List<float>();
		}
		if (cd.vetCrew == null)
		{
			cd.vetCrew = new List<int>();
		}
		while (cd.vetBattles.Count < cd.vetNames.Count)
		{
			cd.vetBattles.Add(0);
		}
		while (cd.vetXP.Count < cd.vetNames.Count)
		{
			cd.vetXP.Add((float)cd.vetBattles[cd.vetXP.Count]);
		}
		while (cd.vetCrew.Count < cd.vetNames.Count)
		{
			cd.vetCrew.Add(-1);
		}
		int idx = cd.vetNames.IndexOf(name);
		if (idx == -1 && create)
		{
			cd.vetNames.Add(name);
			cd.vetBattles.Add(0);
			cd.vetXP.Add(0f);
			cd.vetCrew.Add(-1);
			idx = cd.vetNames.Count - 1;
		}
		return idx;
	}

	public static float GetXP(string name)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return 0f;
		}
		return CampaignManager.instance.campaignData.vetXP[idx];
	}

	public static void SetXP(int idx, float xp)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (xp < 0f)
		{
			xp = 0f;
		}
		cd.vetXP[idx] = xp;
		cd.vetBattles[idx] = Mathf.FloorToInt(xp + 0.001f);
	}

	public static float RankFloor(float xp)
	{
		int b = Mathf.FloorToInt(xp + 0.001f);
		if (b >= 9)
		{
			return 9f;
		}
		if (b >= 5)
		{
			return 5f;
		}
		if (b >= 2)
		{
			return 2f;
		}
		return 0f;
	}

	public static float PreviousRankFloor(float floor)
	{
		if (floor >= 9f)
		{
			return 5f;
		}
		if (floor >= 5f)
		{
			return 2f;
		}
		return 0f;
	}

	public static string RankName(float xp)
	{
		return MobileMapObject.GetVeteranRank(Mathf.FloorToInt(xp + 0.001f));
	}

	public static int FullCrew(string prefab)
	{
		try
		{
			if (EngagementManager.instance != null && EngagementManager.instance.unitDataDictionary.ContainsKey(prefab))
			{
				return EngagementManager.instance.unitDataDictionary[prefab].crew;
			}
		}
		catch
		{
		}
		return 0;
	}

	public static int GetCrew(string name, int full)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return full;
		}
		int crew = CampaignManager.instance.campaignData.vetCrew[idx];
		if (crew < 0 || crew > full)
		{
			return full;
		}
		return crew;
	}

	// Losing a share of the crew takes the same share of the progress towards the next rank. Never drops a rank.
	public static void LoseProgress(int idx, float share)
	{
		float xp = CampaignManager.instance.campaignData.vetXP[idx];
		float floor = ModCrew.RankFloor(xp);
		ModCrew.SetXP(idx, floor + (xp - floor) * (1f - Mathf.Clamp01(share)));
	}

	// ---------------- battle ----------------

	public static void OnBattleStart()
	{
		try
		{
			if (EngagementData.instance == null || !EngagementData.instance.isCampaignEngagement || EngagementManager.instance == null)
			{
				return;
			}
			Dictionary<int, ModCrew.Entry> fresh = new Dictionary<int, ModCrew.Entry>();
			List<Unit> units = new List<Unit>();
			units.AddRange(EngagementManager.instance.playerUnits);
			units.AddRange(EngagementManager.instance.otherUnits);
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u == null || u.unitSea == null || u.damageableSea == null || u.unitData == null || u.unitData.crew <= 0)
				{
					continue;
				}
				int id = u.damageableSea.GetInstanceID();
				if (fresh.ContainsKey(id))
				{
					continue;
				}
				if (ModCrew.battle.ContainsKey(id))
				{
					fresh[id] = ModCrew.battle[id];
					continue;
				}
				ModCrew.Entry e = new ModCrew.Entry();
				e.name = u.unitInstanceName;
				e.faction = (int)u.faction;
				e.full = u.unitData.crew;
				if (e.faction == 0)
				{
					e.start = ModCrew.GetCrew(e.name, e.full);
				}
				else
				{
					e.start = e.full;
				}
				e.lost = 0f;
				e.cells = Mathf.Max(1, u.damageableSea.cellVariables.Count);
				e.applied = false;
				fresh[id] = e;
				if (e.faction == 0)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " enters battle with " + e.start.ToString("#,##0") + " / " + e.full.ToString("#,##0") + " men, " + ModCrew.RankName(ModCrew.GetXP(e.name)) + " (" + ModCrew.GetXP(e.name).ToString("F2") + ")");
				}
				else
				{
					UnityEngine.Debug.Log("[CREW] enemy " + e.name + " enters battle with " + e.start.ToString("#,##0") + " men");
				}
			}
			ModCrew.battle = fresh;
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u != null && u.unitSea != null && u.damageableSea != null)
				{
					Utilities.SetSeaEfficiency(u);
					int parties = ModCrew.Parties(u);
					if (u.unitData != null && parties < u.unitData.damageParties)
					{
						UnityEngine.Debug.Log("[CREW] " + u.unitInstanceName + " is short-handed: " + parties + " of " + u.unitData.damageParties + " damage control parties, efficiency -" + (ModCrew.EfficiencyPenalty(u) * 100f).ToString("F0") + "%");
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] battle start failed: " + ex.ToString());
		}
	}

	// Share of the full crew still aboard (1 when the ship is not tracked)
	public static float CrewShare(Unit u)
	{
		if (u == null || u.damageableSea == null)
		{
			return 1f;
		}
		ModCrew.Entry e;
		if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.full <= 0)
		{
			return 1f;
		}
		return Mathf.Clamp01(((float)e.start - e.lost) / (float)e.full);
	}

	public static float EfficiencyPenalty(Unit u)
	{
		float share = ModCrew.CrewShare(u);
		if (share >= ModCrew.ShortCrewStart)
		{
			return 0f;
		}
		return (ModCrew.ShortCrewStart - share) * ModCrew.ShortCrewFactor;
	}

	public static int Parties(Unit u)
	{
		if (u == null || u.unitData == null)
		{
			return 0;
		}
		int full = u.unitData.damageParties;
		if (full <= 1)
		{
			return full;
		}
		float share = ModCrew.CrewShare(u);
		int parties = full;
		if (share < 0.999f)
		{
			parties = Mathf.Clamp(Mathf.RoundToInt((float)full * share), 1, full);
		}
		try
		{
			ModCrew.Entry e;
			if (u.damageableSea != null && ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e))
			{
				if (e.lastParties != -1 && e.lastParties != parties)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " now has " + parties + " of " + full + " damage control parties (" + (share * 100f).ToString("F0") + "% crew)");
				}
				e.lastParties = parties;
			}
		}
		catch
		{
		}
		return parties;
	}

	public static float CellFactor(CellVariable cv)
	{
		if (cv == null || cv.parentCell == null)
		{
			return 1f;
		}
		switch (cv.parentCell.cellType)
		{
		case CellType.Magazine:
			return 4f;
		case CellType.Bridge:
		case CellType.ControlRoom:
		case CellType.Conning:
			return 2.5f;
		case CellType.Engineering:
		case CellType.ElectricEngine:
		case CellType.Primary:
		case CellType.Secondary:
			return 2f;
		case CellType.Aircraft:
		case CellType.Torpedo:
		case CellType.Torpedo_Room:
			return 1.5f;
		case CellType.Propeller:
		case CellType.DoublePropeller:
		case CellType.Rudder:
		case CellType.PropellersRudder:
		case CellType.Funnel:
		case CellType.Director:
			return 0.5f;
		}
		return 1f;
	}

	public static void AddLoss(DamageableSea ds, CellVariable cv, float share, string what)
	{
		try
		{
			if (ds == null || ModCrew.battle.Count == 0)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.applied)
			{
				return;
			}
			float men = (float)e.start / (float)e.cells * share * ModCrew.CellFactor(cv);
			float maxLoss = (float)e.start - (float)e.full * ModCrew.MinCrew;
			if (maxLoss <= 0f)
			{
				return;
			}
			if (e.lost + men > maxLoss)
			{
				men = maxLoss - e.lost;
			}
			if (men <= 0f)
			{
				return;
			}
			e.lost += men;
			string cellName = (cv != null && cv.parentCell != null) ? (cv.parentCell.cellType.ToString() + " " + cv.parentCell.cellID) : "?";
			UnityEngine.Debug.Log("[CREW] " + e.name + ": " + cellName + " " + what + ", " + men.ToString("F1") + " men lost (battle total " + Mathf.RoundToInt(e.lost) + " of " + e.start + ")");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] loss failed: " + ex.Message);
		}
	}

	public static void OnCellDestroyed(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.DestroyShare, "destroyed");
	}

	public static void OnFire(DamageableSea ds, CellVariable cv, bool isOn)
	{
		if (!isOn || cv == null || cv.isBurning || cv.isDestroyed || cv.parentCell == null || !cv.parentCell.canBurn)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FireShare, "on fire");
	}

	public static void OnFlood(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isFlooded > 0f || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FloodShare, "flooding");
	}

	// ---------------- after battle ----------------

	public static void ApplyBattleLosses(MobileMapObject mmo)
	{
		try
		{
			if (mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
				{
					continue;
				}
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				ModCrew.Entry e = null;
				foreach (ModCrew.Entry candidate in ModCrew.battle.Values)
				{
					if (!candidate.applied && candidate.faction == 0 && candidate.name == shipName)
					{
						e = candidate;
						break;
					}
				}
				if (e == null)
				{
					continue;
				}
				e.applied = true;
				int lostMen = Mathf.RoundToInt(e.lost);
				if (lostMen <= 0)
				{
					continue;
				}
				int idx = ModCrew.Index(shipName, true);
				int crewNow = Mathf.Max(0, e.start - lostMen);
				cd.vetCrew[idx] = crewNow;
				float xpBefore = cd.vetXP[idx];
				ModCrew.LoseProgress(idx, (float)lostMen / (float)e.full);
				UnityEngine.Debug.Log("[CREW] " + shipName + " lost " + lostMen + " men in the battle: crew " + crewNow.ToString("#,##0") + " / " + e.full.ToString("#,##0") + ", experience " + xpBefore.ToString("F2") + " -> " + cd.vetXP[idx].ToString("F2"));
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] applying losses failed: " + ex.ToString());
		}
	}

	// ---------------- port ----------------

	public static void PortTopUp(MobileMapObject mmo)
	{
		try
		{
			if (mmo == null || mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0)
				{
					continue;
				}
				int missing = full - cd.vetCrew[idx];
				cd.vetCrew[idx] = -1;
				if (missing <= 0)
				{
					continue;
				}
				if ((float)missing <= (float)full * ModCrew.FreeTopUp)
				{
					UnityEngine.Debug.Log("[CREW] " + shipName + " topped up " + missing + " men in port (wounded back on duty, no experience lost)");
					continue;
				}
				float xp = cd.vetXP[idx];
				float floor = ModCrew.RankFloor(xp);
				float newXP;
				if (xp - floor > 0.01f)
				{
					newXP = floor;
				}
				else
				{
					newXP = ModCrew.PreviousRankFloor(floor);
				}
				ModCrew.SetXP(idx, newXP);
				UnityEngine.Debug.Log("[CREW] " + shipName + " took on " + missing + " new recruits in port: experience " + xp.ToString("F2") + " -> " + newXP.ToString("F2") + " (" + ModCrew.RankName(xp) + " -> " + ModCrew.RankName(newXP) + ")");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] port top-up failed: " + ex.ToString());
		}
	}
}
```
3. Click **Compile**, then **File > Save Module**.
4. **Close dnSpy, reopen it and reopen the DLL.**

### Step 2 - Utilities.SetSeaEfficiency
1. In class **Utilities**, right-click method **SetSeaEfficiency** > **Edit Method (C#)...**
2. Select all of it and replace it with:
```csharp
public static void SetSeaEfficiency(Unit unit)
{
	float vetBonus = 0f;
	if (unit.faction == Faction.Player && unit.unitInstanceName != null)
	{
		try
		{
			if (EngagementData.instance != null && EngagementData.instance.isCampaignEngagement && CampaignManager.instance != null && CampaignManager.instance.campaignData != null)
			{
				vetBonus = MobileMapObject.GetVeteranBonus(unit.unitInstanceName);
			}
		}
		catch
		{
		}
	}
	float crewPenalty = 0f;
	try
	{
		crewPenalty = ModCrew.EfficiencyPenalty(unit);
	}
	catch
	{
	}
	float num = 1f * Utilities.GetDifficultyModifier(Difficulty.Efficiency, unit.faction) + vetBonus - crewPenalty;
	num -= (float)(unit.damageableSea.cellsOffline.Count + unit.damageableSea.cellsBurning.Count + unit.damageableSea.cellsFlooded.Count) * Config.instance.effLossPerOffBurnFlood;
	if (Utilities.IsCommandOffline(unit))
	{
		num -= Config.instance.effLossNoCommand;
	}
	num = Mathf.Clamp(num, Config.instance.minEfficiency, 1f + vetBonus);
	unit.efficiency = num;
	unit.twoMinusEfficiency = 2f - num;
}
```
3. Click **Compile**.

### Steps 3-5 - use the crew-based party count
In each method below, find the text on the left (Ctrl+F) and type the text on the right over it. Then click **Compile**.

| Step | Class | Method | Find | Replace with | How many |
|---|---|---|---|---|---|
| 3 | DamageControlInterface | **SelectCell** | `this.currentUnit.unitData.damageParties` | `ModCrew.Parties(this.currentUnit)` | 1 |
| 4 | DamageControlInterface | **UpdateDamageControlPartiesLeft** | `this.currentUnit.unitData.damageParties` | `ModCrew.Parties(this.currentUnit)` | 2 |
| 5 | DamageableSea | **CheckAutoDamageControl** | `this.parentUnit.unitData.damageParties` | `ModCrew.Parties(this.parentUnit)` | 1 |

Then **File > Save Module**. If dnSpy writes the text slightly differently (for example without `this.`), replace whatever ends in `.unitData.damageParties` the same way. If you get red errors, send me a screenshot.

**Testing**
1. Take a ship that lost men in an earlier battle (orange or red **Men** on the hover panel) into a battle. The log should show `[CREW] <ship> is short-handed: ...`. Its damage-control screen should show fewer parties and a lower efficiency.
2. In a heavy fight, watch for `[CREW] <ship> now has N of M damage control parties` as it takes damage.

**Tuning:** `ShortCrewStart` (0.9) is where the penalty begins, and `ShortCrewFactor` (0.75) is how hard it bites.


---

## v0.18.3 - Rescue survivors in battle

**What changes**
- **Survivors in the water:** when a ship sinks, some of the men still aboard get off alive: 60% normally, 25% if its magazine blew up, 90% if it was scuttled. They wait where the ship went down, which the tactical map already marks with the sunk-ship icon. The message log says `Survivors of <ship> in the water, about N men`. This works for enemy ships too.
- **Picking them up:** any of your ships within 300 m of the spot, going 5 knots or slower, takes aboard 4 men a second. The log says `<ship> is picking up survivors of <sunk ship>`, then `All survivors of ... picked up` when they're all aboard.
  - **Your own survivors** refill the rescuing ship's crew first, with no loss of experience. Once its crew is full, it can carry spare men up to 25% of its crew size. After the battle, those spare men join other ships in the same task force that are short of men.
  - **Enemy survivors** become prisoners, up to the same 25% space. After the battle, each 10 prisoners give 1 command point.
- **Time matters:** survivors in the water die off at about 3% a minute, and anyone not picked up when the battle ends is lost.
- **Live effects:** rescued men count straight away, so a short-handed rescuer gets its efficiency and damage control parties back during the battle.
- **Experience:** losses still cost progress (v0.18.1), but men taken back aboard from the water don't dilute it.
- **Log lines** (`[RESCUE]`): survivors in the water, pickups, men left behind, spare men joining other ships, and prisoners and command points.

**Install (dnSpy).** Back up the DLL first, then do the steps in order.

### Step 1 - ModCrew (replace the class)
1. Right-click class **ModCrew** > **Edit Class (C#)...**
2. Select everything and paste this over it:
```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModCrew
{
	public class Entry
	{
		public string name;
		public int full;
		public int start;
		public float lost;
		public int cells;
		public bool applied;
		public int faction;
		public int lastParties = -1;
		public float rescued;
		public float passengers;
		public float prisoners;
		public bool sunk;
		public bool magazine;
	}

	public class Group
	{
		public string name;
		public int faction;
		public float men;
		public float rescuedTotal;
		public Transform anchor;
		public bool announced;
	}

	// Share of one compartment's worth of crew lost when that compartment is destroyed / catches fire / starts flooding
	public const float DestroyShare = 0.5f;
	public const float FireShare = 0.15f;
	public const float FloodShare = 0.1f;
	// A ship afloat never drops below this share of its full crew
	public const float MinCrew = 0.15f;
	// Port top-ups this small (wounded returning to duty) cost no experience
	public const float FreeTopUp = 0.03f;
	// Below this share of the crew, reloads and repairs slow down
	public const float ShortCrewStart = 0.9f;
	// Efficiency lost per share of crew below ShortCrewStart (0.75 = -30% efficiency at half crew)
	public const float ShortCrewFactor = 0.75f;

	// Rescue (v0.18.3)
	// Share of the men still aboard who get off a sinking ship alive
	public const float SurviveSinking = 0.6f;
	public const float SurviveMagazine = 0.25f;
	public const float SurviveScuttle = 0.9f;
	// Rescue range (300 m, in 10 m battle units) and the speed a rescuer must be below
	public const float RescueRange = 300f * 0.1f;
	public const float RescueKnots = 5f;
	// Men a rescuing ship takes aboard per second of battle time
	public const float PickupPerSecond = 4f;
	// Share of the survivors in the water lost per second (0.0005 = about 3% a minute)
	public const float DrownPerSecond = 0.0005f;
	// Extra men (spare survivors and prisoners) a ship can carry, as a share of its full crew
	public const float PassengerSpace = 0.25f;
	// Command points per prisoner (0.1 = 1 point per 10 prisoners)
	public const float PrisonerPoints = 0.1f;

	public static Dictionary<int, ModCrew.Entry> battle = new Dictionary<int, ModCrew.Entry>();
	public static List<ModCrew.Group> groups = new List<ModCrew.Group>();
	public static bool groupsReported;

	// ---------------- campaign data ----------------

	public static int Index(string name, bool create)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.vetNames == null)
		{
			cd.vetNames = new List<string>();
		}
		if (cd.vetBattles == null)
		{
			cd.vetBattles = new List<int>();
		}
		if (cd.vetXP == null)
		{
			cd.vetXP = new List<float>();
		}
		if (cd.vetCrew == null)
		{
			cd.vetCrew = new List<int>();
		}
		while (cd.vetBattles.Count < cd.vetNames.Count)
		{
			cd.vetBattles.Add(0);
		}
		while (cd.vetXP.Count < cd.vetNames.Count)
		{
			cd.vetXP.Add((float)cd.vetBattles[cd.vetXP.Count]);
		}
		while (cd.vetCrew.Count < cd.vetNames.Count)
		{
			cd.vetCrew.Add(-1);
		}
		int idx = cd.vetNames.IndexOf(name);
		if (idx == -1 && create)
		{
			cd.vetNames.Add(name);
			cd.vetBattles.Add(0);
			cd.vetXP.Add(0f);
			cd.vetCrew.Add(-1);
			idx = cd.vetNames.Count - 1;
		}
		return idx;
	}

	public static float GetXP(string name)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return 0f;
		}
		return CampaignManager.instance.campaignData.vetXP[idx];
	}

	public static void SetXP(int idx, float xp)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (xp < 0f)
		{
			xp = 0f;
		}
		cd.vetXP[idx] = xp;
		cd.vetBattles[idx] = Mathf.FloorToInt(xp + 0.001f);
	}

	public static float RankFloor(float xp)
	{
		int b = Mathf.FloorToInt(xp + 0.001f);
		if (b >= 9)
		{
			return 9f;
		}
		if (b >= 5)
		{
			return 5f;
		}
		if (b >= 2)
		{
			return 2f;
		}
		return 0f;
	}

	public static float PreviousRankFloor(float floor)
	{
		if (floor >= 9f)
		{
			return 5f;
		}
		if (floor >= 5f)
		{
			return 2f;
		}
		return 0f;
	}

	public static string RankName(float xp)
	{
		return MobileMapObject.GetVeteranRank(Mathf.FloorToInt(xp + 0.001f));
	}

	public static int FullCrew(string prefab)
	{
		try
		{
			if (EngagementManager.instance != null && EngagementManager.instance.unitDataDictionary.ContainsKey(prefab))
			{
				return EngagementManager.instance.unitDataDictionary[prefab].crew;
			}
		}
		catch
		{
		}
		return 0;
	}

	public static int GetCrew(string name, int full)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return full;
		}
		int crew = CampaignManager.instance.campaignData.vetCrew[idx];
		if (crew < 0 || crew > full)
		{
			return full;
		}
		return crew;
	}

	// Losing a share of the crew takes the same share of the progress towards the next rank. Never drops a rank.
	public static void LoseProgress(int idx, float share)
	{
		float xp = CampaignManager.instance.campaignData.vetXP[idx];
		float floor = ModCrew.RankFloor(xp);
		ModCrew.SetXP(idx, floor + (xp - floor) * (1f - Mathf.Clamp01(share)));
	}

	// ---------------- battle ----------------

	public static void OnBattleStart()
	{
		try
		{
			if (EngagementData.instance == null || !EngagementData.instance.isCampaignEngagement || EngagementManager.instance == null)
			{
				return;
			}
			Dictionary<int, ModCrew.Entry> fresh = new Dictionary<int, ModCrew.Entry>();
			bool carried = false;
			List<Unit> units = new List<Unit>();
			units.AddRange(EngagementManager.instance.playerUnits);
			units.AddRange(EngagementManager.instance.otherUnits);
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u == null || u.unitSea == null || u.damageableSea == null || u.unitData == null || u.unitData.crew <= 0)
				{
					continue;
				}
				int id = u.damageableSea.GetInstanceID();
				if (fresh.ContainsKey(id))
				{
					continue;
				}
				if (ModCrew.battle.ContainsKey(id))
				{
					fresh[id] = ModCrew.battle[id];
					carried = true;
					continue;
				}
				ModCrew.Entry e = new ModCrew.Entry();
				e.name = u.unitInstanceName;
				e.faction = (int)u.faction;
				e.full = u.unitData.crew;
				if (e.faction == 0)
				{
					e.start = ModCrew.GetCrew(e.name, e.full);
				}
				else
				{
					e.start = e.full;
				}
				e.lost = 0f;
				e.cells = Mathf.Max(1, u.damageableSea.cellVariables.Count);
				e.applied = false;
				fresh[id] = e;
				if (e.faction == 0)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " enters battle with " + e.start.ToString("#,##0") + " / " + e.full.ToString("#,##0") + " men, " + ModCrew.RankName(ModCrew.GetXP(e.name)) + " (" + ModCrew.GetXP(e.name).ToString("F2") + ")");
				}
				else
				{
					UnityEngine.Debug.Log("[CREW] enemy " + e.name + " enters battle with " + e.start.ToString("#,##0") + " men");
				}
			}
			ModCrew.battle = fresh;
			if (!carried)
			{
				// a new battle: clear any survivors left from the last one
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].anchor != null)
					{
						UnityEngine.Object.Destroy(ModCrew.groups[g].anchor.gameObject);
					}
				}
				ModCrew.groups.Clear();
				ModCrew.groupsReported = false;
			}
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u != null && u.unitSea != null && u.damageableSea != null)
				{
					Utilities.SetSeaEfficiency(u);
					int parties = ModCrew.Parties(u);
					if (u.unitData != null && parties < u.unitData.damageParties)
					{
						UnityEngine.Debug.Log("[CREW] " + u.unitInstanceName + " is short-handed: " + parties + " of " + u.unitData.damageParties + " damage control parties, efficiency -" + (ModCrew.EfficiencyPenalty(u) * 100f).ToString("F0") + "%");
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] battle start failed: " + ex.ToString());
		}
	}

	// Share of the full crew still aboard (1 when the ship is not tracked)
	public static float CrewShare(Unit u)
	{
		if (u == null || u.damageableSea == null)
		{
			return 1f;
		}
		ModCrew.Entry e;
		if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.full <= 0)
		{
			return 1f;
		}
		return Mathf.Clamp01(ModCrew.CrewAboard(e) / (float)e.full);
	}

	// Men in the crew right now (not counting spare survivors or prisoners)
	public static float CrewAboard(ModCrew.Entry e)
	{
		return Mathf.Min((float)e.full, (float)e.start - e.lost + e.rescued);
	}

	public static float EfficiencyPenalty(Unit u)
	{
		float share = ModCrew.CrewShare(u);
		if (share >= ModCrew.ShortCrewStart)
		{
			return 0f;
		}
		return (ModCrew.ShortCrewStart - share) * ModCrew.ShortCrewFactor;
	}

	public static int Parties(Unit u)
	{
		if (u == null || u.unitData == null)
		{
			return 0;
		}
		int full = u.unitData.damageParties;
		if (full <= 1)
		{
			return full;
		}
		float share = ModCrew.CrewShare(u);
		int parties = full;
		if (share < 0.999f)
		{
			parties = Mathf.Clamp(Mathf.RoundToInt((float)full * share), 1, full);
		}
		try
		{
			ModCrew.Entry e;
			if (u.damageableSea != null && ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e))
			{
				if (e.lastParties != -1 && e.lastParties != parties)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " now has " + parties + " of " + full + " damage control parties (" + (share * 100f).ToString("F0") + "% crew)");
				}
				e.lastParties = parties;
			}
		}
		catch
		{
		}
		return parties;
	}

	public static float CellFactor(CellVariable cv)
	{
		if (cv == null || cv.parentCell == null)
		{
			return 1f;
		}
		switch (cv.parentCell.cellType)
		{
		case CellType.Magazine:
			return 4f;
		case CellType.Bridge:
		case CellType.ControlRoom:
		case CellType.Conning:
			return 2.5f;
		case CellType.Engineering:
		case CellType.ElectricEngine:
		case CellType.Primary:
		case CellType.Secondary:
			return 2f;
		case CellType.Aircraft:
		case CellType.Torpedo:
		case CellType.Torpedo_Room:
			return 1.5f;
		case CellType.Propeller:
		case CellType.DoublePropeller:
		case CellType.Rudder:
		case CellType.PropellersRudder:
		case CellType.Funnel:
		case CellType.Director:
			return 0.5f;
		}
		return 1f;
	}

	public static void AddLoss(DamageableSea ds, CellVariable cv, float share, string what)
	{
		try
		{
			if (ds == null || ModCrew.battle.Count == 0)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.applied || e.sunk)
			{
				return;
			}
			if (share >= ModCrew.DestroyShare && cv != null && cv.parentCell != null && cv.parentCell.cellType == CellType.Magazine)
			{
				e.magazine = true;
			}
			float men = (float)e.start / (float)e.cells * share * ModCrew.CellFactor(cv);
			float maxLoss = ModCrew.CrewAboard(e) - (float)e.full * ModCrew.MinCrew;
			if (maxLoss <= 0f)
			{
				return;
			}
			if (men > maxLoss)
			{
				men = maxLoss;
			}
			if (men <= 0f)
			{
				return;
			}
			e.lost += men;
			string cellName = (cv != null && cv.parentCell != null) ? (cv.parentCell.cellType.ToString() + " " + cv.parentCell.cellID) : "?";
			UnityEngine.Debug.Log("[CREW] " + e.name + ": " + cellName + " " + what + ", " + men.ToString("F1") + " men lost (battle total " + Mathf.RoundToInt(e.lost) + ", " + Mathf.RoundToInt(ModCrew.CrewAboard(e)) + " / " + e.full + " aboard)");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] loss failed: " + ex.Message);
		}
	}

	public static void OnCellDestroyed(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.DestroyShare, "destroyed");
	}

	public static void OnFire(DamageableSea ds, CellVariable cv, bool isOn)
	{
		if (!isOn || cv == null || cv.isBurning || cv.isDestroyed || cv.parentCell == null || !cv.parentCell.canBurn)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FireShare, "on fire");
	}

	public static void OnFlood(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isFlooded > 0f || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FloodShare, "flooding");
	}

	// ---------------- survivors (v0.18.3) ----------------

	public static void OnShipSunk(DamageableSea ds)
	{
		try
		{
			if (ds == null || ds.parentUnit == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.sunk)
			{
				return;
			}
			e.sunk = true;
			float aboard = ModCrew.CrewAboard(e) + e.passengers;
			float rate = ModCrew.SurviveSinking;
			string how = "sank";
			if (ds.scuttled)
			{
				rate = ModCrew.SurviveScuttle;
				how = "was scuttled";
			}
			else if (e.magazine)
			{
				rate = ModCrew.SurviveMagazine;
				how = "blew up";
			}
			float men = aboard * rate;
			if (e.prisoners > 0f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(e.prisoners) + " prisoners aboard " + e.name + " were lost with her");
			}
			if (men < 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + e.name + " " + how + " with no survivors");
				return;
			}
			ModCrew.Group g = new ModCrew.Group();
			g.name = e.name;
			g.faction = e.faction;
			g.men = men;
			GameObject marker = new GameObject("ModSurvivors_" + e.name);
			Transform parent = ds.transform.parent;
			if (parent == null && FloatingOrigin.instance != null && FloatingOrigin.instance.transformsToMove != null && FloatingOrigin.instance.transformsToMove.Length > 0)
			{
				parent = FloatingOrigin.instance.transformsToMove[0];
			}
			if (parent != null)
			{
				marker.transform.SetParent(parent, true);
			}
			Vector3 pos = ds.transform.position;
			pos.y = 0f;
			marker.transform.position = pos;
			g.anchor = marker.transform;
			ModCrew.groups.Add(g);
			string side = (e.faction == 0) ? string.Empty : "enemy ";
			UnityEngine.Debug.Log("[RESCUE] " + side + e.name + " " + how + ": " + Mathf.RoundToInt(men) + " of " + Mathf.RoundToInt(aboard) + " men aboard are in the water");
			ModCrew.SendLog("ModSurvivors", "Survivors of " + side + e.name + " in the water, about " + Mathf.RoundToInt(men) + " men");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] sinking failed: " + ex.ToString());
		}
	}

	public static void SendLog(string key, string text)
	{
		try
		{
			if (MessageLog.instance != null)
			{
				// orange for survivors in the water, green for rescues
				string colour = (key == "ModSurvivors") ? "#ffa040" : "#70e070";
				MessageLog.instance.SendMessageToLog(key, "<color=" + colour + ">" + text + "</color>", LogMessageType.DamageControl, true, null, null, false);
			}
		}
		catch
		{
		}
	}

	// Called about once a second by ModRescue with the battle time that has passed
	public static void RescueTick(float dt)
	{
		if (ModCrew.groups.Count == 0 || EngagementManager.instance == null || EngagementManager.instance.playerUnits == null)
		{
			return;
		}
		List<Unit> players = EngagementManager.instance.playerUnits;
		for (int g = 0; g < ModCrew.groups.Count; g++)
		{
			ModCrew.Group grp = ModCrew.groups[g];
			if (grp.men < 1f || grp.anchor == null)
			{
				continue;
			}
			grp.men -= grp.men * ModCrew.DrownPerSecond * dt;
			for (int i = 0; i < players.Count && grp.men >= 1f; i++)
			{
				Unit u = players[i];
				if (u == null || u.isDestroyed || u.unitSea == null || u.damageableSea == null)
				{
					continue;
				}
				ModCrew.Entry e;
				if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.sunk || e.applied)
				{
					continue;
				}
				if (Vector3.Distance(u.transform.position, grp.anchor.position) > ModCrew.RescueRange)
				{
					continue;
				}
				if (Utilities.ConvertMetrePerSecondToKnots(u.currentSpeed) > ModCrew.RescueKnots)
				{
					continue;
				}
				float take = Mathf.Min(grp.men, ModCrew.PickupPerSecond * dt);
				float spare = (float)e.full * ModCrew.PassengerSpace - e.passengers - e.prisoners;
				float taken = 0f;
				if (grp.faction == 0)
				{
					float room = (float)e.full - ModCrew.CrewAboard(e);
					float toCrew = Mathf.Clamp(take, 0f, Mathf.Max(0f, room));
					float toSpare = Mathf.Clamp(take - toCrew, 0f, Mathf.Max(0f, spare));
					e.rescued += toCrew;
					e.passengers += toSpare;
					taken = toCrew + toSpare;
				}
				else
				{
					float toHold = Mathf.Clamp(take, 0f, Mathf.Max(0f, spare));
					e.prisoners += toHold;
					taken = toHold;
				}
				if (taken <= 0f)
				{
					continue;
				}
				grp.men -= taken;
				grp.rescuedTotal += taken;
				if (!grp.announced)
				{
					grp.announced = true;
					UnityEngine.Debug.Log("[RESCUE] " + e.name + " is picking up survivors of " + grp.name);
					ModCrew.SendLog("ModRescuing", e.name + " is picking up survivors of " + grp.name);
				}
				if (grp.faction == 0)
				{
					Utilities.SetSeaEfficiency(u);
				}
				if (grp.men < 1f)
				{
					string what = (grp.faction == 0) ? " survivors" : " prisoners";
					UnityEngine.Debug.Log("[RESCUE] all survivors of " + grp.name + " picked up: " + Mathf.RoundToInt(grp.rescuedTotal) + what);
					ModCrew.SendLog("ModRescued", "All survivors of " + grp.name + " picked up, " + Mathf.RoundToInt(grp.rescuedTotal) + what);
				}
			}
		}
	}

	// ---------------- after battle ----------------

	public static void ApplyBattleLosses(MobileMapObject mmo)
	{
		try
		{
			if (mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			if (!ModCrew.groupsReported)
			{
				ModCrew.groupsReported = true;
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].men >= 1f)
					{
						UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(ModCrew.groups[g].men) + " survivors of " + ModCrew.groups[g].name + " were left in the water");
					}
				}
			}
			List<ModCrew.Entry> found = new List<ModCrew.Entry>();
			List<string> names = new List<string>();
			float spareMen = 0f;
			float prisoners = 0f;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
				{
					continue;
				}
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				ModCrew.Entry e = null;
				foreach (ModCrew.Entry candidate in ModCrew.battle.Values)
				{
					if (!candidate.applied && !candidate.sunk && candidate.faction == 0 && candidate.name == shipName)
					{
						e = candidate;
						break;
					}
				}
				if (e == null)
				{
					continue;
				}
				e.applied = true;
				found.Add(e);
				names.Add(shipName);
				spareMen += e.passengers;
				prisoners += e.prisoners;
			}
			// spare survivors go to the ships in this task force that are still short of men
			for (int k = 0; k < found.Count && spareMen >= 1f; k++)
			{
				float room = (float)found[k].full - ModCrew.CrewAboard(found[k]);
				if (room >= 1f)
				{
					float give = Mathf.Min(room, spareMen);
					found[k].rescued += give;
					spareMen -= give;
					UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(give) + " rescued men join the crew of " + found[k].name);
				}
			}
			for (int k = 0; k < found.Count; k++)
			{
				ModCrew.Entry e = found[k];
				int lostMen = Mathf.RoundToInt(e.lost);
				int rescuedMen = Mathf.RoundToInt(e.rescued);
				if (lostMen <= 0 && rescuedMen <= 0)
				{
					continue;
				}
				int idx = ModCrew.Index(names[k], true);
				int crewNow = Mathf.Clamp(Mathf.RoundToInt(ModCrew.CrewAboard(e)), 0, e.full);
				cd.vetCrew[idx] = (crewNow >= e.full) ? -1 : crewNow;
				float xpBefore = cd.vetXP[idx];
				if (lostMen > 0)
				{
					ModCrew.LoseProgress(idx, (float)lostMen / (float)e.full);
				}
				UnityEngine.Debug.Log("[CREW] " + names[k] + " lost " + lostMen + " men and took aboard " + rescuedMen + " survivors: crew " + crewNow.ToString("#,##0") + " / " + e.full.ToString("#,##0") + ", experience " + xpBefore.ToString("F2") + " -> " + cd.vetXP[idx].ToString("F2"));
			}
			if (spareMen >= 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(spareMen) + " rescued men had no place in the task force and were sent home");
			}
			if (prisoners >= 1f)
			{
				int points = Mathf.RoundToInt(prisoners * ModCrew.PrisonerPoints);
				if (points > 0 && cd.commandPoints != null && cd.commandPoints.Length > 0)
				{
					cd.commandPoints[0] += points;
				}
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(prisoners) + " prisoners taken by " + mmo.mobileName + ": +" + points + " command points");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] applying losses failed: " + ex.ToString());
		}
	}

	// ---------------- port ----------------

	public static void PortTopUp(MobileMapObject mmo)
	{
		try
		{
			if (mmo == null || mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0)
				{
					continue;
				}
				int missing = full - cd.vetCrew[idx];
				cd.vetCrew[idx] = -1;
				if (missing <= 0)
				{
					continue;
				}
				if ((float)missing <= (float)full * ModCrew.FreeTopUp)
				{
					UnityEngine.Debug.Log("[CREW] " + shipName + " topped up " + missing + " men in port (wounded back on duty, no experience lost)");
					continue;
				}
				float xp = cd.vetXP[idx];
				float floor = ModCrew.RankFloor(xp);
				float newXP;
				if (xp - floor > 0.01f)
				{
					newXP = floor;
				}
				else
				{
					newXP = ModCrew.PreviousRankFloor(floor);
				}
				ModCrew.SetXP(idx, newXP);
				UnityEngine.Debug.Log("[CREW] " + shipName + " took on " + missing + " new recruits in port: experience " + xp.ToString("F2") + " -> " + newXP.ToString("F2") + " (" + ModCrew.RankName(xp) + " -> " + ModCrew.RankName(newXP) + ")");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] port top-up failed: " + ex.ToString());
		}
	}
}
```
3. Click **Compile**, then **File > Save Module**.
4. **Close dnSpy, reopen it and reopen the DLL.**

### Step 2 - new class ModRescue
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node) > **Add Class (C#)...**
2. Select everything and paste this over it:
```csharp
using UnityEngine;

public class ModRescue : MonoBehaviour
{
	private void Update()
	{
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

	private float timer;
}
```
3. Click **Compile**, then **File > Save Module**.
4. **Close dnSpy, reopen it and reopen the DLL.**

### Step 3 - EngagementManager.StartCombat
1. Right-click method **StartCombat** (class **EngagementManager**) > **Edit Method (C#)...**
2. Find the line `ModCrew.OnBattleStart();` at the top, and add these lines directly under it:
```csharp
if (base.gameObject.GetComponent<ModRescue>() == null)
{
    base.gameObject.AddComponent<ModRescue>();
}
```
3. Click **Compile**.

### Step 4 - DamageableSea.SinkShip
1. Right-click method **SinkShip** (class **DamageableSea**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
ModCrew.OnShipSunk(this);
```
3. Click **Compile**, then **File > Save Module**.

### Step 5 - message file
Open `override/language/english/dictionary/message_log.txt`. Directly under the line `[DAMAGECONTROL]`, add:
```
ModSurvivors=Survivors in the water
ModSurvivors=audio/ui/AlarmLow
ModRescuing=Picking up survivors
ModRescuing=audio/ui/Click2
ModRescued=Survivors picked up
ModRescued=audio/ui/Click2
```
Without these lines the rescue still works, but the messages won't show in the battle log. The game writes a "Not present in MessageLog Dictionary" error to the output log instead.

**Testing**
1. Sink an enemy ship. The message log should say `Survivors of enemy <ship> in the water, about N men`.
2. Sail one of your ships to the sunk icon and slow to 5 knots or less within 300 m. You should see `<ship> is picking up survivors of <ship>`.
3. After the battle, the log should show `[RESCUE] N prisoners taken by <task force>: +X command points`.
4. If one of your ships sinks, pick up its survivors with another short-handed ship. After the battle, its **Men** should go up, and its experience should only drop for the men it lost itself.

**Tuning:** the numbers at the top of ModCrew under "Rescue (v0.18.3)" set survival rates, range, speed, pickup rate, drowning rate, spare space and points per prisoner.

**Message colours:** survivor messages show in orange, and rescue messages in green (`ModCrew.SendLog`).

**Not in this part:** AI ships don't rescue anyone. Survivors left behind at the end of a battle are lost. v0.18.4 adds rescue missions on the campaign map.


---

## v0.18.4 - Rescue missions on the campaign map

**What changes**
- **Survivors left behind in a battle** are no longer lost straight away. They stay where the battle was fought as a marker on the campaign map: **orange** for your own men, **red** for the enemy's. A message says survivors are still in the water.
- **Random events:** every 3 to 7 days (a random time each time), a report comes in that a ship has been sunk somewhere at sea. Half the time it's one of your merchant ships or transports (40-90 survivors, orange marker). The other half it's an enemy transport (60-150 survivors, red marker). The message tells you what happened and what to do.
- **Picking them up:** sail any of your task forces within **12 km** of a marker (the game's own interaction range). There's no need to stop.
  - **Your own men** join the task force's short-handed ships with no loss of experience. Spare men are sent home for 1 command point per 20 men.
  - **Enemy survivors** are taken prisoner, up to 25% of the task force's total crew size, for 1 command point per 10 prisoners.
- **Time limit:** survivors last **24 hours** and lose about 4% an hour. If nobody reaches your own men in time, a message says they are lost.
- Hovering over a marker shows how many men are left and how many hours remain.
- Markers are saved with the campaign. They aren't saved as map notes, and the notes filter doesn't hide them.
- **Wider message box:** the campaign message box now widens to fit long messages (up to 90% of the screen) and shrinks back for short ones. This applies to all campaign messages, the game's own included (`ModCampaignRescue.FitMessagePanel`).
- **Log lines** (`[RESCUE]`): new markers, events, pickups and losses.

**Install (dnSpy).** Back up the DLL first, then do the steps in order.

### Step 1 - save-file field (CampaignData)
1. Right-click class **CampaignData** > **Edit Class (C#)...**
2. Find `public List<int> vetCrew` (or `vetCrew;`) and add this line directly under it:
```csharp
public List<string> modSurvivors = new List<string>();
```
3. If dnSpy shows `base..ctor();` again, delete that line.
4. Click **Compile**, then **File > Save Module**. **Close dnSpy, reopen it and reopen the DLL.**

### Step 2 - ModCrew (replace the class)
1. Right-click class **ModCrew** > **Edit Class (C#)...**
2. Select everything and paste this over it:
```csharp
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using WorldMapStrategyKit;

public class ModCrew
{
	public class Entry
	{
		public string name;
		public int full;
		public int start;
		public float lost;
		public int cells;
		public bool applied;
		public int faction;
		public int lastParties = -1;
		public float rescued;
		public float passengers;
		public float prisoners;
		public bool sunk;
		public bool magazine;
	}

	public class Group
	{
		public string name;
		public int faction;
		public float men;
		public float rescuedTotal;
		public Transform anchor;
		public bool announced;
	}

	// Share of one compartment's worth of crew lost when that compartment is destroyed / catches fire / starts flooding
	public const float DestroyShare = 0.5f;
	public const float FireShare = 0.15f;
	public const float FloodShare = 0.1f;
	// A ship afloat never drops below this share of its full crew
	public const float MinCrew = 0.15f;
	// Port top-ups this small (wounded returning to duty) cost no experience
	public const float FreeTopUp = 0.03f;
	// Below this share of the crew, reloads and repairs slow down
	public const float ShortCrewStart = 0.9f;
	// Efficiency lost per share of crew below ShortCrewStart (0.75 = -30% efficiency at half crew)
	public const float ShortCrewFactor = 0.75f;

	// Rescue (v0.18.3)
	// Share of the men still aboard who get off a sinking ship alive
	public const float SurviveSinking = 0.6f;
	public const float SurviveMagazine = 0.25f;
	public const float SurviveScuttle = 0.9f;
	// Rescue range (300 m, in 10 m battle units) and the speed a rescuer must be below
	public const float RescueRange = 300f * 0.1f;
	public const float RescueKnots = 5f;
	// Men a rescuing ship takes aboard per second of battle time
	public const float PickupPerSecond = 4f;
	// Share of the survivors in the water lost per second (0.0005 = about 3% a minute)
	public const float DrownPerSecond = 0.0005f;
	// Extra men (spare survivors and prisoners) a ship can carry, as a share of its full crew
	public const float PassengerSpace = 0.25f;
	// Command points per prisoner (0.1 = 1 point per 10 prisoners)
	public const float PrisonerPoints = 0.1f;

	// Campaign map survivors (v0.18.4)
	// Hours survivors last on the campaign map, and the share lost each hour (0.04 = 4%)
	public const float MapSurvivorHours = 24f;
	public const float MapDrownPerHour = 0.04f;
	// Days between "ship sunk, survivors reported" events: a random time between these two
	public const float EventMinDays = 3f;
	public const float EventMaxDays = 7f;
	// Hours until the next event (picked at random; -1 = not picked yet)
	public static float hoursToEvent = -1f;
	// Command points per spare rescued man of your own (0.05 = 1 point per 20 men)
	public const float OwnSparePoints = 0.05f;

	public static Dictionary<int, ModCrew.Entry> battle = new Dictionary<int, ModCrew.Entry>();
	public static List<GameObject> mapMarkers = new List<GameObject>();
	public static List<GameObject> mapTexts = new List<GameObject>();
	public static int loggedRecords = -1;
	public static float lastRebuild = -10f;
	public static List<ModCrew.Group> groups = new List<ModCrew.Group>();
	public static bool groupsReported;

	// ---------------- campaign data ----------------

	public static int Index(string name, bool create)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.vetNames == null)
		{
			cd.vetNames = new List<string>();
		}
		if (cd.vetBattles == null)
		{
			cd.vetBattles = new List<int>();
		}
		if (cd.vetXP == null)
		{
			cd.vetXP = new List<float>();
		}
		if (cd.vetCrew == null)
		{
			cd.vetCrew = new List<int>();
		}
		while (cd.vetBattles.Count < cd.vetNames.Count)
		{
			cd.vetBattles.Add(0);
		}
		while (cd.vetXP.Count < cd.vetNames.Count)
		{
			cd.vetXP.Add((float)cd.vetBattles[cd.vetXP.Count]);
		}
		while (cd.vetCrew.Count < cd.vetNames.Count)
		{
			cd.vetCrew.Add(-1);
		}
		int idx = cd.vetNames.IndexOf(name);
		if (idx == -1 && create)
		{
			cd.vetNames.Add(name);
			cd.vetBattles.Add(0);
			cd.vetXP.Add(0f);
			cd.vetCrew.Add(-1);
			idx = cd.vetNames.Count - 1;
		}
		return idx;
	}

	public static float GetXP(string name)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return 0f;
		}
		return CampaignManager.instance.campaignData.vetXP[idx];
	}

	public static void SetXP(int idx, float xp)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (xp < 0f)
		{
			xp = 0f;
		}
		cd.vetXP[idx] = xp;
		cd.vetBattles[idx] = Mathf.FloorToInt(xp + 0.001f);
	}

	public static float RankFloor(float xp)
	{
		int b = Mathf.FloorToInt(xp + 0.001f);
		if (b >= 9)
		{
			return 9f;
		}
		if (b >= 5)
		{
			return 5f;
		}
		if (b >= 2)
		{
			return 2f;
		}
		return 0f;
	}

	public static float PreviousRankFloor(float floor)
	{
		if (floor >= 9f)
		{
			return 5f;
		}
		if (floor >= 5f)
		{
			return 2f;
		}
		return 0f;
	}

	public static string RankName(float xp)
	{
		return MobileMapObject.GetVeteranRank(Mathf.FloorToInt(xp + 0.001f));
	}

	public static int FullCrew(string prefab)
	{
		try
		{
			if (EngagementManager.instance != null && EngagementManager.instance.unitDataDictionary.ContainsKey(prefab))
			{
				return EngagementManager.instance.unitDataDictionary[prefab].crew;
			}
		}
		catch
		{
		}
		return 0;
	}

	public static int GetCrew(string name, int full)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return full;
		}
		int crew = CampaignManager.instance.campaignData.vetCrew[idx];
		if (crew < 0 || crew > full)
		{
			return full;
		}
		return crew;
	}

	// Losing a share of the crew takes the same share of the progress towards the next rank. Never drops a rank.
	public static void LoseProgress(int idx, float share)
	{
		float xp = CampaignManager.instance.campaignData.vetXP[idx];
		float floor = ModCrew.RankFloor(xp);
		ModCrew.SetXP(idx, floor + (xp - floor) * (1f - Mathf.Clamp01(share)));
	}

	// ---------------- battle ----------------

	public static void OnBattleStart()
	{
		try
		{
			if (EngagementData.instance == null || !EngagementData.instance.isCampaignEngagement || EngagementManager.instance == null)
			{
				return;
			}
			Dictionary<int, ModCrew.Entry> fresh = new Dictionary<int, ModCrew.Entry>();
			bool carried = false;
			List<Unit> units = new List<Unit>();
			units.AddRange(EngagementManager.instance.playerUnits);
			units.AddRange(EngagementManager.instance.otherUnits);
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u == null || u.unitSea == null || u.damageableSea == null || u.unitData == null || u.unitData.crew <= 0)
				{
					continue;
				}
				int id = u.damageableSea.GetInstanceID();
				if (fresh.ContainsKey(id))
				{
					continue;
				}
				if (ModCrew.battle.ContainsKey(id))
				{
					fresh[id] = ModCrew.battle[id];
					carried = true;
					continue;
				}
				ModCrew.Entry e = new ModCrew.Entry();
				e.name = u.unitInstanceName;
				e.faction = (int)u.faction;
				e.full = u.unitData.crew;
				if (e.faction == 0)
				{
					e.start = ModCrew.GetCrew(e.name, e.full);
				}
				else
				{
					e.start = e.full;
				}
				e.lost = 0f;
				e.cells = Mathf.Max(1, u.damageableSea.cellVariables.Count);
				e.applied = false;
				fresh[id] = e;
				if (e.faction == 0)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " enters battle with " + e.start.ToString("#,##0") + " / " + e.full.ToString("#,##0") + " men, " + ModCrew.RankName(ModCrew.GetXP(e.name)) + " (" + ModCrew.GetXP(e.name).ToString("F2") + ")");
				}
				else
				{
					UnityEngine.Debug.Log("[CREW] enemy " + e.name + " enters battle with " + e.start.ToString("#,##0") + " men");
				}
			}
			ModCrew.battle = fresh;
			if (!carried)
			{
				// a new battle: clear any survivors left from the last one
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].anchor != null)
					{
						UnityEngine.Object.Destroy(ModCrew.groups[g].anchor.gameObject);
					}
				}
				ModCrew.groups.Clear();
				ModCrew.groupsReported = false;
			}
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u != null && u.unitSea != null && u.damageableSea != null)
				{
					Utilities.SetSeaEfficiency(u);
					int parties = ModCrew.Parties(u);
					if (u.unitData != null && parties < u.unitData.damageParties)
					{
						UnityEngine.Debug.Log("[CREW] " + u.unitInstanceName + " is short-handed: " + parties + " of " + u.unitData.damageParties + " damage control parties, efficiency -" + (ModCrew.EfficiencyPenalty(u) * 100f).ToString("F0") + "%");
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] battle start failed: " + ex.ToString());
		}
	}

	// Share of the full crew still aboard (1 when the ship is not tracked)
	public static float CrewShare(Unit u)
	{
		if (u == null || u.damageableSea == null)
		{
			return 1f;
		}
		ModCrew.Entry e;
		if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.full <= 0)
		{
			return 1f;
		}
		return Mathf.Clamp01(ModCrew.CrewAboard(e) / (float)e.full);
	}

	// Men in the crew right now (not counting spare survivors or prisoners)
	public static float CrewAboard(ModCrew.Entry e)
	{
		return Mathf.Min((float)e.full, (float)e.start - e.lost + e.rescued);
	}

	public static float EfficiencyPenalty(Unit u)
	{
		float share = ModCrew.CrewShare(u);
		if (share >= ModCrew.ShortCrewStart)
		{
			return 0f;
		}
		return (ModCrew.ShortCrewStart - share) * ModCrew.ShortCrewFactor;
	}

	public static int Parties(Unit u)
	{
		if (u == null || u.unitData == null)
		{
			return 0;
		}
		int full = u.unitData.damageParties;
		if (full <= 1)
		{
			return full;
		}
		float share = ModCrew.CrewShare(u);
		int parties = full;
		if (share < 0.999f)
		{
			parties = Mathf.Clamp(Mathf.RoundToInt((float)full * share), 1, full);
		}
		try
		{
			ModCrew.Entry e;
			if (u.damageableSea != null && ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e))
			{
				if (e.lastParties != -1 && e.lastParties != parties)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " now has " + parties + " of " + full + " damage control parties (" + (share * 100f).ToString("F0") + "% crew)");
				}
				e.lastParties = parties;
			}
		}
		catch
		{
		}
		return parties;
	}

	public static float CellFactor(CellVariable cv)
	{
		if (cv == null || cv.parentCell == null)
		{
			return 1f;
		}
		switch (cv.parentCell.cellType)
		{
		case CellType.Magazine:
			return 4f;
		case CellType.Bridge:
		case CellType.ControlRoom:
		case CellType.Conning:
			return 2.5f;
		case CellType.Engineering:
		case CellType.ElectricEngine:
		case CellType.Primary:
		case CellType.Secondary:
			return 2f;
		case CellType.Aircraft:
		case CellType.Torpedo:
		case CellType.Torpedo_Room:
			return 1.5f;
		case CellType.Propeller:
		case CellType.DoublePropeller:
		case CellType.Rudder:
		case CellType.PropellersRudder:
		case CellType.Funnel:
		case CellType.Director:
			return 0.5f;
		}
		return 1f;
	}

	public static void AddLoss(DamageableSea ds, CellVariable cv, float share, string what)
	{
		try
		{
			if (ds == null || ModCrew.battle.Count == 0)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.applied || e.sunk)
			{
				return;
			}
			if (share >= ModCrew.DestroyShare && cv != null && cv.parentCell != null && cv.parentCell.cellType == CellType.Magazine)
			{
				e.magazine = true;
			}
			float men = (float)e.start / (float)e.cells * share * ModCrew.CellFactor(cv);
			float maxLoss = ModCrew.CrewAboard(e) - (float)e.full * ModCrew.MinCrew;
			if (maxLoss <= 0f)
			{
				return;
			}
			if (men > maxLoss)
			{
				men = maxLoss;
			}
			if (men <= 0f)
			{
				return;
			}
			e.lost += men;
			string cellName = (cv != null && cv.parentCell != null) ? (cv.parentCell.cellType.ToString() + " " + cv.parentCell.cellID) : "?";
			UnityEngine.Debug.Log("[CREW] " + e.name + ": " + cellName + " " + what + ", " + men.ToString("F1") + " men lost (battle total " + Mathf.RoundToInt(e.lost) + ", " + Mathf.RoundToInt(ModCrew.CrewAboard(e)) + " / " + e.full + " aboard)");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] loss failed: " + ex.Message);
		}
	}

	public static void OnCellDestroyed(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.DestroyShare, "destroyed");
	}

	public static void OnFire(DamageableSea ds, CellVariable cv, bool isOn)
	{
		if (!isOn || cv == null || cv.isBurning || cv.isDestroyed || cv.parentCell == null || !cv.parentCell.canBurn)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FireShare, "on fire");
	}

	public static void OnFlood(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isFlooded > 0f || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FloodShare, "flooding");
	}

	// ---------------- survivors (v0.18.3) ----------------

	public static void OnShipSunk(DamageableSea ds)
	{
		try
		{
			if (ds == null || ds.parentUnit == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.sunk)
			{
				return;
			}
			e.sunk = true;
			float aboard = ModCrew.CrewAboard(e) + e.passengers;
			float rate = ModCrew.SurviveSinking;
			string how = "sank";
			if (ds.scuttled)
			{
				rate = ModCrew.SurviveScuttle;
				how = "was scuttled";
			}
			else if (e.magazine)
			{
				rate = ModCrew.SurviveMagazine;
				how = "blew up";
			}
			float men = aboard * rate;
			if (e.prisoners > 0f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(e.prisoners) + " prisoners aboard " + e.name + " were lost with her");
			}
			if (men < 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + e.name + " " + how + " with no survivors");
				return;
			}
			ModCrew.Group g = new ModCrew.Group();
			g.name = e.name;
			g.faction = e.faction;
			g.men = men;
			GameObject marker = new GameObject("ModSurvivors_" + e.name);
			Transform parent = ds.transform.parent;
			if (parent == null && FloatingOrigin.instance != null && FloatingOrigin.instance.transformsToMove != null && FloatingOrigin.instance.transformsToMove.Length > 0)
			{
				parent = FloatingOrigin.instance.transformsToMove[0];
			}
			if (parent != null)
			{
				marker.transform.SetParent(parent, true);
			}
			Vector3 pos = ds.transform.position;
			pos.y = 0f;
			marker.transform.position = pos;
			g.anchor = marker.transform;
			ModCrew.groups.Add(g);
			string side = (e.faction == 0) ? string.Empty : "enemy ";
			UnityEngine.Debug.Log("[RESCUE] " + side + e.name + " " + how + ": " + Mathf.RoundToInt(men) + " of " + Mathf.RoundToInt(aboard) + " men aboard are in the water");
			ModCrew.SendLog("ModSurvivors", "Survivors of " + side + e.name + " in the water, about " + Mathf.RoundToInt(men) + " men");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] sinking failed: " + ex.ToString());
		}
	}

	public static void SendLog(string key, string text)
	{
		try
		{
			if (MessageLog.instance != null)
			{
				// orange for survivors in the water, green for rescues
				string colour = (key == "ModSurvivors") ? "#ffa040" : "#70e070";
				MessageLog.instance.SendMessageToLog(key, "<color=" + colour + ">" + text + "</color>", LogMessageType.DamageControl, true, null, null, false);
			}
		}
		catch
		{
		}
	}

	// Called about once a second by ModRescue with the battle time that has passed
	public static void RescueTick(float dt)
	{
		if (ModCrew.groups.Count == 0 || EngagementManager.instance == null || EngagementManager.instance.playerUnits == null)
		{
			return;
		}
		List<Unit> players = EngagementManager.instance.playerUnits;
		for (int g = 0; g < ModCrew.groups.Count; g++)
		{
			ModCrew.Group grp = ModCrew.groups[g];
			if (grp.men < 1f || grp.anchor == null)
			{
				continue;
			}
			grp.men -= grp.men * ModCrew.DrownPerSecond * dt;
			for (int i = 0; i < players.Count && grp.men >= 1f; i++)
			{
				Unit u = players[i];
				if (u == null || u.isDestroyed || u.unitSea == null || u.damageableSea == null)
				{
					continue;
				}
				ModCrew.Entry e;
				if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.sunk || e.applied)
				{
					continue;
				}
				if (Vector3.Distance(u.transform.position, grp.anchor.position) > ModCrew.RescueRange)
				{
					continue;
				}
				if (Utilities.ConvertMetrePerSecondToKnots(u.currentSpeed) > ModCrew.RescueKnots)
				{
					continue;
				}
				float take = Mathf.Min(grp.men, ModCrew.PickupPerSecond * dt);
				float spare = (float)e.full * ModCrew.PassengerSpace - e.passengers - e.prisoners;
				float taken = 0f;
				if (grp.faction == 0)
				{
					float room = (float)e.full - ModCrew.CrewAboard(e);
					float toCrew = Mathf.Clamp(take, 0f, Mathf.Max(0f, room));
					float toSpare = Mathf.Clamp(take - toCrew, 0f, Mathf.Max(0f, spare));
					e.rescued += toCrew;
					e.passengers += toSpare;
					taken = toCrew + toSpare;
				}
				else
				{
					float toHold = Mathf.Clamp(take, 0f, Mathf.Max(0f, spare));
					e.prisoners += toHold;
					taken = toHold;
				}
				if (taken <= 0f)
				{
					continue;
				}
				grp.men -= taken;
				grp.rescuedTotal += taken;
				if (!grp.announced)
				{
					grp.announced = true;
					UnityEngine.Debug.Log("[RESCUE] " + e.name + " is picking up survivors of " + grp.name);
					ModCrew.SendLog("ModRescuing", e.name + " is picking up survivors of " + grp.name);
				}
				if (grp.faction == 0)
				{
					Utilities.SetSeaEfficiency(u);
				}
				if (grp.men < 1f)
				{
					string what = (grp.faction == 0) ? " survivors" : " prisoners";
					UnityEngine.Debug.Log("[RESCUE] all survivors of " + grp.name + " picked up: " + Mathf.RoundToInt(grp.rescuedTotal) + what);
					ModCrew.SendLog("ModRescued", "All survivors of " + grp.name + " picked up, " + Mathf.RoundToInt(grp.rescuedTotal) + what);
				}
			}
		}
	}

	// ---------------- after battle ----------------

	public static void ApplyBattleLosses(MobileMapObject mmo)
	{
		try
		{
			if (mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			if (!ModCrew.groupsReported)
			{
				ModCrew.groupsReported = true;
				string leftBehind = string.Empty;
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].men >= 1f)
					{
						UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(ModCrew.groups[g].men) + " survivors of " + ModCrew.groups[g].name + " were left in the water, now marked on the campaign map");
						Vector2 battlePos = mmo.gameObjectAnimator.currentMap2DLocation;
						Vector2 offset = new Vector2(UnityEngine.Random.Range(-0.002f, 0.002f), UnityEngine.Random.Range(-0.002f, 0.002f));
						ModCrew.AddMapSurvivors(battlePos + offset, ModCrew.groups[g].men, ModCrew.groups[g].faction, ModCrew.groups[g].name, ModCrew.MapSurvivorHours);
						if (leftBehind != string.Empty)
						{
							leftBehind += ", ";
						}
						leftBehind += ModCrew.groups[g].name;
						ModCrew.groups[g].men = 0f;
					}
				}
				if (leftBehind != string.Empty)
				{
					ModCrew.CampaignMessage("SurvivorsReported", "Survivors are still in the water where the battle was fought (" + leftBehind + "). Send a task force there within " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to pick them up.");
				}
			}
			List<ModCrew.Entry> found = new List<ModCrew.Entry>();
			List<string> names = new List<string>();
			float spareMen = 0f;
			float prisoners = 0f;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
				{
					continue;
				}
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				ModCrew.Entry e = null;
				foreach (ModCrew.Entry candidate in ModCrew.battle.Values)
				{
					if (!candidate.applied && !candidate.sunk && candidate.faction == 0 && candidate.name == shipName)
					{
						e = candidate;
						break;
					}
				}
				if (e == null)
				{
					continue;
				}
				e.applied = true;
				found.Add(e);
				names.Add(shipName);
				spareMen += e.passengers;
				prisoners += e.prisoners;
			}
			// spare survivors go to the ships in this task force that are still short of men
			for (int k = 0; k < found.Count && spareMen >= 1f; k++)
			{
				float room = (float)found[k].full - ModCrew.CrewAboard(found[k]);
				if (room >= 1f)
				{
					float give = Mathf.Min(room, spareMen);
					found[k].rescued += give;
					spareMen -= give;
					UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(give) + " rescued men join the crew of " + found[k].name);
				}
			}
			for (int k = 0; k < found.Count; k++)
			{
				ModCrew.Entry e = found[k];
				int lostMen = Mathf.RoundToInt(e.lost);
				int rescuedMen = Mathf.RoundToInt(e.rescued);
				if (lostMen <= 0 && rescuedMen <= 0)
				{
					continue;
				}
				int idx = ModCrew.Index(names[k], true);
				int crewNow = Mathf.Clamp(Mathf.RoundToInt(ModCrew.CrewAboard(e)), 0, e.full);
				cd.vetCrew[idx] = (crewNow >= e.full) ? -1 : crewNow;
				float xpBefore = cd.vetXP[idx];
				if (lostMen > 0)
				{
					ModCrew.LoseProgress(idx, (float)lostMen / (float)e.full);
				}
				UnityEngine.Debug.Log("[CREW] " + names[k] + " lost " + lostMen + " men and took aboard " + rescuedMen + " survivors: crew " + crewNow.ToString("#,##0") + " / " + e.full.ToString("#,##0") + ", experience " + xpBefore.ToString("F2") + " -> " + cd.vetXP[idx].ToString("F2"));
			}
			if (spareMen >= 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(spareMen) + " rescued men had no place in the task force and were sent home");
			}
			if (prisoners >= 1f)
			{
				int points = Mathf.RoundToInt(prisoners * ModCrew.PrisonerPoints);
				if (points > 0 && cd.commandPoints != null && cd.commandPoints.Length > 0)
				{
					cd.commandPoints[0] += points;
				}
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(prisoners) + " prisoners taken by " + mmo.mobileName + ": +" + points + " command points");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] applying losses failed: " + ex.ToString());
		}
	}

	// ---------------- campaign map survivors (v0.18.4) ----------------
	// Each record in CampaignData.modSurvivors is "x|y|men|faction|hoursLeft|name"

	public static List<string> MapRecords()
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.modSurvivors == null)
		{
			cd.modSurvivors = new List<string>();
		}
		return cd.modSurvivors;
	}

	public static string MakeRecord(Vector2 pos, float men, int faction, float hours, string name)
	{
		CultureInfo ci = CultureInfo.InvariantCulture;
		return pos.x.ToString("R", ci) + "|" + pos.y.ToString("R", ci) + "|" + men.ToString("R", ci) + "|" + faction.ToString(ci) + "|" + hours.ToString("R", ci) + "|" + name.Replace("|", "/");
	}

	public static bool ReadRecord(string rec, out Vector2 pos, out float men, out int faction, out float hours, out string name)
	{
		pos = Vector2.zero;
		men = 0f;
		faction = 0;
		hours = 0f;
		name = string.Empty;
		string[] p = rec.Split(new char[] { '|' });
		if (p.Length < 6)
		{
			return false;
		}
		CultureInfo ci = CultureInfo.InvariantCulture;
		pos = new Vector2(float.Parse(p[0], ci), float.Parse(p[1], ci));
		men = float.Parse(p[2], ci);
		faction = int.Parse(p[3], ci);
		hours = float.Parse(p[4], ci);
		name = p[5];
		return true;
	}

	public static void AddMapSurvivors(Vector2 pos, float men, int faction, string name, float hours)
	{
		try
		{
			ModCrew.MapRecords().Add(ModCrew.MakeRecord(pos, men, faction, hours, name));
			ModCrew.RebuildMapMarkers();
			UnityEngine.Debug.Log("[RESCUE] map survivors added: " + Mathf.RoundToInt(men) + " men of " + name + " (side " + faction + "), " + hours.ToString("F0") + " hours");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] adding map survivors failed: " + ex.ToString());
		}
	}

	public static void CampaignMessage(string key, string text)
	{
		try
		{
			ErrorPanel.instance.SetErrorMessage(key, text, string.Empty, string.Empty);
		}
		catch
		{
		}
	}

	public static Sprite survivorIcon;
	public static bool survivorIconTried;

	// interface/images/map/survivors.png in the override folder (white, tinted orange or red)
	public static Sprite SurvivorIcon()
	{
		if (!ModCrew.survivorIconTried)
		{
			ModCrew.survivorIconTried = true;
			try
			{
				ModCrew.survivorIcon = AssetLoader.instance.ImportSprite("interface/images/map/survivors.png", false, false);
			}
			catch (System.Exception ex)
			{
				UnityEngine.Debug.LogError("[RESCUE] could not load survivors.png: " + ex.Message);
			}
			UnityEngine.Debug.Log("[RESCUE] survivor map icon " + ((ModCrew.survivorIcon != null) ? "loaded" : "not found, using the map note icon"));
		}
		return ModCrew.survivorIcon;
	}

	public static void RebuildMapMarkers()
	{
		for (int i = 0; i < ModCrew.mapMarkers.Count; i++)
		{
			if (ModCrew.mapMarkers[i] != null)
			{
				UnityEngine.Object.Destroy(ModCrew.mapMarkers[i]);
			}
		}
		ModCrew.mapMarkers.Clear();
		for (int i = 0; i < ModCrew.mapTexts.Count; i++)
		{
			if (ModCrew.mapTexts[i] != null)
			{
				UnityEngine.Object.Destroy(ModCrew.mapTexts[i]);
			}
		}
		ModCrew.mapTexts.Clear();
		CampaignInterface ui = CampaignInterface.instance;
		if (ui == null || ui.portPrefab == null)
		{
			return;
		}
		List<string> recs = ModCrew.MapRecords();
		if (recs.Count != ModCrew.loggedRecords)
		{
			ModCrew.loggedRecords = recs.Count;
			UnityEngine.Debug.Log("[RESCUE] " + recs.Count + " survivor markers in this campaign");
		}
		for (int i = 0; i < recs.Count; i++)
		{
			GameObject go = null;
			try
			{
				Vector2 pos;
				float men;
				int faction;
				float hours;
				string name;
				if (ModCrew.ReadRecord(recs[i], out pos, out men, out faction, out hours, out name))
				{
					go = UnityEngine.Object.Instantiate<GameObject>(ui.portPrefab);
					MapLocation loc = go.AddComponent<MapLocation>();
					go.name = "ModSurvivors";
					GameObjectAnimator anim = go.WMSK_MoveTo(pos, 0f, (DURATION_TYPE)0, true, 0f);
					anim.transform.localScale = new Vector3(0.4f, 0.4f, 0.4f);
					anim.autoScale = false;
					anim.isStatic = true;
					// type 7 = map note, so hovering shows its text like a note. It is not put with the
					// player's notes (mapMarkerParent), so it is never saved as a note.
					anim.type = 7;
					loc.gameObjectAnimator = anim;
					loc.locationPosition = pos;
					SpriteRenderer icon = go.GetComponentInChildren<SpriteRenderer>();
					if (icon != null)
					{
						Sprite lifebuoy = ModCrew.SurvivorIcon();
						if (lifebuoy != null)
						{
							icon.sprite = lifebuoy;
						}
						else if (ui.mapDrawIcons != null && ui.mapDrawIcons.Length > 0)
						{
							icon.sprite = ui.mapDrawIcons[0];
						}
						icon.color = (faction == 0) ? new Color(1f, 0.6f, 0.2f, 1f) : new Color(1f, 0.25f, 0.25f, 1f);
					}
					if (anim.transform.childCount > 1)
					{
						anim.transform.GetChild(1).gameObject.SetActive(false);
					}
					// the tooltip shows the description, then the name, on separate lines
					loc.locationDescription = (faction == 0) ? "SURVIVORS" : "ENEMY SURVIVORS";
					loc.locationName = "About " + Mathf.RoundToInt(men) + " men of " + name + "\n" + Mathf.CeilToInt(hours) + " hours remaining";
					UnityEngine.Debug.Log("[RESCUE] map marker " + i + " for " + name + " at " + pos.x.ToString("F4") + ", " + pos.y.ToString("F4") + (icon == null ? " (no icon found!)" : string.Empty));
				}
			}
			catch (System.Exception ex)
			{
				UnityEngine.Debug.LogError("[RESCUE] map marker failed: " + ex.Message);
			}
			ModCrew.mapMarkers.Add(go);
		}
	}

	// Called once a campaign hour from CampaignManager.CheckHourly
	public static void CampaignHour()
	{
		try
		{
			if (CampaignManager.instance == null || CampaignManager.instance.campaignData == null)
			{
				return;
			}
			List<string> recs = ModCrew.MapRecords();
			for (int i = recs.Count - 1; i >= 0; i--)
			{
				Vector2 pos;
				float men;
				int faction;
				float hours;
				string name;
				if (!ModCrew.ReadRecord(recs[i], out pos, out men, out faction, out hours, out name))
				{
					recs.RemoveAt(i);
					continue;
				}
				men -= men * ModCrew.MapDrownPerHour;
				hours -= 1f;
				if (hours <= 0f || men < 1f)
				{
					recs.RemoveAt(i);
					UnityEngine.Debug.Log("[RESCUE] survivors of " + name + " (side " + faction + ") were lost before anyone reached them");
					if (faction == 0)
					{
						ModCrew.CampaignMessage("SurvivorsLost", "No one reached the survivors of " + name + " in time. They are lost.");
					}
					continue;
				}
				recs[i] = ModCrew.MakeRecord(pos, men, faction, hours, name);
			}
			if (ModCrew.hoursToEvent < 0f)
			{
				ModCrew.hoursToEvent = UnityEngine.Random.Range(ModCrew.EventMinDays * 24f, ModCrew.EventMaxDays * 24f);
				UnityEngine.Debug.Log("[RESCUE] next survivor event in " + (ModCrew.hoursToEvent / 24f).ToString("F1") + " days");
			}
			ModCrew.hoursToEvent -= 1f;
			if (ModCrew.hoursToEvent <= 0f)
			{
				ModCrew.CreateSurvivorEvent();
				ModCrew.hoursToEvent = -1f;
			}
			ModCrew.RebuildMapMarkers();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] campaign hour failed: " + ex.ToString());
		}
	}

	public static void CreateSurvivorEvent()
	{
		List<SeaNavigationWaypoint> points = CampaignManager.instance.seaNavigationPoints;
		if (points == null || points.Count == 0)
		{
			return;
		}
		Vector3 wp = points[UnityEngine.Random.Range(0, points.Count)].positionRadius;
		Vector2 pos = new Vector2(wp.x, wp.y);
		bool playerIsUS = CampaignManager.instance.campaignData.campaignID != "campaign002";
		int faction = (UnityEngine.Random.value < 0.5f) ? 0 : 1;
		float men;
		string name;
		string text;
		if (faction == 0)
		{
			men = (float)UnityEngine.Random.Range(40, 91);
			name = playerIsUS ? "an American merchant ship" : "a Japanese transport";
			text = "Reports say " + name + " was torpedoed and sunk. About " + Mathf.RoundToInt(men) + " survivors are adrift (orange marker on the map). Send a task force within " + (CampaignManager.instance.campaignData.interactionDistanceMetres / 1000f).ToString("F0") + " km of them in the next " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to pick them up.";
		}
		else
		{
			men = (float)UnityEngine.Random.Range(60, 151);
			name = playerIsUS ? "a Japanese transport" : "an Allied merchant ship";
			text = "Our aircraft report that " + name + " has sunk. About " + Mathf.RoundToInt(men) + " enemy survivors are adrift (red marker on the map). Send a task force within " + (CampaignManager.instance.campaignData.interactionDistanceMetres / 1000f).ToString("F0") + " km of them in the next " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to take them prisoner.";
		}
		ModCrew.MapRecords().Add(ModCrew.MakeRecord(pos, men, faction, ModCrew.MapSurvivorHours, name));
		UnityEngine.Debug.Log("[RESCUE] event: " + name + " sunk at " + pos.x.ToString("F4") + ", " + pos.y.ToString("F4") + ", " + Mathf.RoundToInt(men) + " survivors (side " + faction + ")");
		ModCrew.CampaignMessage("SurvivorsReported", text);
	}

	// Called every frame on the campaign map by ModCampaignRescue
	public static void CampaignRescueCheck()
	{
		CampaignManager cm = CampaignManager.instance;
		if (cm == null || cm.campaignData == null || cm.playerMobile == null)
		{
			return;
		}
		List<string> recs = ModCrew.MapRecords();
		if (recs.Count == 0)
		{
			return;
		}
		bool rebuild = ModCrew.mapMarkers.Count != recs.Count;
		for (int i = 0; i < ModCrew.mapMarkers.Count && !rebuild; i++)
		{
			if (ModCrew.mapMarkers[i] == null)
			{
				// markers are lost when a save is loaded: make them again
				rebuild = true;
				UnityEngine.Debug.Log("[RESCUE] survivor markers were removed (save loaded?), drawing " + recs.Count + " again");
			}
		}
		if (rebuild && Time.unscaledTime - ModCrew.lastRebuild > 2f)
		{
			ModCrew.lastRebuild = Time.unscaledTime;
			ModCrew.RebuildMapMarkers();
		}
		bool changed = false;
		for (int r = recs.Count - 1; r >= 0; r--)
		{
			Vector2 pos;
			float men;
			int faction;
			float hours;
			string name;
			if (!ModCrew.ReadRecord(recs[r], out pos, out men, out faction, out hours, out name))
			{
				continue;
			}
			for (int m = 0; m < cm.playerMobile.Count; m++)
			{
				GameObjectAnimator goa = cm.playerMobile[m];
				if (goa == null || goa.mobileMapObject == null)
				{
					continue;
				}
				MobileMapObject mmo = goa.mobileMapObject;
				if (mmo.type != 0 || mmo.currentFaction != 0 || mmo.unitPrefabs.Count == 0)
				{
					continue;
				}
				if (cm.GetDistanceInMetresBetweenMapObjects(goa.currentMap2DLocation, pos) > cm.campaignData.interactionDistanceMetres)
				{
					continue;
				}
				ModCrew.RescueOnMap(mmo, men, faction, name);
				recs.RemoveAt(r);
				changed = true;
				break;
			}
		}
		if (changed)
		{
			ModCrew.RebuildMapMarkers();
		}
	}

	public static void RescueOnMap(MobileMapObject mmo, float men, int faction, string name)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		int total = Mathf.RoundToInt(men);
		int points = 0;
		string text;
		if (faction == 0)
		{
			float left = men;
			int joined = 0;
			for (int i = 0; i < mmo.unitPrefabs.Count && left >= 1f; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0 || cd.vetCrew[idx] >= full)
				{
					continue;
				}
				int give = Mathf.Min(full - cd.vetCrew[idx], Mathf.FloorToInt(left));
				cd.vetCrew[idx] += give;
				if (cd.vetCrew[idx] >= full)
				{
					cd.vetCrew[idx] = -1;
				}
				left -= (float)give;
				joined += give;
				UnityEngine.Debug.Log("[RESCUE] " + give + " rescued men join the crew of " + shipName);
			}
			points = Mathf.RoundToInt(left * ModCrew.OwnSparePoints);
			text = mmo.mobileName + " picked up " + total + " survivors of " + name + ". " + joined + " joined short-handed crews";
			if (points > 0)
			{
				text += ", the rest were sent home (+" + points + " command points).";
			}
			else
			{
				text += ".";
			}
		}
		else
		{
			float space = 0f;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				space += (float)ModCrew.FullCrew(mmo.unitPrefabs[i]) * ModCrew.PassengerSpace;
			}
			int taken = Mathf.RoundToInt(Mathf.Min(men, space));
			points = Mathf.RoundToInt((float)taken * ModCrew.PrisonerPoints);
			text = mmo.mobileName + " took " + taken + " enemy survivors of " + name + " prisoner (+" + points + " command points).";
		}
		if (points > 0 && cd.commandPoints != null && cd.commandPoints.Length > 0)
		{
			cd.commandPoints[0] += points;
		}
		UnityEngine.Debug.Log("[RESCUE] " + text);
		ModCrew.CampaignMessage("SurvivorsRescued", text);
	}

	// ---------------- port ----------------

	public static void PortTopUp(MobileMapObject mmo)
	{
		try
		{
			if (mmo == null || mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0)
				{
					continue;
				}
				int missing = full - cd.vetCrew[idx];
				cd.vetCrew[idx] = -1;
				if (missing <= 0)
				{
					continue;
				}
				if ((float)missing <= (float)full * ModCrew.FreeTopUp)
				{
					UnityEngine.Debug.Log("[CREW] " + shipName + " topped up " + missing + " men in port (wounded back on duty, no experience lost)");
					continue;
				}
				float xp = cd.vetXP[idx];
				float floor = ModCrew.RankFloor(xp);
				float newXP;
				if (xp - floor > 0.01f)
				{
					newXP = floor;
				}
				else
				{
					newXP = ModCrew.PreviousRankFloor(floor);
				}
				ModCrew.SetXP(idx, newXP);
				UnityEngine.Debug.Log("[CREW] " + shipName + " took on " + missing + " new recruits in port: experience " + xp.ToString("F2") + " -> " + newXP.ToString("F2") + " (" + ModCrew.RankName(xp) + " -> " + ModCrew.RankName(newXP) + ")");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] port top-up failed: " + ex.ToString());
		}
	}
}
```
3. Click **Compile**, then **File > Save Module**. **Close dnSpy, reopen it and reopen the DLL.**

### Step 3 - new class ModCampaignRescue
1. Right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node) > **Add Class (C#)...**
2. Select everything and paste this over it:
```csharp
using UnityEngine;
using UnityEngine.UI;

public class ModCampaignRescue : MonoBehaviour
{
	private void Update()
	{
		try
		{
			// testers: F4 on the campaign map creates a survivor event straight away
			if (Input.GetKeyDown(KeyCode.F4))
			{
				ModCrew.CreateSurvivorEvent();
				ModCrew.RebuildMapMarkers();
			}
			ModCrew.CampaignRescueCheck();
		}
		catch (System.Exception ex)
		{
			if (!this.reported)
			{
				this.reported = true;
				UnityEngine.Debug.LogError("[RESCUE] campaign check failed: " + ex.ToString());
			}
		}
		this.FitMessagePanel();
	}

	// Widens the campaign message box so long messages fit, and shrinks it back for short ones
	private void FitMessagePanel()
	{
		try
		{
			ErrorPanel ep = ErrorPanel.instance;
			if (ep == null || ep.messageText == null || ep.panelImage == null)
			{
				return;
			}
			Text text = ep.messageText;
			if (text.text == this.lastText)
			{
				return;
			}
			this.lastText = text.text;
			RectTransform panel = ep.panelImage.rectTransform;
			RectTransform textRect = text.rectTransform;
			if (!this.sized)
			{
				this.sized = true;
				this.panelSize = panel.sizeDelta;
				this.textSize = textRect.sizeDelta;
				this.textWidth = textRect.rect.width;
				this.textStretched = textRect.anchorMin.x != textRect.anchorMax.x;
			}
			float maxWidth = 1600f;
			if (ep.panelImage.canvas != null)
			{
				RectTransform root = ep.panelImage.canvas.rootCanvas.GetComponent<RectTransform>();
				if (root != null)
				{
					maxWidth = root.rect.width * 0.9f;
				}
			}
			float need = Mathf.Min(text.preferredWidth + 30f, maxWidth);
			float extra = Mathf.Max(0f, need - this.textWidth);
			panel.sizeDelta = new Vector2(this.panelSize.x + extra, this.panelSize.y);
			if (!this.textStretched)
			{
				textRect.sizeDelta = new Vector2(this.textSize.x + extra, this.textSize.y);
			}
		}
		catch
		{
		}
	}

	private bool reported;

	private string lastText;

	private bool sized;

	private bool textStretched;

	private float textWidth;

	private Vector2 panelSize;

	private Vector2 textSize;
}
```
3. Click **Compile**, then **File > Save Module**. **Close dnSpy, reopen it and reopen the DLL.**

### Step 4 - CampaignManager.CheckHourly
1. Right-click method **CheckHourly** (class **CampaignManager**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
ModCrew.CampaignHour();
if (base.gameObject.GetComponent<ModCampaignRescue>() == null)
{
    base.gameObject.AddComponent<ModCampaignRescue>();
}
```
3. Click **Compile**, then **File > Save Module**.

### Step 4b - CampaignInterface.Update (markers back straight away after loading)
1. Right-click method **Update** (class **CampaignInterface**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (CampaignManager.instance != null && CampaignManager.instance.gameObject.GetComponent<ModCampaignRescue>() == null)
{
    CampaignManager.instance.gameObject.AddComponent<ModCampaignRescue>();
}
```
3. Click **Compile**, then **File > Save Module**.

Without this step, markers only come back after the first campaign hour following a load.

### Step 5 - message file
Open `override/language/english/dictionary/campaign_message.txt` and add these lines at the end:
```
SurvivorsReported=<0>
SurvivorsReported=audio/ui/AlarmHigh
SurvivorsRescued=<0>
SurvivorsRescued=audio/ui/AlarmBlip
SurvivorsLost=<0>
SurvivorsLost=audio/ui/AlarmLow
```

### Step 6 - map icon
Unzip `survivor_icon_v1.8.4.zip` into your StreamingAssets folder. It adds `override/interface/images/map/survivors.png`, a white lifebuoy that the game tints orange (yours) or red (enemy). Without the file, the markers use the map-note square instead.

**Testing**
1. Sink a ship in battle and leave without picking up its survivors. Back on the map, you should get the "still in the water" message and a marker where the battle was fought.
2. Sail a task force over the marker. The message should say how many were picked up, and the log shows `[RESCUE] ... join the crew of ...` or prisoners and command points.
3. Press **F4** on the campaign map (testers key) to create a survivor event straight away. The log shows `[RESCUE] map marker 0 for ... at ...`, and a marker should appear. Otherwise, let time run for 3-7 days for a random one.
4. Save and reload with a marker on the map. It should still be there.

**Tuning:** the numbers at the top of ModCrew under "Campaign map survivors (v0.18.4)" set how long survivors last, the hourly losses, the shortest and longest time between events (`EventMinDays`, `EventMaxDays`) and the points for spare men. The time to the next event is picked again when you load a save.

**If a marker doesn't show up:** the survivors still work (the log and messages show them). Send me a screenshot. The markers borrow the game's map-note icon, and it may need adjusting.

---

## v0.18.5 - Short-handed from 80%

**What changes:**
- A ship now counts as **short-handed below 80%** of her crew (was 90%). Above 80% she works normally and keeps all her damage control parties.
- Below 80%, reloads and repairs slow down as before, and the effect at half crew is the same as before (about 30% slower). Damage control parties drop with the crew left, never below 1.
- The **Men** line on the hover panel turns orange below 80% (was 90%), and the Crew tab's short-handed warning comes at 80%.
- The Crews and Home Ports rules page says 80%.

| Crew left | Efficiency | Damage control parties (4 normally) |
|---|---|---|
| 80% or more | no change | 4 |
| 70% | -10% | 3 |
| 50% | -30% | 2 |
| 30% | -50% | 1 |

**Install (dnSpy).** Back up the DLL first.

### Step 1 - ModCrew (replace the class)
1. Right-click class **ModCrew** > **Edit Class (C#)...**
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using WorldMapStrategyKit;

public class ModCrew
{
	public class Entry
	{
		public string name;
		public int full;
		public int start;
		public float lost;
		public int cells;
		public bool applied;
		public int faction;
		public int lastParties = -1;
		public float rescued;
		public float passengers;
		public float prisoners;
		public bool sunk;
		public bool magazine;
		// Crew tab (v0.19.2): losses waiting to be reported, what caused them, and when the last one happened
		public float pendingLoss;
		public string pendingWhat = string.Empty;
		public float lastLossTime;
		public bool shortWarned;
	}

	public class Group
	{
		public string name;
		public int faction;
		public float men;
		public float rescuedTotal;
		public Transform anchor;
		public bool announced;
	}

	// Share of one compartment's worth of crew lost when that compartment is destroyed / catches fire / starts flooding
	public const float DestroyShare = 0.5f;
	public const float FireShare = 0.15f;
	public const float FloodShare = 0.1f;
	// A ship afloat never drops below this share of its full crew
	public const float MinCrew = 0.15f;
	// Port top-ups this small (wounded returning to duty) cost no experience
	public const float FreeTopUp = 0.03f;
	// Below this share of the crew, reloads and repairs slow down
	// v0.18.5: was 0.9 (90%)
	public const float ShortCrewStart = 0.8f;
	// Efficiency lost per share of crew below ShortCrewStart (1.0 = -30% efficiency at half crew, as before)
	public const float ShortCrewFactor = 1f;

	// Rescue (v1.8.3)
	// Share of the men still aboard who get off a sinking ship alive
	public const float SurviveSinking = 0.6f;
	public const float SurviveMagazine = 0.25f;
	public const float SurviveScuttle = 0.9f;
	// Rescue range (300 m, in 10 m battle units) and the speed a rescuer must be below
	public const float RescueRange = 300f * 0.1f;
	public const float RescueKnots = 5f;
	// Men a rescuing ship takes aboard per second of battle time
	public const float PickupPerSecond = 4f;
	// Share of the survivors in the water lost per second (0.0005 = about 3% a minute)
	public const float DrownPerSecond = 0.0005f;
	// Extra men (spare survivors and prisoners) a ship can carry, as a share of its full crew
	public const float PassengerSpace = 0.25f;
	// Command points per prisoner (0.1 = 1 point per 10 prisoners)
	public const float PrisonerPoints = 0.1f;

	// Campaign map survivors (v1.8.4)
	// Hours survivors last on the campaign map, and the share lost each hour (0.04 = 4%)
	public const float MapSurvivorHours = 24f;
	public const float MapDrownPerHour = 0.04f;
	// Days between "ship sunk, survivors reported" events: a random time between these two
	public const float EventMinDays = 3f;
	public const float EventMaxDays = 7f;
	// Hours until the next event (picked at random; -1 = not picked yet)
	public static float hoursToEvent = -1f;
	// Command points per spare rescued man of your own (0.05 = 1 point per 20 men)
	public const float OwnSparePoints = 0.05f;

	public static Dictionary<int, ModCrew.Entry> battle = new Dictionary<int, ModCrew.Entry>();
	public static List<GameObject> mapMarkers = new List<GameObject>();
	public static List<GameObject> mapTexts = new List<GameObject>();
	public static int loggedRecords = -1;
	public static float lastRebuild = -10f;
	public static List<ModCrew.Group> groups = new List<ModCrew.Group>();
	public static bool groupsReported;

	// ---------------- campaign data ----------------

	public static int Index(string name, bool create)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.vetNames == null)
		{
			cd.vetNames = new List<string>();
		}
		if (cd.vetBattles == null)
		{
			cd.vetBattles = new List<int>();
		}
		if (cd.vetXP == null)
		{
			cd.vetXP = new List<float>();
		}
		if (cd.vetCrew == null)
		{
			cd.vetCrew = new List<int>();
		}
		while (cd.vetBattles.Count < cd.vetNames.Count)
		{
			cd.vetBattles.Add(0);
		}
		while (cd.vetXP.Count < cd.vetNames.Count)
		{
			cd.vetXP.Add((float)cd.vetBattles[cd.vetXP.Count]);
		}
		while (cd.vetCrew.Count < cd.vetNames.Count)
		{
			cd.vetCrew.Add(-1);
		}
		int idx = cd.vetNames.IndexOf(name);
		if (idx == -1 && create)
		{
			cd.vetNames.Add(name);
			cd.vetBattles.Add(0);
			cd.vetXP.Add(0f);
			cd.vetCrew.Add(-1);
			idx = cd.vetNames.Count - 1;
		}
		return idx;
	}

	public static float GetXP(string name)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return 0f;
		}
		return CampaignManager.instance.campaignData.vetXP[idx];
	}

	public static void SetXP(int idx, float xp)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (xp < 0f)
		{
			xp = 0f;
		}
		cd.vetXP[idx] = xp;
		cd.vetBattles[idx] = Mathf.FloorToInt(xp + 0.001f);
	}

	public static float RankFloor(float xp)
	{
		int b = Mathf.FloorToInt(xp + 0.001f);
		if (b >= 9)
		{
			return 9f;
		}
		if (b >= 5)
		{
			return 5f;
		}
		if (b >= 2)
		{
			return 2f;
		}
		return 0f;
	}

	public static float PreviousRankFloor(float floor)
	{
		if (floor >= 9f)
		{
			return 5f;
		}
		if (floor >= 5f)
		{
			return 2f;
		}
		return 0f;
	}

	public static string RankName(float xp)
	{
		return MobileMapObject.GetVeteranRank(Mathf.FloorToInt(xp + 0.001f));
	}

	public static int FullCrew(string prefab)
	{
		try
		{
			if (EngagementManager.instance != null && EngagementManager.instance.unitDataDictionary.ContainsKey(prefab))
			{
				return EngagementManager.instance.unitDataDictionary[prefab].crew;
			}
		}
		catch
		{
		}
		return 0;
	}

	public static int GetCrew(string name, int full)
	{
		int idx = ModCrew.Index(name, false);
		if (idx == -1)
		{
			return full;
		}
		int crew = CampaignManager.instance.campaignData.vetCrew[idx];
		if (crew < 0 || crew > full)
		{
			return full;
		}
		return crew;
	}

	// Losing a share of the crew takes the same share of the progress towards the next rank. Never drops a rank.
	public static void LoseProgress(int idx, float share)
	{
		float xp = CampaignManager.instance.campaignData.vetXP[idx];
		float floor = ModCrew.RankFloor(xp);
		ModCrew.SetXP(idx, floor + (xp - floor) * (1f - Mathf.Clamp01(share)));
	}

	// ---------------- battle ----------------

	public static void OnBattleStart()
	{
		try
		{
			if (EngagementData.instance == null || !EngagementData.instance.isCampaignEngagement || EngagementManager.instance == null)
			{
				return;
			}
			Dictionary<int, ModCrew.Entry> fresh = new Dictionary<int, ModCrew.Entry>();
			bool carried = false;
			List<Unit> units = new List<Unit>();
			units.AddRange(EngagementManager.instance.playerUnits);
			units.AddRange(EngagementManager.instance.otherUnits);
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u == null || u.unitSea == null || u.damageableSea == null || u.unitData == null || u.unitData.crew <= 0)
				{
					continue;
				}
				int id = u.damageableSea.GetInstanceID();
				if (fresh.ContainsKey(id))
				{
					continue;
				}
				if (ModCrew.battle.ContainsKey(id))
				{
					fresh[id] = ModCrew.battle[id];
					carried = true;
					continue;
				}
				ModCrew.Entry e = new ModCrew.Entry();
				e.name = u.unitInstanceName;
				e.faction = (int)u.faction;
				e.full = u.unitData.crew;
				if (e.faction == 0)
				{
					e.start = ModCrew.GetCrew(e.name, e.full);
				}
				else
				{
					e.start = e.full;
				}
				e.lost = 0f;
				e.cells = Mathf.Max(1, u.damageableSea.cellVariables.Count);
				e.applied = false;
				// a ship that starts short-handed is reported once at the start, not again later
				e.shortWarned = (float)e.start < (float)e.full * ModCrew.ShortCrewStart;
				fresh[id] = e;
				if (e.faction == 0)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " enters battle with " + e.start.ToString("#,##0") + " / " + e.full.ToString("#,##0") + " men, " + ModCrew.RankName(ModCrew.GetXP(e.name)) + " (" + ModCrew.GetXP(e.name).ToString("F2") + ")");
				}
				else
				{
					UnityEngine.Debug.Log("[CREW] enemy " + e.name + " enters battle with " + e.start.ToString("#,##0") + " men");
				}
			}
			ModCrew.battle = fresh;
			if (!carried)
			{
				// a new battle: clear any survivors left from the last one
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].anchor != null)
					{
						UnityEngine.Object.Destroy(ModCrew.groups[g].anchor.gameObject);
					}
				}
				ModCrew.groups.Clear();
				ModCrew.groupsReported = false;
				ModHitLog.Clear();
			}
			for (int i = 0; i < units.Count; i++)
			{
				Unit u = units[i];
				if (u != null && u.unitSea != null && u.damageableSea != null)
				{
					Utilities.SetSeaEfficiency(u);
					int parties = ModCrew.Parties(u);
					if (u.unitData != null && parties < u.unitData.damageParties)
					{
						UnityEngine.Debug.Log("[CREW] " + u.unitInstanceName + " is short-handed: " + parties + " of " + u.unitData.damageParties + " damage control parties, efficiency -" + (ModCrew.EfficiencyPenalty(u) * 100f).ToString("F0") + "%");
						if ((int)u.faction == 0)
						{
							ModLogTabs.AddCrew(ModCrew.Paint(u.unitInstanceName, ModCrew.ColourOwnShip) + " starts the battle " + ModCrew.Paint("short-handed", ModCrew.ColourWarning) + ": " + Mathf.RoundToInt(ModCrew.CrewShare(u) * 100f) + "% crew, " + parties + " of " + u.unitData.damageParties + " damage control parties");
						}
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] battle start failed: " + ex.ToString());
		}
	}

	// Share of the full crew still aboard (1 when the ship is not tracked)
	public static float CrewShare(Unit u)
	{
		if (u == null || u.damageableSea == null)
		{
			return 1f;
		}
		ModCrew.Entry e;
		if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.full <= 0)
		{
			return 1f;
		}
		return Mathf.Clamp01(ModCrew.CrewAboard(e) / (float)e.full);
	}

	// Men in the crew right now (not counting spare survivors or prisoners)
	public static float CrewAboard(ModCrew.Entry e)
	{
		return Mathf.Min((float)e.full, (float)e.start - e.lost + e.rescued);
	}

	public static float EfficiencyPenalty(Unit u)
	{
		float share = ModCrew.CrewShare(u);
		if (share >= ModCrew.ShortCrewStart)
		{
			return 0f;
		}
		return (ModCrew.ShortCrewStart - share) * ModCrew.ShortCrewFactor;
	}

	public static int Parties(Unit u)
	{
		if (u == null || u.unitData == null)
		{
			return 0;
		}
		int full = u.unitData.damageParties;
		if (full <= 1)
		{
			return full;
		}
		float share = ModCrew.CrewShare(u);
		int parties = full;
		// v0.18.5: parties only drop once the ship is short-handed (below ShortCrewStart)
		if (share < ModCrew.ShortCrewStart)
		{
			parties = Mathf.Clamp(Mathf.RoundToInt((float)full * share), 1, full);
		}
		try
		{
			ModCrew.Entry e;
			if (u.damageableSea != null && ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e))
			{
				if (e.lastParties != -1 && e.lastParties != parties)
				{
					UnityEngine.Debug.Log("[CREW] " + e.name + " now has " + parties + " of " + full + " damage control parties (" + (share * 100f).ToString("F0") + "% crew)");
					if (e.faction == 0)
					{
						ModLogTabs.AddCrew(ModCrew.Paint(e.name, ModCrew.ColourOwnShip) + " is down to " + ModCrew.Paint(parties + " of " + full + " damage control parties", ModCrew.ColourWarning));
					}
				}
				e.lastParties = parties;
			}
		}
		catch
		{
		}
		return parties;
	}

	public static float CellFactor(CellVariable cv)
	{
		if (cv == null || cv.parentCell == null)
		{
			return 1f;
		}
		switch (cv.parentCell.cellType)
		{
		case CellType.Magazine:
			return 4f;
		case CellType.Bridge:
		case CellType.ControlRoom:
		case CellType.Conning:
			return 2.5f;
		case CellType.Engineering:
		case CellType.ElectricEngine:
		case CellType.Primary:
		case CellType.Secondary:
			return 2f;
		case CellType.Aircraft:
		case CellType.Torpedo:
		case CellType.Torpedo_Room:
			return 1.5f;
		case CellType.Propeller:
		case CellType.DoublePropeller:
		case CellType.Rudder:
		case CellType.PropellersRudder:
		case CellType.Funnel:
		case CellType.Director:
			return 0.5f;
		}
		return 1f;
	}

	public static void AddLoss(DamageableSea ds, CellVariable cv, float share, string what)
	{
		try
		{
			if (ds == null || ModCrew.battle.Count == 0)
			{
				return;
			}
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.applied || e.sunk)
			{
				return;
			}
			if (share >= ModCrew.DestroyShare && cv != null && cv.parentCell != null && cv.parentCell.cellType == CellType.Magazine)
			{
				e.magazine = true;
			}
			float men = (float)e.start / (float)e.cells * share * ModCrew.CellFactor(cv);
			float maxLoss = ModCrew.CrewAboard(e) - (float)e.full * ModCrew.MinCrew;
			if (maxLoss <= 0f)
			{
				return;
			}
			if (men > maxLoss)
			{
				men = maxLoss;
			}
			if (men <= 0f)
			{
				return;
			}
			e.lost += men;
			if (e.faction == 0)
			{
				// collected and reported in the Crew tab once the hits stop for a moment
				string cause = (what == "destroyed") ? "compartments destroyed" : ((what == "on fire") ? "fire" : what);
				e.pendingLoss += men;
				if (e.pendingWhat.IndexOf(cause) < 0)
				{
					e.pendingWhat += ((e.pendingWhat != string.Empty) ? ", " : string.Empty) + cause;
				}
				e.lastLossTime = Time.time;
			}
			string cellName = (cv != null && cv.parentCell != null) ? (cv.parentCell.cellType.ToString() + " " + cv.parentCell.cellID) : "?";
			UnityEngine.Debug.Log("[CREW] " + e.name + ": " + cellName + " " + what + ", " + men.ToString("F1") + " men lost (battle total " + Mathf.RoundToInt(e.lost) + ", " + Mathf.RoundToInt(ModCrew.CrewAboard(e)) + " / " + e.full + " aboard)");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] loss failed: " + ex.Message);
		}
	}

	public static void OnCellDestroyed(DamageableSea ds, CellVariable cv)
	{
		if (cv == null || cv.isDestroyed)
		{
			return;
		}
		ModHitLog.Note(ds, "destroyed");
		ModCrew.AddLoss(ds, cv, ModCrew.DestroyShare, "destroyed");
	}

	public static void OnFire(DamageableSea ds, CellVariable cv, bool isOn)
	{
		if (isOn && cv != null && !cv.isBurning)
		{
			ModHitLog.Note(ds, "fire");
		}
		if (!isOn || cv == null || cv.isBurning || cv.isDestroyed || cv.parentCell == null || !cv.parentCell.canBurn)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FireShare, "on fire");
	}

	public static void OnFlood(DamageableSea ds, CellVariable cv)
	{
		if (cv != null && cv.isFlooded <= 0f)
		{
			ModHitLog.Note(ds, "flood");
		}
		if (cv == null || cv.isFlooded > 0f || cv.isDestroyed)
		{
			return;
		}
		ModCrew.AddLoss(ds, cv, ModCrew.FloodShare, "flooding");
	}

	// ---------------- survivors (v1.8.3) ----------------

	public static void OnShipSunk(DamageableSea ds)
	{
		try
		{
			if (ds == null || ds.parentUnit == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModHitLog.Finish();
			ModHitLog.Sunk(ds.parentUnit);
			ModCrew.Entry e;
			if (!ModCrew.battle.TryGetValue(ds.GetInstanceID(), out e) || e.sunk)
			{
				return;
			}
			e.sunk = true;
			float aboard = ModCrew.CrewAboard(e) + e.passengers;
			float rate = ModCrew.SurviveSinking;
			string how = "sank";
			if (ds.scuttled)
			{
				rate = ModCrew.SurviveScuttle;
				how = "was scuttled";
			}
			else if (e.magazine)
			{
				rate = ModCrew.SurviveMagazine;
				how = "blew up";
			}
			float men = aboard * rate;
			if (e.prisoners > 0f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(e.prisoners) + " prisoners aboard " + e.name + " were lost with her");
			}
			if (men < 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + e.name + " " + how + " with no survivors");
				return;
			}
			ModCrew.Group g = new ModCrew.Group();
			g.name = e.name;
			g.faction = e.faction;
			g.men = men;
			GameObject marker = new GameObject("ModSurvivors_" + e.name);
			Transform parent = ds.transform.parent;
			if (parent == null && FloatingOrigin.instance != null && FloatingOrigin.instance.transformsToMove != null && FloatingOrigin.instance.transformsToMove.Length > 0)
			{
				parent = FloatingOrigin.instance.transformsToMove[0];
			}
			if (parent != null)
			{
				marker.transform.SetParent(parent, true);
			}
			Vector3 pos = ds.transform.position;
			pos.y = 0f;
			marker.transform.position = pos;
			g.anchor = marker.transform;
			ModCrew.groups.Add(g);
			string side = (e.faction == 0) ? string.Empty : "enemy ";
			UnityEngine.Debug.Log("[RESCUE] " + side + e.name + " " + how + ": " + Mathf.RoundToInt(men) + " of " + Mathf.RoundToInt(aboard) + " men aboard are in the water");
			ModCrew.SendLog("ModSurvivors", "Survivors of " + side + e.name + " in the water, about " + Mathf.RoundToInt(men) + " men");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] sinking failed: " + ex.ToString());
		}
	}

	public static void SendLog(string key, string text)
	{
		try
		{
			// v0.19.2: survivor and rescue messages go to the Crew tab of the message log
			// orange for survivors in the water, green for rescues
			string colour = (key == "ModSurvivors") ? "#ffa040" : "#70e070";
			ModLogTabs.AddCrew("<color=" + colour + ">" + text + "</color>");
		}
		catch
		{
		}
	}

	// Crew tab colours
	public const string ColourOwnShip = "#80b8ff";
	public const string ColourLoss = "#ff9a40";
	public const string ColourWarning = "#ffe070";
	// Seconds without new losses before a ship's casualties are reported
	public const float LossReportDelay = 2f;

	public static string Paint(string text, string colour)
	{
		return "<color=" + colour + ">" + text + "</color>";
	}

	// Reports your ships' casualties in the Crew tab, one line per ship once the hits stop for a moment
	public static void FlushLosses()
	{
		try
		{
			foreach (ModCrew.Entry e in ModCrew.battle.Values)
			{
				if (e.faction != 0 || e.pendingLoss < 0.5f || Time.time - e.lastLossTime < ModCrew.LossReportDelay)
				{
					continue;
				}
				int men = Mathf.Max(1, Mathf.RoundToInt(e.pendingLoss));
				float aboard = ModCrew.CrewAboard(e);
				string lost = ModCrew.Paint(men + ((men == 1) ? " man" : " men") + " lost", ModCrew.ColourLoss);
				string line = ModCrew.Paint(e.name, ModCrew.ColourOwnShip) + ": " + lost + " (" + e.pendingWhat + ")";
				if (!e.sunk)
				{
					line += ", " + Mathf.RoundToInt(aboard).ToString("#,##0") + " / " + e.full.ToString("#,##0") + " aboard";
				}
				ModLogTabs.AddCrew(line);
				e.pendingLoss = 0f;
				e.pendingWhat = string.Empty;
				if (!e.shortWarned && !e.sunk && e.full > 0 && aboard / (float)e.full < ModCrew.ShortCrewStart)
				{
					e.shortWarned = true;
					ModLogTabs.AddCrew(ModCrew.Paint(e.name, ModCrew.ColourOwnShip) + " is " + ModCrew.Paint("short-handed", ModCrew.ColourWarning) + " (" + Mathf.RoundToInt(aboard / (float)e.full * 100f) + "% crew): slower reloads and repairs");
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] crew tab report failed: " + ex.Message);
		}
	}

	// Called about once a second by ModRescue with the battle time that has passed
	public static void RescueTick(float dt)
	{
		ModCrew.FlushLosses();
		if (ModCrew.groups.Count == 0 || EngagementManager.instance == null || EngagementManager.instance.playerUnits == null)
		{
			return;
		}
		List<Unit> players = EngagementManager.instance.playerUnits;
		for (int g = 0; g < ModCrew.groups.Count; g++)
		{
			ModCrew.Group grp = ModCrew.groups[g];
			if (grp.men < 1f || grp.anchor == null)
			{
				continue;
			}
			grp.men -= grp.men * ModCrew.DrownPerSecond * dt;
			for (int i = 0; i < players.Count && grp.men >= 1f; i++)
			{
				Unit u = players[i];
				if (u == null || u.isDestroyed || u.unitSea == null || u.damageableSea == null)
				{
					continue;
				}
				ModCrew.Entry e;
				if (!ModCrew.battle.TryGetValue(u.damageableSea.GetInstanceID(), out e) || e.sunk || e.applied)
				{
					continue;
				}
				if (Vector3.Distance(u.transform.position, grp.anchor.position) > ModCrew.RescueRange)
				{
					continue;
				}
				if (Utilities.ConvertMetrePerSecondToKnots(u.currentSpeed) > ModCrew.RescueKnots)
				{
					continue;
				}
				float take = Mathf.Min(grp.men, ModCrew.PickupPerSecond * dt);
				float spare = (float)e.full * ModCrew.PassengerSpace - e.passengers - e.prisoners;
				float taken = 0f;
				if (grp.faction == 0)
				{
					float room = (float)e.full - ModCrew.CrewAboard(e);
					float toCrew = Mathf.Clamp(take, 0f, Mathf.Max(0f, room));
					float toSpare = Mathf.Clamp(take - toCrew, 0f, Mathf.Max(0f, spare));
					e.rescued += toCrew;
					e.passengers += toSpare;
					taken = toCrew + toSpare;
				}
				else
				{
					float toHold = Mathf.Clamp(take, 0f, Mathf.Max(0f, spare));
					e.prisoners += toHold;
					taken = toHold;
				}
				if (taken <= 0f)
				{
					continue;
				}
				grp.men -= taken;
				grp.rescuedTotal += taken;
				if (!grp.announced)
				{
					grp.announced = true;
					UnityEngine.Debug.Log("[RESCUE] " + e.name + " is picking up survivors of " + grp.name);
					ModCrew.SendLog("ModRescuing", e.name + " is picking up survivors of " + grp.name);
				}
				if (grp.faction == 0)
				{
					Utilities.SetSeaEfficiency(u);
				}
				if (grp.men < 1f)
				{
					string what = (grp.faction == 0) ? " survivors" : " prisoners";
					UnityEngine.Debug.Log("[RESCUE] all survivors of " + grp.name + " picked up: " + Mathf.RoundToInt(grp.rescuedTotal) + what);
					ModCrew.SendLog("ModRescued", "All survivors of " + grp.name + " picked up, " + Mathf.RoundToInt(grp.rescuedTotal) + what);
				}
			}
		}
	}

	// ---------------- after battle ----------------

	public static void ApplyBattleLosses(MobileMapObject mmo)
	{
		try
		{
			if (mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			if (!ModCrew.groupsReported)
			{
				ModCrew.groupsReported = true;
				ModHitLog.Clear();
				string leftBehind = string.Empty;
				for (int g = 0; g < ModCrew.groups.Count; g++)
				{
					if (ModCrew.groups[g].men >= 1f)
					{
						UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(ModCrew.groups[g].men) + " survivors of " + ModCrew.groups[g].name + " were left in the water, now marked on the campaign map");
						Vector2 battlePos = mmo.gameObjectAnimator.currentMap2DLocation;
						Vector2 offset = new Vector2(UnityEngine.Random.Range(-0.002f, 0.002f), UnityEngine.Random.Range(-0.002f, 0.002f));
						ModCrew.AddMapSurvivors(battlePos + offset, ModCrew.groups[g].men, ModCrew.groups[g].faction, ModCrew.groups[g].name, ModCrew.MapSurvivorHours);
						if (leftBehind != string.Empty)
						{
							leftBehind += ", ";
						}
						leftBehind += ModCrew.groups[g].name;
						ModCrew.groups[g].men = 0f;
					}
				}
				if (leftBehind != string.Empty)
				{
					ModCrew.CampaignMessage("SurvivorsReported", "Survivors are still in the water where the battle was fought (" + leftBehind + "). Send a task force there within " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to pick them up.");
				}
			}
			List<ModCrew.Entry> found = new List<ModCrew.Entry>();
			List<string> names = new List<string>();
			float spareMen = 0f;
			float prisoners = 0f;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
				{
					continue;
				}
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				ModCrew.Entry e = null;
				foreach (ModCrew.Entry candidate in ModCrew.battle.Values)
				{
					if (!candidate.applied && !candidate.sunk && candidate.faction == 0 && candidate.name == shipName)
					{
						e = candidate;
						break;
					}
				}
				if (e == null)
				{
					continue;
				}
				e.applied = true;
				found.Add(e);
				names.Add(shipName);
				spareMen += e.passengers;
				prisoners += e.prisoners;
			}
			// spare survivors go to the ships in this task force that are still short of men
			for (int k = 0; k < found.Count && spareMen >= 1f; k++)
			{
				float room = (float)found[k].full - ModCrew.CrewAboard(found[k]);
				if (room >= 1f)
				{
					float give = Mathf.Min(room, spareMen);
					found[k].rescued += give;
					spareMen -= give;
					UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(give) + " rescued men join the crew of " + found[k].name);
				}
			}
			for (int k = 0; k < found.Count; k++)
			{
				ModCrew.Entry e = found[k];
				int lostMen = Mathf.RoundToInt(e.lost);
				int rescuedMen = Mathf.RoundToInt(e.rescued);
				if (lostMen <= 0 && rescuedMen <= 0)
				{
					continue;
				}
				int idx = ModCrew.Index(names[k], true);
				int crewNow = Mathf.Clamp(Mathf.RoundToInt(ModCrew.CrewAboard(e)), 0, e.full);
				cd.vetCrew[idx] = (crewNow >= e.full) ? -1 : crewNow;
				float xpBefore = cd.vetXP[idx];
				if (lostMen > 0)
				{
					ModCrew.LoseProgress(idx, (float)lostMen / (float)e.full);
				}
				UnityEngine.Debug.Log("[CREW] " + names[k] + " lost " + lostMen + " men and took aboard " + rescuedMen + " survivors: crew " + crewNow.ToString("#,##0") + " / " + e.full.ToString("#,##0") + ", experience " + xpBefore.ToString("F2") + " -> " + cd.vetXP[idx].ToString("F2"));
			}
			if (spareMen >= 1f)
			{
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(spareMen) + " rescued men had no place in the task force and were sent home");
			}
			if (prisoners >= 1f)
			{
				int points = Mathf.RoundToInt(prisoners * ModCrew.PrisonerPoints);
				if (points > 0 && cd.commandPoints != null && cd.commandPoints.Length > 0)
				{
					cd.commandPoints[0] += points;
				}
				UnityEngine.Debug.Log("[RESCUE] " + Mathf.RoundToInt(prisoners) + " prisoners taken by " + mmo.mobileName + ": +" + points + " command points");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] applying losses failed: " + ex.ToString());
		}
	}

	// ---------------- campaign map survivors (v1.8.4) ----------------
	// Each record in CampaignData.modSurvivors is "x|y|men|faction|hoursLeft|name"

	public static List<string> MapRecords()
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		if (cd.modSurvivors == null)
		{
			cd.modSurvivors = new List<string>();
		}
		return cd.modSurvivors;
	}

	public static string MakeRecord(Vector2 pos, float men, int faction, float hours, string name)
	{
		CultureInfo ci = CultureInfo.InvariantCulture;
		return pos.x.ToString("R", ci) + "|" + pos.y.ToString("R", ci) + "|" + men.ToString("R", ci) + "|" + faction.ToString(ci) + "|" + hours.ToString("R", ci) + "|" + name.Replace("|", "/");
	}

	public static bool ReadRecord(string rec, out Vector2 pos, out float men, out int faction, out float hours, out string name)
	{
		pos = Vector2.zero;
		men = 0f;
		faction = 0;
		hours = 0f;
		name = string.Empty;
		string[] p = rec.Split(new char[] { '|' });
		if (p.Length < 6)
		{
			return false;
		}
		CultureInfo ci = CultureInfo.InvariantCulture;
		pos = new Vector2(float.Parse(p[0], ci), float.Parse(p[1], ci));
		men = float.Parse(p[2], ci);
		faction = int.Parse(p[3], ci);
		hours = float.Parse(p[4], ci);
		name = p[5];
		return true;
	}

	public static void AddMapSurvivors(Vector2 pos, float men, int faction, string name, float hours)
	{
		try
		{
			ModCrew.MapRecords().Add(ModCrew.MakeRecord(pos, men, faction, hours, name));
			ModCrew.RebuildMapMarkers();
			UnityEngine.Debug.Log("[RESCUE] map survivors added: " + Mathf.RoundToInt(men) + " men of " + name + " (side " + faction + "), " + hours.ToString("F0") + " hours");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] adding map survivors failed: " + ex.ToString());
		}
	}

	public static void CampaignMessage(string key, string text)
	{
		try
		{
			ErrorPanel.instance.SetErrorMessage(key, text, string.Empty, string.Empty);
		}
		catch
		{
		}
	}

	public static Sprite survivorIcon;
	public static bool survivorIconTried;

	// interface/images/map/survivors.png in the override folder (white, tinted orange or red)
	public static Sprite SurvivorIcon()
	{
		if (!ModCrew.survivorIconTried)
		{
			ModCrew.survivorIconTried = true;
			try
			{
				ModCrew.survivorIcon = AssetLoader.instance.ImportSprite("interface/images/map/survivors.png", false, false);
			}
			catch (System.Exception ex)
			{
				UnityEngine.Debug.LogError("[RESCUE] could not load survivors.png: " + ex.Message);
			}
			UnityEngine.Debug.Log("[RESCUE] survivor map icon " + ((ModCrew.survivorIcon != null) ? "loaded" : "not found, using the map note icon"));
		}
		return ModCrew.survivorIcon;
	}

	public static void RebuildMapMarkers()
	{
		for (int i = 0; i < ModCrew.mapMarkers.Count; i++)
		{
			if (ModCrew.mapMarkers[i] != null)
			{
				UnityEngine.Object.Destroy(ModCrew.mapMarkers[i]);
			}
		}
		ModCrew.mapMarkers.Clear();
		for (int i = 0; i < ModCrew.mapTexts.Count; i++)
		{
			if (ModCrew.mapTexts[i] != null)
			{
				UnityEngine.Object.Destroy(ModCrew.mapTexts[i]);
			}
		}
		ModCrew.mapTexts.Clear();
		CampaignInterface ui = CampaignInterface.instance;
		if (ui == null || ui.portPrefab == null)
		{
			return;
		}
		List<string> recs = ModCrew.MapRecords();
		if (recs.Count != ModCrew.loggedRecords)
		{
			ModCrew.loggedRecords = recs.Count;
			UnityEngine.Debug.Log("[RESCUE] " + recs.Count + " survivor markers in this campaign");
		}
		for (int i = 0; i < recs.Count; i++)
		{
			GameObject go = null;
			try
			{
				Vector2 pos;
				float men;
				int faction;
				float hours;
				string name;
				if (ModCrew.ReadRecord(recs[i], out pos, out men, out faction, out hours, out name))
				{
					go = UnityEngine.Object.Instantiate<GameObject>(ui.portPrefab);
					MapLocation loc = go.AddComponent<MapLocation>();
					go.name = "ModSurvivors";
					GameObjectAnimator anim = go.WMSK_MoveTo(pos, 0f, (DURATION_TYPE)0, true, 0f);
					anim.transform.localScale = new Vector3(0.4f, 0.4f, 0.4f);
					anim.autoScale = false;
					anim.isStatic = true;
					// type 7 = map note, so hovering shows its text like a note. It is not put with the
					// player's notes (mapMarkerParent), so it is never saved as a note.
					anim.type = 7;
					loc.gameObjectAnimator = anim;
					loc.locationPosition = pos;
					SpriteRenderer icon = go.GetComponentInChildren<SpriteRenderer>();
					if (icon != null)
					{
						Sprite lifebuoy = ModCrew.SurvivorIcon();
						if (lifebuoy != null)
						{
							icon.sprite = lifebuoy;
						}
						else if (ui.mapDrawIcons != null && ui.mapDrawIcons.Length > 0)
						{
							icon.sprite = ui.mapDrawIcons[0];
						}
						icon.color = (faction == 0) ? new Color(1f, 0.6f, 0.2f, 1f) : new Color(1f, 0.25f, 0.25f, 1f);
					}
					if (anim.transform.childCount > 1)
					{
						anim.transform.GetChild(1).gameObject.SetActive(false);
					}
					// the tooltip shows the description, then the name, on separate lines
					loc.locationDescription = (faction == 0) ? "SURVIVORS" : "ENEMY SURVIVORS";
					loc.locationName = "About " + Mathf.RoundToInt(men) + " men of " + name + "\n" + Mathf.CeilToInt(hours) + " hours remaining";
					UnityEngine.Debug.Log("[RESCUE] map marker " + i + " for " + name + " at " + pos.x.ToString("F4") + ", " + pos.y.ToString("F4") + (icon == null ? " (no icon found!)" : string.Empty));
				}
			}
			catch (System.Exception ex)
			{
				UnityEngine.Debug.LogError("[RESCUE] map marker failed: " + ex.Message);
			}
			ModCrew.mapMarkers.Add(go);
		}
	}

	// Called once a campaign hour from CampaignManager.CheckHourly
	public static void CampaignHour()
	{
		try
		{
			if (CampaignManager.instance == null || CampaignManager.instance.campaignData == null)
			{
				return;
			}
			List<string> recs = ModCrew.MapRecords();
			for (int i = recs.Count - 1; i >= 0; i--)
			{
				Vector2 pos;
				float men;
				int faction;
				float hours;
				string name;
				if (!ModCrew.ReadRecord(recs[i], out pos, out men, out faction, out hours, out name))
				{
					recs.RemoveAt(i);
					continue;
				}
				men -= men * ModCrew.MapDrownPerHour;
				hours -= 1f;
				if (hours <= 0f || men < 1f)
				{
					recs.RemoveAt(i);
					UnityEngine.Debug.Log("[RESCUE] survivors of " + name + " (side " + faction + ") were lost before anyone reached them");
					if (faction == 0)
					{
						ModCrew.CampaignMessage("SurvivorsLost", "No one reached the survivors of " + name + " in time. They are lost.");
					}
					continue;
				}
				recs[i] = ModCrew.MakeRecord(pos, men, faction, hours, name);
			}
			if (ModCrew.hoursToEvent < 0f)
			{
				ModCrew.hoursToEvent = UnityEngine.Random.Range(ModCrew.EventMinDays * 24f, ModCrew.EventMaxDays * 24f);
				UnityEngine.Debug.Log("[RESCUE] next survivor event in " + (ModCrew.hoursToEvent / 24f).ToString("F1") + " days");
			}
			ModCrew.hoursToEvent -= 1f;
			if (ModCrew.hoursToEvent <= 0f)
			{
				ModCrew.CreateSurvivorEvent();
				ModCrew.hoursToEvent = -1f;
			}
			ModCrew.RebuildMapMarkers();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[RESCUE] campaign hour failed: " + ex.ToString());
		}
	}

	public static void CreateSurvivorEvent()
	{
		List<SeaNavigationWaypoint> points = CampaignManager.instance.seaNavigationPoints;
		if (points == null || points.Count == 0)
		{
			return;
		}
		Vector3 wp = points[UnityEngine.Random.Range(0, points.Count)].positionRadius;
		Vector2 pos = new Vector2(wp.x, wp.y);
		bool playerIsUS = CampaignManager.instance.campaignData.campaignID != "campaign002";
		int faction = (UnityEngine.Random.value < 0.5f) ? 0 : 1;
		float men;
		string name;
		string text;
		if (faction == 0)
		{
			men = (float)UnityEngine.Random.Range(40, 91);
			name = playerIsUS ? "an American merchant ship" : "a Japanese transport";
			text = "Reports say " + name + " was torpedoed and sunk. About " + Mathf.RoundToInt(men) + " survivors are adrift (orange marker on the map). Send a task force within " + (CampaignManager.instance.campaignData.interactionDistanceMetres / 1000f).ToString("F0") + " km of them in the next " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to pick them up.";
		}
		else
		{
			men = (float)UnityEngine.Random.Range(60, 151);
			name = playerIsUS ? "a Japanese transport" : "an Allied merchant ship";
			text = "Our aircraft report that " + name + " has sunk. About " + Mathf.RoundToInt(men) + " enemy survivors are adrift (red marker on the map). Send a task force within " + (CampaignManager.instance.campaignData.interactionDistanceMetres / 1000f).ToString("F0") + " km of them in the next " + ModCrew.MapSurvivorHours.ToString("F0") + " hours to take them prisoner.";
		}
		ModCrew.MapRecords().Add(ModCrew.MakeRecord(pos, men, faction, ModCrew.MapSurvivorHours, name));
		UnityEngine.Debug.Log("[RESCUE] event: " + name + " sunk at " + pos.x.ToString("F4") + ", " + pos.y.ToString("F4") + ", " + Mathf.RoundToInt(men) + " survivors (side " + faction + ")");
		ModCrew.CampaignMessage("SurvivorsReported", text);
	}

	// Called every frame on the campaign map by ModCampaignRescue
	public static void CampaignRescueCheck()
	{
		CampaignManager cm = CampaignManager.instance;
		if (cm == null || cm.campaignData == null || cm.playerMobile == null)
		{
			return;
		}
		List<string> recs = ModCrew.MapRecords();
		if (recs.Count == 0)
		{
			return;
		}
		bool rebuild = ModCrew.mapMarkers.Count != recs.Count;
		for (int i = 0; i < ModCrew.mapMarkers.Count && !rebuild; i++)
		{
			if (ModCrew.mapMarkers[i] == null)
			{
				// markers are lost when a save is loaded: make them again
				rebuild = true;
				UnityEngine.Debug.Log("[RESCUE] survivor markers were removed (save loaded?), drawing " + recs.Count + " again");
			}
		}
		if (rebuild && Time.unscaledTime - ModCrew.lastRebuild > 2f)
		{
			ModCrew.lastRebuild = Time.unscaledTime;
			ModCrew.RebuildMapMarkers();
		}
		bool changed = false;
		for (int r = recs.Count - 1; r >= 0; r--)
		{
			Vector2 pos;
			float men;
			int faction;
			float hours;
			string name;
			if (!ModCrew.ReadRecord(recs[r], out pos, out men, out faction, out hours, out name))
			{
				continue;
			}
			for (int m = 0; m < cm.playerMobile.Count; m++)
			{
				GameObjectAnimator goa = cm.playerMobile[m];
				if (goa == null || goa.mobileMapObject == null)
				{
					continue;
				}
				MobileMapObject mmo = goa.mobileMapObject;
				if (mmo.type != 0 || mmo.currentFaction != 0 || mmo.unitPrefabs.Count == 0)
				{
					continue;
				}
				if (cm.GetDistanceInMetresBetweenMapObjects(goa.currentMap2DLocation, pos) > cm.campaignData.interactionDistanceMetres)
				{
					continue;
				}
				ModCrew.RescueOnMap(mmo, men, faction, name);
				recs.RemoveAt(r);
				changed = true;
				break;
			}
		}
		if (changed)
		{
			ModCrew.RebuildMapMarkers();
		}
	}

	public static void RescueOnMap(MobileMapObject mmo, float men, int faction, string name)
	{
		CampaignData cd = CampaignManager.instance.campaignData;
		int total = Mathf.RoundToInt(men);
		int points = 0;
		string text;
		if (faction == 0)
		{
			float left = men;
			int joined = 0;
			for (int i = 0; i < mmo.unitPrefabs.Count && left >= 1f; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0 || cd.vetCrew[idx] >= full)
				{
					continue;
				}
				int give = Mathf.Min(full - cd.vetCrew[idx], Mathf.FloorToInt(left));
				cd.vetCrew[idx] += give;
				if (cd.vetCrew[idx] >= full)
				{
					cd.vetCrew[idx] = -1;
				}
				left -= (float)give;
				joined += give;
				UnityEngine.Debug.Log("[RESCUE] " + give + " rescued men join the crew of " + shipName);
			}
			points = Mathf.RoundToInt(left * ModCrew.OwnSparePoints);
			text = mmo.mobileName + " picked up " + total + " survivors of " + name + ". " + joined + " joined short-handed crews";
			if (points > 0)
			{
				text += ", the rest were sent home (+" + points + " command points).";
			}
			else
			{
				text += ".";
			}
		}
		else
		{
			float space = 0f;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				space += (float)ModCrew.FullCrew(mmo.unitPrefabs[i]) * ModCrew.PassengerSpace;
			}
			int taken = Mathf.RoundToInt(Mathf.Min(men, space));
			points = Mathf.RoundToInt((float)taken * ModCrew.PrisonerPoints);
			text = mmo.mobileName + " took " + taken + " enemy survivors of " + name + " prisoner (+" + points + " command points).";
		}
		if (points > 0 && cd.commandPoints != null && cd.commandPoints.Length > 0)
		{
			cd.commandPoints[0] += points;
		}
		UnityEngine.Debug.Log("[RESCUE] " + text);
		ModCrew.CampaignMessage("SurvivorsRescued", text);
	}

	// ---------------- port ----------------

	public static void PortTopUp(MobileMapObject mmo)
	{
		try
		{
			if (mmo == null || mmo.currentFaction != 0 || mmo.type != 0)
			{
				return;
			}
			CampaignData cd = CampaignManager.instance.campaignData;
			for (int i = 0; i < mmo.unitPrefabs.Count; i++)
			{
				string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
				int full = ModCrew.FullCrew(mmo.unitPrefabs[i]);
				int idx = ModCrew.Index(shipName, false);
				if (full <= 0 || idx == -1 || cd.vetCrew[idx] < 0)
				{
					continue;
				}
				int missing = full - cd.vetCrew[idx];
				cd.vetCrew[idx] = -1;
				if (missing <= 0)
				{
					continue;
				}
				if ((float)missing <= (float)full * ModCrew.FreeTopUp)
				{
					UnityEngine.Debug.Log("[CREW] " + shipName + " topped up " + missing + " men in port (wounded back on duty, no experience lost)");
					continue;
				}
				float xp = cd.vetXP[idx];
				float floor = ModCrew.RankFloor(xp);
				float newXP;
				if (xp - floor > 0.01f)
				{
					newXP = floor;
				}
				else
				{
					newXP = ModCrew.PreviousRankFloor(floor);
				}
				ModCrew.SetXP(idx, newXP);
				UnityEngine.Debug.Log("[CREW] " + shipName + " took on " + missing + " new recruits in port: experience " + xp.ToString("F2") + " -> " + newXP.ToString("F2") + " (" + ModCrew.RankName(xp) + " -> " + ModCrew.RankName(newXP) + ")");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CREW] port top-up failed: " + ex.ToString());
		}
	}
}
```

### Step 2 - MobileMapObject.AppendShipInfoFromKey (one number)
1. Right-click method **AppendShipInfoFromKey** (class **MobileMapObject**) > **Edit Method (C#)...**
2. Press Ctrl+F and find `0.9f`. There is one, in the line `else if ((float)crew < (float)full * 0.9f)`.
3. Change `0.9f` to `0.8f`.
4. **Compile**, then **File > Save Module**.

### Step 3 - rules popup
Replace `modrules5.txt` in both campaigns (`override/language/english/campaign/campaign001/event/` and `campaign002/event/`) with the copies in `rules_popups_v0.18.5.zip`.

**Testing**
1. In battle, a ship that has lost a few men (above 80%) should keep all her damage control parties and get no short-handed line in the Crew tab.
2. Once she drops below 80%, the Crew tab should say she is short-handed, and her parties should start to drop.
3. On the campaign map, the **Men** line should only turn orange below 80%.
