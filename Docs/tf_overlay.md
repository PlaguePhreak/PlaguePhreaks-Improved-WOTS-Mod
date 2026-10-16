# v0.21.4 Task force overlay [TFOVERLAY]

Status: planned. Design and install steps written, not compiled or tested yet.

## What it does
Press **F11** on the campaign map to switch the overlay on or off (F11 is free on the campaign map, see keybinds.md).
- Under each of your task forces a small label: name, days of fuel left, speed in knots. Orange below 5 days, red below 3.
- Around the **selected** task force, one ring: how far it can still sail on its remaining fuel at its current speed.
- Updates once a second while it is on. Nothing is saved, nothing changes in the game, so it cannot break a campaign.

Later versions can add to it (detection rings, ammo, formation) without redoing the base.

## What the game code showed (so the design uses real data)
- Your task forces are `CampaignManager.instance.playerMobile` (a list of `GameObjectAnimator`). Each has `.mobileMapObject` (type 0 = ships).
- Fuel is `MobileMapObject.fuelUsedDays` against a fixed 10 days (`CampaignManager`, the fuel block near the LOW fuel warning). Days left = 10 - fuelUsedDays. The game's own text already shows this for the selected force only.
- `MobileMapObject.speed` is metres per second; the map ring radius is in km, so km = days left x 86,400 x speed / 1,000.
- The map can draw labels (`CampaignInterface.AddMarker2DText`) and rings (`CampaignInterface.map.AddCircle`, the game uses it for its own selection circle).
- The mod already adds its own map component the same way (`ModCampaignRescue`, added from `CampaignManager.CheckHourly`), so this follows a proven pattern.

## Decisions (defaults chosen, tell me if you want different)
1. Key: F11. 
2. Labels for all your task forces, ring only for the selected one (less clutter).
3. Fuel ring only in this first version. Detection ring is left out because the units of the sensor ranges are not confirmed yet.

## Install steps (dnSpy)
### Step 1 - add the new class
1. In dnSpy, right-click **Assembly-CSharp** > **Add Class...** (or right-click the `-` namespace > Add Class...).
2. Paste the whole code below, replacing what is there (the `using WorldMapStrategyKit;` line at the top is needed), then click **Compile**.

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using WorldMapStrategyKit;

public class ModTFOverlay : MonoBehaviour
{
	public static bool on;

	private float timer;

	private bool reported;

	private List<GameObject> objects = new List<GameObject>();

	private void Update()
	{
		try
		{
			CampaignInterface ci = CampaignInterface.instance;
			if (ci == null || CampaignManager.instance == null)
			{
				return;
			}
			if (Input.GetKeyDown(KeyCode.F11))
			{
				on = !on;
				timer = 0f;
				if (!on)
				{
					Clear();
				}
				Debug.Log("[TFOVERLAY] overlay " + (on ? "on" : "off"));
			}
			if (!on)
			{
				return;
			}
			timer -= Time.unscaledDeltaTime;
			if (timer > 0f)
			{
				return;
			}
			timer = 1f;
			Rebuild(ci);
		}
		catch (Exception ex)
		{
			if (!reported)
			{
				reported = true;
				Debug.LogError("[TFOVERLAY] failed: " + ex.ToString());
			}
		}
	}

	private void Clear()
	{
		for (int i = 0; i < objects.Count; i++)
		{
			if (objects[i] != null)
			{
				UnityEngine.Object.Destroy(objects[i]);
			}
		}
		objects.Clear();
	}

	private void Rebuild(CampaignInterface ci)
	{
		Clear();
		List<GameObjectAnimator> list = CampaignManager.instance.playerMobile;
		for (int i = 0; i < list.Count; i++)
		{
			GameObjectAnimator goa = list[i];
			if (goa == null || goa.mobileMapObject == null)
			{
				continue;
			}
			MobileMapObject mmo = goa.mobileMapObject;
			if (mmo.type != 0 || mmo.unitPrefabs.Count == 0)
			{
				continue;
			}
			float daysLeft = Mathf.Max(0f, 10f - mmo.fuelUsedDays);
			float knots = mmo.speed / 0.514444f;
			Color colour = Color.white;
			if (daysLeft < 3f)
			{
				colour = new Color(1f, 0.3f, 0.3f, 1f);
			}
			else if (daysLeft < 5f)
			{
				colour = new Color(1f, 0.6f, 0.15f, 1f);
			}
			Vector2 pos = goa.currentMap2DLocation;
			string text = mmo.mobileName + "\n" + daysLeft.ToString("F1") + " d fuel  " + knots.ToString("F0") + " kn";
			TextMesh tm = ci.AddMarker2DText(text, new Vector3(pos.x, pos.y - 0.012f, 0f), 6f, colour, false, false);
			if (tm != null)
			{
				objects.Add(tm.gameObject);
			}
			if (goa == ci.currentMapObject)
			{
				float km = daysLeft * 86400f * mmo.speed / 1000f;
				GameObject ring = ci.map.AddCircle(pos, km, 0.97f, 1f, new Color(1f, 0.6f, 0.1f, 0.7f));
				if (ring != null)
				{
					objects.Add(ring);
				}
			}
		}
	}
}
```

### Step 2 - start it with the campaign
1. In class **CampaignManager**, right-click method **CheckHourly** > **Edit Method (C#)...**
2. Find the lines that add `ModCampaignRescue` (an `if` that checks `GetComponent<ModCampaignRescue>() == null` and then `AddComponent<ModCampaignRescue>()`).
3. Directly after that whole `if { ... }` block, paste:
```csharp
if (base.gameObject.GetComponent<ModTFOverlay>() == null)
{
	base.gameObject.AddComponent<ModTFOverlay>();
}
```
4. Click **Compile**, then File > Save Module.

### Step 3 - test
1. Load a campaign, let one hour pass (the component starts on the first hourly check).
2. Press **F11**. Each of your task forces should get a label under it. Select one: an orange ring should appear.
3. Press F11 again: everything disappears.
4. Check `output_log.txt` for `[TFOVERLAY] overlay on`. If anything went wrong it says `[TFOVERLAY] failed:` with the reason.

## Things the test will tell us (could not be checked without running the game)
- Label size: `6f` in the `AddMarker2DText` call is a guess. Bigger number = bigger text.
- Label height: `pos.y - 0.012f` is a guess for how far below the icon it sits.
- If the ring looks too big or small, the game's `AddCircle` radius may not be km; tell me what you see and I will fix the maths.
- The speed shown is the force's set speed, even when it is stopped.
