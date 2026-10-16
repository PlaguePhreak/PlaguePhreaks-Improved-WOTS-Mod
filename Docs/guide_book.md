# v0.22.5 Features and change log book [GUIDE]

Status: installed and tested (v0.22.5). Text updated for v0.23 to v0.23.2 (new pages Custom ships and Credits): see "Updating the book text" below. The update is not compiled yet.

## Updating the book text (v0.23.2) - short steps
The book text is inside the DLL, so it needs one dnSpy edit. Only the lists `titles` and `bodies` changed (3 new pages: CUSTOM SHIPS after SUPPLY, CREDITS at the end; page 1 and the supply convoy text changed).
1. In dnSpy, open Assembly-CSharp and find the class **ModGuide**.
2. Right-click the class **ModGuide** > **Edit Class (C#)...**
3. Select all the code, delete it, and paste the whole class from the code block below (Step 1).
4. Click **Compile**. If it gives errors, send me the exact message.
5. **File > Save Module**.
6. Start the game, open a campaign and click the book: you should see 12 pages. Check page 1, page 4 (CUSTOM SHIPS) and the last page (CREDITS).

No other method changes. Nothing else in the DLL needs touching.

## What it does
- A **book button** at the top left of the campaign map. The fuel barrel button moves down one slot (the mod's button maker stacks buttons by index: book = 0, fuel = 1).
- Hover the book: the tip says "Features and change log".
- Click it: a text-only popup in the style of the F5 Campaign Summary, with a scroll wheel / scroll bar and three buttons: **Previous**, **Close**, **Next**. Previous is hidden on the first page, Next on the last.
- Page 1 is "What's new" (short change log). Every page after that covers one area of the mod (events, repair and damage, crews, fuel, AI, air, torpedoes, battle UI, keys). Within a page you scroll down through the features.
- Nothing is saved and nothing changes in the game.

To add or change text later, only the `titles` / `bodies` lists in `ModGuide` are touched. Text colours: `<color=#E0B030>gold</color>` for headings, `<b>bold</b>` for names.

## How it fits the game code (checked in the decompiled DLL, v0.21.4+)
- `ModTFOverlay.MakeButton(root, index, icon, fallbackText, tooltip, action, out back)` is public and static, builds a 40x40 button at the top left, `index` x 46 pixels down, with a hover tip. `ModGuide` reuses it.
- `ModTFOverlay.BuildButton` runs whenever the campaign interface exists and the fuel button is missing, so the book is built at the same time and also rebuilt after a load.
- Icon is loaded the same way as the fuel barrel: `AssetLoader.instance.ImportSprite("interface/images/map/guidebook.png")`. If the picture is missing the button shows the word BOOK instead.

## Install steps (dnSpy)
### Step 0 - the icon (file, no dnSpy)
Copy `Override/interface/images/map/guidebook.png` from this repo into the game's `Override\interface\images\map\` folder (same place as `survivors.png`).

### Step 1 - add the new class
1. In dnSpy, right-click **Assembly-CSharp** > **Add Class...**
2. Paste the whole code below, replacing what is there, then click **Compile**.

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

public static class ModGuide
{
	private static GameObject button;
	private static GameObject panel;
	private static Text titleText;
	private static Text bodyText;
	private static Text pageText;
	private static RectTransform contentRect;
	private static GameObject prevButton;
	private static GameObject nextButton;
	private static int page;
	private static Font font;
	private static int fontSize = 16;

	private static readonly Color gold = new Color(0.72f, 0.58f, 0.3f, 1f);
	private static readonly Color dark = new Color(0.07f, 0.12f, 0.19f, 0.97f);

	private static string[] titles = new string[]
	{
		"WHAT'S NEW",
		"EVENTS",
		"SUPPLY",
		"CUSTOM SHIPS",
		"REPAIR AND DAMAGE",
		"CREWS AND VETERANCY",
		"FUEL AND SHIPS",
		"SMARTER AI",
		"AIR",
		"TORPEDOES",
		"BATTLE UI AND KEYS",
		"CREDITS"
	};

	private static string[] bodies = new string[]
	{
		"<color=#E0B030><b>Version 0.23 to 0.23.2</b></color>\n" +
		"23 new merchant ships, oilers and transports from the TTE team (not made by the mod author), in limited numbers: 10-30 of each type for each side. The Manley now sits between the submarines and the destroyers in the ship list.\n\n" +
		"<color=#E0B030><b>Version 0.22.5</b></color>\n" +
		"This book. It lists what the mod has added and what the keys are. Use Next and Previous to turn the pages and scroll down inside a page.\n\n" +
		"<color=#E0B030><b>Version 0.22.4</b></color>\n" +
		"Admiralty supply convoy event: every 20-30 days a convoy sails to your home port.\n\n" +
		"<color=#E0B030><b>Version 0.22</b></color>\n" +
		"Troops use supplies every day. The AI sends supply convoys to its low outposts. Weekly supplies at home ports went up to 6,000.\n\n" +
		"<color=#E0B030><b>Version 0.21</b></color>\n" +
		"Faster ship buying, historical torpedo duds and glancing hits that bounce, and the fuel overlay (button below this one, or F11).\n\n" +
		"The full list is in the Change Log file.",

		"<color=#E0B030><b>Survivors event</b></color>\n" +
		"Every few days a ship is reported sunk somewhere on the campaign map. Sail a task force to the lifebuoy marker within 24 hours to save the survivors. Your own men refill your crews without losing experience. Enemy survivors become prisoners (command points).\n\n" +
		"<color=#E0B030><b>Supply convoy event</b></color>\n" +
		"Every 20-30 days the Admiralty sends a convoy of 3 transports, 1 oiler and some destroyers. It appears on the northern edge of the map. For now it does not sail by itself (a fix is planned), so send it to your home port yourself. The enemy knows where it is for the first 6 hours. Ships that are sunk take their cargo with them, so you only get what survives. Do not lose it.",

		"<color=#E0B030><b>Troop supplies</b></color>\n" +
		"Every day each location with troops spends 3% of its troop number in supplies. A garrison that runs dry slowly loses troops. The location panel shows how many days of supply are left.\n\n" +
		"<color=#E0B030><b>AI convoys</b></color>\n" +
		"The AI sends convoys to its outposts that are running low. You can sink them.\n\n" +
		"<color=#E0B030><b>Numbers</b></color>\n" +
		"Weekly supplies at home ports are 6,000. Outposts start with 1 supply per troop.",

		"<color=#E0B030><b>New merchant ships</b></color>\n" +
		"23 merchant ships, transports, a hospital ship, an oiler (Patapsco) and a destroyer escort (Manley) were added. ALL of them are made by the TTE team and used with their permission. They are not the work of the mod author.\n\n" +
		"<color=#E0B030><b>Limited numbers</b></color>\n" +
		"Each type has a pool of 10-30 ships for each side. A ship that is built or sunk is gone for good. The stock merchants (C3 Cargo, Nippon Maru, Kamogawa Maru) are unlimited, so convoys can still form when the new pools run out.\n\n" +
		"<color=#E0B030><b>Convoys</b></color>\n" +
		"The AI builds its convoys from a random mix of the merchants and oilers, new ones included. A hospital ship can turn up in a convoy.\n\n" +
		"<color=#E0B030><b>Ship list</b></color>\n" +
		"The Manley sits between the submarines and the destroyers.",

		"<color=#E0B030><b>Lasting damage</b></color>\n" +
		"Knocked-out equipment stays broken until you get to a port.\n\n" +
		"<color=#E0B030><b>Damaged ships</b></color>\n" +
		"Damaged ships slow their task force. Ships can list and capsize, and counter-flooding helps.\n\n" +
		"<color=#E0B030><b>Damage control</b></color>\n" +
		"Works on the most urgent job first, and fires being fought can't spread. Colours: yellow light damage, orange heavy damage, red knocked out (fixable at sea), black destroyed or needs a port, grey patched as far as it can go (needs a port). Engine rooms can always be repaired at sea, but only back to 50% health and half power until a port repair.",

		"<color=#E0B030><b>Veterancy</b></color>\n" +
		"Only counts from real fights (an enemy has to be there, and something has to be sunk or shot down).\n\n" +
		"<color=#E0B030><b>Crews</b></color>\n" +
		"Every ship has its real crew size (hover over a ship to see Men). Ships lose men from hits, fires and flooding, and losing men costs progress towards the next rank. Ships below 80% crew reload and repair slower and have fewer damage control parties.\n\n" +
		"<color=#E0B030><b>Recruits</b></color>\n" +
		"Taking on new recruits at port (Rearm) resets your progress, or drops a rank.",

		"<color=#E0B030><b>Fuel overlay</b></color>\n" +
		"Click the fuel barrel button (or press F11 on the campaign map). Every task force of yours gets a label with days of fuel left and speed (orange below 5 days, red below 3). The selected one gets a ring showing how far it sails in 1 day.\n\n" +
		"<color=#E0B030><b>Ordering ships</b></color>\n" +
		"Ships have to be ordered and built, with build times and deposits. After you order a ship, the name list moves on to the next ship of that class you can still buy.\n\n" +
		"<color=#E0B030><b>Task forces</b></color>\n" +
		"Up to 20 ships, new formations and bigger AI fleets. Several task forces can join the same battle (pincers).",

		"<color=#E0B030><b>Formations</b></color>\n" +
		"AI fleets hold formation.\n\n" +
		"<color=#E0B030><b>Torpedo attacks</b></color>\n" +
		"They coordinate torpedo attacks.\n\n" +
		"<color=#E0B030><b>Movement</b></color>\n" +
		"They think before chasing you and retreat away from you, not into you. Far-away task forces head straight for you instead of sailing in circles.\n\n" +
		"<color=#E0B030><b>Submarines</b></color>\n" +
		"Subs ambush from further out and come back for more.",

		"<color=#E0B030><b>Strikes</b></color>\n" +
		"Up to 72 planes per side. Mixed strike packages arrive in one wave. Real steep dive bombing, bombers attack on their own, hammer and anvil torpedo attacks.\n\n" +
		"<color=#E0B030><b>Fighters</b></color>\n" +
		"Escorts protect their bombers. CAP follows its carrier.\n\n" +
		"<color=#E0B030><b>Damage</b></color>\n" +
		"Every plane type has its own toughness and armour, and guns do damage by calibre.",

		"<color=#E0B030><b>Duds</b></color>\n" +
		"Historical dud rates (US Mark 13/14/15 fail often, Mark 18 about 10%, Japanese torpedoes 3-6%). Only active when the game's dud torpedoes option is on.\n\n" +
		"<color=#E0B030><b>Glancing hits</b></color>\n" +
		"Torpedoes that hit a ship at under 15 degrees bounce off and keep running. Early US torpedoes also dud more on a square 90 degree hit. Bounces show in the Hit log.\n\n" +
		"<color=#E0B030><b>High hits</b></color>\n" +
		"Torpedoes that hit high on a ship now always do damage.",

		"<color=#E0B030><b>Message log tabs (battle)</b></color>\n" +
		"General, Hit log and Crew. Press F2 or click a tab.\n\n" +
		"<color=#E0B030><b>Group orders (battle)</b></color>\n" +
		"Ctrl+A all ships, Ctrl+D destroyers, Ctrl+C cruisers, Ctrl+B battleships and carriers. Ctrl+Shift+1-5 saves the ticked ships as a group, Ctrl+1-5 selects it again.\n\n" +
		"<color=#E0B030><b>Minimap (battle)</b></color>\n" +
		"Torpedo tracks, smoke, lookout and radar rings, enemy last-seen markers. Buttons above the map toolbar, or F11 for all.\n\n" +
		"<color=#E0B030><b>Keys</b></color>\n" +
		"F11 campaign map: fuel overlay. F11 battle: minimap layers. F2 battle: message log tab.\n" +
		"Testers: F9 reveal enemies (map), F4 create a survivor event (map), F3 developer view (battle).",

		"<color=#E0B030><b>Custom ships</b></color>\n" +
		"All custom merchant ships in the game (merchants, transports, hospital ship, oilers and the destroyer escort) are from the TTE team and are used with their permission. They are not the work of the mod author.\n" +
		"The TTE mod is about 4 years old and the team is no longer active. Their assets are used with credit, and will be removed at the request of any TTE member.\n\n" +
		"<color=#E0B030><b>Inspiration</b></color>\n" +
		"The events and the survivors system were inspired by Kiko. The Hit log is a copy of the idea from the ADBA Mod Team's Hitlog."
	};

	public static void Build(Transform root)
	{
		Remove();
		Sprite icon = null;
		try
		{
			icon = AssetLoader.instance.ImportSprite("interface/images/map/guidebook.png");
		}
		catch (Exception ex)
		{
			Debug.LogError("[GUIDE] could not load guidebook.png: " + ex.Message);
		}
		Image back;
		button = ModTFOverlay.MakeButton(root, 0, icon, "BOOK", "Features and change log", new UnityAction(Toggle), out back);
		BuildPanel(root);
		Debug.Log("[GUIDE] book button added, icon " + (icon != null ? "loaded" : "not found"));
	}

	public static void Remove()
	{
		if (button != null)
		{
			UnityEngine.Object.Destroy(button);
		}
		if (panel != null)
		{
			UnityEngine.Object.Destroy(panel);
		}
		button = null;
		panel = null;
	}

	private static void Toggle()
	{
		if (panel == null)
		{
			return;
		}
		bool open = !panel.activeSelf;
		if (open)
		{
			page = 0;
			ShowPage();
		}
		panel.SetActive(open);
	}

	private static void Close()
	{
		if (panel != null)
		{
			panel.SetActive(false);
		}
	}

	private static void Next()
	{
		if (page < titles.Length - 1)
		{
			page++;
			ShowPage();
		}
	}

	private static void Previous()
	{
		if (page > 0)
		{
			page--;
			ShowPage();
		}
	}

	private static void ShowPage()
	{
		titleText.text = titles[page];
		bodyText.text = bodies[page];
		pageText.text = "Page " + (page + 1) + " / " + titles.Length;
		prevButton.SetActive(page > 0);
		nextButton.SetActive(page < titles.Length - 1);
		contentRect.anchoredPosition = Vector2.zero;
	}

	private static RectTransform NewRect(string name, Transform parent)
	{
		GameObject go = new GameObject(name, typeof(RectTransform));
		go.transform.SetParent(parent, false);
		return go.GetComponent<RectTransform>();
	}

	private static void Stretch(RectTransform rt, float left, float bottom, float right, float top)
	{
		rt.anchorMin = Vector2.zero;
		rt.anchorMax = Vector2.one;
		rt.offsetMin = new Vector2(left, bottom);
		rt.offsetMax = new Vector2(-right, -top);
	}

	private static Text NewText(RectTransform rt, int size, TextAnchor anchor, Color colour)
	{
		Text t = rt.gameObject.AddComponent<Text>();
		t.font = font;
		t.fontSize = size;
		t.alignment = anchor;
		t.color = colour;
		t.supportRichText = true;
		t.horizontalOverflow = HorizontalWrapMode.Wrap;
		t.verticalOverflow = VerticalWrapMode.Overflow;
		t.raycastTarget = false;
		return t;
	}

	private static GameObject NewButton(Transform parent, string label, float anchorX, UnityAction action)
	{
		RectTransform rt = NewRect("Btn " + label, parent);
		rt.anchorMin = new Vector2(anchorX, 0f);
		rt.anchorMax = new Vector2(anchorX, 0f);
		rt.pivot = new Vector2(0.5f, 0f);
		rt.anchoredPosition = new Vector2(0f, 18f);
		rt.sizeDelta = new Vector2(150f, 40f);
		Image edge = rt.gameObject.AddComponent<Image>();
		edge.color = gold;
		Button b = rt.gameObject.AddComponent<Button>();
		b.targetGraphic = edge;
		b.onClick.AddListener(action);
		RectTransform inner = NewRect("Back", rt);
		Stretch(inner, 2f, 2f, 2f, 2f);
		Image innerImg = inner.gameObject.AddComponent<Image>();
		innerImg.color = new Color(0.1f, 0.17f, 0.26f, 1f);
		innerImg.raycastTarget = false;
		RectTransform txt = NewRect("Text", rt);
		Stretch(txt, 0f, 0f, 0f, 0f);
		Text t = NewText(txt, fontSize + 2, TextAnchor.MiddleCenter, Color.white);
		t.text = label;
		return rt.gameObject;
	}

	private static void BuildPanel(Transform root)
	{
		font = null;
		fontSize = 16;
		if (TooltipManager.instance != null && TooltipManager.instance.toolTipText != null)
		{
			font = TooltipManager.instance.toolTipText.font;
			fontSize = TooltipManager.instance.toolTipText.fontSize;
		}
		if (font == null)
		{
			font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		}

		// Full screen dimmer that also blocks clicks on the map behind the book.
		RectTransform dim = NewRect("ModGuide", root);
		Stretch(dim, 0f, 0f, 0f, 0f);
		Image dimImg = dim.gameObject.AddComponent<Image>();
		dimImg.color = new Color(0f, 0f, 0f, 0.35f);
		panel = dim.gameObject;

		// The book itself, 50% x 76% of the screen, in the middle.
		RectTransform win = NewRect("Window", dim);
		win.anchorMin = new Vector2(0.25f, 0.12f);
		win.anchorMax = new Vector2(0.75f, 0.88f);
		win.offsetMin = Vector2.zero;
		win.offsetMax = Vector2.zero;
		Image winEdge = win.gameObject.AddComponent<Image>();
		winEdge.color = gold;
		RectTransform winBack = NewRect("Back", win);
		Stretch(winBack, 2f, 2f, 2f, 2f);
		Image winBackImg = winBack.gameObject.AddComponent<Image>();
		winBackImg.color = dark;
		winBackImg.raycastTarget = false;

		// Title and a thin line under it.
		RectTransform title = NewRect("Title", win);
		title.anchorMin = new Vector2(0f, 1f);
		title.anchorMax = new Vector2(1f, 1f);
		title.pivot = new Vector2(0.5f, 1f);
		title.anchoredPosition = new Vector2(0f, -14f);
		title.sizeDelta = new Vector2(-40f, 40f);
		titleText = NewText(title, fontSize + 10, TextAnchor.MiddleCenter, Color.white);
		RectTransform line = NewRect("Line", win);
		line.anchorMin = new Vector2(0f, 1f);
		line.anchorMax = new Vector2(1f, 1f);
		line.pivot = new Vector2(0.5f, 1f);
		line.anchoredPosition = new Vector2(0f, -58f);
		line.sizeDelta = new Vector2(-50f, 2f);
		Image lineImg = line.gameObject.AddComponent<Image>();
		lineImg.color = gold;
		lineImg.raycastTarget = false;

		// Scroll area with a scroll bar on the right.
		RectTransform scroll = NewRect("Scroll", win);
		Stretch(scroll, 30f, 110f, 30f, 72f);
		ScrollRect sr = scroll.gameObject.AddComponent<ScrollRect>();
		RectTransform viewport = NewRect("Viewport", scroll);
		Stretch(viewport, 0f, 0f, 22f, 0f);
		Image vpImg = viewport.gameObject.AddComponent<Image>();
		vpImg.color = new Color(0f, 0f, 0f, 0f);
		viewport.gameObject.AddComponent<RectMask2D>();
		contentRect = NewRect("Content", viewport);
		contentRect.anchorMin = new Vector2(0f, 1f);
		contentRect.anchorMax = new Vector2(1f, 1f);
		contentRect.pivot = new Vector2(0.5f, 1f);
		contentRect.anchoredPosition = Vector2.zero;
		contentRect.sizeDelta = Vector2.zero;
		bodyText = NewText(contentRect, fontSize + 1, TextAnchor.UpperLeft, new Color(0.9f, 0.92f, 0.95f, 1f));
		bodyText.lineSpacing = 1.1f;
		ContentSizeFitter fit = contentRect.gameObject.AddComponent<ContentSizeFitter>();
		fit.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

		RectTransform bar = NewRect("Scrollbar", scroll);
		bar.anchorMin = new Vector2(1f, 0f);
		bar.anchorMax = new Vector2(1f, 1f);
		bar.pivot = new Vector2(1f, 1f);
		bar.anchoredPosition = Vector2.zero;
		bar.sizeDelta = new Vector2(12f, 0f);
		Image barImg = bar.gameObject.AddComponent<Image>();
		barImg.color = new Color(0.03f, 0.06f, 0.1f, 1f);
		RectTransform slide = NewRect("Sliding Area", bar);
		Stretch(slide, 0f, 0f, 0f, 0f);
		RectTransform handle = NewRect("Handle", slide);
		handle.sizeDelta = Vector2.zero;
		Image handleImg = handle.gameObject.AddComponent<Image>();
		handleImg.color = gold;
		Scrollbar sb = bar.gameObject.AddComponent<Scrollbar>();
		sb.direction = Scrollbar.Direction.BottomToTop;
		sb.handleRect = handle;
		sb.targetGraphic = handleImg;

		sr.content = contentRect;
		sr.viewport = viewport;
		sr.horizontal = false;
		sr.vertical = true;
		sr.movementType = ScrollRect.MovementType.Clamped;
		sr.scrollSensitivity = 30f;
		sr.verticalScrollbar = sb;
		sr.verticalScrollbarVisibility = ScrollRect.ScrollbarVisibility.Permanent;

		// Page number and the three buttons.
		RectTransform pg = NewRect("Page", win);
		pg.anchorMin = new Vector2(0.5f, 0f);
		pg.anchorMax = new Vector2(0.5f, 0f);
		pg.pivot = new Vector2(0.5f, 0f);
		pg.anchoredPosition = new Vector2(0f, 66f);
		pg.sizeDelta = new Vector2(300f, 26f);
		pageText = NewText(pg, fontSize, TextAnchor.MiddleCenter, gold);

		prevButton = NewButton(win, "Previous", 0.2f, new UnityAction(Previous));
		NewButton(win, "Close", 0.5f, new UnityAction(Close));
		nextButton = NewButton(win, "Next", 0.8f, new UnityAction(Next));

		panel.SetActive(false);
	}
}
```

### Step 2 - move the fuel button down and build the book
1. In class **ModTFOverlay**, right-click method **BuildButton** > **Edit Method (C#)...**
2. Find the line that starts `buttonObject = MakeButton(transform, 0,` and change the **0** to **1**, so it reads `buttonObject = MakeButton(transform, 1, ...`.
3. Directly after that line (still inside the same `{ }`), add:
```csharp
ModGuide.Build(transform);
```
4. Click **Compile**.
5. In class **ModTFOverlay**, right-click method **OnDisable** > **Edit Method (C#)...**. Add this line as the first line inside the method:
```csharp
ModGuide.Remove();
```
6. Click **Compile**, then **File > Save Module**.

(The guide is started by the same `AddComponent<ModTFOverlay>()` lines the fuel overlay already uses, so nothing in CampaignManager changes.)

### Step 3 - test
1. Copy `guidebook.png` into the game's `Override\interface\images\map\` folder, load a campaign and wait for the first hour (or load a save).
2. A book button should be top left, with the fuel barrel under it. Hover the book: "Features and change log".
3. Click it: the popup opens on page 1 with Close and Next. Next shows Previous too; the last page has no Next. Scroll the page with the mouse wheel and the bar. Close shuts it.
4. Check `output_log.txt` for `[GUIDE] book button added, icon loaded`. If something went wrong the fuel overlay log says `[TFOVERLAY] failed:` or `[GUIDE]` lines say why.

## Things the test will tell us (could not be checked without running the game)
- Text size and window size: `fontSize + 1` and the 25% to 75% window are guesses. Tell me what you see.
- The mouse wheel might also zoom the map behind the popup; if it does I will block it.
- The popup is built on the game's top canvas, so it should sit over everything. If part of the game UI shows on top of it, I will change where it is parented.
- Page text is a first draft taken from the README. Tell me what to add, reword or reorder.
