# Campaign clock fix (v0.17.12)

## The bug
Day 0 starts at 12:00 and the day counter ticks over at 12:00, but the daily refresh (supplies, command points, repairs, aircraft replenishment and so on) happens a little earlier every day. After 70 days it can come at about 09:00.

**Found in the code:** the game runs two separate clocks.
- The clock you see (and the day counter) is `CampaignInterface.dateTime`, moved on every frame in `CampaignInterface.Update`. It is exact.
- The refreshes use their own counters in `CampaignManager.FixedUpdate` (`timer1Min`, `timer5Min`, `timerHour`, `timerDay`, `timerWeek`). Each is a `float` that gets a tiny step added 50 times a second, and fires when it reaches 60 s / 5 min / 1 h / 24 h / 1 week.
- A `float` can't hold a number like 80,000 very precisely, so each tiny step is rounded, and here it rounds up. At x1 speed the daily counter fills about **28 minutes early** each day. At x60 it is about 0.4 minutes early, and at x300 and above it is exact. So how far the refresh drifts depends on how much time you spend at slow speed, and the drift adds up day after day. The timers are saved with the campaign, so the drift carries over between sessions.

## The fix
The refreshes now follow the clock you see. Each one fires when the clock itself passes the next minute, 5 minutes, hour, day (12:00) or week, counted from the campaign start. The game's own timers are still kept up to date, as they are saved with the campaign. Existing saves are fixed as soon as they are loaded: the first refresh after loading comes at the right time.

## Install (2 steps)
1. **Add Class (C#)** (right-click `Assembly-CSharp` > Add Class (C#)), paste all of `ModClock.cs` below, **Compile**, then **File > Save Module**. Close and reopen dnSpy.
2. Find `CampaignManager`, right-click the method **`FixedUpdate`** > **Edit Method (C#)**, replace the whole method with the code below, **Compile**, then **File > Save Module**.

### ModClock.cs
```csharp
using UnityEngine;

// v0.17.12: campaign refreshes (daily supplies, command points, repairs, hourly checks...) follow the campaign clock.
// The game counted them with separate float timers. Adding tiny steps to a big float rounds up at slow time speeds
// (at x1 a "day" timer filled about 28 minutes early), so refreshes crept earlier every day while the day counter
// stayed at 12:00. Now each refresh fires when the clock itself passes the minute, 5 minutes, hour, day (12:00) or week.
public class ModClock
{
	// 1 min, 5 min, hour, day, week (the same intervals the game sets in CampaignManager.Awake)
	public static double[] intervals = new double[] { 60.0, 300.0, 3600.0, 86400.0, 604800.0 };
	public static long[] last = new long[5];
	public static CampaignData data;
	public static double lastElapsed = -1.0;

	// Called from CampaignManager.FixedUpdate. Returns bits: 1 = 1 min, 2 = 5 min, 4 = hour, 8 = day, 16 = week
	public static int Due(CampaignData cd)
	{
		try
		{
			double el = (CampaignInterface.instance.dateTime - CampaignInterface.instance.startDate).TotalSeconds;
			if (el < 0.0)
			{
				el = 0.0;
			}
			// new or loaded campaign, the clock went backwards, or it jumped more than half a day (being set while loading):
			// line up with the clock without firing anything
			if (cd != ModClock.data || el < ModClock.lastElapsed || el - ModClock.lastElapsed > 43200.0)
			{
				double expected = el - System.Math.Floor(el / 86400.0) * 86400.0;
				double ahead = cd.timerDay - expected;
				if (ahead > 43200.0)
				{
					ahead -= 86400.0;
				}
				if (ahead < -43200.0)
				{
					ahead += 86400.0;
				}
				UnityEngine.Debug.Log("[CLOCK] synced refresh timers to the campaign clock at day " + System.Math.Floor(el / 86400.0).ToString("F0") + ", " + CampaignInterface.instance.dateTime.ToString("HH:mm") + " (the game's old daily timer was " + (ahead / 60.0).ToString("F0") + " min ahead)");
				ModClock.data = cd;
				for (int i = 0; i < 5; i++)
				{
					ModClock.last[i] = (long)System.Math.Floor(el / ModClock.intervals[i]);
				}
			}
			ModClock.lastElapsed = el;
			int bits = 0;
			for (int i = 0; i < 5; i++)
			{
				long idx = (long)System.Math.Floor(el / ModClock.intervals[i]);
				if (idx > ModClock.last[i])
				{
					ModClock.last[i] = idx;
					bits |= 1 << i;
				}
			}
			// keep the game's own timers roughly right too (they are saved with the campaign)
			cd.timer1Min = (float)(el - System.Math.Floor(el / 60.0) * 60.0);
			cd.timer5Min = (float)(el - System.Math.Floor(el / 300.0) * 300.0);
			cd.timerHour = (float)(el - System.Math.Floor(el / 3600.0) * 3600.0);
			cd.timerDay = (float)(el - System.Math.Floor(el / 86400.0) * 86400.0);
			cd.timerWeek = (float)(el - System.Math.Floor(el / 604800.0) * 604800.0);
			if ((bits & 8) != 0)
			{
				UnityEngine.Debug.Log("[CLOCK] daily refresh for day " + ModClock.last[3] + " at " + CampaignInterface.instance.dateTime.ToString("HH:mm"));
			}
			return bits;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[CLOCK] failed: " + ex.Message);
			return 0;
		}
	}
}
```

### CampaignManager.FixedUpdate
```csharp
private void FixedUpdate()
{
	if (CampaignInterface.instance.map.timeSpeed == 0f)
	{
		return;
	}
	this.campaignData.timerWeather += Time.deltaTime * CampaignInterface.instance.map.timeSpeed;
	// v0.17.12: refreshes follow the campaign clock (ModClock)
	int due = ModClock.Due(this.campaignData);
	if ((due & 16) != 0)
	{
		this.CheckWeekly();
	}
	if ((due & 8) != 0)
	{
		this.CheckDaily();
	}
	if ((due & 4) != 0)
	{
		this.CheckHourly();
	}
	if ((due & 2) != 0)
	{
		this.Check5Min();
	}
	if ((due & 1) != 0)
	{
		this.Check1Min();
	}
}
```

## Testing
1. Load a save that has the problem (for example your day 70 campaign) and play to the next 12:00.
2. Supplies, command points and repairs should now come at 12:00 on the clock, the same moment the day counter changes.
3. In `output_log.txt`:
   - after loading: `[CLOCK] synced refresh timers to the campaign clock at day 70, 08:15 (the game's old daily timer was 182 min ahead)`. This shows how far off the old timer was.
   - each day: `[CLOCK] daily refresh for day 71 at 12:00`.
4. Try a day at x1 speed: it should still refresh at 12:00.

## Notes
- Daily refreshes, the day counter and the 12:00 tick-over are now always the same moment.
- If the game ever jumps the clock forward by more than half a day in one go, the timers line up again without firing (so nothing gets paid twice).
- `timerWeather` is left as it was (the game never reads it).
- Tag: `[CLOCK]`. I could not compile or run this.
