using System;
using System.Collections.Generic;
using UnityEngine;

// A weekly news pop-up: every Monday of the campaign, the headlines of the past week from
// campaign/<campaignID>/news.txt (one JSON line per item: day, month, year, text). Campaigns without the
// file get nothing. Turned off with the "Weekly news" switch in Mod Options.
// Called once per campaign day from CampaignManager.CheckDaily, after ModHistory.Daily().
public static class ModNews
{
	public class NewsItem
	{
		public int day;
		public int month;
		public int year;
		public string text = string.Empty;
	}

	public static string EventFile = "news";      // language/campaign/<id>/event/news.txt gives the header and frame
	public static DayOfWeek PaperDay = DayOfWeek.Monday;

	private static string loadedFor;
	private static List<NewsItem> items = new List<NewsItem>();
	private static DateTime lastDay = DateTime.MinValue;

	public static void Daily()
	{
		try
		{
			CampaignManager cm = CampaignManager.instance;
			if (cm == null || cm.campaignData == null || CampaignInterface.instance == null) return;
			string id = cm.campaignData.campaignID;
			if (loadedFor != id) { Load(id); lastDay = DateTime.MinValue; }
			if (items.Count == 0) return;
			DateTime today = CampaignInterface.instance.dateTime.Date;
			if (lastDay == DateTime.MinValue || today <= lastDay || (today - lastDay).TotalDays > 7.0) lastDay = today.AddDays(-1.0);
			bool paperDay = false;
			for (DateTime d = lastDay.AddDays(1.0); d <= today; d = d.AddDays(1.0)) if (d.DayOfWeek == PaperDay) paperDay = true;
			lastDay = today;
			if (!paperDay || !ModOptions.News) return;
			DateTime from = today.AddDays(-7.0);
			List<NewsItem> week = new List<NewsItem>();
			for (int i = 0; i < items.Count; i++)
			{
				DateTime when = new DateTime(items[i].year, items[i].month, items[i].day);
				if (when > from && when <= today) week.Add(items[i]);
			}
			if (week.Count == 0) return;
			Show(today, week);
		}
		catch (Exception ex)
		{
			Debug.Log("[NEWS] error " + ex.Message + " " + ex.StackTrace);
		}
	}

	private static void Load(string id)
	{
		loadedFor = id;
		items.Clear();
		string path = "campaign/" + id + "/news.txt";
		if (!Utilities.DoesGameFileExist(path)) return;
		string[] lines = AssetLoader.instance.ImportText(path);
		if (lines == null) return;
		for (int i = 0; i < lines.Length; i++)
		{
			string line = lines[i].Trim();
			if (line.Length == 0 || line.StartsWith("//")) continue;
			NewsItem n = new NewsItem();
			JsonUtility.FromJsonOverwrite(line, n);
			if (n.year > 0 && !string.IsNullOrEmpty(n.text)) items.Add(n);
		}
		items.Sort((a, b) => new DateTime(a.year, a.month, a.day).CompareTo(new DateTime(b.year, b.month, b.day)));
		Debug.Log("[NEWS] " + items.Count + " news items loaded for " + id);
	}

	private static void Show(DateTime today, List<NewsItem> week)
	{
		CampaignEvent ev = CampaignEvent.instance;
		if (ev == null) return;
		if (ev.gameObject.activeSelf) { Debug.Log("[NEWS] another pop-up is open, this week's paper is skipped"); return; }
		ev.CreateEvent(EventFile);
		System.Text.StringBuilder sb = new System.Text.StringBuilder();
		sb.Append("<size=18><b>WEEK ENDING ").Append(today.ToString("d MMMM yyyy").ToUpper()).Append("</b></size>\n");
		for (int i = 0; i < week.Count; i++)
		{
			NewsItem n = week[i];
			sb.Append("\n<color=#caa809>").Append(new DateTime(n.year, n.month, n.day).ToString("d MMM")).Append("</color>  ").Append(n.text);
		}
		sb.Append("\n\n<size=12><i>The weekly news can be turned off in Mod Options.</i></size>");
		ev.contentText.text = sb.ToString();
		Debug.Log("[NEWS] " + week.Count + " items for the week ending " + today.ToString("yyyy-MM-dd"));
	}
}
