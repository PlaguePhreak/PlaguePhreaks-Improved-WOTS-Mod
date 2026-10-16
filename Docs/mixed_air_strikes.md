# Mixed air strike packages

**What was wrong (found in the code)**
- The Create New Air panel has a number counter for every aircraft type, but `CampaignInterface.PlayerDoneNewAirStrike` only launches the one highlighted type.
- Each air group on the map can only hold one aircraft type with one payload. The AI gets round this by launching one group per type and making the faster groups escort the slowest one (`CampaignAI.GroupAIAirStrike`), so they fly together.

**What changes**
1. **Done launches a package:** every aircraft type with a number above 0 takes off.
2. **Payloads:** the highlighted type uses the payload chosen in the dropdown. Every other type uses its first (standard) payload, for example bombs for dive bombers and a torpedo for torpedo bombers. Fighters carry nothing.
3. **One package:** the groups stay together on the map. The faster ones escort the slowest one, the same way the AI does it. You give orders to the slowest group (it is selected after launch) and the others follow it. They enter the battle together, so with the air wave fix they arrive as one wave.
4. Aircraft counts, launch cooldowns and the "aircraft launched" messages work as before, once per type.

Back up the DLL first.

## Step 1 - CampaignInterface.PlayerDoneNewAirStrike
1. Right-click **PlayerDoneNewAirStrike** (class **CampaignInterface**) > **Edit Method (C#)...**
2. Press **Ctrl+A** and paste this over everything:
```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using WorldMapStrategyKit;

public partial class CampaignInterface : MonoBehaviour
{
	public void PlayerDoneNewAirStrike()
	{
		if (!this.CheckAirAllowed())
		{
			return;
		}
		int selectedIndex = this.GetAirStrikeIndex();
		int selectedPayload = this.payloadDropdown.value;
		List<GameObjectAnimator> package = new List<GameObjectAnimator>();
		for (int t = 0; t < this.prefabsToLaunch.Count && t < this.numberToLaunch.Count; t++)
		{
			if (this.numberToLaunch[t] <= 0)
			{
				continue;
			}
			if (package.Count > 0)
			{
				this.ClearNewGroupData(this.newTaskForce);
			}
			for (int i = 0; i < this.numberToLaunch[t]; i++)
			{
				this.newTaskForce.unitPrefabs.Add(this.prefabsToLaunch[t]);
				this.newTaskForce.paint.Add(0);
			}
			this.newTaskForce.currentFaction = 0;
			this.newTaskForce.formation = 5;
			this.newTaskForce.formationSpacing = 50;
			this.newTaskForce.payload = new List<int>();
			UnitListData airData = EngagementManager.instance.unitAirDictionary[this.newTaskForce.unitPrefabs[0]];
			int payloadChoice = (t == selectedIndex) ? selectedPayload : 0;
			if (payloadChoice >= airData.payloadDisplayNames.Count - 1 || payloadChoice >= airData.payloadIndexes.Count)
			{
				this.newTaskForce.payload.Clear();
			}
			else
			{
				string[] parts = airData.payloadIndexes[payloadChoice].Split(new char[] { '|' });
				for (int j = 0; j < parts.Length; j++)
				{
					this.newTaskForce.payload.Add(int.Parse(parts[j].Trim()));
				}
			}
			if (this.currentMapObject.mobileMapObject != null && this.currentMapObject.mobileMapObject.type == 0)
			{
				int shipIndex = this.GetShipHighlightedIndex();
				List<int> carried = CampaignManager.instance.GetIntListFromString(this.currentMapObject.mobileMapObject.currentAircraft[shipIndex]);
				carried[t] = carried[t] - this.numberToLaunch[t];
				this.currentMapObject.mobileMapObject.currentAircraft[shipIndex] = CampaignManager.instance.SetIntListToString(carried);
				CampaignManager.instance.ApplyCooldownToAirLauncher(null, this.currentMapObject.mobileMapObject, shipIndex, this.newTaskForce);
				ErrorPanel.instance.SetErrorMessage("NewAir", this.numberToLaunch[t].ToString(), EngagementManager.instance.unitDataDictionary[this.newTaskForce.unitPrefabs[0]].unitName, this.currentMapObject.mobileMapObject.unitDisplayNames[shipIndex]);
			}
			else
			{
				MapLocation location = this.currentMapObject.GetComponent<MapLocation>();
				location.inTheAir[t] = location.inTheAir[t] + this.numberToLaunch[t];
				CampaignManager.instance.ApplyCooldownToAirLauncher(location, null, -1, this.newTaskForce);
				ErrorPanel.instance.SetErrorMessage("NewAir", this.numberToLaunch[t].ToString(), EngagementManager.instance.unitDataDictionary[this.newTaskForce.unitPrefabs[0]].unitName, location.locationName);
			}
			List<string> origin = new List<string>();
			string displayName = string.Empty;
			if (this.currentMapObject.type == 3)
			{
				origin.Add(this.currentMapObject.GetComponent<MapLocation>().locationID);
				displayName = this.currentMapObject.GetComponent<MapLocation>().locationName;
			}
			else
			{
				int shipIndex2 = this.GetShipHighlightedIndex();
				origin.Add(this.currentMapObject.mobileMapObject.unitPrefabs[shipIndex2]);
				origin.Add(this.currentMapObject.mobileMapObject.unitInstances[shipIndex2].ToString());
				displayName = this.currentMapObject.mobileMapObject.unitDisplayNames[shipIndex2];
			}
			GameObjectAnimator launched = this.CreateNewMobileObject(CampaignObjectType.Air, this.newTaskForce, this.currentMapObject.currentMap2DLocation, false, origin, displayName);
			if (launched != null)
			{
				package.Add(launched);
			}
		}
		if (package.Count == 0)
		{
			return;
		}
		GameObjectAnimator leader = package[0];
		for (int p = 1; p < package.Count; p++)
		{
			if (package[p].mobileMapObject.speed < leader.mobileMapObject.speed)
			{
				leader = package[p];
			}
		}
		for (int p = 0; p < package.Count; p++)
		{
			if (package[p] != leader)
			{
				package[p].mobileMapObject.escortingThisGOA = leader;
			}
		}
		this.ApplyHighlightColor(this.currentMapObject, false);
		this.SelectMapObject(leader);
		this.payloadDropdown.value = 0;
		this.currentMapObject.isMoving = false;
		this.isSelectingAircraftType = false;
	}
}
```
3. **Compile**, then **File > Save Module**.

If Compile shows errors, send me a screenshot of the error list. The names most likely to need a tweak are `UnitListData` (the type of the aircraft data) and `ClearNewGroupData`.

## Testing
1. On a carrier, open Create New Air. Set Wildcat 8, Avenger 8 and the third type 8 (or whatever you carry). Highlight the Avenger and pick its torpedo payload. Press Done.
2. You should get one "launched" message per type, and three air groups take off. The slowest one is selected.
3. Send the selected group at a target: the other two should follow it.
4. In battle, all three types should arrive together.
5. Launching a single type still works as before (set the other types to 0).

Note: I could not compile or run this.


## Final working version (tested)
Fixes found in testing:
1. `CreateNewMobileObject` makes the new air group the game's "current map object". The method now saves the launcher (airfield or carrier) first and restores it before each launch. Without this the second type crashed and the panel froze.
2. `ClearNewGroupData` resets the scratch group to a ship group, so `RefundUnpurchasedShips` crashed every time a panel closed. Add `this.newTaskForce.type = 1;` after `this.newTaskForce.currentFaction = 0;`.
3. **OpenCreateAirStrike:** the counters start at 0, so only the types you raise with + are launched. Paste just before the method's closing brace:
```csharp
for (int z = 0; z < this.numberToLaunch.Count && z < this.availableAircraftNumbers.Length; z++)
{
    this.numberToLaunch[z] = 0;
    if (this.availableAircraftNumbers[z] != null && z < this.maxToLaunch.Count)
    {
        this.availableAircraftNumbers[z].text = "0 / " + this.maxToLaunch[z].ToString();
    }
}
```
Result: each type is its own air group, and the faster groups escort the slowest one, so the package flies and arrives together. A true single mixed group was not attempted: payload, flight split, endurance, speed and the return to base all assume one aircraft type per group.
