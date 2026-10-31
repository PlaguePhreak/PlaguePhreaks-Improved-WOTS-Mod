using System;
using System.Collections.Generic;
using UnityEngine;

// Historical events on fixed dates, read from campaign/<campaignID>/history.txt (one JSON line per event).
// A campaign without that file has no historical events, so the stock campaigns are not affected.
// Called once per campaign day from CampaignManager.CheckDaily.
public static class ModHistory
{
	public class HistoryEvent
	{
		public string id = string.Empty;
		public int day;
		public int month;
		public int year;
		public string location = string.Empty;
		public int ifOwner = -1;          // only happens if the location belongs to this side (0 player, 1 enemy, 2 neutral, -1 any)
		public string check = "none";     // "none", "carriers" or "ships" (player warships)
		public float rangeKm = 500f;
		public int minCount = 1;
		public string passEvent = string.Empty;
		public string failEvent = string.Empty;
		public int passOwner = -1;        // new owner of the location (-1 = no change)
		public int failOwner = -1;
		public int passTroops;
		public int failTroops;
		public int passCP;                // command points given to the player (can be negative)
		public int failCP;
		public string warnEvent = string.Empty; // popup shown warnDays before the event (empty = no warning)
		public int warnDays = 7;
	}

	private static string loadedFor;
	private static List<HistoryEvent> events = new List<HistoryEvent>();
	private static DateTime lastDay = DateTime.MinValue;

	public static void Daily()
	{
		try
		{
			CampaignManager cm = CampaignManager.instance;
			string campaignID = cm.campaignData.campaignID;
			if (loadedFor != campaignID)
			{
				Load(campaignID);
				lastDay = DateTime.MinValue;
			}
			if (events.Count == 0)
			{
				return;
			}
			DateTime today = CampaignInterface.instance.dateTime.Date;
			// first call after starting or loading, or a jump in time (another save): only look at today
			if (lastDay == DateTime.MinValue || today <= lastDay || (today - lastDay).TotalDays > 7.0)
			{
				lastDay = today.AddDays(-1.0);
			}
			List<string> shown = new List<string>();
			for (int i = 0; i < events.Count; i++)
			{
				HistoryEvent e = events[i];
				DateTime date = new DateTime(e.year, e.month, e.day);
				DateTime warn = date.AddDays(-e.warnDays);
				if (!string.IsNullOrEmpty(e.warnEvent) && warn > lastDay && warn <= today && StillPossible(e))
				{
					Debug.Log("[HISTORY] " + e.id + " warning, " + e.warnDays + " days to go");
					shown.Add(e.warnEvent);
				}
				if (date > lastDay && date <= today)
				{
					string popup = Run(e);
					if (!string.IsNullOrEmpty(popup))
					{
						shown.Add(popup);
					}
				}
			}
			lastDay = today;
			Show(shown);
		}
		catch (Exception ex)
		{
			Debug.Log("[HISTORY] error " + ex.Message + " " + ex.StackTrace);
		}
	}

	private static void Load(string campaignID)
	{
		loadedFor = campaignID;
		events.Clear();
		string path = "campaign/" + campaignID + "/history.txt";
		if (!Utilities.DoesGameFileExist(path))
		{
			return;
		}
		string[] lines = AssetLoader.instance.ImportText(path);
		if (lines == null)
		{
			return;
		}
		for (int i = 0; i < lines.Length; i++)
		{
			string line = lines[i].Trim();
			if (line.Length == 0 || line.StartsWith("//"))
			{
				continue;
			}
			HistoryEvent e = new HistoryEvent();
			JsonUtility.FromJsonOverwrite(line, e);
			events.Add(e);
		}
		Debug.Log("[HISTORY] " + events.Count + " historical events loaded for " + campaignID);
	}

	// the event will still happen: its location has not changed hands
	private static bool StillPossible(HistoryEvent e)
	{
		MapLocation loc = string.IsNullOrEmpty(e.location) ? null : CampaignManager.instance.GetMapLocationObject(e.location);
		return loc == null || e.ifOwner < 0 || loc.currentFaction == e.ifOwner;
	}

