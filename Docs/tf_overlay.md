# v0.21.4 Task force overlay [TFOVERLAY]

Status: planned. Design and install steps written, not compiled or tested yet.

## What it does
Press **F11** on the campaign map, or click the **fuel barrel button** at the top left, to switch the overlay on or off (F11 is free on the campaign map, see keybinds.md). Hovering over the button shows "Distance 1 day of fuel gives". The button is built by `ModTFOverlay.MakeButton(root, index, icon, text, tooltip, action, out back)`, so future mod buttons use index 1, 2, 3... and stack down the left side (46 pixels apart).
- Under each of your task forces a small label: name, days of fuel left, speed in knots. Orange below 5 days, red below 3.
- Around the **selected** task force, one ring: how far it sails in 1 day (`ringDays`) at its current speed, or less if it has less than a day of fuel left. (Fuel burns per day spent moving, not by speed, so a faster force goes further on the same fuel.)
- Updates once a second while it is on. Nothing is saved, nothing changes in the game, so it cannot break a campaign.

Later versions can add to it (detection rings, ammo, formation) without redoing the base.

## What the game code showed (so the design uses real data)
- Your task forces are `CampaignManager.instance.playerMobile` (a list of `GameObjectAnimator`). Each has `.mobileMapObject` (type 0 = ships).
- Fuel is `MobileMapObject.fuelUsedDays` against a fixed 10 days (`CampaignManager`, the fuel block near the LOW fuel warning). Days left = 10 - fuelUsedDays. The game's own text already shows this for the selected force only.
- `MobileMapObject.speed` is metres per second. The map ring (`AddCircle`) does NOT use real km on this map: the game turns metres into map units with `campaignData.mapWidthMetres`, and `AddCircle` turns km into map units with the whole-Earth width (40,030 km). So the code converts metres to map units first, then multiplies by 40,030. Test 1 showed the ring was ~450 km instead of the expected size, which is what led to this.
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
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using WorldMapStrategyKit;

public class ModTFOverlay : MonoBehaviour
{
	public static bool on;

	public static float labelSize = 0.01f;

	public static float ringDays = 1f;

	public static string tip = "Distance 1 day of fuel gives";

	private float timer;

	private bool reported;

	private bool buttonReported;

	private List<GameObject> objects = new List<GameObject>();

	private GameObject buttonObject;

	private Image buttonBack;

