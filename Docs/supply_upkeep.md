# v0.22 Troop supply upkeep [SUPPLY]

Status: tested by Aaron, works as intended. Covers both sides: the player and the AI.

## What it does
- Every campaign day, each location with troops (yours and the AI's) spends supplies to feed them: `ceil(troops x upkeepPerTroopPerDay)`. Default 0.03, so 1,000 troops use 30 supplies a day (the base game only spends supplies in ground fights, at 0.05 per troop a day).
- If the location cannot pay in full, it pays what it has and the troops go short: they lose `shortageLossPerDay` (default 2%) of their number that day, scaled by how much of the upkeep was missing. A garrison never drops below 1 troop.
- The location panel shows the days left next to the supply number, for example `4,000 (133 d)`.
- **AI resupply convoys:** each time the AI makes a strategic decision, before anything else, it looks at its non-home-port locations. The one with the fewest days of supply left, if under 10 days, gets a Convoy task force sent to it (the game's own Convoy missions carry supplies on every third transport and unload at the destination). Each location is only sent a convoy once every 12 days. This is checked first, so resupply has priority over reinforcements and invasions. You can sink these convoys.
- Weak supply also hurts ground fights, as in the base game: below 1 supply per troop a garrison fights at reduced strength.
- Nothing new is saved. A line `[SUPPLY]` is written to output_log.txt when a garrison goes short or a convoy is sent.

## Number changes (text files, both campaigns)
- Weekly income at home ports: supplies 4,000 -> 6,000 (`replenish0` and `replenish1` in each `setup.txt`). Check: all your garrisons together use about 360 supplies a day (about 2,500 a week), so the home port keeps about 3,500 a week for upgrades and shipping, more than before the change.
- Starting supplies of every outpost (not Rabaul / New Hebrides) cut from 2 x troops down to 1 x troops (new `mapLandLocations.txt` files in `Override/campaign/campaign001` and `campaign002`). That is about 33 days at the start, so the first convoys matter in the first month. The home ports keep their 20,000.
- To reload: copy these files into the game's override folder.

## What the game code showed
- `MapLocation.troops[faction]` and `MapLocation.supplies[faction]` are the stocks. Faction 0 is the player.
- Supplies are only used in `CampaignManager.CheckTroopEngagements` (ground fights) and for upgrades, aircraft and shipping, so a quiet garrison never starves in the base game.
- `CampaignManager.CheckDaily` already runs every campaign day and calls `CheckTroopEngagements()`; the new call goes right after it.
- `CampaignInterface.SetLocationPanelData` writes the four-line stock readout (troops, supplies, engineering, fuel); line 2 is the one changed.
- Starting numbers were read from `mapLandLocations.txt` (your side: about 12,000-14,700 troops in total, outposts 250-1,000 troops, home port 10,000). Unverified: how much one transport carries (`UnitData.cargo[1]`), so convoy size is judged in the first test.
- `CampaignAI.CreateAIMobileSea` already creates the Convoy and takes its cost from the AI's command points; the supplies on the ships appear from nothing (not taken from a port stock).

## Install steps (dnSpy)
### Step 1 - add the new class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Paste all the code below, click **Compile**.

```csharp
using System;
using UnityEngine;

public static class ModSupply
{
	public static float upkeepPerTroopPerDay = 0.03f;

	public static float shortageLossPerDay = 0.02f;

	public static bool playerOnly = false;

	public static int Upkeep(int troops)
	{
		if (troops <= 0)
		{
			return 0;
		}
		return Mathf.CeilToInt((float)troops * upkeepPerTroopPerDay);
	}

	public static string DaysLeft(MapLocation ml, int faction)
	{
		int num = Upkeep(ml.troops[faction]);
		if (num <= 0)
		{
			return string.Empty;
		}
		int num2 = ml.supplies[faction] / num;
		if (num2 > 99)
		{
			return " (99+ d)";
		}
		return " (" + num2 + " d)";
	}

	public static int day;

	public static System.Collections.Generic.Dictionary<string, int> lastConvoy = new System.Collections.Generic.Dictionary<string, int>();

	public static void AIResupply()
	{
		try
		{
			MapLocation mapLocation = null;
			int num = 10;
			for (int i = 0; i < CampaignManager.instance.landMapLocations.Count; i++)
			{
				MapLocation mapLocation2 = CampaignManager.instance.landMapLocations[i];
				if (mapLocation2.currentFaction != 1 || mapLocation2.troops[1] <= 0 || CampaignManager.instance.IsHomePort(mapLocation2, 1) || !CampaignManager.instance.seaNavigationIndexes.ContainsKey(mapLocation2.locationID))
				{
					continue;
				}
				if (lastConvoy.ContainsKey(mapLocation2.locationID) && day - lastConvoy[mapLocation2.locationID] < 12)
				{
					continue;
				}
				int num2 = mapLocation2.supplies[1] / Upkeep(mapLocation2.troops[1]);
				if (num2 < num)
				{
					num = num2;
					mapLocation = mapLocation2;
				}
			}
			if (!((UnityEngine.Object)mapLocation == (UnityEngine.Object)null) && CampaignAI.instance.CreateAIMobileSea(CampaignAI.instance.GetMissionByType(MissionType.Convoy), mapLocation.locationID))
			{
				lastConvoy[mapLocation.locationID] = day;
				Debug.Log("[SUPPLY] AI convoy sent to " + mapLocation.locationName + " with " + num + " days of supply left");
			}
		}
		catch (Exception ex)
		{
			Debug.Log("[SUPPLY] AI convoy error " + ex.Message);
		}
	}

	public static void Daily()
	{
		day++;
		try
		{
			for (int i = 0; i < CampaignManager.instance.landMapLocations.Count; i++)
			{
				MapLocation mapLocation = CampaignManager.instance.landMapLocations[i];
				for (int j = 0; j < 2; j++)
				{
					if (playerOnly && j != 0)
					{
						continue;
					}
					int num = mapLocation.troops[j];
					int num2 = Upkeep(num);
					if (num2 <= 0)
					{
						continue;
					}
					if (mapLocation.supplies[j] >= num2)
					{
						mapLocation.supplies[j] -= num2;
						continue;
					}
					float num3 = 1f - (float)mapLocation.supplies[j] / (float)num2;
					mapLocation.supplies[j] = 0;
					int num4 = Mathf.Max(1, Mathf.CeilToInt((float)num * shortageLossPerDay * num3));
					mapLocation.troops[j] = Mathf.Max(1, num - num4);
					Debug.Log("[SUPPLY] " + mapLocation.locationName + " faction " + j + " short of supplies, lost " + num4 + " troops, " + mapLocation.troops[j] + " left");
				}
			}
		}
		catch (Exception ex)
		{
			Debug.Log("[SUPPLY] error " + ex.Message);
		}
	}
}
```

### Step 2 - daily upkeep
1. Open **CampaignManager** > method **CheckDaily**.
2. Right-click the line `CheckTroopEngagements();` > **Edit Method...**
3. Under that line add: `ModSupply.Daily();`
4. Click **Compile**.

### Step 3 - AI convoys first
1. Open **CampaignAI** > method **MakeStrategicDecision**.
2. Right-click > **Edit Method...**
3. Find the first block `if (GetForceAvailable() < 0)` `{ return; }` (right after `strategicMMOCreated = false;`).
4. Directly after that block (before `bool flag = false;`) add: `ModSupply.AIResupply();`
5. Click **Compile**.

### Step 4 - days left on the location panel
1. Open **CampaignInterface** > method **SetLocationPanelData**.
2. Right-click > **Edit Method...**
3. Find the line: `empty = empty + component.supplies[0].ToString("#,##0") + "\n";`
4. Replace it with: `empty = empty + component.supplies[0].ToString("#,##0") + ModSupply.DaysLeft(component, 0) + "\n";`
5. Click **Compile**, then **File > Save Module**.

## Test
1. Start a campaign and open one of your locations that has troops. Check the supplies line shows `(NN d)`.
2. Let a few days pass (time acceleration). Supplies should go down by about the upkeep each day.
3. Use a small outpost with little supply, or lower supplies by building an upgrade. When the days left reach 0, troops should drop a little each day and `[SUPPLY]` lines should appear in output_log.txt.
4. Watch an AI outpost: after a few weeks a convoy should head for it (look for `[SUPPLY] AI convoy` in the log) and its supplies jump when it arrives.
5. Tell me the troop and supply numbers you see so I can tune the two rates.

## Later parts of v0.22
- v0.22.1 a warning message when a garrison has under 3 days left.
- v0.22.2 AI convoys take their supplies from the home port stock instead of creating them from nothing; a supply-only convoy mission.
- v0.22.3 supply convoys / delivery to far garrisons.
