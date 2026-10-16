# Limited number of the new TTE ships

Each new ship type now has a fixed pool of 10-30 ships (a random number per type, fixed in the files). Once a ship is built or sunk, it is gone from the pool.

## Pool sizes
heywood 14, president_jackson 27, attack_transport 26, hospital_ship 23, arcturus 27, harris 19, mount_hood 24, patapsco 15, manley 15 (its existing list), mccawley 28, generic_maru 26, type_1b 17, type_1c 26, type_1k 18, type_2tl 11, type_3a 15, type_a_merchant 30, ural_maru 30, akita_maru 30, kasagisan_maru 30, taihosan_maru 11, hakushika_maru 10, aratama_maru 29.

## How it works
- **Player:** each ship class lists `namesInClass` / `instancesInClass` in `language\english\unit\sea\<id>.txt`. One name = one ship you can own. To change a pool, add or remove names (the two lists must have the same length).
- **AI:** the game does not count AI merchants or oilers (it always picks instance 0). So `CampaignAI.GetMissionPrefabs` needs the edit below. Ships with no names (the stock merchants) stay unlimited, as before.

## dnSpy steps (CampaignAI.GetMissionPrefabs)
1. Open Assembly-CSharp in dnSpy, find class **CampaignAI**, method **GetMissionPrefabs**.
2. Right-click the method > **Edit Method (C#)...**
3. Select all, paste the code below, click **Compile**.
4. **File > Save Module**.

```csharp
private List<string> GetMissionPrefabs(List<string> unitTypes)
{
	List<string> list = new List<string>();
	Func<List<string>, string> pickLimited = delegate(List<string> pool)
	{
		List<string> list3 = new List<string>(pool);
		while (list3.Count > 0)
		{
			int index = Random.Range(0, list3.Count);
			string text2 = list3[index];
			list3.RemoveAt(index);
			UnitData unitData = EngagementManager.instance.unitDataDictionary[text2];
			if (unitData.namesInClass.Count == 0)
			{
				return text2 + "|0";
			}
			if (CampaignManager.instance.IsEnemyShipClassAvailable(text2))
			{
				for (int k = 0; k < unitData.instancesInClass.Count; k++)
				{
					if (CampaignManager.instance.IsEnemyShipInstanceAvailable(text2, k) == -1)
					{
						CampaignManager.instance.ModifyShipInLists(isAdded: true, text2, k, 0, CampaignManager.instance.campaignData.enemyOwnedShipClasses, CampaignManager.instance.campaignData.enemyOwnedShipInstances, CampaignManager.instance.campaignData.enemyOwnedRepairDays);
						return text2 + "|" + k;
					}
				}
			}
		}
		return string.Empty;
	};
	for (int i = 0; i < unitTypes.Count; i++)
	{
		string text = string.Empty;
		if (alternates.ContainsKey(unitTypes[i]))
		{
			List<string> list2 = alternates[unitTypes[i]];
			for (int j = 0; j < list2.Count; j++)
			{
				if (list2[j] == "Merchant" && transports.Count > 0)
				{
					text = pickLimited(transports);
				}
				else if (list2[j] == "Oiler" && oilers.Count > 0)
				{
					text = pickLimited(oilers);
				}
				else if (availableDesignations.ContainsKey(list2[j]))
				{
					text = GetAvailableShipClassString(availableDesignations[list2[j]]);
				}
				if (text != string.Empty)
				{
					list.Add(text);
					break;
				}
			}
		}
		else if (unitTypes[i] == "Transport" && transports.Count > 0)
		{
			text = pickLimited(transports);
			if (text != string.Empty)
			{
				list.Add(text);
			}
		}
		else if (unitTypes[i] == "Oiler" && oilers.Count > 0)
		{
			text = pickLimited(oilers);
			if (text != string.Empty)
			{
				list.Add(text);
			}
		}
	}
	return list;
}
```

If dnSpy complains about `Func` or `Random`, add `using System;` / `using UnityEngine;` at the top of the editor window, or write `System.Func<...>` and `UnityEngine.Random`.

## Test
1. New campaign, let the AI send convoys for a few weeks. Sunk AI ships should not come back, and no ship name appears twice in one convoy.
2. Buy ships as the player: each ship name can be bought once.
3. Tell me if convoys stop forming: that means every Merchant/Oiler pool is empty and only the stock ships are left.