	private void Update()
	{
		try
		{
			CampaignInterface ci = CampaignInterface.instance;
			if (ci == null || CampaignManager.instance == null)
			{
				return;
			}
			if (buttonObject == null)
			{
				BuildButton(ci);
			}
			if (Input.GetKeyDown(KeyCode.F11))
			{
				Toggle();
			}
			if (buttonBack != null)
			{
				buttonBack.color = on ? new Color(0.5f, 0.3f, 0.08f, 0.95f) : new Color(0.07f, 0.12f, 0.19f, 0.92f);
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

	private void OnDisable()
	{
		Clear();
		if (buttonObject != null)
		{
			UnityEngine.Object.Destroy(buttonObject);
		}
	}

	private void Toggle()
	{
		on = !on;
		timer = 0f;
		if (!on)
		{
			Clear();
		}
		Debug.Log("[TFOVERLAY] overlay " + (on ? "on" : "off"));
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

	private void BuildButton(CampaignInterface ci)
	{
		if (ci.pauseButtonImage == null || ci.pauseButtonImage.canvas == null)
		{
			return;
		}
		Transform root = ci.pauseButtonImage.canvas.rootCanvas.transform;
		Sprite icon = null;
		try
		{
			icon = AssetLoader.instance.ImportSprite("interface/images/map/fuelbarrel.png");
		}
		catch (Exception ex)
		{
			Debug.LogError("[TFOVERLAY] could not load fuelbarrel.png: " + ex.Message);
		}
		if (!buttonReported)
		{
			buttonReported = true;
			Debug.Log("[TFOVERLAY] button added, icon " + ((icon != null) ? "loaded" : "not found"));
		}
		buttonObject = MakeButton(root, 0, icon, "FUEL", tip, new UnityAction(Toggle), out buttonBack);
	}

	public static GameObject MakeButton(Transform root, int index, Sprite icon, string fallbackText, string tooltip, UnityAction action, out Image back)
	{
		GameObject go = new GameObject("ModButton " + index, new Type[1] { typeof(RectTransform) });
		go.transform.SetParent(root, false);
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.anchorMin = new Vector2(0f, 1f);
		rt.anchorMax = new Vector2(0f, 1f);
		rt.pivot = new Vector2(0f, 1f);
		rt.anchoredPosition = new Vector2(10f, -10f - (float)index * 46f);
		rt.sizeDelta = new Vector2(40f, 40f);
		Image frame = go.AddComponent<Image>();
		frame.color = new Color(0.72f, 0.58f, 0.3f, 1f);
		Button button = go.AddComponent<Button>();
		button.targetGraphic = frame;
		button.onClick.AddListener(action);
		GameObject inner = new GameObject("Back", new Type[1] { typeof(RectTransform) });
		inner.transform.SetParent(go.transform, false);
		RectTransform irt = inner.GetComponent<RectTransform>();
		irt.anchorMin = Vector2.zero;
		irt.anchorMax = Vector2.one;
		irt.offsetMin = new Vector2(2f, 2f);
		irt.offsetMax = new Vector2(-2f, -2f);
		back = inner.AddComponent<Image>();
		back.color = new Color(0.07f, 0.12f, 0.19f, 0.92f);
		back.raycastTarget = false;
		GameObject face = new GameObject("Icon", new Type[1] { typeof(RectTransform) });
		face.transform.SetParent(go.transform, false);
		RectTransform frt = face.GetComponent<RectTransform>();
		frt.anchorMin = Vector2.zero;
		frt.anchorMax = Vector2.one;
		frt.offsetMin = new Vector2(5f, 5f);
		frt.offsetMax = new Vector2(-5f, -5f);
		if (icon != null)
		{
			Image img = face.AddComponent<Image>();
			img.sprite = icon;
			img.preserveAspect = true;
			img.raycastTarget = false;
		}
		else
		{
			Text label = face.AddComponent<Text>();
			label.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
			label.text = fallbackText;
			label.fontSize = 11;
			label.alignment = TextAnchor.MiddleCenter;
			label.color = new Color(1f, 0.67f, 0.24f, 1f);
			label.raycastTarget = false;
		}
		EventTrigger trigger = go.AddComponent<EventTrigger>();
		EventTrigger.Entry enter = new EventTrigger.Entry();
		enter.eventID = EventTriggerType.PointerEnter;
		enter.callback.AddListener(delegate(BaseEventData d)
		{
			if (TooltipManager.instance != null)
			{
				TooltipManager.instance.isBasicTip = true;
				TooltipManager.instance.SetToolTip(tooltip);
			}
		});
		trigger.triggers.Add(enter);
		EventTrigger.Entry exit = new EventTrigger.Entry();
		exit.eventID = EventTriggerType.PointerExit;
		exit.callback.AddListener(delegate(BaseEventData d)
		{
			if (TooltipManager.instance != null)
			{
				TooltipManager.instance.ClearToolTip();
			}
		});
		trigger.triggers.Add(exit);
		return go;
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
			TextMesh tm = ci.AddMarker2DText(text, new Vector3(pos.x, pos.y - 0.012f, 0f), labelSize, colour, false, false);
			if (tm != null)
			{
				objects.Add(tm.gameObject);
			}
			if (goa == ci.currentMapObject)
			{
				float metres = Mathf.Min(ringDays, daysLeft) * 86400f * mmo.speed;
				float km = metres / CampaignManager.instance.campaignData.mapWidthMetres * 40030f;
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

### Step 1b - the barrel icon
1. Copy [fuelbarrel.png](/mnt/project-files/v0.21.4/fuelbarrel.png) into the game's Override folder at `Override/interface/images/map/fuelbarrel.png` (the same folder as survivors.png). The repo already has it there.
2. If the file is missing the button still works and shows the word FUEL instead.

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
- Label size: `labelSize = 0.01f` at the top of the class is a guess (it was 6, which was far too big and is the likely cause of the white blob in the first test). Bigger number = bigger text.
- Label height: `pos.y - 0.012f` is a guess for how far below the icon it sits.
- Ring size: test with the `\` ruler. A force at 21 kn should show a ring about 930 km from the icon (24 hours at 39 km/h). `ringDays = 1f` can be changed (2f = two days).
- The speed shown is the force's set speed, even when it is stopped.