	private static string Run(HistoryEvent e)
	{
		CampaignManager cm = CampaignManager.instance;
		MapLocation loc = string.IsNullOrEmpty(e.location) ? null : cm.GetMapLocationObject(e.location);
		if (loc != null && e.ifOwner >= 0 && loc.currentFaction != e.ifOwner)
		{
			Debug.Log("[HISTORY] " + e.id + " skipped, " + e.location + " belongs to side " + loc.currentFaction);
			return null;
		}
		bool pass = true;
		int count = 0;
		if (loc != null && e.check != "none")
		{
			count = CountPlayerShips(loc, e.check == "carriers", e.rangeKm);
			pass = count >= e.minCount;
		}
		Debug.Log("[HISTORY] " + e.id + " " + (pass ? "PASS" : "FAIL") + " (" + e.check + " within " + e.rangeKm + " km: " + count + ", need " + e.minCount + ")");
		int owner = pass ? e.passOwner : e.failOwner;
		int troops = pass ? e.passTroops : e.failTroops;
		int cp = pass ? e.passCP : e.failCP;
		if (loc != null && owner >= 0 && owner != loc.currentFaction)
		{
			SetOwner(loc, owner, troops);
		}
		if (cp != 0)
		{
			cm.campaignData.commandPoints[0] = Mathf.Max(0, cm.campaignData.commandPoints[0] + cp);
		}
		return pass ? e.passEvent : e.failEvent;
	}

	private static int CountPlayerShips(MapLocation loc, bool carriersOnly, float rangeKm)
	{
		CampaignManager cm = CampaignManager.instance;
		Vector2 where = (loc.gameObjectAnimator != null) ? loc.gameObjectAnimator.currentMap2DLocation : loc.locationPosition;
		int count = 0;
		for (int i = 0; i < cm.playerMobile.Count; i++)
		{
			WorldMapStrategyKit.GameObjectAnimator goa = cm.playerMobile[i];
			if (goa == null || goa.mobileMapObject == null || goa.mobileMapObject.type != 0)
			{
				continue;
			}
			MobileMapObject mmo = goa.mobileMapObject;
			if (cm.GetDistanceInMetresBetweenMapObjects(goa.currentMap2DLocation, where) / 1000f > rangeKm)
			{
				continue;
			}
			for (int j = 0; j < mmo.unitPrefabs.Count; j++)
			{
				UnitData data;
				if (!EngagementManager.instance.unitDataDictionary.TryGetValue(mmo.unitPrefabs[j], out data))
				{
					continue;
				}
				UnitSubType t = data.unitSubtype;
				if (carriersOnly)
				{
					if (t == UnitSubType.Aircraft_Carrier || t == UnitSubType.Light_Carrier)
					{
						count++;
					}
				}
				else if (t != UnitSubType.Merchant && t != UnitSubType.Oiler)
				{
					count++;
				}
			}
		}
		return count;
	}

	private static void SetOwner(MapLocation loc, int faction, int troops)
	{
		CampaignInterface.instance.SetFireToLocation(loc, false);
		for (int s = 0; s < 2; s++)
		{
			loc.troops[s] = 0;
			loc.supplies[s] = 0;
			loc.engineering[s] = 0;
			loc.fuel[s] = 0;
		}
		loc.currentFaction = faction;
		if (faction < 2)
		{
			loc.troops[faction] = troops;
			loc.supplies[faction] = troops * 2;
		}
		loc.GetComponentInChildren<SpriteRenderer>().color = CampaignInterface.instance.factionColours[faction];
		CampaignAI.instance.CheckUnsafeLocations(loc);
		Debug.Log("[HISTORY] " + loc.locationName + " now belongs to side " + faction + " with " + troops + " troops");
	}

	private static void Show(List<string> names)
	{
		if (names.Count == 0)
		{
			return;
		}
		CampaignEvent.instance.CreateEvent(names[0]);
		// more than one event on the same day: add the others to the first popup
		for (int i = 1; i < names.Count; i++)
		{
			string[] lines = AssetLoader.instance.ImportText("language/campaign/" + CampaignManager.instance.campaignData.campaignID + "/event/" + names[i] + ".txt");
			if (lines == null)
			{
				continue;
			}
			CampaignEventData d = new CampaignEventData();
			JsonUtility.FromJsonOverwrite(lines[0], d);
			CampaignEvent.instance.contentText.text = CampaignEvent.instance.contentText.text + "\n\n" + d.content;
		}
	}
}
