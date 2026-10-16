# v0.22.4 Admiralty supply convoy event [CONVOY]

Status: planned, code written, not yet compiled or tested. Builds on the v0.22 supply work (`supply_upkeep.md`).

## What it does
- Every 20 to 30 days (random) the Admiralty sends a supply convoy to your first home port. A popup announces it.
- It appears at a random spot on the northern edge of the map (a random one of the 40 northernmost sea waypoints, so anywhere from west to east) and sails to the home port by itself.
- Ships: 3 transports (one carries troops, one supplies, one engineering), 1 oiler (fuel) and 1 to 3 destroyers.
- Cargo is random but never below 2,000 supplies, 2,000 troops, 100 fuel and 100 engineering. The top end is whatever each ship can carry (read from the unit files), so if a ship cannot carry the minimum it just carries its maximum. The log line `[CONVOY]` shows the numbers.
- The convoy belongs to **you** (the game has no neutral side). The enemy AI hunts spotted player fleets and goes for transports and oilers first. For the first 6 game hours the enemy is told where it is (it is added to the enemy's spotted list). After that they must find it themselves.
- At 12 km from the home port the cargo is unloaded into the port, the convoy is removed and a popup shows. Ships that were sunk take their cargo with them, so you only receive what survives.
- If every transport and oiler is sunk, a "Convoy Lost" popup shows and the next timer starts.
- Not saved: if you save and reload while the convoy is at sea, it stays on the map as a normal task force (you can unload it by hand) and a new timer starts.

## Files (text, both campaigns)
Copy `Override/language/english/campaign/campaign001/event/` and `campaign002/event/` files `convoyspawn.txt`, `convoyarrived.txt`, `convoylost.txt`, and the pictures `Override/campaign/image/rules_convoy.jpg` and `rules_convoylost.jpg`, into the game's override folder.

## Install steps (dnSpy)
### Step 1 - add the new class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Paste all the code below, click **Compile**.

```csharp
using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using WorldMapStrategyKit;

public static class ModConvoy
{
	public static int minTroops = 2000;
	public static int minSupplies = 2000;
	public static int minEngineering = 100;
	public static int minFuel = 100;
	public static int minDays = 20;
	public static int maxDays = 30;
	public static int huntHours = 6;

	public static int daysLeft = -1;
	public static GameObjectAnimator convoy;
	public static MapLocation destination;

	private static string Pick(UnitSubType subtype)
	{
		List<string> list = new List<string>();
		foreach (KeyValuePair<string, UnitListData> kv in EngagementManager.instance.unitSeaDictionary)
		{
			if (CampaignManager.instance.campaignData.nations0.Contains(kv.Value.nation) && EngagementManager.instance.unitDataDictionary[kv.Key].unitSubtype == subtype)
			{
				list.Add(kv.Key);
			}
		}
		if (list.Count == 0)
		{
			return null;
		}
		return list[UnityEngine.Random.Range(0, list.Count)];
	}

	private static int Roll(string prefab, int cargoIndex, int minimum)
	{
		List<int> cargo = EngagementManager.instance.unitDataDictionary[prefab].cargo;
		if (cargo == null || cargo.Count != 4)
		{
			return 0;
		}
		int max = cargo[cargoIndex];
		if (max < minimum)
		{
			return max;
		}
		return UnityEngine.Random.Range(minimum, max + 1);
	}

	public static void Daily()
	{
		try
		{
			if ((UnityEngine.Object)convoy != (UnityEngine.Object)null)
			{
				return;
			}
			if (daysLeft < 0)
			{
				daysLeft = UnityEngine.Random.Range(minDays, maxDays + 1);
				Debug.Log("[CONVOY] next convoy in " + daysLeft + " days");
				return;
			}
			daysLeft--;
			if (daysLeft > 0)
			{
				return;
			}
			if (!Spawn())
			{
				daysLeft = 1;
			}
			else
			{
				daysLeft = -1;
			}
		}
		catch (Exception ex)
		{
			Debug.Log("[CONVOY] error " + ex.Message + " " + ex.StackTrace);
			daysLeft = -1;
		}
	}

	public static bool Spawn()
	{
		CampaignAI ai = CampaignAI.instance;
		CampaignManager cm = CampaignManager.instance;
		destination = null;
		for (int i = 0; i < ai.playerHomePorts.Count; i++)
		{
			if (ai.playerHomePorts[i].currentFaction == 0)
			{
				destination = ai.playerHomePorts[i];
				break;
			}
		}
		if ((UnityEngine.Object)destination == (UnityEngine.Object)null)
		{
			return false;
		}
		List<SeaNavigationWaypoint> top = new List<SeaNavigationWaypoint>();
		for (int j = 0; j < cm.seaNavigationPoints.Count; j++)
		{
			if (!cm.seaNavigationPoints[j].isLocation)
			{
				top.Add(cm.seaNavigationPoints[j]);
			}
		}
		top.Sort((SeaNavigationWaypoint a, SeaNavigationWaypoint b) => b.positionRadius.y.CompareTo(a.positionRadius.y));
		SeaNavigationWaypoint spawn = top[UnityEngine.Random.Range(0, Math.Min(40, top.Count))];

		string merchant = Pick(UnitSubType.Merchant);
		string oiler = Pick(UnitSubType.Oiler);
		if (merchant == null || oiler == null)
		{
			Debug.Log("[CONVOY] no allied transport or oiler found");
			return false;
		}
		List<string> prefabs = new List<string> { merchant, merchant, merchant, oiler };
		int[] amount = new int[4];
		List<string> cargo = new List<string>();
		amount[0] = Roll(merchant, 0, minTroops);
		amount[1] = Roll(merchant, 1, minSupplies);
		amount[2] = Roll(merchant, 2, minEngineering);
		amount[3] = Roll(oiler, 3, minFuel);
		cargo.Add(amount[0] + "|0|0|0");
		cargo.Add("0|" + amount[1] + "|0|0");
		cargo.Add("0|0|" + amount[2] + "|0");
		cargo.Add("0|0|0|" + amount[3]);
		int escorts = UnityEngine.Random.Range(1, 4);
		for (int e = 0; e < escorts; e++)
		{
			string destroyer = Pick(UnitSubType.Destroyer);
			if (destroyer == null)
			{
				break;
			}
			prefabs.Add(destroyer);
			cargo.Add("0|0|0|0");
		}

		MobileMapObject tf = ai.newTaskForce;
		CampaignInterface.instance.ClearNewGroupData(tf);
		tf.unitPrefabs = prefabs;
		for (int k = 0; k < prefabs.Count; k++)
		{
			UnitData ud = EngagementManager.instance.unitDataDictionary[prefabs[k]];
			tf.unitInstances.Add(0);
			tf.unitDisplayNames.Add(ud.namesInClass.Count > 0 ? ud.namesInClass[0] : ud.unitName);
			tf.cellVariables.Add(string.Empty);
			tf.ammunitionRemaining.Add(string.Empty);
			tf.aircraftCooldown.Add(string.Empty);
			tf.cargo.Add(cargo[k]);
			tf.bombardments.Add(0);
			tf.paint.Add(0);
			tf.speedModifier.Add(1f);
			tf.currentAircraft.Add(string.Empty);
		}
		tf.formation = 8;
		tf.formationSpacing = 0;
		tf.mobileName = "SUPPLY CONVOY";
		tf.customName = true;
		cm.SetMobileMapObjectSensors(tf);
		tf.currentFaction = 0;

		GameObjectAnimator previous = CampaignInterface.instance.currentMapObject;
		GameObjectAnimator goa = CampaignInterface.instance.CreateNewMobileObject(CampaignObjectType.Sea, tf, new Vector2(spawn.positionRadius.x, spawn.positionRadius.y), false, null, string.Empty);
		CampaignInterface.instance.currentMapObject = previous;
		convoy = goa;

		CampaignInterface.instance.MoveMobileToDestination(goa, destination.gameObjectAnimator.currentMap2DLocation, true);

		goa.mobileMapObject.spottedTimer = huntHours * 3600f;
		if (!cm.spottedContacts.Contains(goa.mobileMapObject))
		{
			cm.spottedContacts.Add(goa.mobileMapObject);
		}

		Debug.Log("[CONVOY] spawned at " + spawn.waypointName + " heading for " + destination.locationName + " troops " + amount[0] + " supplies " + amount[1] + " engineering " + amount[2] + " fuel " + amount[3] + " escorts " + escorts);
		CampaignEvent.instance.CreateEvent("convoyspawn");
		CampaignEvent.instance.contentText.text = CampaignEvent.instance.contentText.text + "\n\n<b>Cargo:</b> " + amount[0] + " troops, " + amount[1] + " supplies, " + amount[2] + " engineering, " + amount[3] + " fuel.\n<b>Destination:</b> " + destination.locationName + ".";
		return true;
	}

	public static void Tick()
	{
		try
		{
			if ((UnityEngine.Object)convoy == (UnityEngine.Object)null)
			{
				return;
			}
			MobileMapObject mmo = convoy.mobileMapObject;
			if ((UnityEngine.Object)mmo == (UnityEngine.Object)null || (Utilities.DoesMobileContainSubtype(mmo, UnitSubType.Merchant).Count == 0 && Utilities.DoesMobileContainSubtype(mmo, UnitSubType.Oiler).Count == 0))
			{
				Lost();
				return;
			}
			MapLocation near = CampaignManager.instance.GetClosestLocation(convoy);
			if ((UnityEngine.Object)near == (UnityEngine.Object)null || (UnityEngine.Object)near != (UnityEngine.Object)destination || near.currentFaction != 0)
			{
				return;
			}
			int[] got = new int[4];
			for (int i = 0; i < mmo.cargo.Count; i++)
			{
				string[] parts = mmo.cargo[i].Split(new char[1] { '|' });
				for (int j = 0; j < 4 && j < parts.Length; j++)
				{
					got[j] += int.Parse(parts[j]);
				}
			}
			CampaignManager.instance.RemoveAllCargoFromShips(mmo);
			GameObjectAnimator done = convoy;
			convoy = null;
			CampaignInterface.instance.DestroyMapMobileObject(done);
			Debug.Log("[CONVOY] arrived at " + near.locationName + " troops " + got[0] + " supplies " + got[1] + " engineering " + got[2] + " fuel " + got[3]);
			CampaignEvent.instance.CreateEvent("convoyarrived");
			CampaignEvent.instance.contentText.text = CampaignEvent.instance.contentText.text + "\n\n<b>Delivered:</b> " + got[0] + " troops, " + got[1] + " supplies, " + got[2] + " engineering, " + got[3] + " fuel.";
		}
		catch (Exception ex)
		{
			Debug.Log("[CONVOY] tick error " + ex.Message + " " + ex.StackTrace);
		}
	}

	private static void Lost()
	{
		convoy = null;
		Debug.Log("[CONVOY] convoy lost");
		CampaignEvent.instance.CreateEvent("convoylost");
	}
}
```

### Step 2 - daily timer
1. Open **CampaignManager** > method **CheckDaily**.
2. Right-click > **Edit Method...**
3. Find the line `CheckTroopEngagements();` and add under it: `ModConvoy.Daily();`
   (If you already added `ModSupply.Daily();` there, put this one on the next line.)
4. Click **Compile**.

### Step 3 - arrival and loss check
1. Open **CampaignManager** > method **Check1Min**.
2. Right-click > **Edit Method...**
3. Add as the very first line inside the method: `ModConvoy.Tick();`
4. Click **Compile**, then **File > Save Module**.

## Test
1. Start a campaign and pass 20 to 30 days (time acceleration). Check output_log.txt for `[CONVOY] next convoy in N days`, then `[CONVOY] spawned at ...`.
2. When the popup shows, check the convoy is on the map at the top edge and moving towards your home port. If it sits at the bottom of the map instead, the "top" direction is flipped: tell me and I flip one sign.
3. Check an enemy task force heads for it in the first hours.
4. Let it reach the port: you should see "Convoy Arrived", the home port supplies/troops/fuel/engineering go up, and the log line `[CONVOY] arrived`.
5. Tell me anything odd: the convoy stops at land, no popup, cargo smaller than 2,000 (a ship may be too small to carry it, the log shows the numbers), or a crash (send the log).

## Known risks
- The route is found by the map's water pathfinder, not by the AI waypoints, so it may take a different path than the AI convoys.
- Port stock limits (`replenish0Max`) are not checked by me; the game's own unload code decides what happens if a port is full.
- The spawn can be deep in enemy waters. That is part of the danger.
