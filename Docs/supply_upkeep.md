# v0.22 Troop supply upkeep [SUPPLY]

Status: planned, code written, not yet compiled or tested.

## What it does
- Every campaign day, each of your locations with troops spends supplies to feed them: `ceil(troops x upkeepPerTroopPerDay)`. Default 0.02, so 1,000 troops use 20 supplies a day (the base game only spends supplies in ground fights, at 0.05 per troop a day).
- If the location cannot pay in full, it pays what it has and the troops go short: they lose `shortageLossPerDay` (default 2%) of their number that day, scaled by how much of the upkeep was missing. A garrison never drops below 1 troop.
- The location panel shows the days left next to the supply number, for example `4,000 (200 d)`. Locations with no troops show the plain number.
- By design the AI side is NOT affected yet (it has no way to resupply its outlying bases; that is a later v0.22.x part). `playerOnly` is the one setting to change that.
- Nothing new is saved: days left is worked out from the numbers the game already saves. A line `[SUPPLY]` is written to output_log.txt whenever a garrison goes short.

## What the game code showed
- `MapLocation.troops[faction]` and `MapLocation.supplies[faction]` are the stocks. Faction 0 is the player.
- Supplies are only used in `CampaignManager.CheckTroopEngagements` (ground fights) and for upgrades, aircraft and shipping, so a quiet garrison never starves in the base game.
- `CampaignManager.CheckDaily` already runs every campaign day and calls `CheckTroopEngagements()`; the new call goes right after it.
- `CampaignInterface.SetLocationPanelData` writes the four-line stock readout (troops, supplies, engineering, fuel); line 2 is the one changed.
- Unknown until tested: how many troops and supplies locations start with, so the default rates are a guess. Look at the panel numbers in a test and tune the two numbers in `ModSupply`.

## Install steps (dnSpy)
### Step 1 - add the new class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Paste all the code below, click **Compile**.

```csharp
using System;
using UnityEngine;

public static class ModSupply
{
	public static float upkeepPerTroopPerDay = 0.02f;

	public static float shortageLossPerDay = 0.02f;

	public static bool playerOnly = true;

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

	public static void Daily()
	{
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

### Step 3 - days left on the location panel
1. Open **CampaignInterface** > method **SetLocationPanelData**.
2. Right-click > **Edit Method...**
3. Find the line: `empty = empty + component.supplies[0].ToString("#,##0") + "\n";`
4. Replace it with: `empty = empty + component.supplies[0].ToString("#,##0") + ModSupply.DaysLeft(component, 0) + "\n";`
5. Click **Compile**, then **File > Save Module**.

## Test
1. Start a campaign and open one of your locations that has troops. Check the supplies line shows `(NN d)`.
2. Let a few days pass (time acceleration). Supplies should go down by about the upkeep each day.
3. Use a small outpost with little supply, or lower supplies by building an upgrade. When the days left reach 0, troops should drop a little each day and `[SUPPLY]` lines should appear in output_log.txt.
4. Tell me the troop and supply numbers you see so I can tune the two rates.

## Later parts of v0.22
- v0.22.1 a warning message when a garrison has under 3 days left.
- v0.22.2 AI side upkeep, together with the AI resupplying its own bases.
- v0.22.3 supply convoys / delivery to far garrisons.
