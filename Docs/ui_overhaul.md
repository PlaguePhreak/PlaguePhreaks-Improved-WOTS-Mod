# UI Overhaul (v0.19 and onwards)

UI work goes under v0.19, then v0.19.1, v0.19.2 and so on.

| Version | Part | Status |
|---|---|---|
| v0.19 | Hit log panel `[HITLOG]` | Tested |
| v0.19.1 | Message log tabs (General / Hit log) `[LOGTABS]` | Tested |
| v0.19.2 | Crew tab, cleaner hit log wording | Tested |
| v0.19.3 | Faster group orders `[GROUPS]` | Tested |
| v0.19.4 | Group numbers on the roster | Tested |
| v0.19.5 | Minimap upgrades `[MINIMAP]` | Tested |

---

## v0.19 - Hit log

**What it does:** a small panel at the top right of the battle screen lists the last 9 hits on ships, for example:
```
18:23 Helena hit by AP shell from Chokai: 3 compartments damaged (120), fire
18:24 Chokai hit by HE shell from Helena: armour held
18:25 Unidentified ship hit by torpedo from Benham: 4 compartments damaged (610), 2 destroyed, flooding
18:31 Chokai SINKING
```
- **Colours:**
  - Ship names: **blue** for yours (the game's friendly colour) and **red** for the enemy's. The firing ship is coloured by its own side, so friendly fire shows two blue names.
  - Damage is **yellow**, destroyed compartments **orange**, **fire** bright orange, **flooding** light blue and **armour held** grey. **Torpedo** is white and bold, and **SINKING** lines are bold in the ship's side colour.
  - The colours are set at the top of ModHitLog (`ColourOwn`, `ColourEnemy`, `ColourArmour`, `ColourDamage`, `ColourDestroyed`, `ColourFire`, `ColourFlood`, `ColourTorpedo`).
- **What hit:** AP shell, HE shell, torpedo, bomb or depth charge, and who fired it if known. Aircraft show as "our aircraft" or "enemy aircraft". Unidentified enemies show as "Unidentified ship", so the panel doesn't give away what you haven't spotted.
- **The result:** how many compartments were damaged and the total damage, how many were destroyed, and whether a fire or flooding started. If a hit does less than 30% of the shell's damage, the panel shows **armour held**. A fire or flooding started by the hit is listed even when the armour holds. Torpedoes that do little show **torpedo defence held**. Compartments a torpedo destroys outright are listed even if nothing else was damaged. Near misses that do damage are marked as near misses, and ones that do nothing aren't listed.
- The panel widens to fit its longest line, up to 60% of the screen.
- **F2** shows or hides the panel. It appears with the first hit of a battle and is cleared at the start and end of each battle.
- Light hits from machine guns and strafing aren't listed, so they don't flood the panel.
- Each hit also writes a `[HITLOG]` line to `output_log.txt` with the exact numbers.

**How it works:** the hit is caught at the start of the game's main hit method (`DamageableSea.ApplyDamage`). The compartment damage that follows in the same frame (`ApplyDamageToCell`), and the fires, flooding and destroyed compartments ModCrew already sees, are added to it. The line is written on the next frame.

**Install (dnSpy).** Back up the DLL first, then do the steps in order.

### Step 1 - new class ModHitLog
1. Right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node) > **Add Class (C#)...**
2. Select everything and paste this over it:
```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModHitLog
{
	public class Hit
	{
		public DamageableSea ds;
		public int frame;
		public string target;
		public bool playerShip;
		public string what;
		public string firer;
		public int firerSide = -1;
		public float expected;
		public float damage;
		public int cells;
		public int destroyed;
		public int fires;
		public int floods;
		public bool nearMiss;
	}

	// How many lines the panel keeps
	public const int MaxLines = 9;
	// A hit doing less than this share of the shell's damage counts as "armour held"
	public const float ArmourHeldShare = 0.3f;

	public static List<string> lines = new List<string>();
	public static ModHitLog.Hit current;
	public static bool visible = true;
	public static GUIStyle style;
	public static GUIStyle boxStyle;

	// ---------- called from the game ----------

	// First line of DamageableSea.ApplyDamage
	public static void BeginHit(DamageableSea ds, AmmunitionDamage ammo, bool directHit)
	{
		try
		{
			ModHitLog.Finish();
			if (ds == null || ds.parentUnit == null || ammo == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModHitLog.Hit h = new ModHitLog.Hit();
			h.ds = ds;
			h.frame = Time.frameCount;
			Unit target = ds.parentUnit;
			h.playerShip = (int)target.faction == 0;
			h.target = ModHitLog.ShipName(target);
			if (ammo.isTorpedo)
			{
				h.what = "torpedo";
			}
			else if (ammo.isBomb)
			{
				h.what = "bomb";
			}
			else if (ammo.isdepthCharge)
			{
				h.what = "depth charge";
			}
			else if (ammo.armorPiercing)
			{
				h.what = "AP shell";
			}
			else
			{
				h.what = "HE shell";
			}
			h.firer = ModHitLog.FirerName(ammo.firedByUnitID, out h.firerSide);
			h.expected = ammo.damageAmount;
			h.nearMiss = !directHit && !ammo.isTorpedo;
			ModHitLog.current = h;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[HITLOG] begin failed: " + ex.Message);
		}
	}

	// First line of DamageableSea.ApplyDamageToCell
	public static void CellDamage(DamageableSea ds, CellVariable cv, float amount)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount || amount <= 0f)
		{
			return;
		}
		h.damage += amount;
		h.cells++;
	}

	// Called by ModCrew when a compartment is destroyed ("destroyed"), catches fire ("fire") or starts flooding ("flood")
	public static void Note(DamageableSea ds, string kind)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount)
		{
			return;
		}
		if (kind == "destroyed")
		{
			h.destroyed++;
		}
		else if (kind == "fire")
		{
			h.fires++;
		}
		else if (kind == "flood")
		{
			h.floods++;
		}
	}

	// Called by ModCrew when a ship sinks
	public static void Sunk(Unit u)
	{
		try
		{
			if (u == null)
			{
				return;
			}
			bool player = (int)u.faction == 0;
			string colour = player ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
			ModHitLog.Add(ModHitLog.Paint("<b>" + ModHitLog.ShipName(u) + " SINKING</b>", colour));
		}
		catch
		{
		}
	}

	// ---------- every frame (from ModRescue) ----------

	public static void Tick()
	{
		if (Input.GetKeyDown(KeyCode.F2))
		{
			ModHitLog.visible = !ModHitLog.visible;
		}
		if (ModHitLog.current != null && ModHitLog.current.frame != Time.frameCount)
		{
			ModHitLog.Finish();
		}
	}

	public static void Draw()
	{
		if (!ModHitLog.visible || ModHitLog.lines.Count == 0)
		{
			return;
		}
		if (ModHitLog.style == null)
		{
			ModHitLog.style = new GUIStyle(GUI.skin.label);
			ModHitLog.style.richText = true;
			ModHitLog.style.fontSize = 13;
			ModHitLog.style.wordWrap = false;
			ModHitLog.boxStyle = new GUIStyle(GUI.skin.box);
		}
		string text = "<b>HIT LOG</b>  (F2 to hide)";
		for (int i = 0; i < ModHitLog.lines.Count; i++)
		{
			text += "\n" + ModHitLog.lines[i];
		}
		// as wide as the longest line, up to 60% of the screen
		float width = 300f;
		for (int i = 0; i < ModHitLog.lines.Count; i++)
		{
			float w = ModHitLog.style.CalcSize(new GUIContent(ModHitLog.lines[i])).x + 24f;
			if (w > width)
			{
				width = w;
			}
		}
		width = Mathf.Min(width, (float)Screen.width * 0.6f);
		float height = 22f + 17f * (float)Mathf.Max(1, ModHitLog.lines.Count);
		Rect r = new Rect((float)Screen.width - width - 70f, 10f, width, height);
		GUI.Box(r, GUIContent.none, ModHitLog.boxStyle);
		GUI.Label(new Rect(r.x + 8f, r.y + 3f, r.width - 12f, r.height - 4f), text, ModHitLog.style);
	}

	// ---------- helpers ----------

	// Colours used in the panel
	public const string ColourOwn = "#80b8ff";
	public const string ColourEnemy = "#ff7070";
	public const string ColourArmour = "#b0b0b0";
	public const string ColourDamage = "#ffe070";
	public const string ColourDestroyed = "#ff9a40";
	public const string ColourFire = "#ff8c1a";
	public const string ColourFlood = "#40d0ff";
	public const string ColourTorpedo = "#ffffff";

	public static string Paint(string text, string colour)
	{
		return "<color=" + colour + ">" + text + "</color>";
	}

	public static void Finish()
	{
		ModHitLog.Hit h = ModHitLog.current;
		ModHitLog.current = null;
		if (h == null)
		{
			return;
		}
		if (h.nearMiss && h.cells == 0 && h.fires == 0 && h.floods == 0)
		{
			return;
		}
		string result;
		bool damaged = h.cells > 0 && h.damage >= h.expected * ModHitLog.ArmourHeldShare;
		if (!damaged && h.destroyed == 0)
		{
			string held = h.nearMiss ? "near miss" : ((h.what == "torpedo") ? "torpedo defence held" : "armour held");
			result = ModHitLog.Paint(held, ModHitLog.ColourArmour);
		}
		else
		{
			// torpedoes often destroy compartments directly, without the normal compartment damage
			result = damaged ? ModHitLog.Paint(h.cells + ((h.cells == 1) ? " compartment" : " compartments") + " damaged (" + Mathf.RoundToInt(h.damage) + ")", ModHitLog.ColourDamage) : string.Empty;
			if (h.destroyed > 0)
			{
				result += ((result != string.Empty) ? ", " : string.Empty) + ModHitLog.Paint("<b>" + h.destroyed + " destroyed</b>", ModHitLog.ColourDestroyed);
			}
			if (h.nearMiss)
			{
				result = "near miss: " + result;
			}
		}
		// a shell can start a fire or flooding even when the armour holds
		if (h.fires > 0)
		{
			result += ", " + ModHitLog.Paint("<b>fire</b>", ModHitLog.ColourFire);
		}
		if (h.floods > 0)
		{
			result += ", " + ModHitLog.Paint("<b>flooding</b>", ModHitLog.ColourFlood);
		}
		string targetColour = h.playerShip ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string firerColour = (h.firerSide == 0) ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string what = (h.what == "torpedo") ? ModHitLog.Paint("<b>torpedo</b>", ModHitLog.ColourTorpedo) : h.what;
		string by = (h.firer != string.Empty) ? (" from " + ModHitLog.Paint(h.firer, firerColour)) : string.Empty;
		string line = ModHitLog.Paint(h.target, targetColour) + " hit by " + what + by + ": " + result;
		ModHitLog.Add(line);
		UnityEngine.Debug.Log("[HITLOG] " + h.target + " hit by " + h.what + " from " + h.firer + ": " + h.cells + " cells, damage " + h.damage.ToString("F0") + " of " + h.expected.ToString("F0") + ", destroyed " + h.destroyed + ", fires " + h.fires + ", floods " + h.floods);
	}

	public static void Add(string line)
	{
		string time = string.Empty;
		try
		{
			time = EngagementManager.instance.dateTime.ToString("HH:mm") + " ";
		}
		catch
		{
		}
		ModHitLog.lines.Add(time + line);
		while (ModHitLog.lines.Count > ModHitLog.MaxLines)
		{
			ModHitLog.lines.RemoveAt(0);
		}
	}

	public static void Clear()
	{
		ModHitLog.lines.Clear();
		ModHitLog.current = null;
	}

	public static string ShipName(Unit u)
	{
		if (u == null)
		{
			return "?";
		}
		if ((int)u.faction != 0 && !u.identified)
		{
			return "Unidentified ship";
		}
		return u.unitInstanceName;
	}

	public static string FirerName(int id, out int side)
	{
		side = -1;
		try
		{
			List<Unit>[] lists = new List<Unit>[] { EngagementManager.instance.playerUnits, EngagementManager.instance.otherUnits };
			for (int l = 0; l < lists.Length; l++)
			{
				List<Unit> list = lists[l];
				for (int i = 0; i < list.Count; i++)
				{
					if ((object)list[i] != null && list[i].unitID == id)
					{
						side = (int)list[i].faction;
						if (list[i].unitAir != null)
						{
							return ((int)list[i].faction == 0) ? "our aircraft" : "enemy aircraft";
						}
						return ModHitLog.ShipName(list[i]);
					}
				}
			}
		}
		catch
		{
		}
		return string.Empty;
	}
}
```
3. Click **Compile**, then **File > Save Module**. **Close dnSpy, reopen it and reopen the DLL.**

### Step 2 - ModCrew (replace the class)
Five small additions: it tells the hit log about fires, flooding, destroyed compartments and sinkings, and clears it between battles.
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

	// ---------------- survivors (v0.18.3) ----------------

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
3. Click **Compile**, then **File > Save Module**.

### Step 3 - ModRescue (replace the class)
It now runs the hit log every frame and draws the panel.
1. Right-click class **ModRescue** > **Edit Class (C#)...** (check the title says *ModRescue*, not ModCampaignRescue)
2. Select everything and paste this over it:
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
3. Click **Compile**, then **File > Save Module**.

### Steps 4-5 - one line at the start of each method
For each method below, right-click it > **Edit Method (C#)...**, click just after the opening `{`, press Enter, paste the line and click **Compile**.

| Step | Class | Method | Line to paste |
|---|---|---|---|
| 4 | DamageableSea | **ApplyDamage** | `ModHitLog.BeginHit(this, ammunitionDamage, directHit);` |
| 5 | DamageableSea | **ApplyDamageToCell** | `ModHitLog.CellDamage(this, cv, amount);` |

Then **File > Save Module**. **ApplyDamage** is a very long method. If Compile shows a red error in the game's own code (like the `.main` / `.shape` ones before), send me a screenshot.

**Testing**
1. Start a battle and open fire. The panel should appear at the top right with the first hit.
2. Press **F2** to hide and show it.
3. Check that a heavy shell on a battleship belt sometimes shows **armour held**, and that a torpedo hit shows flooding.
4. Send me the `output_log.txt` after a battle. The `[HITLOG]` lines show the numbers behind each line, so we can tune the "armour held" threshold.

**Tuning:** `MaxLines` (9) and `ArmourHeldShare` (0.3) at the top of ModHitLog. (From v0.19.1 the number of lines is `MaxHitLines` in ModLogTabs.)

---

## v0.19.1 - Message log tabs

**What it does:** the hit log moves out of its own panel and into the game's battle message log, as a second tab.
- Two tabs sit on the top edge of the message log (bottom left of the battle screen), at its right-hand end above the pause and speed buttons: **General** (the game's own messages, as before) and **Hit log** (the hit lines from v0.19, same colours and wording). If the message log is at the top of the screen, the tabs go on its bottom edge instead.
- Click a tab, or press **F2**, to switch. The open tab is highlighted.
- A closed tab counts new lines, for example **Hit log (3)**, so you can see hits are coming in while reading General, and the other way round.
- The hit log keeps the last **25** hits (the game's message log also keeps 25), uses the game's timestamp setting, and is cleared at the start of each battle.
- The old top-right panel is gone.
- `[LOGTABS]` lines in `output_log.txt`: one when the tabs are added (with the message log's position on screen) and one each time you switch tab.

**How it works:** hit lines are made from the same text prefab the game uses for its messages and placed in the same scroll list. Switching tab hides one set of lines and shows the other. The tabs follow the message log when you minimise it.

**Install (dnSpy).** Back up the DLL first. ModRescue and the two ApplyDamage lines from v0.19 stay as they are.

### Step 1 - new class ModLogTabs
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Delete everything in the window and paste the code below.
3. Click **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

// v0.19.1: tabs on the game's battle message log - "General" (the game's own messages) and "Hit log"
public class ModLogTabs
{
	// How many hit log lines the tab keeps
	public const int MaxHitLines = 25;

	public static List<GameObject> hitObjects = new List<GameObject>();
	public static bool showHits = false;
	public static int unreadHits = 0;
	public static int unreadGeneral = 0;
	public static object lastGeneral;

	public static RectTransform bar;
	public static Button generalButton;
	public static Button hitButton;
	public static Text generalText;
	public static Text hitText;
	public static MessageLog builtFor;

	// ---------- called from ModHitLog ----------

	// Every frame, from ModHitLog.Tick
	public static void Tick()
	{
		try
		{
			MessageLog log = MessageLog.instance;
			if (log == null || log.messageLogPanel == null || log.chatPanel == null)
			{
				return;
			}
			if (ModLogTabs.bar == null || ModLogTabs.builtFor != log)
			{
				ModLogTabs.Build(log);
			}
			ModLogTabs.PlaceBar(log);
			List<Message> list = ModLogTabs.GameMessages(log);
			if (list == null)
			{
				return;
			}
			// keep the game's own messages hidden while the Hit log tab is open
			for (int i = 0; i < list.Count; i++)
			{
				Message m = list[i];
				if (m != null && m.textObject != null && m.textObject.gameObject.activeSelf == ModLogTabs.showHits)
				{
					m.textObject.gameObject.SetActive(!ModLogTabs.showHits);
				}
			}
			// count new game messages that arrive while the Hit log tab is open
			object newest = (list.Count > 0) ? list[list.Count - 1] : null;
			if (newest != ModLogTabs.lastGeneral)
			{
				if (ModLogTabs.showHits && newest != null)
				{
					ModLogTabs.unreadGeneral++;
				}
				ModLogTabs.lastGeneral = newest;
			}
			// remove destroyed lines
			for (int i = ModLogTabs.hitObjects.Count - 1; i >= 0; i--)
			{
				if (ModLogTabs.hitObjects[i] == null)
				{
					ModLogTabs.hitObjects.RemoveAt(i);
				}
			}
			ModLogTabs.UpdateLabels();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] tick failed: " + ex.Message);
			ModLogTabs.bar = null;
		}
	}

	// Adds one line to the Hit log tab
	public static void AddHit(string line)
	{
		try
		{
			MessageLog log = MessageLog.instance;
			if (log == null || log.textObject == null || log.chatPanel == null)
			{
				return;
			}
			GameObject go = Object.Instantiate<GameObject>(log.textObject, log.chatPanel.transform);
			go.name = "ModHitLine";
			Text t = go.GetComponent<Text>();
			if (t != null)
			{
				t.supportRichText = true;
				// the prefab's own text colour is see-through (the game always adds a colour), so give the plain parts one
				t.text = "<color=#dcdcdc>" + line + "</color>";
			}
			// hit lines have no "go to unit" button
			Button b = go.GetComponentInChildren<Button>(true);
			if (b != null)
			{
				b.onClick.RemoveAllListeners();
				b.gameObject.SetActive(false);
			}
			go.SetActive(ModLogTabs.showHits);
			ModLogTabs.hitObjects.Add(go);
			while (ModLogTabs.hitObjects.Count > ModLogTabs.MaxHitLines)
			{
				if (ModLogTabs.hitObjects[0] != null)
				{
					Object.Destroy(ModLogTabs.hitObjects[0]);
				}
				ModLogTabs.hitObjects.RemoveAt(0);
			}
			if (!ModLogTabs.showHits)
			{
				ModLogTabs.unreadHits++;
			}
			ModLogTabs.UpdateLabels();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] add failed: " + ex.Message);
		}
	}

	// New battle: remove the old hit lines
	public static void Clear()
	{
		for (int i = 0; i < ModLogTabs.hitObjects.Count; i++)
		{
			if (ModLogTabs.hitObjects[i] != null)
			{
				Object.Destroy(ModLogTabs.hitObjects[i]);
			}
		}
		ModLogTabs.hitObjects.Clear();
		ModLogTabs.unreadHits = 0;
		ModLogTabs.unreadGeneral = 0;
		ModLogTabs.UpdateLabels();
	}

	// F2 switches between the two tabs
	public static void Toggle()
	{
		if (ModLogTabs.showHits)
		{
			ModLogTabs.ShowGeneral();
		}
		else
		{
			ModLogTabs.ShowHits();
		}
	}

	public static void ShowGeneral()
	{
		ModLogTabs.Switch(false);
	}

	public static void ShowHits()
	{
		ModLogTabs.Switch(true);
	}

	// ---------- helpers ----------

	public static System.Reflection.FieldInfo listField;

	// The game's message list is private, so it is read this way
	public static List<Message> GameMessages(MessageLog log)
	{
		if (ModLogTabs.listField == null)
		{
			ModLogTabs.listField = typeof(MessageLog).GetField("messageList", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);
		}
		if (ModLogTabs.listField == null)
		{
			return null;
		}
		return ModLogTabs.listField.GetValue(log) as List<Message>;
	}

	public static void Switch(bool hits)
	{
		try
		{
			ModLogTabs.showHits = hits;
			if (hits)
			{
				ModLogTabs.unreadHits = 0;
			}
			else
			{
				ModLogTabs.unreadGeneral = 0;
			}
			for (int i = 0; i < ModLogTabs.hitObjects.Count; i++)
			{
				if (ModLogTabs.hitObjects[i] != null)
				{
					ModLogTabs.hitObjects[i].SetActive(hits);
				}
			}
			MessageLog log = MessageLog.instance;
			List<Message> list = (log != null) ? ModLogTabs.GameMessages(log) : null;
			if (list != null)
			{
				for (int i = 0; i < list.Count; i++)
				{
					Message m = list[i];
					if (m != null && m.textObject != null)
					{
						m.textObject.gameObject.SetActive(!hits);
					}
				}
				if (log.logScrollbar != null)
				{
					log.logScrollbar.value = 0f;
				}
			}
			ModLogTabs.UpdateLabels();
			UnityEngine.Debug.Log("[LOGTABS] tab " + (hits ? "Hit log" : "General"));
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] switch failed: " + ex.Message);
		}
	}

	public static void Build(MessageLog log)
	{
		if (ModLogTabs.bar != null)
		{
			Object.Destroy(ModLogTabs.bar.gameObject);
		}
		Font font = null;
		Text sample = log.textObject.GetComponent<Text>();
		if (sample != null)
		{
			font = sample.font;
		}
		if (font == null)
		{
			font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		}
		GameObject barObject = new GameObject("ModLogTabs", new System.Type[] { typeof(RectTransform) });
		barObject.transform.SetParent(log.messageLogPanel.parent, false);
		ModLogTabs.bar = barObject.GetComponent<RectTransform>();
		ModLogTabs.bar.anchorMin = new Vector2(0.5f, 0.5f);
		ModLogTabs.bar.anchorMax = new Vector2(0.5f, 0.5f);
		ModLogTabs.bar.pivot = new Vector2(0f, 0f);
		ModLogTabs.bar.sizeDelta = new Vector2(232f, 22f);
		LayoutElement le = barObject.AddComponent<LayoutElement>();
		le.ignoreLayout = true;
		ModLogTabs.generalButton = ModLogTabs.MakeTab(barObject.transform, "General", 0f, font, out ModLogTabs.generalText);
		ModLogTabs.generalButton.onClick.AddListener(new UnityAction(ModLogTabs.ShowGeneral));
		ModLogTabs.hitButton = ModLogTabs.MakeTab(barObject.transform, "Hit log", 116f, font, out ModLogTabs.hitText);
		ModLogTabs.hitButton.onClick.AddListener(new UnityAction(ModLogTabs.ShowHits));
		ModLogTabs.builtFor = log;
		barObject.transform.SetAsLastSibling();
		ModLogTabs.PlaceBar(log);
		ModLogTabs.UpdateLabels();
		Vector3[] c = new Vector3[4];
		log.messageLogPanel.GetWorldCorners(c);
		UnityEngine.Debug.Log("[LOGTABS] tabs added, message log panel from " + c[0] + " to " + c[2] + ", screen " + Screen.width + "x" + Screen.height);
	}

	public static Button MakeTab(Transform parent, string label, float x, Font font, out Text text)
	{
		GameObject go = new GameObject("ModTab " + label, new System.Type[] { typeof(RectTransform) });
		go.transform.SetParent(parent, false);
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.anchorMin = new Vector2(0f, 0f);
		rt.anchorMax = new Vector2(0f, 0f);
		rt.pivot = new Vector2(0f, 0f);
		rt.anchoredPosition = new Vector2(x, 0f);
		rt.sizeDelta = new Vector2(112f, 22f);
		Image img = go.AddComponent<Image>();
		img.color = new Color(0f, 0f, 0f, 0.6f);
		Button b = go.AddComponent<Button>();
		b.targetGraphic = img;
		GameObject textObject = new GameObject("Label", new System.Type[] { typeof(RectTransform) });
		textObject.transform.SetParent(go.transform, false);
		RectTransform trt = textObject.GetComponent<RectTransform>();
		trt.anchorMin = Vector2.zero;
		trt.anchorMax = Vector2.one;
		trt.offsetMin = Vector2.zero;
		trt.offsetMax = Vector2.zero;
		text = textObject.AddComponent<Text>();
		text.font = font;
		text.fontSize = 13;
		text.alignment = TextAnchor.MiddleCenter;
		text.supportRichText = true;
		text.raycastTarget = false;
		text.text = label;
		return b;
	}

	// Keeps the tabs on the top right edge of the message log (or the bottom edge if the log is at the top of the screen)
	public static void PlaceBar(MessageLog log)
	{
		Vector3[] c = new Vector3[4];
		log.messageLogPanel.GetWorldCorners(c);
		// right-hand end, so the tabs stay clear of the ship list buttons on the left
		if (c[2].y + 24f > (float)Screen.height)
		{
			ModLogTabs.bar.pivot = new Vector2(1f, 1f);
			ModLogTabs.bar.position = c[3];
		}
		else
		{
			ModLogTabs.bar.pivot = new Vector2(1f, 0f);
			ModLogTabs.bar.position = c[2];
		}
	}

	public static void UpdateLabels()
	{
		if (ModLogTabs.generalText == null || ModLogTabs.hitText == null)
		{
			return;
		}
		ModLogTabs.generalText.text = ModLogTabs.Label("General", ModLogTabs.unreadGeneral, !ModLogTabs.showHits);
		ModLogTabs.hitText.text = ModLogTabs.Label("Hit log", ModLogTabs.unreadHits, ModLogTabs.showHits);
		ModLogTabs.generalButton.targetGraphic.color = ModLogTabs.showHits ? new Color(0f, 0f, 0f, 0.45f) : new Color(0.2f, 0.3f, 0.45f, 0.9f);
		ModLogTabs.hitButton.targetGraphic.color = ModLogTabs.showHits ? new Color(0.2f, 0.3f, 0.45f, 0.9f) : new Color(0f, 0f, 0f, 0.45f);
	}

	public static string Label(string name, int unread, bool open)
	{
		string text = open ? ("<b>" + name + "</b>") : ("<color=#b0b0b0>" + name + "</color>");
		if (unread > 0 && !open)
		{
			text += " <color=#ffe070>(" + unread + ")</color>";
		}
		return text;
	}
}
```

### Step 2 - ModHitLog (replace the class)
1. Right-click class **ModHitLog** > **Edit Class (C#)...**
2. Select all, delete, and paste the code below.
3. Click **Compile**, then **File > Save Module**.
4. Close dnSpy and open it again (a class was added and fields were removed).

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModHitLog
{
	public class Hit
	{
		public DamageableSea ds;
		public int frame;
		public string target;
		public bool playerShip;
		public string what;
		public string firer;
		public int firerSide = -1;
		public float expected;
		public float damage;
		public int cells;
		public int destroyed;
		public int fires;
		public int floods;
		public bool nearMiss;
	}

	// A hit doing less than this share of the shell's damage counts as "armour held"
	public const float ArmourHeldShare = 0.3f;

	public static ModHitLog.Hit current;

	// ---------- called from the game ----------

	// First line of DamageableSea.ApplyDamage
	public static void BeginHit(DamageableSea ds, AmmunitionDamage ammo, bool directHit)
	{
		try
		{
			ModHitLog.Finish();
			if (ds == null || ds.parentUnit == null || ammo == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModHitLog.Hit h = new ModHitLog.Hit();
			h.ds = ds;
			h.frame = Time.frameCount;
			Unit target = ds.parentUnit;
			h.playerShip = (int)target.faction == 0;
			h.target = ModHitLog.ShipName(target);
			if (ammo.isTorpedo)
			{
				h.what = "torpedo";
			}
			else if (ammo.isBomb)
			{
				h.what = "bomb";
			}
			else if (ammo.isdepthCharge)
			{
				h.what = "depth charge";
			}
			else if (ammo.armorPiercing)
			{
				h.what = "AP shell";
			}
			else
			{
				h.what = "HE shell";
			}
			h.firer = ModHitLog.FirerName(ammo.firedByUnitID, out h.firerSide);
			h.expected = ammo.damageAmount;
			h.nearMiss = !directHit && !ammo.isTorpedo;
			ModHitLog.current = h;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[HITLOG] begin failed: " + ex.Message);
		}
	}

	// First line of DamageableSea.ApplyDamageToCell
	public static void CellDamage(DamageableSea ds, CellVariable cv, float amount)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount || amount <= 0f)
		{
			return;
		}
		h.damage += amount;
		h.cells++;
	}

	// Called by ModCrew when a compartment is destroyed ("destroyed"), catches fire ("fire") or starts flooding ("flood")
	public static void Note(DamageableSea ds, string kind)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount)
		{
			return;
		}
		if (kind == "destroyed")
		{
			h.destroyed++;
		}
		else if (kind == "fire")
		{
			h.fires++;
		}
		else if (kind == "flood")
		{
			h.floods++;
		}
	}

	// Called by ModCrew when a ship sinks
	public static void Sunk(Unit u)
	{
		try
		{
			if (u == null)
			{
				return;
			}
			bool player = (int)u.faction == 0;
			string colour = player ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
			ModHitLog.Add(ModHitLog.Paint("<b>" + ModHitLog.ShipName(u) + " SINKING</b>", colour));
		}
		catch
		{
		}
	}

	// ---------- every frame (from ModRescue) ----------

	public static void Tick()
	{
		if (Input.GetKeyDown(KeyCode.F2))
		{
			ModLogTabs.Toggle();
		}
		if (ModHitLog.current != null && ModHitLog.current.frame != Time.frameCount)
		{
			ModHitLog.Finish();
		}
		ModLogTabs.Tick();
	}

	// v0.19.1: the hit log now lives in a tab on the game's message log, so the old panel is gone
	public static void Draw()
	{
	}

	// ---------- helpers ----------

	// Colours used in the panel
	public const string ColourOwn = "#80b8ff";
	public const string ColourEnemy = "#ff7070";
	public const string ColourArmour = "#b0b0b0";
	public const string ColourDamage = "#ffe070";
	public const string ColourDestroyed = "#ff9a40";
	public const string ColourFire = "#ff8c1a";
	public const string ColourFlood = "#40d0ff";
	public const string ColourTorpedo = "#ffffff";

	public static string Paint(string text, string colour)
	{
		return "<color=" + colour + ">" + text + "</color>";
	}

	public static void Finish()
	{
		ModHitLog.Hit h = ModHitLog.current;
		ModHitLog.current = null;
		if (h == null)
		{
			return;
		}
		if (h.nearMiss && h.cells == 0 && h.fires == 0 && h.floods == 0)
		{
			return;
		}
		string result;
		bool damaged = h.cells > 0 && h.damage >= h.expected * ModHitLog.ArmourHeldShare;
		if (!damaged && h.destroyed == 0)
		{
			string held = h.nearMiss ? "near miss" : ((h.what == "torpedo") ? "torpedo defence held" : "armour held");
			result = ModHitLog.Paint(held, ModHitLog.ColourArmour);
		}
		else
		{
			// torpedoes often destroy compartments directly, without the normal compartment damage
			result = damaged ? ModHitLog.Paint(h.cells + ((h.cells == 1) ? " compartment" : " compartments") + " damaged (" + Mathf.RoundToInt(h.damage) + ")", ModHitLog.ColourDamage) : string.Empty;
			if (h.destroyed > 0)
			{
				result += ((result != string.Empty) ? ", " : string.Empty) + ModHitLog.Paint("<b>" + h.destroyed + " destroyed</b>", ModHitLog.ColourDestroyed);
			}
			if (h.nearMiss)
			{
				result = "near miss: " + result;
			}
		}
		// a shell can start a fire or flooding even when the armour holds
		if (h.fires > 0)
		{
			result += ", " + ModHitLog.Paint("<b>fire</b>", ModHitLog.ColourFire);
		}
		if (h.floods > 0)
		{
			result += ", " + ModHitLog.Paint("<b>flooding</b>", ModHitLog.ColourFlood);
		}
		string targetColour = h.playerShip ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string firerColour = (h.firerSide == 0) ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string what = (h.what == "torpedo") ? ModHitLog.Paint("<b>torpedo</b>", ModHitLog.ColourTorpedo) : h.what;
		string by = (h.firer != string.Empty) ? (" from " + ModHitLog.Paint(h.firer, firerColour)) : string.Empty;
		string line = ModHitLog.Paint(h.target, targetColour) + " hit by " + what + by + ": " + result;
		ModHitLog.Add(line);
		UnityEngine.Debug.Log("[HITLOG] " + h.target + " hit by " + h.what + " from " + h.firer + ": " + h.cells + " cells, damage " + h.damage.ToString("F0") + " of " + h.expected.ToString("F0") + ", destroyed " + h.destroyed + ", fires " + h.fires + ", floods " + h.floods);
	}

	public static void Add(string line)
	{
		string time = string.Empty;
		try
		{
			if (Config.instance.timeStampMessageLog)
			{
				time = Utilities.GetDateTimeText(EngagementManager.instance.dateTime, Config.instance.timeFormat) + " ";
			}
		}
		catch
		{
		}
		ModLogTabs.AddHit(time + line);
	}

	public static void Clear()
	{
		ModHitLog.current = null;
		ModLogTabs.Clear();
	}

	public static string ShipName(Unit u)
	{
		if (u == null)
		{
			return "?";
		}
		if ((int)u.faction != 0 && !u.identified)
		{
			return "Unidentified ship";
		}
		return u.unitInstanceName;
	}

	public static string FirerName(int id, out int side)
	{
		side = -1;
		try
		{
			List<Unit>[] lists = new List<Unit>[] { EngagementManager.instance.playerUnits, EngagementManager.instance.otherUnits };
			for (int l = 0; l < lists.Length; l++)
			{
				List<Unit> list = lists[l];
				for (int i = 0; i < list.Count; i++)
				{
					if ((object)list[i] != null && list[i].unitID == id)
					{
						side = (int)list[i].faction;
						if (list[i].unitAir != null)
						{
							return ((int)list[i].faction == 0) ? "our aircraft" : "enemy aircraft";
						}
						return ModHitLog.ShipName(list[i]);
					}
				}
			}
		}
		catch
		{
		}
		return string.Empty;
	}
}
```

**Testing**
1. Start a battle. Two tabs, **General** and **Hit log**, should appear on the edge of the message log.
2. Open fire. While General is open, the Hit log tab should count up: **Hit log (1)**, **(2)** and so on.
3. Click **Hit log** (or press F2). The game's messages disappear and the hit lines show, with their colours.
4. Click **General**. The game's messages come back, and the hit lines hide.
5. Minimise the message log. The tabs should stay on its edge.
6. If the tabs are in the wrong place, or don't show, send a screenshot and `output_log.txt` (the `[LOGTABS] tabs added` line gives the message log's position).

---

## v0.19.2 - Crew tab and a cleaner hit log

**What it does:**
- **Crew tab:** a third tab on the message log, next to General and Hit log. **F2** now steps through General > Hit log > Crew. It lists, for your ships:
  - **Casualties**, one line per ship once the hits stop for 2 seconds: `Mahan: 6 men lost (fire, flooding), 312 / 329 aboard`
  - **Short-handed** warnings when a ship drops below 90% crew (slower reloads and repairs), and when it loses a damage control party: `Mahan is down to 2 of 3 damage control parties`
  - Ships that **start the battle short-handed**.
  - **Survivors and rescues** (the orange and green lines), which used to go to General.
- **Cleaner hit log:** each line reads attacker, action, target, result, with no damage numbers:
  ```
  12:02 Monaghan hit Dale with an HE shell: armour held, fire, flooding
  12:03 Lang hit Mustin with a torpedo: 2 compartments destroyed, flooding
  12:04 Our aircraft hit Chokai with a bomb: damaged, fire
  12:05 Dale was hit by an HE shell: damaged
  ```
  - Results: **damaged**, **armour held**, **torpedo defence held**, **compartment(s) destroyed**, **fire**, **flooding**. A near miss reads "near-missed".
  - When the attacker isn't known, the line reads "Dale was hit by ...".
  - The exact numbers are still written to `output_log.txt` in the `[HITLOG]` lines.
- `[LOGTABS]` and `[CREW]` log lines as before.

**Install (dnSpy).** Back up the DLL first, and do the steps in this order (ModCrew needs the new ModLogTabs).

### Step 1 - ModLogTabs (replace the class)
1. Right-click class **ModLogTabs** > **Edit Class (C#)...**
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

// v0.19.1: tabs on the game's battle message log
// v0.19.2: third tab "Crew" for casualties, short-handed ships, survivors and rescues
public class ModLogTabs
{
	public const int General = 0;
	public const int Hits = 1;
	public const int Crew = 2;

	// How many lines each mod tab keeps
	public const int MaxLines = 25;
	public const float TabWidth = 92f;

	public static string[] names = new string[] { "General", "Hit log", "Crew" };
	public static List<GameObject>[] lines = new List<GameObject>[] { new List<GameObject>(), new List<GameObject>(), new List<GameObject>() };
	public static int[] unread = new int[3];
	public static int tab = 0;
	public static object lastGeneral;

	public static RectTransform bar;
	public static Button[] buttons = new Button[3];
	public static Text[] texts = new Text[3];
	public static MessageLog builtFor;

	// ---------- called from other mod classes ----------

	// Every frame, from ModHitLog.Tick
	public static void Tick()
	{
		try
		{
			MessageLog log = MessageLog.instance;
			if (log == null || log.messageLogPanel == null || log.chatPanel == null)
			{
				return;
			}
			if (ModLogTabs.bar == null || ModLogTabs.builtFor != log)
			{
				ModLogTabs.Build(log);
			}
			ModLogTabs.PlaceBar(log);
			List<Message> list = ModLogTabs.GameMessages(log);
			if (list == null)
			{
				return;
			}
			// keep the game's own messages hidden while another tab is open
			bool showGame = ModLogTabs.tab == ModLogTabs.General;
			for (int i = 0; i < list.Count; i++)
			{
				Message m = list[i];
				if (m != null && m.textObject != null && m.textObject.gameObject.activeSelf != showGame)
				{
					m.textObject.gameObject.SetActive(showGame);
				}
			}
			// count new game messages that arrive while another tab is open
			object newest = (list.Count > 0) ? list[list.Count - 1] : null;
			if (newest != ModLogTabs.lastGeneral)
			{
				if (!showGame && newest != null)
				{
					ModLogTabs.unread[ModLogTabs.General]++;
				}
				ModLogTabs.lastGeneral = newest;
			}
			// remove destroyed lines
			for (int t = 1; t < 3; t++)
			{
				for (int i = ModLogTabs.lines[t].Count - 1; i >= 0; i--)
				{
					if (ModLogTabs.lines[t][i] == null)
					{
						ModLogTabs.lines[t].RemoveAt(i);
					}
				}
			}
			ModLogTabs.UpdateLabels();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] tick failed: " + ex.Message);
			ModLogTabs.bar = null;
		}
	}

	// Adds one line to the Hit log tab (from ModHitLog)
	public static void AddHit(string line)
	{
		ModLogTabs.AddLine(ModLogTabs.Hits, line);
	}

	// Adds one line to the Crew tab (from ModCrew), with the game's timestamp
	public static void AddCrew(string line)
	{
		string time = string.Empty;
		try
		{
			if (Config.instance.timeStampMessageLog)
			{
				time = Utilities.GetDateTimeText(EngagementManager.instance.dateTime, Config.instance.timeFormat) + " ";
			}
		}
		catch
		{
		}
		ModLogTabs.AddLine(ModLogTabs.Crew, time + line);
	}

	public static void AddLine(int t, string line)
	{
		try
		{
			MessageLog log = MessageLog.instance;
			if (log == null || log.textObject == null || log.chatPanel == null)
			{
				return;
			}
			GameObject go = Object.Instantiate<GameObject>(log.textObject, log.chatPanel.transform);
			go.name = "ModLogLine " + ModLogTabs.names[t];
			Text text = go.GetComponent<Text>();
			if (text != null)
			{
				text.supportRichText = true;
				// the prefab's own text colour is see-through (the game always adds a colour), so give the plain parts one
				text.text = "<color=#dcdcdc>" + line + "</color>";
			}
			// mod lines have no "go to unit" button
			Button b = go.GetComponentInChildren<Button>(true);
			if (b != null)
			{
				b.onClick.RemoveAllListeners();
				b.gameObject.SetActive(false);
			}
			go.SetActive(ModLogTabs.tab == t);
			ModLogTabs.lines[t].Add(go);
			while (ModLogTabs.lines[t].Count > ModLogTabs.MaxLines)
			{
				if (ModLogTabs.lines[t][0] != null)
				{
					Object.Destroy(ModLogTabs.lines[t][0]);
				}
				ModLogTabs.lines[t].RemoveAt(0);
			}
			if (ModLogTabs.tab != t)
			{
				ModLogTabs.unread[t]++;
			}
			ModLogTabs.UpdateLabels();
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] add failed: " + ex.Message);
		}
	}

	// New battle: remove the old mod lines
	public static void Clear()
	{
		for (int t = 1; t < 3; t++)
		{
			for (int i = 0; i < ModLogTabs.lines[t].Count; i++)
			{
				if (ModLogTabs.lines[t][i] != null)
				{
					Object.Destroy(ModLogTabs.lines[t][i]);
				}
			}
			ModLogTabs.lines[t].Clear();
		}
		for (int t = 0; t < 3; t++)
		{
			ModLogTabs.unread[t] = 0;
		}
		ModLogTabs.UpdateLabels();
	}

	// F2 goes to the next tab: General > Hit log > Crew > General
	public static void Toggle()
	{
		ModLogTabs.Switch((ModLogTabs.tab + 1) % 3);
	}

	public static void ShowGeneral()
	{
		ModLogTabs.Switch(ModLogTabs.General);
	}

	public static void ShowHits()
	{
		ModLogTabs.Switch(ModLogTabs.Hits);
	}

	public static void ShowCrew()
	{
		ModLogTabs.Switch(ModLogTabs.Crew);
	}

	// ---------- helpers ----------

	public static System.Reflection.FieldInfo listField;

	// The game's message list is private, so it is read this way
	public static List<Message> GameMessages(MessageLog log)
	{
		if (ModLogTabs.listField == null)
		{
			ModLogTabs.listField = typeof(MessageLog).GetField("messageList", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);
		}
		if (ModLogTabs.listField == null)
		{
			return null;
		}
		return ModLogTabs.listField.GetValue(log) as List<Message>;
	}

	public static void Switch(int t)
	{
		try
		{
			ModLogTabs.tab = t;
			ModLogTabs.unread[t] = 0;
			for (int k = 1; k < 3; k++)
			{
				for (int i = 0; i < ModLogTabs.lines[k].Count; i++)
				{
					if (ModLogTabs.lines[k][i] != null)
					{
						ModLogTabs.lines[k][i].SetActive(k == t);
					}
				}
			}
			MessageLog log = MessageLog.instance;
			List<Message> list = (log != null) ? ModLogTabs.GameMessages(log) : null;
			if (list != null)
			{
				for (int i = 0; i < list.Count; i++)
				{
					Message m = list[i];
					if (m != null && m.textObject != null)
					{
						m.textObject.gameObject.SetActive(t == ModLogTabs.General);
					}
				}
				if (log.logScrollbar != null)
				{
					log.logScrollbar.value = 0f;
				}
			}
			ModLogTabs.UpdateLabels();
			UnityEngine.Debug.Log("[LOGTABS] tab " + ModLogTabs.names[t]);
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[LOGTABS] switch failed: " + ex.Message);
		}
	}

	public static void Build(MessageLog log)
	{
		if (ModLogTabs.bar != null)
		{
			Object.Destroy(ModLogTabs.bar.gameObject);
		}
		Font font = null;
		Text sample = log.textObject.GetComponent<Text>();
		if (sample != null)
		{
			font = sample.font;
		}
		if (font == null)
		{
			font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		}
		GameObject barObject = new GameObject("ModLogTabs", new System.Type[] { typeof(RectTransform) });
		barObject.transform.SetParent(log.messageLogPanel.parent, false);
		ModLogTabs.bar = barObject.GetComponent<RectTransform>();
		ModLogTabs.bar.anchorMin = new Vector2(0.5f, 0.5f);
		ModLogTabs.bar.anchorMax = new Vector2(0.5f, 0.5f);
		ModLogTabs.bar.pivot = new Vector2(1f, 0f);
		ModLogTabs.bar.sizeDelta = new Vector2(3f * ModLogTabs.TabWidth + 4f, 22f);
		LayoutElement le = barObject.AddComponent<LayoutElement>();
		le.ignoreLayout = true;
		for (int t = 0; t < 3; t++)
		{
			ModLogTabs.buttons[t] = ModLogTabs.MakeTab(barObject.transform, ModLogTabs.names[t], (float)t * (ModLogTabs.TabWidth + 2f), font, out ModLogTabs.texts[t]);
		}
		ModLogTabs.buttons[ModLogTabs.General].onClick.AddListener(new UnityAction(ModLogTabs.ShowGeneral));
		ModLogTabs.buttons[ModLogTabs.Hits].onClick.AddListener(new UnityAction(ModLogTabs.ShowHits));
		ModLogTabs.buttons[ModLogTabs.Crew].onClick.AddListener(new UnityAction(ModLogTabs.ShowCrew));
		ModLogTabs.builtFor = log;
		barObject.transform.SetAsLastSibling();
		ModLogTabs.PlaceBar(log);
		ModLogTabs.UpdateLabels();
		Vector3[] c = new Vector3[4];
		log.messageLogPanel.GetWorldCorners(c);
		UnityEngine.Debug.Log("[LOGTABS] tabs added, message log panel from " + c[0] + " to " + c[2] + ", screen " + Screen.width + "x" + Screen.height);
	}

	public static Button MakeTab(Transform parent, string label, float x, Font font, out Text text)
	{
		GameObject go = new GameObject("ModTab " + label, new System.Type[] { typeof(RectTransform) });
		go.transform.SetParent(parent, false);
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.anchorMin = new Vector2(0f, 0f);
		rt.anchorMax = new Vector2(0f, 0f);
		rt.pivot = new Vector2(0f, 0f);
		rt.anchoredPosition = new Vector2(x, 0f);
		rt.sizeDelta = new Vector2(ModLogTabs.TabWidth, 22f);
		Image img = go.AddComponent<Image>();
		img.color = new Color(0f, 0f, 0f, 0.6f);
		Button b = go.AddComponent<Button>();
		b.targetGraphic = img;
		GameObject textObject = new GameObject("Label", new System.Type[] { typeof(RectTransform) });
		textObject.transform.SetParent(go.transform, false);
		RectTransform trt = textObject.GetComponent<RectTransform>();
		trt.anchorMin = Vector2.zero;
		trt.anchorMax = Vector2.one;
		trt.offsetMin = Vector2.zero;
		trt.offsetMax = Vector2.zero;
		text = textObject.AddComponent<Text>();
		text.font = font;
		text.fontSize = 13;
		text.alignment = TextAnchor.MiddleCenter;
		text.supportRichText = true;
		text.raycastTarget = false;
		text.text = label;
		return b;
	}

	// Keeps the tabs on the top right edge of the message log (or the bottom edge if the log is at the top of the screen)
	public static void PlaceBar(MessageLog log)
	{
		Vector3[] c = new Vector3[4];
		log.messageLogPanel.GetWorldCorners(c);
		// right-hand end, so the tabs stay clear of the ship list buttons on the left
		if (c[2].y + 24f > (float)Screen.height)
		{
			ModLogTabs.bar.pivot = new Vector2(1f, 1f);
			ModLogTabs.bar.position = c[3];
		}
		else
		{
			ModLogTabs.bar.pivot = new Vector2(1f, 0f);
			ModLogTabs.bar.position = c[2];
		}
	}

	public static void UpdateLabels()
	{
		for (int t = 0; t < 3; t++)
		{
			if (ModLogTabs.texts[t] == null || ModLogTabs.buttons[t] == null)
			{
				return;
			}
		}
		for (int t = 0; t < 3; t++)
		{
			bool open = ModLogTabs.tab == t;
			ModLogTabs.texts[t].text = ModLogTabs.Label(ModLogTabs.names[t], ModLogTabs.unread[t], open);
			ModLogTabs.buttons[t].targetGraphic.color = open ? new Color(0.2f, 0.3f, 0.45f, 0.9f) : new Color(0f, 0f, 0f, 0.45f);
		}
	}

	public static string Label(string name, int count, bool open)
	{
		string text = open ? ("<b>" + name + "</b>") : ("<color=#b0b0b0>" + name + "</color>");
		if (count > 0 && !open)
		{
			text += " <color=#ffe070>(" + count + ")</color>";
		}
		return text;
	}
}
```

### Step 2 - ModHitLog (replace the class)
1. Right-click class **ModHitLog** > **Edit Class (C#)...**
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ModHitLog
{
	public class Hit
	{
		public DamageableSea ds;
		public int frame;
		public string target;
		public bool playerShip;
		public string what;
		public string firer;
		public int firerSide = -1;
		public float expected;
		public float damage;
		public int cells;
		public int destroyed;
		public int fires;
		public int floods;
		public bool nearMiss;
	}

	// A hit doing less than this share of the shell's damage counts as "armour held"
	public const float ArmourHeldShare = 0.3f;

	public static ModHitLog.Hit current;

	// ---------- called from the game ----------

	// First line of DamageableSea.ApplyDamage
	public static void BeginHit(DamageableSea ds, AmmunitionDamage ammo, bool directHit)
	{
		try
		{
			ModHitLog.Finish();
			if (ds == null || ds.parentUnit == null || ammo == null || ds.parentUnit.isDestroyed)
			{
				return;
			}
			ModHitLog.Hit h = new ModHitLog.Hit();
			h.ds = ds;
			h.frame = Time.frameCount;
			Unit target = ds.parentUnit;
			h.playerShip = (int)target.faction == 0;
			h.target = ModHitLog.ShipName(target);
			if (ammo.isTorpedo)
			{
				h.what = "torpedo";
			}
			else if (ammo.isBomb)
			{
				h.what = "bomb";
			}
			else if (ammo.isdepthCharge)
			{
				h.what = "depth charge";
			}
			else if (ammo.armorPiercing)
			{
				h.what = "AP shell";
			}
			else
			{
				h.what = "HE shell";
			}
			h.firer = ModHitLog.FirerName(ammo.firedByUnitID, out h.firerSide);
			h.expected = ammo.damageAmount;
			h.nearMiss = !directHit && !ammo.isTorpedo;
			ModHitLog.current = h;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[HITLOG] begin failed: " + ex.Message);
		}
	}

	// First line of DamageableSea.ApplyDamageToCell
	public static void CellDamage(DamageableSea ds, CellVariable cv, float amount)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount || amount <= 0f)
		{
			return;
		}
		h.damage += amount;
		h.cells++;
	}

	// Called by ModCrew when a compartment is destroyed ("destroyed"), catches fire ("fire") or starts flooding ("flood")
	public static void Note(DamageableSea ds, string kind)
	{
		ModHitLog.Hit h = ModHitLog.current;
		if (h == null || h.ds != ds || h.frame != Time.frameCount)
		{
			return;
		}
		if (kind == "destroyed")
		{
			h.destroyed++;
		}
		else if (kind == "fire")
		{
			h.fires++;
		}
		else if (kind == "flood")
		{
			h.floods++;
		}
	}

	// Called by ModCrew when a ship sinks
	public static void Sunk(Unit u)
	{
		try
		{
			if (u == null)
			{
				return;
			}
			bool player = (int)u.faction == 0;
			string colour = player ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
			ModHitLog.Add(ModHitLog.Paint("<b>" + ModHitLog.ShipName(u) + " SINKING</b>", colour));
		}
		catch
		{
		}
	}

	// ---------- every frame (from ModRescue) ----------

	public static void Tick()
	{
		if (Input.GetKeyDown(KeyCode.F2))
		{
			ModLogTabs.Toggle();
		}
		if (ModHitLog.current != null && ModHitLog.current.frame != Time.frameCount)
		{
			ModHitLog.Finish();
		}
		ModLogTabs.Tick();
	}

	// v0.19.1: the hit log now lives in a tab on the game's message log, so the old panel is gone
	public static void Draw()
	{
	}

	// ---------- helpers ----------

	// Colours used in the panel
	public const string ColourOwn = "#80b8ff";
	public const string ColourEnemy = "#ff7070";
	public const string ColourArmour = "#b0b0b0";
	public const string ColourDamage = "#ffe070";
	public const string ColourDestroyed = "#ff9a40";
	public const string ColourFire = "#ff8c1a";
	public const string ColourFlood = "#40d0ff";
	public const string ColourTorpedo = "#ffffff";

	public static string Paint(string text, string colour)
	{
		return "<color=" + colour + ">" + text + "</color>";
	}

	public static void Finish()
	{
		ModHitLog.Hit h = ModHitLog.current;
		ModHitLog.current = null;
		if (h == null)
		{
			return;
		}
		if (h.nearMiss && h.cells == 0 && h.fires == 0 && h.floods == 0)
		{
			return;
		}
		// v0.19.2 format: attacker, action, target, result (no damage numbers)
		bool damaged = h.cells > 0 && h.damage >= h.expected * ModHitLog.ArmourHeldShare;
		List<string> parts = new List<string>();
		if (h.destroyed > 0)
		{
			// torpedoes often destroy compartments directly, without the normal compartment damage
			parts.Add(ModHitLog.Paint("<b>" + ((h.destroyed == 1) ? "compartment destroyed" : (h.destroyed + " compartments destroyed")) + "</b>", ModHitLog.ColourDestroyed));
		}
		else if (damaged)
		{
			parts.Add(ModHitLog.Paint("damaged", ModHitLog.ColourDamage));
		}
		else if (!h.nearMiss)
		{
			parts.Add(ModHitLog.Paint((h.what == "torpedo") ? "torpedo defence held" : "armour held", ModHitLog.ColourArmour));
		}
		// a shell can start a fire or flooding even when the armour holds
		if (h.fires > 0)
		{
			parts.Add(ModHitLog.Paint("<b>fire</b>", ModHitLog.ColourFire));
		}
		if (h.floods > 0)
		{
			parts.Add(ModHitLog.Paint("<b>flooding</b>", ModHitLog.ColourFlood));
		}
		if (parts.Count == 0)
		{
			parts.Add(ModHitLog.Paint(h.nearMiss ? "splinter damage" : "no damage", ModHitLog.ColourArmour));
		}
		string result = string.Join(", ", parts.ToArray());
		string targetColour = h.playerShip ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string firerColour = (h.firerSide == 0) ? ModHitLog.ColourOwn : ModHitLog.ColourEnemy;
		string weapon = ModHitLog.WithArticle(h.what);
		if (h.what == "torpedo")
		{
			weapon = "a " + ModHitLog.Paint("<b>torpedo</b>", ModHitLog.ColourTorpedo);
		}
		string target = ModHitLog.Paint(h.target, targetColour);
		string action = h.nearMiss ? "near-missed" : "hit";
		string line;
		if (h.firer != string.Empty)
		{
			// "Monaghan hit Dale with an HE shell: armour held, fire"
			line = ModHitLog.Paint(ModHitLog.Capital(h.firer), firerColour) + " " + action + " " + target + " with " + weapon + ": " + result;
		}
		else
		{
			// firer unknown: "Dale was hit by an HE shell: damaged"
			line = target + " was " + (h.nearMiss ? "near-missed" : "hit") + " by " + weapon + ": " + result;
		}
		ModHitLog.Add(line);
		UnityEngine.Debug.Log("[HITLOG] " + h.target + " hit by " + h.what + " from " + h.firer + ": " + h.cells + " cells, damage " + h.damage.ToString("F0") + " of " + h.expected.ToString("F0") + ", destroyed " + h.destroyed + ", fires " + h.fires + ", floods " + h.floods);
	}

	public static void Add(string line)
	{
		string time = string.Empty;
		try
		{
			if (Config.instance.timeStampMessageLog)
			{
				time = Utilities.GetDateTimeText(EngagementManager.instance.dateTime, Config.instance.timeFormat) + " ";
			}
		}
		catch
		{
		}
		ModLogTabs.AddHit(time + line);
	}

	public static void Clear()
	{
		ModHitLog.current = null;
		ModLogTabs.Clear();
	}

	// "an HE shell", "a bomb", "an AP shell", "a depth charge"
	public static string WithArticle(string what)
	{
		if (what.StartsWith("AP") || what.StartsWith("HE"))
		{
			return "an " + what;
		}
		return "a " + what;
	}

	// "our aircraft" -> "Our aircraft" at the start of a line
	public static string Capital(string text)
	{
		if (string.IsNullOrEmpty(text))
		{
			return text;
		}
		return char.ToUpper(text[0]) + text.Substring(1);
	}

	public static string ShipName(Unit u)
	{
		if (u == null)
		{
			return "?";
		}
		if ((int)u.faction != 0 && !u.identified)
		{
			return "Unidentified ship";
		}
		return u.unitInstanceName;
	}

	public static string FirerName(int id, out int side)
	{
		side = -1;
		try
		{
			List<Unit>[] lists = new List<Unit>[] { EngagementManager.instance.playerUnits, EngagementManager.instance.otherUnits };
			for (int l = 0; l < lists.Length; l++)
			{
				List<Unit> list = lists[l];
				for (int i = 0; i < list.Count; i++)
				{
					if ((object)list[i] != null && list[i].unitID == id)
					{
						side = (int)list[i].faction;
						if (list[i].unitAir != null)
						{
							return ((int)list[i].faction == 0) ? "our aircraft" : "enemy aircraft";
						}
						return ModHitLog.ShipName(list[i]);
					}
				}
			}
		}
		catch
		{
		}
		return string.Empty;
	}
}
```

### Step 3 - ModCrew (replace the class)
1. Right-click class **ModCrew** > **Edit Class (C#)...**
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**.
4. Close dnSpy and open it again (fields were added).

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
	public const float ShortCrewStart = 0.9f;
	// Efficiency lost per share of crew below ShortCrewStart (0.75 = -30% efficiency at half crew)
	public const float ShortCrewFactor = 0.75f;

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

**Testing**
1. Start a battle. There should be three tabs: **General**, **Hit log**, **Crew**.
2. Press **F2** a few times. It should step General > Hit log > Crew > General.
3. Exchange fire. Hit log lines should read like "Monaghan hit Dale with an HE shell: armour held".
4. When one of your ships takes damage, the Crew tab should count up and show "X men lost (...)" a couple of seconds after the hits stop.
5. Sink a ship and pick up survivors. The orange and green lines should be in Crew, not General.

---

## v0.19.3 - Faster group orders

**What the game already does:** you can tick several ships in the roster (shift-click works too), and Attack, Cease, Form Up, Smoke, Evade, Sensors and Auto gunnery already go to every ticked ship. The speed slider, the turn slider and map waypoints only went to the ship you were looking at.

**What it does:**
- **Selection keys (battle):**
  - **Ctrl+A** ticks all your ships.
  - **Ctrl+D** destroyers (and destroyer escorts), **Ctrl+C** cruisers, **Ctrl+B** battleships, battlecruisers and carriers.
  - **Ctrl+Shift+1** to **5** saves the ticked ships as a group. **Ctrl+1** to **5** selects that group again. Saved groups are forgotten at the end of the battle, and sunk ships drop out.
  - The first ship becomes the one you're looking at, unless it is already in the selection. A short blue line in General confirms what was selected.
  - While Ctrl is held the game's own keys are ignored, so Ctrl+1 doesn't also pick weapon 1 and Ctrl+A doesn't also put the rudder over.
- **Group movement:** with several ships ticked:
  - The **speed slider** (and the speed keys) sets the same speed on every ticked ship, up to each ship's top speed.
  - The **turn slider** (and the rudder keys) sets the same rudder on every ticked ship.
  - **Clicking a waypoint** on the map sends every ticked ship. Each ship's waypoint is moved by its distance from the ship you're looking at, so the group keeps its shape instead of piling onto one spot. Clicking more waypoints adds them to the path of every ticked ship.
  - Ships keeping station in a formation are left alone (they follow their leader), and so are ships in the middle of a manoeuvre. Rudder orders also skip ships already following waypoints, like the game does for a single ship.
- `[GROUPS]` lines in `output_log.txt` for each selection, saved group, waypoint order and speed change.

**Install (dnSpy).** Back up the DLL first.

### Step 1 - new class ModGroups
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Delete everything in the window and paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// v0.19.3: faster group orders in battle
// - Ctrl+A all ships, Ctrl+D destroyers, Ctrl+C cruisers, Ctrl+B battleships and carriers
// - Ctrl+Shift+1-5 saves the ticked ships as a group, Ctrl+1-5 selects that group again
// - speed, turn and map waypoints go to every ticked ship, not just the one you are looking at
public class ModGroups
{
	public const int SavedGroupCount = 5;

	public static List<Unit>[] saved = new List<Unit>[] { new List<Unit>(), new List<Unit>(), new List<Unit>(), new List<Unit>(), new List<Unit>() };
	// frame the game last switched the current ship (its sliders are reset then, which must not be copied to the group)
	public static int switchFrame = -1;
	public static List<Unit> lastPlayerUnits;

	// ---------- keys ----------

	public static bool CtrlHeld()
	{
		return Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.RightControl);
	}

	// First line of InputManager.Update: while Ctrl is held (and no mouse button), the game's own keys are ignored,
	// so Ctrl+1 doesn't also pick weapon 1 and Ctrl+A doesn't also turn the ship
	public static bool BlockGameKeys()
	{
		return ModGroups.CtrlHeld() && !Input.GetMouseButton(0) && !Input.GetMouseButton(1);
	}

	// Every frame, from ModRescue.Update
	public static void Tick()
	{
		try
		{
			if (EngagementManager.instance == null || RosterInterface.instance == null || CombatInterface.instance == null)
			{
				return;
			}
			// a new battle: forget the saved groups
			if (ModGroups.lastPlayerUnits != EngagementManager.instance.playerUnits)
			{
				ModGroups.lastPlayerUnits = EngagementManager.instance.playerUnits;
				for (int g = 0; g < ModGroups.SavedGroupCount; g++)
				{
					ModGroups.saved[g].Clear();
				}
			}
			if (!ModGroups.CtrlHeld())
			{
				return;
			}
			bool shift = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
			for (int g = 0; g < ModGroups.SavedGroupCount; g++)
			{
				if (Input.GetKeyDown(KeyCode.Alpha1 + g) || Input.GetKeyDown(KeyCode.Keypad1 + g))
				{
					if (shift)
					{
						ModGroups.SaveGroup(g);
					}
					else
					{
						ModGroups.RecallGroup(g);
					}
					return;
				}
			}
			if (Input.GetKeyDown(KeyCode.A))
			{
				ModGroups.SelectType("all ships", -1);
			}
			else if (Input.GetKeyDown(KeyCode.D))
			{
				ModGroups.SelectType("destroyers", 0);
			}
			else if (Input.GetKeyDown(KeyCode.C))
			{
				ModGroups.SelectType("cruisers", 1);
			}
			else if (Input.GetKeyDown(KeyCode.B))
			{
				ModGroups.SelectType("battleships and carriers", 2);
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] keys failed: " + ex.Message);
		}
	}

	// ---------- selection ----------

	// kind: -1 all ships, 0 destroyers, 1 cruisers, 2 battleships and carriers
	public static bool IsKind(Unit u, int kind)
	{
		if (kind == -1)
		{
			return true;
		}
		UnitSubType st = u.unitData.unitSubtype;
		if (kind == 0)
		{
			return st == UnitSubType.Destroyer || st == UnitSubType.Destroyer_Escort;
		}
		if (kind == 1)
		{
			return st == UnitSubType.Light_Cruiser || st == UnitSubType.Heavy_Cruiser;
		}
		return st == UnitSubType.Battleship || st == UnitSubType.Battlecruiser || st == UnitSubType.Aircraft_Carrier || st == UnitSubType.Light_Carrier;
	}

	public static bool Usable(Unit u)
	{
		return u != null && !u.isDestroyed && u.unitData != null && u.unitSea != null && u.gameObject.activeInHierarchy;
	}

	public static void SelectType(string what, int kind)
	{
		List<Unit> pick = new List<Unit>();
		List<Unit> units = EngagementManager.instance.playerUnits;
		for (int i = 0; i < units.Count; i++)
		{
			if (ModGroups.Usable(units[i]) && ModGroups.IsKind(units[i], kind))
			{
				pick.Add(units[i]);
			}
		}
		if (pick.Count == 0)
		{
			ModGroups.Say("No " + what + " to select");
			return;
		}
		ModGroups.Select(pick);
		ModGroups.Say("Selected " + what + ": " + pick.Count + ((pick.Count == 1) ? " ship" : " ships"));
	}

	public static void SaveGroup(int g)
	{
		List<Unit> ticked = RosterInterface.instance.GetSelectedRosterUnits();
		ModGroups.saved[g].Clear();
		for (int i = 0; i < ticked.Count; i++)
		{
			if (ModGroups.Usable(ticked[i]))
			{
				ModGroups.saved[g].Add(ticked[i]);
			}
		}
		ModGroups.Say("Group " + (g + 1) + " saved: " + ModGroups.saved[g].Count + ((ModGroups.saved[g].Count == 1) ? " ship" : " ships") + " (Ctrl+" + (g + 1) + " to select)");
	}

	public static void RecallGroup(int g)
	{
		List<Unit> pick = new List<Unit>();
		for (int i = 0; i < ModGroups.saved[g].Count; i++)
		{
			if (ModGroups.Usable(ModGroups.saved[g][i]))
			{
				pick.Add(ModGroups.saved[g][i]);
			}
		}
		if (pick.Count == 0)
		{
			ModGroups.Say("Group " + (g + 1) + " is empty (Ctrl+Shift+" + (g + 1) + " saves the ticked ships)");
			return;
		}
		ModGroups.Select(pick);
		ModGroups.Say("Group " + (g + 1) + " selected: " + pick.Count + ((pick.Count == 1) ? " ship" : " ships"));
	}

	// Makes the first ship the current one, then ticks exactly these ships in the roster
	public static void Select(List<Unit> pick)
	{
		RosterInterface roster = RosterInterface.instance;
		// show the ship roster (not the aircraft one)
		if (roster.switchType != null && roster.switchType.isOn)
		{
			roster.switchType.isOn = false;
		}
		if (!pick.Contains(CombatInterface.instance.currentUnit))
		{
			Map.instance.SwitchToUnit(pick[0]);
		}
		List<Unit> units = EngagementManager.instance.playerUnits;
		for (int i = 0; i < units.Count && i < roster.rosterToggles.Count; i++)
		{
			Toggle t = roster.rosterToggles[i];
			if (t == null)
			{
				continue;
			}
			bool on = pick.Contains(units[i]) && t.gameObject.activeSelf && t.interactable;
			if (t.isOn != on)
			{
				t.isOn = on;
			}
			roster.SetToggleColor(i);
		}
		UnityEngine.Debug.Log("[GROUPS] selected " + pick.Count + " ships, current " + CombatInterface.instance.currentUnit.unitInstanceName);
	}

	// Ticked ships other than the one you are looking at
	public static List<Unit> Others(CombatInterface ci)
	{
		List<Unit> result = new List<Unit>();
		if (RosterInterface.instance == null || ci.currentUnit == null)
		{
			return result;
		}
		List<Unit> ticked = RosterInterface.instance.GetSelectedRosterUnits();
		for (int i = 0; i < ticked.Count; i++)
		{
			Unit u = ticked[i];
			if (u != ci.currentUnit && ModGroups.Usable(u) && u.unitAI != null)
			{
				result.Add(u);
			}
		}
		return result;
	}

	// ---------- group movement ----------

	// First line of CombatInterface.SelectCurrentUnit
	public static void OnSwitchUnit()
	{
		ModGroups.switchFrame = Time.frameCount;
	}

	// First line of CombatInterface.SpeedSlider
	public static void GroupSpeed(CombatInterface ci)
	{
		try
		{
			if (Time.frameCount == ModGroups.switchFrame || ci.currentUnit == null || ci.currentUnit.lockSliderInput || ci.currentUnit.unitSea == null)
			{
				return;
			}
			List<Unit> others = ModGroups.Others(ci);
			if (others.Count == 0)
			{
				return;
			}
			float value = ci.speedChange.value;
			int changed = 0;
			for (int i = 0; i < others.Count; i++)
			{
				Unit u = others[i];
				// ships keeping station in a formation, or in the middle of a manoeuvre, follow their own orders
				if (u.lockSliderInput || (int)u.unitAI.currentAIAction == 2 || (int)u.unitAI.currentManeuvre != 0)
				{
					continue;
				}
				u.wantedSpeed = Mathf.Clamp(value, -5f, u.unitData.maxSpeed);
				if (Mathf.Abs(u.wantedSpeed) < Utilities.ConvertKnotToMetrePerSecond(0.5f))
				{
					u.wantedSpeed = 0f;
				}
				u.lastSliderValues.y = u.wantedSpeed;
				changed++;
			}
			if (changed > 0 && Time.frameCount % 30 == 0)
			{
				UnityEngine.Debug.Log("[GROUPS] speed set for " + (changed + 1) + " ships");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] speed failed: " + ex.Message);
		}
	}

	// First line of CombatInterface.TurnSlider
	public static void GroupTurn(CombatInterface ci)
	{
		try
		{
			if (Time.frameCount == ModGroups.switchFrame || ci.currentUnit == null || ci.currentUnit.lockSliderInput || ci.currentUnit.unitSea == null)
			{
				return;
			}
			List<Unit> others = ModGroups.Others(ci);
			if (others.Count == 0)
			{
				return;
			}
			float value = ci.turnChange.value;
			for (int i = 0; i < others.Count; i++)
			{
				Unit u = others[i];
				// ships following waypoints or a formation, or in a manoeuvre, follow their own orders
				int action = (int)u.unitAI.currentAIAction;
				if (u.lockSliderInput || action == 1 || action == 2 || (int)u.unitAI.currentManeuvre != 0)
				{
					continue;
				}
				u.wantedTurnRate = value / Config.instance.turnIncrements * u.unitData.maxTurnRate;
				u.lastSliderValues.z = u.wantedTurnRate;
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] turn failed: " + ex.Message);
		}
	}

	// Replaces the SetUnitWaypointPosition line in CombatInterface.ClickedMap.
	// Every ticked ship gets the waypoint, moved by its distance from the current ship, so the group keeps its shape.
	public static void GroupWaypoint(CombatInterface ci, Vector3 point)
	{
		Unit lead = ci.currentUnit;
		List<Unit> others = new List<Unit>();
		List<Vector3> offsets = new List<Vector3>();
		try
		{
			if (lead.unitSea != null)
			{
				Vector3 leadFrom = ModGroups.LastPoint(lead);
				List<Unit> candidates = ModGroups.Others(ci);
				for (int i = 0; i < candidates.Count; i++)
				{
					Unit u = candidates[i];
					// ships keeping station in a formation follow their leader
					if ((int)u.unitAI.currentAIAction == 2)
					{
						continue;
					}
					Vector3 offset = ModGroups.LastPoint(u) - leadFrom;
					offset.y = 0f;
					others.Add(u);
					offsets.Add(offset);
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] waypoint setup failed: " + ex.Message);
		}
		int before = lead.unitAI.navPoints.Count;
		ci.SetUnitWaypointPosition(lead, point);
		// the game refused the point (too close): don't send the others either
		if (lead.unitAI.navPoints.Count == before || others.Count == 0)
		{
			return;
		}
		try
		{
			for (int i = 0; i < others.Count; i++)
			{
				ci.SetUnitWaypointPosition(others[i], point + offsets[i]);
			}
			Map.instance.DrawNavLinesForUnit();
			UnityEngine.Debug.Log("[GROUPS] waypoint for " + (others.Count + 1) + " ships");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] waypoint failed: " + ex.Message);
		}
	}

	// Where a ship will be when it reaches its last waypoint (or where it is now)
	public static Vector3 LastPoint(Unit u)
	{
		if (u.unitAI != null && u.unitAI.navPoints.Count > 0)
		{
			return u.unitAI.navPoints[u.unitAI.navPoints.Count - 1];
		}
		Vector3 p = u.transform.position;
		p.y = 0f;
		return p;
	}

	// ---------- messages ----------

	public static void Say(string text)
	{
		UnityEngine.Debug.Log("[GROUPS] " + text);
		try
		{
			if (MessageLog.instance != null)
			{
				MessageLog.instance.SendMessageToLog("ModGroups", "<color=#80b8ff>" + text + "</color>", LogMessageType.DamageControl, true, null, null, false);
			}
		}
		catch
		{
		}
	}
}
```

### Step 2 - ModRescue (replace the class)
1. Right-click class **ModRescue** > **Edit Class (C#)...** (check the title says *ModRescue*, not ModCampaignRescue)
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**.

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

### Steps 3-6 - one line at the start of each method
For each method below, right-click it > **Edit Method (C#)...**, click just after the opening `{`, press Enter, paste the line and click **Compile**.

| Step | Class | Method | Line to paste |
|---|---|---|---|
| 3 | InputManager | **Update** | `if (ModGroups.BlockGameKeys()) { return; }` |
| 4 | CombatInterface | **SelectCurrentUnit** | `ModGroups.OnSwitchUnit();` |
| 5 | CombatInterface | **SpeedSlider** | `ModGroups.GroupSpeed(this);` |
| 6 | CombatInterface | **TurnSlider** | `ModGroups.GroupTurn(this);` |

### Step 7 - CombatInterface.ClickedMap (change one line)
1. Right-click method **ClickedMap** (class **CombatInterface**) > **Edit Method (C#)...**
2. Near the end, find the line that starts with `this.SetUnitWaypointPosition(this.currentUnit,`. It looks like:
   `this.SetUnitWaypointPosition(this.currentUnit, vector);`
3. Replace that whole line with:
   `ModGroups.GroupWaypoint(this, vector);`
   If dnSpy calls it something other than `vector`, keep that name (the word after the comma).
4. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 8 - message file
Open `override/language/english/dictionary/message_log.txt`. Directly under the `ModRescued` lines (under `[DAMAGECONTROL]`), add:
```
ModGroups=Group orders
ModGroups=audio/ui/Click2
```

**Testing**
1. Start a battle with a few ships. Press **Ctrl+A**. All ships should be ticked, and General should say `Selected all ships: N ships`.
2. Move the speed slider. Every ticked ship should change speed (check one with the F3 developer view, or switch to it).
3. Click a waypoint on the map. All ticked ships should turn towards their own points, keeping their spacing.
4. Tick two destroyers, press **Ctrl+Shift+1**, then **Ctrl+A**, then **Ctrl+1**. Only the two destroyers should be ticked again.
5. Press **Ctrl+1** on its own without the weapons changing, and check the ship doesn't turn when you press **Ctrl+A** or **Ctrl+D**.
6. If something doesn't work, send `output_log.txt` (the `[GROUPS]` lines) and a screenshot.

---

## v0.19.4 - Group numbers on the roster

**What it does:** each ship in a saved group (Ctrl+Shift+1-5) shows its group number in yellow at the right of its roster entry, just left of the arrow button. A ship in more than one group shows all of them, for example `1 3`.
- The numbers update straight away when you save a group, and drop off when a ship sinks.
- The coloured tiles on the left are still the game's formation colours, so you can see both at once.

**Install (dnSpy).** Back up the DLL first.
1. Right-click class **ModGroups** > **Edit Class (C#)...**
2. Select all, delete, paste the code below.
3. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// v0.19.3: faster group orders in battle
// - Ctrl+A all ships, Ctrl+D destroyers, Ctrl+C cruisers, Ctrl+B battleships and carriers
// - Ctrl+Shift+1-5 saves the ticked ships as a group, Ctrl+1-5 selects that group again
// - speed, turn and map waypoints go to every ticked ship, not just the one you are looking at
// v0.19.4: the roster shows each ship's saved group number(s) next to its name
public class ModGroups
{
	public const int SavedGroupCount = 5;

	public static List<Unit>[] saved = new List<Unit>[] { new List<Unit>(), new List<Unit>(), new List<Unit>(), new List<Unit>(), new List<Unit>() };
	// frame the game last switched the current ship (its sliders are reset then, which must not be copied to the group)
	public static int switchFrame = -1;
	public static List<Unit> lastPlayerUnits;

	// ---------- keys ----------

	public static bool CtrlHeld()
	{
		return Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.RightControl);
	}

	// First line of InputManager.Update: while Ctrl is held (and no mouse button), the game's own keys are ignored,
	// so Ctrl+1 doesn't also pick weapon 1 and Ctrl+A doesn't also turn the ship
	public static bool BlockGameKeys()
	{
		return ModGroups.CtrlHeld() && !Input.GetMouseButton(0) && !Input.GetMouseButton(1);
	}

	// Every frame, from ModRescue.Update
	public static void Tick()
	{
		try
		{
			if (EngagementManager.instance == null || RosterInterface.instance == null || CombatInterface.instance == null)
			{
				return;
			}
			// a new battle: forget the saved groups
			if (ModGroups.lastPlayerUnits != EngagementManager.instance.playerUnits)
			{
				ModGroups.lastPlayerUnits = EngagementManager.instance.playerUnits;
				for (int g = 0; g < ModGroups.SavedGroupCount; g++)
				{
					ModGroups.saved[g].Clear();
				}
			}
			// keep the group numbers on the roster up to date (sunk ships, new battle, rebuilt roster)
			if (Time.frameCount % 15 == 0)
			{
				ModGroups.UpdateBadges();
			}
			if (!ModGroups.CtrlHeld())
			{
				return;
			}
			bool shift = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
			for (int g = 0; g < ModGroups.SavedGroupCount; g++)
			{
				if (Input.GetKeyDown(KeyCode.Alpha1 + g) || Input.GetKeyDown(KeyCode.Keypad1 + g))
				{
					if (shift)
					{
						ModGroups.SaveGroup(g);
					}
					else
					{
						ModGroups.RecallGroup(g);
					}
					return;
				}
			}
			if (Input.GetKeyDown(KeyCode.A))
			{
				ModGroups.SelectType("all ships", -1);
			}
			else if (Input.GetKeyDown(KeyCode.D))
			{
				ModGroups.SelectType("destroyers", 0);
			}
			else if (Input.GetKeyDown(KeyCode.C))
			{
				ModGroups.SelectType("cruisers", 1);
			}
			else if (Input.GetKeyDown(KeyCode.B))
			{
				ModGroups.SelectType("battleships and carriers", 2);
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] keys failed: " + ex.Message);
		}
	}

	// ---------- selection ----------

	// kind: -1 all ships, 0 destroyers, 1 cruisers, 2 battleships and carriers
	public static bool IsKind(Unit u, int kind)
	{
		if (kind == -1)
		{
			return true;
		}
		UnitSubType st = u.unitData.unitSubtype;
		if (kind == 0)
		{
			return st == UnitSubType.Destroyer || st == UnitSubType.Destroyer_Escort;
		}
		if (kind == 1)
		{
			return st == UnitSubType.Light_Cruiser || st == UnitSubType.Heavy_Cruiser;
		}
		return st == UnitSubType.Battleship || st == UnitSubType.Battlecruiser || st == UnitSubType.Aircraft_Carrier || st == UnitSubType.Light_Carrier;
	}

	public static bool Usable(Unit u)
	{
		return u != null && !u.isDestroyed && u.unitData != null && u.unitSea != null && u.gameObject.activeInHierarchy;
	}

	public static void SelectType(string what, int kind)
	{
		List<Unit> pick = new List<Unit>();
		List<Unit> units = EngagementManager.instance.playerUnits;
		for (int i = 0; i < units.Count; i++)
		{
			if (ModGroups.Usable(units[i]) && ModGroups.IsKind(units[i], kind))
			{
				pick.Add(units[i]);
			}
		}
		if (pick.Count == 0)
		{
			ModGroups.Say("No " + what + " to select");
			return;
		}
		ModGroups.Select(pick);
		ModGroups.Say("Selected " + what + ": " + pick.Count + ((pick.Count == 1) ? " ship" : " ships"));
	}

	public static void SaveGroup(int g)
	{
		List<Unit> ticked = RosterInterface.instance.GetSelectedRosterUnits();
		ModGroups.saved[g].Clear();
		for (int i = 0; i < ticked.Count; i++)
		{
			if (ModGroups.Usable(ticked[i]))
			{
				ModGroups.saved[g].Add(ticked[i]);
			}
		}
		ModGroups.UpdateBadges();
		ModGroups.Say("Group " + (g + 1) + " saved: " + ModGroups.saved[g].Count + ((ModGroups.saved[g].Count == 1) ? " ship" : " ships") + " (Ctrl+" + (g + 1) + " to select)");
	}

	public static void RecallGroup(int g)
	{
		List<Unit> pick = new List<Unit>();
		for (int i = 0; i < ModGroups.saved[g].Count; i++)
		{
			if (ModGroups.Usable(ModGroups.saved[g][i]))
			{
				pick.Add(ModGroups.saved[g][i]);
			}
		}
		if (pick.Count == 0)
		{
			ModGroups.Say("Group " + (g + 1) + " is empty (Ctrl+Shift+" + (g + 1) + " saves the ticked ships)");
			return;
		}
		ModGroups.Select(pick);
		ModGroups.Say("Group " + (g + 1) + " selected: " + pick.Count + ((pick.Count == 1) ? " ship" : " ships"));
	}

	// Makes the first ship the current one, then ticks exactly these ships in the roster
	public static void Select(List<Unit> pick)
	{
		RosterInterface roster = RosterInterface.instance;
		// show the ship roster (not the aircraft one)
		if (roster.switchType != null && roster.switchType.isOn)
		{
			roster.switchType.isOn = false;
		}
		if (!pick.Contains(CombatInterface.instance.currentUnit))
		{
			Map.instance.SwitchToUnit(pick[0]);
		}
		List<Unit> units = EngagementManager.instance.playerUnits;
		for (int i = 0; i < units.Count && i < roster.rosterToggles.Count; i++)
		{
			Toggle t = roster.rosterToggles[i];
			if (t == null)
			{
				continue;
			}
			bool on = pick.Contains(units[i]) && t.gameObject.activeSelf && t.interactable;
			if (t.isOn != on)
			{
				t.isOn = on;
			}
			roster.SetToggleColor(i);
		}
		UnityEngine.Debug.Log("[GROUPS] selected " + pick.Count + " ships, current " + CombatInterface.instance.currentUnit.unitInstanceName);
	}

	// Ticked ships other than the one you are looking at
	public static List<Unit> Others(CombatInterface ci)
	{
		List<Unit> result = new List<Unit>();
		if (RosterInterface.instance == null || ci.currentUnit == null)
		{
			return result;
		}
		List<Unit> ticked = RosterInterface.instance.GetSelectedRosterUnits();
		for (int i = 0; i < ticked.Count; i++)
		{
			Unit u = ticked[i];
			if (u != ci.currentUnit && ModGroups.Usable(u) && u.unitAI != null)
			{
				result.Add(u);
			}
		}
		return result;
	}

	// ---------- group movement ----------

	// First line of CombatInterface.SelectCurrentUnit
	public static void OnSwitchUnit()
	{
		ModGroups.switchFrame = Time.frameCount;
	}

	// First line of CombatInterface.SpeedSlider
	public static void GroupSpeed(CombatInterface ci)
	{
		try
		{
			if (Time.frameCount == ModGroups.switchFrame || ci.currentUnit == null || ci.currentUnit.lockSliderInput || ci.currentUnit.unitSea == null)
			{
				return;
			}
			List<Unit> others = ModGroups.Others(ci);
			if (others.Count == 0)
			{
				return;
			}
			float value = ci.speedChange.value;
			int changed = 0;
			for (int i = 0; i < others.Count; i++)
			{
				Unit u = others[i];
				// ships keeping station in a formation, or in the middle of a manoeuvre, follow their own orders
				if (u.lockSliderInput || (int)u.unitAI.currentAIAction == 2 || (int)u.unitAI.currentManeuvre != 0)
				{
					continue;
				}
				u.wantedSpeed = Mathf.Clamp(value, -5f, u.unitData.maxSpeed);
				if (Mathf.Abs(u.wantedSpeed) < Utilities.ConvertKnotToMetrePerSecond(0.5f))
				{
					u.wantedSpeed = 0f;
				}
				u.lastSliderValues.y = u.wantedSpeed;
				changed++;
			}
			if (changed > 0 && Time.frameCount % 30 == 0)
			{
				UnityEngine.Debug.Log("[GROUPS] speed set for " + (changed + 1) + " ships");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] speed failed: " + ex.Message);
		}
	}

	// First line of CombatInterface.TurnSlider
	public static void GroupTurn(CombatInterface ci)
	{
		try
		{
			if (Time.frameCount == ModGroups.switchFrame || ci.currentUnit == null || ci.currentUnit.lockSliderInput || ci.currentUnit.unitSea == null)
			{
				return;
			}
			List<Unit> others = ModGroups.Others(ci);
			if (others.Count == 0)
			{
				return;
			}
			float value = ci.turnChange.value;
			for (int i = 0; i < others.Count; i++)
			{
				Unit u = others[i];
				// ships following waypoints or a formation, or in a manoeuvre, follow their own orders
				int action = (int)u.unitAI.currentAIAction;
				if (u.lockSliderInput || action == 1 || action == 2 || (int)u.unitAI.currentManeuvre != 0)
				{
					continue;
				}
				u.wantedTurnRate = value / Config.instance.turnIncrements * u.unitData.maxTurnRate;
				u.lastSliderValues.z = u.wantedTurnRate;
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] turn failed: " + ex.Message);
		}
	}

	// Replaces the SetUnitWaypointPosition line in CombatInterface.ClickedMap.
	// Every ticked ship gets the waypoint, moved by its distance from the current ship, so the group keeps its shape.
	public static void GroupWaypoint(CombatInterface ci, Vector3 point)
	{
		Unit lead = ci.currentUnit;
		List<Unit> others = new List<Unit>();
		List<Vector3> offsets = new List<Vector3>();
		try
		{
			if (lead.unitSea != null)
			{
				Vector3 leadFrom = ModGroups.LastPoint(lead);
				List<Unit> candidates = ModGroups.Others(ci);
				for (int i = 0; i < candidates.Count; i++)
				{
					Unit u = candidates[i];
					// ships keeping station in a formation follow their leader
					if ((int)u.unitAI.currentAIAction == 2)
					{
						continue;
					}
					Vector3 offset = ModGroups.LastPoint(u) - leadFrom;
					offset.y = 0f;
					others.Add(u);
					offsets.Add(offset);
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] waypoint setup failed: " + ex.Message);
		}
		int before = lead.unitAI.navPoints.Count;
		ci.SetUnitWaypointPosition(lead, point);
		// the game refused the point (too close): don't send the others either
		if (lead.unitAI.navPoints.Count == before || others.Count == 0)
		{
			return;
		}
		try
		{
			for (int i = 0; i < others.Count; i++)
			{
				ci.SetUnitWaypointPosition(others[i], point + offsets[i]);
			}
			Map.instance.DrawNavLinesForUnit();
			UnityEngine.Debug.Log("[GROUPS] waypoint for " + (others.Count + 1) + " ships");
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] waypoint failed: " + ex.Message);
		}
	}

	// Where a ship will be when it reaches its last waypoint (or where it is now)
	public static Vector3 LastPoint(Unit u)
	{
		if (u.unitAI != null && u.unitAI.navPoints.Count > 0)
		{
			return u.unitAI.navPoints[u.unitAI.navPoints.Count - 1];
		}
		Vector3 p = u.transform.position;
		p.y = 0f;
		return p;
	}

	// ---------- group numbers on the roster ----------

	public const string BadgeName = "ModGroupBadge";
	public const string BadgeColour = "#ffe070";

	// Writes "1" (or "1 3" for a ship in two groups) at the right of each roster entry, left of the arrow button
	public static void UpdateBadges()
	{
		try
		{
			RosterInterface roster = RosterInterface.instance;
			List<Unit> units = EngagementManager.instance.playerUnits;
			if (roster == null || roster.rosterToggles == null || units == null)
			{
				return;
			}
			for (int i = 0; i < roster.rosterToggles.Count && i < units.Count; i++)
			{
				Toggle t = roster.rosterToggles[i];
				if (t == null)
				{
					continue;
				}
				string numbers = string.Empty;
				for (int g = 0; g < ModGroups.SavedGroupCount; g++)
				{
					if (ModGroups.Usable(units[i]) && ModGroups.saved[g].Contains(units[i]))
					{
						numbers += ((numbers != string.Empty) ? " " : string.Empty) + (g + 1);
					}
				}
				Text badge = ModGroups.GetBadge(t, numbers != string.Empty);
				if (badge != null)
				{
					ModGroups.PlaceBadge(t, badge);
					string wanted = (numbers != string.Empty) ? ("<b><color=" + ModGroups.BadgeColour + ">" + numbers + "</color></b>") : string.Empty;
					if (badge.text != wanted)
					{
						badge.text = wanted;
					}
				}
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[GROUPS] badges failed: " + ex.Message);
		}
	}

	// Puts the number just left of the entry's arrow button (the "go to ship" button on the right of the bar)
	public static void PlaceBadge(Toggle t, Text badge)
	{
		Button arrow = null;
		Button[] buttons = t.GetComponentsInChildren<Button>(true);
		for (int b = 0; b < buttons.Length; b++)
		{
			if (buttons[b] != null && buttons[b].gameObject != t.gameObject)
			{
				arrow = buttons[b];
				break;
			}
		}
		if (arrow == null)
		{
			return;
		}
		RectTransform ar = arrow.GetComponent<RectTransform>();
		RectTransform br = badge.GetComponent<RectTransform>();
		if (ar == null || br == null)
		{
			return;
		}
		Vector3[] c = new Vector3[4];
		ar.GetWorldCorners(c);
		// c[0] bottom left, c[1] top left of the arrow button
		Vector3 leftMiddle = (c[0] + c[1]) * 0.5f;
		br.pivot = new Vector2(1f, 0.5f);
		br.position = leftMiddle - new Vector3(4f * br.lossyScale.x, 0f, 0f);
	}

	// Finds the badge on a roster entry, and makes one if needed (only when there is something to show)
	public static Text GetBadge(Toggle t, bool create)
	{
		Transform found = t.transform.Find(ModGroups.BadgeName);
		if (found != null)
		{
			return found.GetComponent<Text>();
		}
		if (!create)
		{
			return null;
		}
		Text sample = t.GetComponentInChildren<Text>(true);
		GameObject go = new GameObject(ModGroups.BadgeName, new System.Type[] { typeof(RectTransform) });
		go.transform.SetParent(t.transform, false);
		LayoutElement le = go.AddComponent<LayoutElement>();
		le.ignoreLayout = true;
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.anchorMin = new Vector2(1f, 0.5f);
		rt.anchorMax = new Vector2(1f, 0.5f);
		rt.pivot = new Vector2(1f, 0.5f);
		rt.anchoredPosition = new Vector2(-26f, 0f);
		rt.sizeDelta = new Vector2(48f, 20f);
		Text text = go.AddComponent<Text>();
		text.font = (sample != null && sample.font != null) ? sample.font : Resources.GetBuiltinResource<Font>("Arial.ttf");
		text.fontSize = 14;
		text.alignment = TextAnchor.MiddleRight;
		text.supportRichText = true;
		text.raycastTarget = false;
		text.horizontalOverflow = HorizontalWrapMode.Overflow;
		text.text = string.Empty;
		go.transform.SetAsLastSibling();
		return text;
	}

	// ---------- messages ----------

	public static void Say(string text)
	{
		UnityEngine.Debug.Log("[GROUPS] " + text);
		try
		{
			if (MessageLog.instance != null)
			{
				MessageLog.instance.SendMessageToLog("ModGroups", "<color=#80b8ff>" + text + "</color>", LogMessageType.DamageControl, true, null, null, false);
			}
		}
		catch
		{
		}
	}
}
```

**Testing**
1. Tick two ships and press **Ctrl+Shift+1**. A yellow **1** should appear at the right of both roster entries.
2. Tick one of them plus another ship and press **Ctrl+Shift+2**. The shared ship should show **1 2**.
3. Save group 1 again with different ships. The old ships should lose their **1**.
4. The number should sit just left of the arrow button on each bar. If it's somewhere else, send a screenshot.

---

## v0.19.5 - Minimap upgrades

**What it does:** four new layers on the battle minimap (and the full-screen map from Tab). Each has its own button in a row at the bottom right, on the minimap just above the map toolbar. The buttons remember their setting between battles, and **F11** turns all four off or back on.
- **Torpedoes:** every torpedo the game already shows on the map (yours, and enemy ones your ships have detected) gets a fading track behind it, about the last 30 seconds, and a faint line ahead to where its run ends. Blue for yours, red for the enemy's.
- **Smoke:** grey patches where smoke has been laid. They grow and drift with the wind like the real smoke, and vanish when it clears (about a minute).
- **Rings:** two circles around the ship you're looking at. White is how far her lookouts can see a ship of her own size in the current weather and light. Green is her surface radar range against an average ship, shown only while her radar is on.
- **Last seen:** when an enemy ship drops out of sight, a faded red X stays where she was last seen, with her name (or "Contact" if not identified) and how many minutes ago. It goes when she is seen again, sunk, or after 20 minutes.
- `[MINIMAP]` lines in `output_log.txt`: when the overlay and buttons are added, each button change, each enemy lost from sight, and a count once a minute.

**Fix (torpedo colours):** in the first test, enemy aircraft torpedoes were drawn blue. The torpedo's own side flag isn't set for aircraft torpedoes, so the colour now comes from the unit that fired it (`ModMinimap.FiredByPlayer`).

**Install (dnSpy).** Back up the DLL first.

### Step 1 - new class ModMinimap
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Delete everything in the window and paste the code below.
3. **Compile**, then **File > Save Module**.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

// v0.19.5: minimap upgrades, each with its own on/off button (F11 turns them all on or off)
// - torpedo tracks: a fading line behind every torpedo on the map, and a faint line ahead to the end of its run
// - smoke screens: grey patches where smoke has been laid
// - rings: lookout and radar range of the ship you are looking at
// - last seen: a faded X where an enemy ship was last seen, with its name and how long ago
// The buttons sit at the bottom right, on the minimap just above the map toolbar
public class ModMinimap
{
	public class Track
	{
		public List<Vector3> points = new List<Vector3>();
		public float lastSample;
		public float firstSeen;
		public float timeToRun;
		public LineRenderer trail;
		public LineRenderer ahead;
		public bool seen;
	}

	public class Ghost
	{
		public Vector3 mapPos;
		public float lostAt;
		public LineRenderer a;
		public LineRenderer b;
		public Text label;
	}

	// settings
	public static string[] names = new string[] { "Torpedoes", "Smoke", "Rings", "Last seen" };
	public static string[] keys = new string[] { "ModMinimapTorps", "ModMinimapSmoke", "ModMinimapRings", "ModMinimapLastSeen" };
	public static bool[] on = new bool[] { true, true, true, true };
	public static bool loaded;

	// tuning
	public const float TrailSampleSeconds = 1f;
	public const int TrailPoints = 30;
	public const float MaxAheadUnits = 400f;
	public const float GhostMinutes = 20f;
	public const int MaxSmoke = 200;

	public static Transform root;
	public static List<Unit> battleUnits;
	public static Dictionary<int, ModMinimap.Track> tracks = new Dictionary<int, ModMinimap.Track>();
	public static List<LineRenderer> smokeLines = new List<LineRenderer>();
	public static LineRenderer visualRing;
	public static LineRenderer radarRing;
	public static Dictionary<Unit, Vector3> lastSeenPos = new Dictionary<Unit, Vector3>();
	public static Dictionary<Unit, ModMinimap.Ghost> ghosts = new Dictionary<Unit, ModMinimap.Ghost>();
	public static float slowTimer;
	public static float logTimer;

	// buttons
	public static RectTransform bar;
	public static Button[] buttons = new Button[4];
	public static Text[] buttonTexts = new Text[4];

	// ---------- every frame, from ModRescue.Update ----------

	public static void Tick()
	{
		try
		{
			if (Map.instance == null || Map.instance.unitLayer == null || EngagementManager.instance == null || FloatingOrigin.instance == null)
			{
				return;
			}
			ModMinimap.LoadSettings();
			if (ModMinimap.battleUnits != EngagementManager.instance.playerUnits)
			{
				ModMinimap.battleUnits = EngagementManager.instance.playerUnits;
				ModMinimap.ClearAll();
			}
			if (ModMinimap.root == null)
			{
				GameObject go = new GameObject("ModMinimapLayer");
				go.transform.SetParent(Map.instance.unitLayer, false);
				go.transform.localPosition = Vector3.zero;
				go.transform.localRotation = Quaternion.identity;
				go.transform.localScale = Vector3.one;
				go.layer = Map.instance.unitLayer.gameObject.layer;
				ModMinimap.root = go.transform;
				ModMinimap.ClearAll();
				UnityEngine.Debug.Log("[MINIMAP] overlay added, canvas " + (go.GetComponentInParent<Canvas>() != null ? "found" : "not found") + ", map scale " + Map.instance.unitLayer.lossyScale.x.ToString("F4"));
			}
			if (Input.GetKeyDown(KeyCode.F11))
			{
				bool any = ModMinimap.on[0] || ModMinimap.on[1] || ModMinimap.on[2] || ModMinimap.on[3];
				for (int i = 0; i < 4; i++)
				{
					ModMinimap.Set(i, !any);
				}
			}
			ModMinimap.UpdateButtons();
			ModMinimap.UpdateTorpedoes();
			ModMinimap.slowTimer -= Time.unscaledDeltaTime;
			if (ModMinimap.slowTimer <= 0f)
			{
				ModMinimap.slowTimer = 0.5f;
				ModMinimap.UpdateSmoke();
				ModMinimap.UpdateRings();
				ModMinimap.UpdateLastSeen();
			}
			ModMinimap.logTimer -= Time.unscaledDeltaTime;
			if (ModMinimap.logTimer <= 0f)
			{
				ModMinimap.logTimer = 60f;
				UnityEngine.Debug.Log("[MINIMAP] torpedo tracks " + ModMinimap.tracks.Count + ", smoke patches " + ModMinimap.CountActive(ModMinimap.smokeLines) + ", last seen markers " + ModMinimap.ghosts.Count);
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[MINIMAP] tick failed: " + ex.ToString());
			ModMinimap.slowTimer = 2f;
		}
	}

	// ---------- torpedo tracks ----------

	public static void UpdateTorpedoes()
	{
		foreach (ModMinimap.Track t in ModMinimap.tracks.Values)
		{
			t.seen = false;
		}
		if (ModMinimap.on[0] && Map.instance.allMapTorpedoes != null)
		{
			float w = ModMinimap.LineWidth();
			for (int i = 0; i < Map.instance.allMapTorpedoes.Count; i++)
			{
				MapTorpedo mt = Map.instance.allMapTorpedoes[i];
				// only torpedoes the game shows on the map (yours, and enemy ones your ships have detected)
				if (mt == null || !mt.gameObject.activeInHierarchy || mt.ammoTorpedo == null || !mt.ammoTorpedo.gameObject.activeInHierarchy)
				{
					continue;
				}
				AmmunitionMoveTorpedo torp = mt.ammoTorpedo;
				int id = torp.GetInstanceID();
				ModMinimap.Track t;
				if (!ModMinimap.tracks.TryGetValue(id, out t))
				{
					t = new ModMinimap.Track();
					t.firstSeen = Time.time;
					t.lastSample = -100f;
					t.timeToRun = (torp.parentAmmunition != null && torp.parentAmmunition.ammunitionTimer != null) ? torp.parentAmmunition.ammunitionTimer.timeToRun : 0f;
					bool own = ModMinimap.FiredByPlayer(torp);
					Color c = own ? new Color(0.5f, 0.72f, 1f, 1f) : new Color(1f, 0.44f, 0.44f, 1f);
					t.trail = ModMinimap.MakeLine("ModTorpTrail", c);
					t.ahead = ModMinimap.MakeLine("ModTorpAhead", c);
					ModMinimap.tracks[id] = t;
				}
				t.seen = true;
				Vector3 now = ModMinimap.MapPos(torp.transform.position, -2f);
				if (Time.time - t.lastSample >= ModMinimap.TrailSampleSeconds)
				{
					t.lastSample = Time.time;
					t.points.Add(now);
					while (t.points.Count > ModMinimap.TrailPoints)
					{
						t.points.RemoveAt(0);
					}
				}
				if (t.trail != null)
				{
					t.trail.positionCount = t.points.Count + 1;
					for (int p = 0; p < t.points.Count; p++)
					{
						t.trail.SetPosition(p, t.points[p]);
					}
					t.trail.SetPosition(t.points.Count, now);
					t.trail.widthMultiplier = w * 0.6f;
					ModMinimap.SetAlpha(t.trail, 0f, 0.8f);
				}
				if (t.ahead != null)
				{
					Vector3 fwd = torp.transform.forward;
					fwd.y = 0f;
					float speed = 0f;
					if (torp.parentAmmunition != null && torp.parentAmmunition.ammoRigidbody != null)
					{
						Vector3 v = torp.parentAmmunition.ammoRigidbody.velocity;
						v.y = 0f;
						speed = v.magnitude;
					}
					float left = Mathf.Max(0f, t.timeToRun - (Time.time - t.firstSeen));
					float dist = Mathf.Min(ModMinimap.MaxAheadUnits, speed * left);
					Vector3 dir = new Vector3(fwd.x, fwd.z, 0f).normalized;
					t.ahead.positionCount = 2;
					t.ahead.SetPosition(0, now);
					t.ahead.SetPosition(1, now + dir * dist);
					t.ahead.widthMultiplier = w * 0.4f;
					ModMinimap.SetAlpha(t.ahead, 0.45f, 0f);
				}
			}
		}
		// remove tracks whose torpedo has gone (or when the layer is switched off)
		List<int> gone = new List<int>();
		foreach (KeyValuePair<int, ModMinimap.Track> kv in ModMinimap.tracks)
		{
			if (!kv.Value.seen)
			{
				gone.Add(kv.Key);
			}
		}
		for (int i = 0; i < gone.Count; i++)
		{
			ModMinimap.Track t = ModMinimap.tracks[gone[i]];
			ModMinimap.Kill(t.trail);
			ModMinimap.Kill(t.ahead);
			ModMinimap.tracks.Remove(gone[i]);
		}
	}

	// ---------- smoke ----------

	public static void UpdateSmoke()
	{
		int used = 0;
		if (ModMinimap.on[1])
		{
			SmokeCollisionObject[] all = Object.FindObjectsOfType<SmokeCollisionObject>();
			for (int i = 0; i < all.Length && used < ModMinimap.MaxSmoke; i++)
			{
				SmokeCollisionObject s = all[i];
				if (s == null || !s.gameObject.activeInHierarchy || s.sc == null)
				{
					continue;
				}
				float r = s.sc.radius * Mathf.Abs(s.transform.lossyScale.x);
				if (r <= 0f)
				{
					continue;
				}
				if (used >= ModMinimap.smokeLines.Count)
				{
					ModMinimap.smokeLines.Add(ModMinimap.MakeLine("ModSmoke", new Color(0.75f, 0.75f, 0.75f, 1f)));
				}
				LineRenderer lr = ModMinimap.smokeLines[used];
				if (lr == null)
				{
					lr = ModMinimap.MakeLine("ModSmoke", new Color(0.75f, 0.75f, 0.75f, 1f));
					ModMinimap.smokeLines[used] = lr;
				}
				// a ring of radius r/2 drawn r wide fills the whole circle
				ModMinimap.Circle(lr, ModMinimap.MapPos(s.transform.position, -0.5f), r * 0.5f, 20);
				lr.widthMultiplier = r * Mathf.Abs(Map.instance.unitLayer.lossyScale.x);
				ModMinimap.SetAlpha(lr, 0.3f, 0.3f);
				lr.gameObject.SetActive(true);
				used++;
			}
		}
		for (int i = used; i < ModMinimap.smokeLines.Count; i++)
		{
			if (ModMinimap.smokeLines[i] != null && ModMinimap.smokeLines[i].gameObject.activeSelf)
			{
				ModMinimap.smokeLines[i].gameObject.SetActive(false);
			}
		}
	}

	// ---------- lookout and radar rings ----------

	public static void UpdateRings()
	{
		if (ModMinimap.visualRing == null)
		{
			ModMinimap.visualRing = ModMinimap.MakeLine("ModVisualRing", new Color(1f, 1f, 1f, 1f));
		}
		if (ModMinimap.radarRing == null)
		{
			ModMinimap.radarRing = ModMinimap.MakeLine("ModRadarRing", new Color(0.4f, 0.9f, 0.55f, 1f));
		}
		Unit u = (CombatInterface.instance != null) ? CombatInterface.instance.currentUnit : null;
		bool show = ModMinimap.on[2] && u != null && !u.isDestroyed && u.unitSea != null && u.unitData != null && EngagementData.instance != null;
		if (!show)
		{
			ModMinimap.visualRing.gameObject.SetActive(false);
			ModMinimap.radarRing.gameObject.SetActive(false);
			return;
		}
		Vector3 centre = ModMinimap.MapPos(u.transform.position, -0.8f);
		float w = ModMinimap.LineWidth() * 0.5f;
		// lookouts against a ship of the same size, in this weather and light (km, then 10 m map units)
		float visualKm = 2f * u.unitData.visualHorizonDistance * EngagementData.instance.currentVisibilityModifier * Utilities.GetDifficultyModifier(Difficulty.Visual, u.faction);
		ModMinimap.Circle(ModMinimap.visualRing, centre, visualKm * 100f, 72);
		ModMinimap.visualRing.widthMultiplier = w;
		ModMinimap.SetAlpha(ModMinimap.visualRing, 0.4f, 0.4f);
		ModMinimap.visualRing.gameObject.SetActive(visualKm > 0f);
		// surface radar against an average-sized ship, when the radar is on
		float radarKm = 0f;
		if (u.usingRadar && u.unitData.surfaceRadarStrength > 0f)
		{
			float weather = EngagementData.instance.currentRadarModifier;
			if (weather > 0f)
			{
				float rain = (EngagementData.instance.isRaining || EngagementData.instance.isSnowing) ? Config.instance.rainRadarMaxPenalty : 1f;
				radarKm = u.unitData.surfaceRadarStrength * weather * rain * Utilities.GetDifficultyModifier(Difficulty.Radar, u.faction);
			}
		}
		ModMinimap.Circle(ModMinimap.radarRing, centre, radarKm * 100f, 72);
		ModMinimap.radarRing.widthMultiplier = w;
		ModMinimap.SetAlpha(ModMinimap.radarRing, 0.55f, 0.55f);
		ModMinimap.radarRing.gameObject.SetActive(radarKm > 0f);
	}

	// ---------- last seen ----------

	public static void UpdateLastSeen()
	{
		List<Unit> enemies = EngagementManager.instance.otherUnits;
		float nowSec = EngagementManager.instance.combatTimeElapsed;
		float w = ModMinimap.LineWidth();
		Text sample = null;
		for (int i = 0; i < Map.instance.allMapUnits.Count && sample == null; i++)
		{
			if (Map.instance.allMapUnits[i] != null && Map.instance.allMapUnits[i].mapUnitText != null && Map.instance.allMapUnits[i].gameObject.activeInHierarchy)
			{
				sample = Map.instance.allMapUnits[i].mapUnitText;
			}
		}
		HashSet<Unit> keep = new HashSet<Unit>();
		if (ModMinimap.on[3] && enemies != null)
		{
			for (int i = 0; i < enemies.Count; i++)
			{
				Unit e = enemies[i];
				if (e == null || e.unitSea == null || e.isDestroyed)
				{
					continue;
				}
				bool seenNow = e.detectedBy != null && e.detectedBy.Count > 0;
				if (seenNow)
				{
					ModMinimap.lastSeenPos[e] = ModMinimap.MapPos(e.transform.position, -4f);
					continue;
				}
				Vector3 pos;
				if (!ModMinimap.lastSeenPos.TryGetValue(e, out pos))
				{
					continue;
				}
				ModMinimap.Ghost g;
				if (!ModMinimap.ghosts.TryGetValue(e, out g))
				{
					g = new ModMinimap.Ghost();
					g.mapPos = pos;
					g.lostAt = nowSec;
					Color c = new Color(1f, 0.44f, 0.44f, 1f);
					g.a = ModMinimap.MakeLine("ModGhostA", c);
					g.b = ModMinimap.MakeLine("ModGhostB", c);
					g.label = ModMinimap.MakeLabel(sample);
					ModMinimap.ghosts[e] = g;
					UnityEngine.Debug.Log("[MINIMAP] lost sight of " + ModMinimap.EnemyName(e));
				}
				float minutes = (nowSec - g.lostAt) / 60f;
				if (minutes > ModMinimap.GhostMinutes)
				{
					continue;
				}
				keep.Add(e);
				// a small X that stays the same size on screen
				float s = w * 5f / Mathf.Max(0.0001f, Mathf.Abs(Map.instance.unitLayer.lossyScale.x));
				ModMinimap.Segment(g.a, g.mapPos + new Vector3(-s, -s, 0f), g.mapPos + new Vector3(s, s, 0f));
				ModMinimap.Segment(g.b, g.mapPos + new Vector3(-s, s, 0f), g.mapPos + new Vector3(s, -s, 0f));
				g.a.widthMultiplier = w * 0.8f;
				g.b.widthMultiplier = w * 0.8f;
				ModMinimap.SetAlpha(g.a, 0.6f, 0.6f);
				ModMinimap.SetAlpha(g.b, 0.6f, 0.6f);
				if (g.label != null)
				{
					g.label.text = "<color=#ff9090>" + ModMinimap.EnemyName(e) + " " + Mathf.FloorToInt(minutes) + " min</color>";
					g.label.rectTransform.localPosition = g.mapPos + new Vector3(s * 1.6f, 0f, 0f);
					if (sample != null)
					{
						Vector3 want = sample.transform.lossyScale;
						Vector3 parent = ModMinimap.root.lossyScale;
						g.label.transform.localScale = new Vector3(want.x / Mathf.Max(0.0001f, parent.x), want.y / Mathf.Max(0.0001f, parent.y), 1f);
						g.label.fontSize = sample.fontSize;
					}
				}
			}
		}
		// remove markers for ships seen again, sunk, too old, or when switched off
		List<Unit> drop = new List<Unit>();
		foreach (KeyValuePair<Unit, ModMinimap.Ghost> kv in ModMinimap.ghosts)
		{
			if (!keep.Contains(kv.Key))
			{
				drop.Add(kv.Key);
			}
		}
		for (int i = 0; i < drop.Count; i++)
		{
			ModMinimap.Ghost g = ModMinimap.ghosts[drop[i]];
			ModMinimap.Kill(g.a);
			ModMinimap.Kill(g.b);
			if (g.label != null)
			{
				Object.Destroy(g.label.gameObject);
			}
			ModMinimap.ghosts.Remove(drop[i]);
		}
	}

	// Who fired the torpedo: the game keeps the firer's map icon at index firedByUnitID (it uses the same lookup itself)
	public static bool FiredByPlayer(AmmunitionMoveTorpedo torp)
	{
		if (torp.parentAmmunition == null)
		{
			return true;
		}
		int id = torp.parentAmmunition.firedByUnitID;
		List<MapUnit> units = Map.instance.allMapUnits;
		if (units != null && id >= 0 && id < units.Count && units[id] != null && units[id].thisUnit != null)
		{
			return (int)units[id].thisUnit.faction == 0;
		}
		return torp.parentAmmunition.faction == 0;
	}

	public static string EnemyName(Unit e)
	{
		if (e.identified)
		{
			return e.unitInstanceName;
		}
		return "Contact";
	}

	// ---------- buttons (bottom right, just above the map toolbar) ----------

	// Height of the buttons above the bottom of the screen (at 100% UI scale)
	public const float BarHeightAboveBottom = 40f;

	public static void UpdateButtons()
	{
		RosterInterface roster = RosterInterface.instance;
		if (roster == null || roster.rosterToggles == null || roster.rosterToggles.Count == 0)
		{
			return;
		}
		if (ModMinimap.bar == null)
		{
			ModMinimap.BuildButtons(roster);
			if (ModMinimap.bar == null)
			{
				return;
			}
		}
		// bottom right: on the minimap's bottom edge, just above the map toolbar, starting from the minimap's left side
		Canvas cv = ModMinimap.bar.GetComponentInParent<Canvas>();
		float k = (cv != null) ? cv.scaleFactor : 1f;
		float x = (float)Screen.width - (4f * 78f + 8f) * k;
		if (Map.instance.mapBorder != null && Map.instance.mapBorder.gameObject.activeInHierarchy)
		{
			Vector3[] c = new Vector3[4];
			Map.instance.mapBorder.GetWorldCorners(c);
			x = c[0].x + 6f * k;
		}
		ModMinimap.bar.position = new Vector3(x, ModMinimap.BarHeightAboveBottom * k, 0f);
		for (int i = 0; i < 4; i++)
		{
			if (ModMinimap.buttonTexts[i] != null)
			{
				ModMinimap.buttonTexts[i].text = ModMinimap.on[i] ? ("<b>" + ModMinimap.names[i] + "</b>") : ("<color=#909090>" + ModMinimap.names[i] + "</color>");
				ModMinimap.buttons[i].targetGraphic.color = ModMinimap.on[i] ? new Color(0.2f, 0.3f, 0.45f, 0.9f) : new Color(0f, 0f, 0f, 0.45f);
			}
		}
	}

	public static void BuildButtons(RosterInterface roster)
	{
		Canvas rosterCanvas = roster.rosterToggles[0].GetComponentInParent<Canvas>();
		Transform parent = (rosterCanvas != null) ? rosterCanvas.rootCanvas.transform : null;
		if (parent == null)
		{
			return;
		}
		Font font = null;
		Text sample = roster.rosterToggles[0].GetComponentInChildren<Text>(true);
		if (sample != null)
		{
			font = sample.font;
		}
		if (font == null)
		{
			font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		}
		GameObject barObject = new GameObject("ModMinimapButtons", new System.Type[] { typeof(RectTransform) });
		barObject.transform.SetParent(parent, false);
		ModMinimap.bar = barObject.GetComponent<RectTransform>();
		ModMinimap.bar.anchorMin = new Vector2(0.5f, 0.5f);
		ModMinimap.bar.anchorMax = new Vector2(0.5f, 0.5f);
		ModMinimap.bar.pivot = new Vector2(0f, 0f);
		ModMinimap.bar.sizeDelta = new Vector2(4f * 78f, 20f);
		LayoutElement le = barObject.AddComponent<LayoutElement>();
		le.ignoreLayout = true;
		for (int i = 0; i < 4; i++)
		{
			GameObject go = new GameObject("ModMinimapButton " + ModMinimap.names[i], new System.Type[] { typeof(RectTransform) });
			go.transform.SetParent(barObject.transform, false);
			RectTransform rt = go.GetComponent<RectTransform>();
			rt.anchorMin = Vector2.zero;
			rt.anchorMax = Vector2.zero;
			rt.pivot = Vector2.zero;
			rt.anchoredPosition = new Vector2((float)i * 78f, 0f);
			rt.sizeDelta = new Vector2(76f, 20f);
			Image img = go.AddComponent<Image>();
			img.color = new Color(0f, 0f, 0f, 0.6f);
			Button b = go.AddComponent<Button>();
			b.targetGraphic = img;
			GameObject textObject = new GameObject("Label", new System.Type[] { typeof(RectTransform) });
			textObject.transform.SetParent(go.transform, false);
			RectTransform trt = textObject.GetComponent<RectTransform>();
			trt.anchorMin = Vector2.zero;
			trt.anchorMax = Vector2.one;
			trt.offsetMin = Vector2.zero;
			trt.offsetMax = Vector2.zero;
			Text text = textObject.AddComponent<Text>();
			text.font = font;
			text.fontSize = 12;
			text.alignment = TextAnchor.MiddleCenter;
			text.supportRichText = true;
			text.raycastTarget = false;
			ModMinimap.buttons[i] = b;
			ModMinimap.buttonTexts[i] = text;
		}
		ModMinimap.buttons[0].onClick.AddListener(new UnityAction(ModMinimap.ToggleTorps));
		ModMinimap.buttons[1].onClick.AddListener(new UnityAction(ModMinimap.ToggleSmoke));
		ModMinimap.buttons[2].onClick.AddListener(new UnityAction(ModMinimap.ToggleRings));
		ModMinimap.buttons[3].onClick.AddListener(new UnityAction(ModMinimap.ToggleLastSeen));
		barObject.transform.SetAsLastSibling();
		UnityEngine.Debug.Log("[MINIMAP] buttons added");
	}

	public static void ToggleTorps()
	{
		ModMinimap.Set(0, !ModMinimap.on[0]);
	}

	public static void ToggleSmoke()
	{
		ModMinimap.Set(1, !ModMinimap.on[1]);
	}

	public static void ToggleRings()
	{
		ModMinimap.Set(2, !ModMinimap.on[2]);
	}

	public static void ToggleLastSeen()
	{
		ModMinimap.Set(3, !ModMinimap.on[3]);
	}

	public static void Set(int i, bool value)
	{
		ModMinimap.on[i] = value;
		try
		{
			PlayerPrefs.SetInt(ModMinimap.keys[i], value ? 1 : 0);
			PlayerPrefs.Save();
		}
		catch
		{
		}
		ModMinimap.slowTimer = 0f;
		UnityEngine.Debug.Log("[MINIMAP] " + ModMinimap.names[i] + (value ? " on" : " off"));
	}

	public static void LoadSettings()
	{
		if (ModMinimap.loaded)
		{
			return;
		}
		ModMinimap.loaded = true;
		for (int i = 0; i < 4; i++)
		{
			ModMinimap.on[i] = PlayerPrefs.GetInt(ModMinimap.keys[i], 1) == 1;
		}
	}

	// ---------- helpers ----------

	// The game's map position for a world position (same sum the game uses for ship icons)
	public static Vector3 MapPos(Vector3 world, float z)
	{
		Vector3 origin = FloatingOrigin.instance.transformsToMove[0].position;
		return new Vector3(world.x - origin.x, world.z - origin.z, z);
	}

	// The width the game uses for its waypoint lines at the current zoom
	public static float LineWidth()
	{
		return Map.instance.mapCamera.orthographicSize / Config.instance.mapDefaultOrtho * Config.instance.mapLineThickness * Map.instance.mapMain.transform.localScale.x;
	}

	public static LineRenderer MakeLine(string name, Color colour)
	{
		if (ModMinimap.root == null || Map.instance.mapUnitNavRenderSegment == null)
		{
			return null;
		}
		GameObject go = Object.Instantiate<GameObject>(Map.instance.mapUnitNavRenderSegment, ModMinimap.root);
		go.name = name;
		go.transform.localPosition = Vector3.zero;
		go.transform.localRotation = Quaternion.identity;
		go.transform.localScale = Vector3.one;
		LineRenderer lr = go.GetComponent<LineRenderer>();
		if (lr == null)
		{
			Object.Destroy(go);
			return null;
		}
		lr.useWorldSpace = false;
		lr.loop = false;
		lr.positionCount = 0;
		// tint a copy of the line material, the vertex colours carry the fade
		lr.material = new Material(lr.sharedMaterial);
		lr.material.color = new Color(colour.r, colour.g, colour.b, 1f);
		lr.startColor = Color.white;
		lr.endColor = Color.white;
		return lr;
	}

	public static Text MakeLabel(Text sample)
	{
		if (ModMinimap.root == null || ModMinimap.root.GetComponentInParent<Canvas>() == null)
		{
			return null;
		}
		GameObject go = new GameObject("ModGhostLabel", new System.Type[] { typeof(RectTransform) });
		go.transform.SetParent(ModMinimap.root, false);
		go.layer = ModMinimap.root.gameObject.layer;
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.pivot = new Vector2(0f, 0.5f);
		rt.sizeDelta = new Vector2(200f, 30f);
		Text text = go.AddComponent<Text>();
		text.font = (sample != null && sample.font != null) ? sample.font : Resources.GetBuiltinResource<Font>("Arial.ttf");
		text.fontSize = (sample != null) ? sample.fontSize : 14;
		text.alignment = TextAnchor.MiddleLeft;
		text.supportRichText = true;
		text.raycastTarget = false;
		text.horizontalOverflow = HorizontalWrapMode.Overflow;
		return text;
	}

	public static void SetAlpha(LineRenderer lr, float start, float end)
	{
		if (lr == null)
		{
			return;
		}
		lr.startColor = new Color(1f, 1f, 1f, start);
		lr.endColor = new Color(1f, 1f, 1f, end);
	}

	public static void Circle(LineRenderer lr, Vector3 centre, float radius, int segments)
	{
		if (lr == null)
		{
			return;
		}
		lr.loop = true;
		lr.positionCount = segments;
		for (int i = 0; i < segments; i++)
		{
			float a = (float)i / (float)segments * Mathf.PI * 2f;
			lr.SetPosition(i, centre + new Vector3(Mathf.Cos(a) * radius, Mathf.Sin(a) * radius, 0f));
		}
	}

	public static void Segment(LineRenderer lr, Vector3 from, Vector3 to)
	{
		if (lr == null)
		{
			return;
		}
		lr.loop = false;
		lr.positionCount = 2;
		lr.SetPosition(0, from);
		lr.SetPosition(1, to);
	}

	public static void Kill(LineRenderer lr)
	{
		if (lr != null)
		{
			Object.Destroy(lr.gameObject);
		}
	}

	public static int CountActive(List<LineRenderer> list)
	{
		int n = 0;
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i] != null && list[i].gameObject.activeSelf)
			{
				n++;
			}
		}
		return n;
	}

	// New battle (or the map was rebuilt): remove everything the mod drew
	public static void ClearAll()
	{
		foreach (ModMinimap.Track t in ModMinimap.tracks.Values)
		{
			ModMinimap.Kill(t.trail);
			ModMinimap.Kill(t.ahead);
		}
		ModMinimap.tracks.Clear();
		for (int i = 0; i < ModMinimap.smokeLines.Count; i++)
		{
			ModMinimap.Kill(ModMinimap.smokeLines[i]);
		}
		ModMinimap.smokeLines.Clear();
		ModMinimap.Kill(ModMinimap.visualRing);
		ModMinimap.Kill(ModMinimap.radarRing);
		ModMinimap.visualRing = null;
		ModMinimap.radarRing = null;
		foreach (ModMinimap.Ghost g in ModMinimap.ghosts.Values)
		{
			ModMinimap.Kill(g.a);
			ModMinimap.Kill(g.b);
			if (g.label != null)
			{
				Object.Destroy(g.label.gameObject);
			}
		}
		ModMinimap.ghosts.Clear();
		ModMinimap.lastSeenPos.Clear();
	}
}
```

### Step 2 - ModRescue (replace the class)
1. Right-click class **ModRescue** > **Edit Class (C#)...** (check the title says *ModRescue*, not ModCampaignRescue)
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
1. Start a battle. A row of four buttons (Torpedoes, Smoke, Rings, Last seen) should appear at the bottom right, just above the map toolbar.
2. **Rings:** a white circle should sit around the ship you're looking at. Turn her radar on and a green circle should appear (on radar-fitted ships).
3. **Torpedoes:** fire torpedoes. Each should leave a blue track on the minimap, with a faint line ahead.
4. **Smoke:** lay smoke with a destroyer. Grey patches should appear behind her on the map.
5. **Last seen:** lose sight of an enemy. A red X with her name and minutes should stay where she was.
6. Click each button to switch its layer off and on, and press **F11** to switch them all.
7. Lines may be too thick, too thin, or drawn over the ship icons. If so, send a screenshot of the minimap, zoomed in and out, and the `[MINIMAP]` lines from `output_log.txt`. The sizes are easy to tune.
