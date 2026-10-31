using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class StartFleetLine
{
	public string name;

	public string at;

	public string to;

	public int formation;

	public List<string> ships;
}

// 1.0 prep (S1): historical start fleets read from Override/campaign/<id>/startfleets.txt (one JSON line per task force):
// {"name":"Enterprise Carrier Force","at":"G..","to":"G..","formation":12,"ships":["yorktown:enterprise","northampton:chester"]}
// Each ship is classID:shipName; "?classID:shipName" is optional (left out quietly when that class is not installed, e.g. CTM ships).
// Each ship is classID:shipName. If the name is not in the class (or already taken) the first free ship of the class is used.
// Hook: CampaignAI.CreateStandingMissions calls Add(...) with its six lists just before ModShipPick.FixStart, so the stock
// start-fleet code builds these forces for the player exactly like the campaign001/002 ones (log tag [STARTFLEET]).
public static class ModStartFleets
{
	public const bool On = true;

	public static void Add(List<string[]> classes, List<string[]> names, List<string> from, List<string> to, List<int> formations, List<string> titles)
	{
		if (!On)
		{
			return;
		}
		try
		{
			CampaignData campaignData = CampaignManager.instance.campaignData;
			if (campaignData == null)
			{
				return;
			}
			string text = "campaign/" + campaignData.campaignID + "/startfleets.txt";
			if (!Utilities.DoesGameFileExist(text))
			{
				return;
			}
			string[] array = AssetLoader.instance.ImportText(text);
			if (array == null)
			{
				return;
			}
			HashSet<string> hashSet = new HashSet<string>();
			for (int i = 0; i < classes.Count; i++)
			{
				for (int j = 0; j < classes[i].Length && j < names[i].Length; j++)
				{
					hashSet.Add(classes[i][j] + "|" + names[i][j]);
				}
			}
			int num = 0;
			int num2 = 0;
			for (int k = 0; k < array.Length; k++)
			{
				string text2 = array[k].Trim();
				if (text2.Length == 0 || text2.StartsWith("//"))
				{
					continue;
				}
				StartFleetLine startFleetLine = new StartFleetLine();
				try
				{
					JsonUtility.FromJsonOverwrite(text2, startFleetLine);
				}
				catch (Exception ex)
				{
					Debug.LogError("[STARTFLEET] startfleets.txt line " + (k + 1) + " is not valid: " + ex.Message);
					continue;
				}
				if (startFleetLine.ships == null || startFleetLine.ships.Count == 0 || string.IsNullOrEmpty(startFleetLine.at))
				{
					continue;
				}
				if (!CampaignManager.instance.seaNavigationIndexes.ContainsKey(startFleetLine.at))
				{
					Debug.LogError("[STARTFLEET] startfleets.txt: unknown waypoint " + startFleetLine.at + " for " + startFleetLine.name);
					continue;
				}
				string item = startFleetLine.at;
				if (!string.IsNullOrEmpty(startFleetLine.to) && CampaignManager.instance.seaNavigationIndexes.ContainsKey(startFleetLine.to))
				{
					item = startFleetLine.to;
				}
				List<string> list = new List<string>();
				List<string> list2 = new List<string>();
				for (int l = 0; l < startFleetLine.ships.Count; l++)
				{
					string text3 = startFleetLine.ships[l].Trim();
					string want = string.Empty;
					bool flag = text3.StartsWith("?");
					if (flag)
					{
						text3 = text3.Substring(1).Trim();
					}
					int num3 = text3.IndexOf(':');
					if (num3 >= 0)
					{
						want = text3.Substring(num3 + 1).Trim();
						text3 = text3.Substring(0, num3).Trim();
					}
					if (!EngagementManager.instance.unitDataDictionary.TryGetValue(text3, out var value))
					{
						if (flag)
						{
							Debug.Log("[STARTFLEET] optional class " + text3 + " is not installed, left out of " + startFleetLine.name);
							continue;
						}
						Debug.LogError("[STARTFLEET] startfleets.txt: unknown class " + text3 + " in " + startFleetLine.name);
						continue;
					}
					string text4 = PickShip(text3, value, want, hashSet, campaignData);
					if (text4 == null)
					{
						Debug.LogError("[STARTFLEET] startfleets.txt: no free ship left in class " + text3 + " for " + startFleetLine.name);
						continue;
					}
					hashSet.Add(text3 + "|" + text4);
					list.Add(text3);
					list2.Add(text4);
				}
				if (list.Count != 0)
				{
					classes.Add(list.ToArray());
					names.Add(list2.ToArray());
					from.Add(startFleetLine.at);
					to.Add(item);
					formations.Add(startFleetLine.formation);
					titles.Add(startFleetLine.name ?? string.Empty);
					num++;
					num2 += list.Count;
				}
			}
			Debug.Log("[STARTFLEET] startfleets.txt: " + num + " historical task forces, " + num2 + " ships");
		}
		catch (Exception ex2)
		{
			Debug.LogError("[STARTFLEET] startfleets.txt failed: " + ex2.Message);
		}
	}

	private static string PickShip(string cls, UnitData data, string want, HashSet<string> used, CampaignData cd)
	{
		List<string> instancesInClass = data.instancesInClass;
		if (instancesInClass == null || instancesInClass.Count == 0)
		{
			return null;
		}
		if (want.Length > 0)
		{
			for (int i = 0; i < instancesInClass.Count; i++)
			{
				if (string.Equals(instancesInClass[i], want, StringComparison.OrdinalIgnoreCase) && Free(cls, i, instancesInClass[i], used, cd))
				{
					return instancesInClass[i];
				}
			}
			Debug.Log("[STARTFLEET] " + want + " is not a free ship of class " + cls + ", using the next free one");
		}
		for (int j = 0; j < instancesInClass.Count; j++)
		{
			if (Free(cls, j, instancesInClass[j], used, cd))
			{
				return instancesInClass[j];
			}
		}
		return null;
	}

	private static bool Free(string cls, int index, string name, HashSet<string> used, CampaignData cd)
	{
		if (used.Contains(cls + "|" + name))
		{
			return false;
		}
		return CampaignManager.instance.GetIndexInDoubleList(cls, index, cd.playerOwnedShipClasses, cd.playerOwnedShipInstances) == -1;
	}
}
