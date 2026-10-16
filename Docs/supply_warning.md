# v0.22.1 Low supply warning [SUPPLY]

Status: planned, code written, not yet compiled or tested. Builds on v0.22 (supply_upkeep.md).

## What it does
- When one of YOUR locations has 3 days of supply left or fewer, a message appears with the alarm sound: `Low on supplies: Port Moresby (2 d), Milne Bay (OUT)`.
- `(OUT)` means the supply is gone and the troops are starving (they lose men every day).
- One combined message per day (up to 4 locations, then "and N more"), so messages do not cover each other.
- Each location warns once when it gets low and once more when it runs out. It warns again only after it has been resupplied above 3 days and runs low again, so it does not nag every day.
- The game does not pause. (`pauseOnWarning` in the code can be set to true if you want it to pause.)
- The warning is only for your side. The AI side has no messages.

## What the game code showed
- `ErrorPanel.instance.SetErrorMessage(key, s0, s1, s2)` shows a message and plays the sound for that key; the texts live in `language/dictionary/campaign_message.txt` as two lines per key (the text, then the sound). Messages like "ship delivered" use the same panel.
- `<0>` in a text is replaced by the first string passed in, so the new key `SupplyLow=<0>` simply shows the whole line the code builds.

## Install steps
### Part A - text file (already done if I copied it for you)
`language/campaign_message.txt` in the `v0.22` folder has two new lines at the end (`SupplyLow=<0>` and its sound). It goes to `...\StreamingAssets\override\language\english\dictionary\campaign_message.txt`.

### Part B - dnSpy: replace the ModSupply class
1. In dnSpy open **Assembly-CSharp** and find the class **ModSupply** (in the `-` namespace).
2. Right-click **ModSupply** > **Edit Class (C#)...** (if you only see Edit Method, delete the class and add it again with Add Class).
3. Select all the text, paste the whole code below over it, click **Compile**.
4. **File > Save Module**.

No other edits are needed: the existing `ModSupply.Daily();` call already runs it.

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

public static class ModSupply
{
	public static float upkeepPerTroopPerDay = 0.03f;

	public static float shortageLossPerDay = 0.02f;

	public static bool playerOnly = false;

	public static int warnDays = 3;

	public static bool pauseOnWarning = false;

	public static int day;

	public static Dictionary<string, int> lastConvoy = new Dictionary<string, int>();

	public static Dictionary<string, int> warnLevel = new Dictionary<string, int>();

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

	private static string CheckWarning(MapLocation ml, bool shortToday)
	{
		string locationID = ml.locationID;
		int num = Upkeep(ml.troops[0]);
		if (num <= 0)
		{
			warnLevel.Remove(locationID);
			return string.Empty;
		}
		int num2 = ml.supplies[0] / num;
		int num3 = 0;
		if (shortToday || ml.supplies[0] <= 0)
		{
			num3 = 2;
		}
		else if (num2 <= warnDays)
		{
			num3 = 1;
		}
		int num4 = 0;
		if (warnLevel.ContainsKey(locationID))
		{
			num4 = warnLevel[locationID];
		}
		warnLevel[locationID] = num3;
		if (num3 > num4)
		{
			if (num3 == 2)
			{
				return ml.locationName + " (OUT)";
			}
			return ml.locationName + " (" + num2 + " d)";
		}
		return string.Empty;
	}

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
			List<string> list = new List<string>();
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
					bool shortToday = false;
					if (mapLocation.supplies[j] >= num2)
					{
						mapLocation.supplies[j] -= num2;
					}
					else
					{
						shortToday = true;
						float num3 = 1f - (float)mapLocation.supplies[j] / (float)num2;
						mapLocation.supplies[j] = 0;
						int num4 = Mathf.Max(1, Mathf.CeilToInt((float)num * shortageLossPerDay * num3));
						mapLocation.troops[j] = Mathf.Max(1, num - num4);
						Debug.Log("[SUPPLY] " + mapLocation.locationName + " faction " + j + " short of supplies, lost " + num4 + " troops, " + mapLocation.troops[j] + " left");
					}
					if (j == 0)
					{
						string text = CheckWarning(mapLocation, shortToday);
						if (text != string.Empty)
						{
							list.Add(text);
						}
					}
				}
			}
			if (list.Count > 0)
			{
				string text2 = string.Empty;
				for (int k = 0; k < list.Count && k < 4; k++)
				{
					if (k > 0)
					{
						text2 += ", ";
					}
					text2 += list[k];
				}
				if (list.Count > 4)
				{
					text2 = text2 + " and " + (list.Count - 4) + " more";
				}
				ErrorPanel.instance.SetErrorMessage("SupplyLow", "Low on supplies: " + text2, string.Empty, string.Empty);
				Debug.Log("[SUPPLY] warning: " + text2);
				if (pauseOnWarning)
				{
					CampaignInterface.instance.PauseCampaign();
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

## Test
1. Use time acceleration on a campaign and watch an outpost of yours (about 33 days from the start at 1 supply per troop). To get there faster, load supplies from an outpost onto a ship with the cargo screen to drain it.
2. When a location reaches 3 days of supply, the message `Low on supplies: ...` should appear once with the alarm sound.
3. When it hits 0, one more message with `(OUT)`.
4. Resupply it (unload a convoy there) and let it fall low again: the warning should come back.
5. Check `[SUPPLY] warning` lines in output_log.txt.
