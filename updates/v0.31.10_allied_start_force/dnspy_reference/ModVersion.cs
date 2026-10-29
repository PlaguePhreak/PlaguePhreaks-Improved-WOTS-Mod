using System;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;
using Object = UnityEngine.Object;

// Main menu: mod name + version bottom left, a "Change Log" button top right.
// The button opens a window in the logbook (ModGuide) style that shows only the changelog.
public static class ModVersion
{
	public const string Current = "0.31.10";

	private const string ChangelogTitle = "Change Log";

	private const string ChangelogBody = "<color=#E0B030><b>0.31.10</b></color> allied AI:\n- The RAN force you start the Allied campaign with now sails under RAN command (yellow)\n<color=#E0B030><b>0.31.9</b></color> ship fires:\n- One burning compartment is a small fire; more grow it into a roaring blaze\n- Big fires glow, light up the ship and sea, and send up a black smoke column\n<color=#E0B030><b>0.31.6</b></color> enemy scouts:\n- Enemy scouting is done by flying boats and floatplanes only\n- Every enemy airfield gets floatplane scouts (saved campaigns too)\n<color=#E0B030><b>0.31.5</b></color> fixes:\n- The battle message log starts empty in every new battle\n<color=#E0B030><b>0.31.4</b></color> ships handle like the real thing:\n- Every ship turns on a real WW2 turning circle; big ships swing slowly\n- The rudder and the swing take time to build; hard turns cost speed\n- Ships carry way: cut the engines and she coasts on for minutes\n<color=#E0B030><b>0.31.3</b></color> 3D fire and hit blasts:\n- Burning ships show real 3D flames and a thick plume of smoke\n- Shell and bomb hits on ships burst in 3D fire, smoke, chunks and sparks\n<color=#E0B030><b>0.31.2</b></color> a smarter enemy, scaled by difficulty:\n- Enemy scouts fan out from every airfield, many single planes\n- Strike groups gather at a rally point, then attack together\n- Strikes and fighter cover sized to the ships involved\n- A magazine blast can tear any ship apart, even a battleship\n- Enemy airfields fly scout patrols; a pop-up names the force they spot\n- Enemy groups hunt you on the map; Elite fights like a real commander\n- Enemy ships press home in battle, spread fire, finish cripples\n- More aircraft types at every enemy airfield (new campaigns)\n- Switches in Mod Options (Enemy AI section)\n<color=#E0B030><b>0.29.9</b></color> ships go down like the real thing, planes break up:\n- Torpedo hits throw up a huge splash (the game's own, made bigger)\n- A broken back sets off both magazines: two huge blasts, then it splits\n- Blasts start small, burst into a fireball, then smoke; sized by shells\n- Big magazine blasts sink the ship, often blowing off bow or stern\n- Ships capsize, plunge by the bow or stern, or settle, by their flooding\n- Real floating wreckage and wide, spreading oil slicks where ships sink\n- Shot planes shed real wings, tails, engines; crews bail out by parachute\n- Your ships answer your controls again; fewer planes explode\n- Mod models now live in StreamingAssets/override/ModAssets\n- Air auto resolve window restyled to match the game\n- Plus the 0.28 air combat update (0.28.18 and hotfix)";

	private const float Margin = 30f;

	private static GameObject root;

	private static GameObject panel;

	private static RectTransform contentRect;

	private static readonly Color gold = new Color(0.72f, 0.58f, 0.3f, 1f);

	private static readonly Color dark = new Color(0.07f, 0.12f, 0.19f, 0.97f);

	private static readonly Color buttonBack = new Color(0.1f, 0.17f, 0.26f, 1f);

	private static readonly Color bodyColour = new Color(0.9f, 0.92f, 0.95f, 1f);

	public static void Build()
	{
		try
		{
			MenuSystem instance = MenuSystem.instance;
			if (instance == null || instance.mainInterface == null)
			{
				return;
			}
			if (root != null)
			{
				Object.Destroy(root);
			}
			root = null;
			panel = null;
			Canvas canvas = instance.mainInterface.GetComponentInParent<Canvas>();
			if (canvas == null)
			{
				Debug.LogError("[VERSION] no canvas found");
				return;
			}
			canvas = canvas.rootCanvas;
			Font menuFont = null;
			Text menuText = instance.mainInterface.GetComponentInChildren<Text>(true);
			if (menuText != null)
			{
				menuFont = menuText.font;
			}
			if (menuFont == null)
			{
				menuFont = Resources.GetBuiltinResource<Font>("Arial.ttf");
			}
			// the logbook uses the tooltip font; fall back to the menu font
			Font bookFont = menuFont;
			int bookSize = 16;
			if (TooltipManager.instance != null && TooltipManager.instance.toolTipText != null && TooltipManager.instance.toolTipText.font != null)
			{
				bookFont = TooltipManager.instance.toolTipText.font;
				bookSize = TooltipManager.instance.toolTipText.fontSize;
			}
			Vector3[] corners = new Vector3[4];
			((RectTransform)canvas.transform).GetWorldCorners(corners);
			float scale = canvas.transform.lossyScale.x;
			GameObject go = new GameObject("ModVersion", new Type[1] { typeof(RectTransform) });
			go.transform.SetParent(instance.mainInterface.transform, false);
			go.transform.SetAsLastSibling();
			root = go;

			// "Change Log" button, top right
			RectTransform btn = NewRect("ChangeLogButton", go.transform, new Vector2(1f, 1f));
			btn.sizeDelta = new Vector2(190f, 44f);
			btn.position = new Vector3(corners[2].x - Margin * scale, corners[2].y - 20f * scale, corners[2].z);
			MakeButton(btn, menuFont, 22, ChangelogTitle.ToUpper(), new UnityAction(Open));

			// version label, bottom left
			RectTransform label = NewRect("Version", go.transform, new Vector2(0f, 0f));
			label.sizeDelta = new Vector2(500f, 60f);
			label.position = new Vector3(corners[0].x + Margin * scale, corners[0].y + 20f * scale, corners[0].z);
			NewText(label, menuFont, 20, TextAnchor.LowerLeft, bodyColour).text = "Plague's Better WOTS mod\n<color=#E0B030>Version " + Current + "</color>";

			BuildPanel(go.transform, corners, bookFont, bookSize);
			go.transform.SetAsLastSibling();
		}
		catch (Exception ex)
		{
			Debug.LogError("[VERSION] build failed: " + ex.ToString());
		}
	}

	private static void Open()
	{
		if (panel == null)
		{
			return;
		}
		panel.transform.SetAsLastSibling();
		panel.SetActive(true);
		if (contentRect != null)
		{
			contentRect.anchoredPosition = Vector2.zero;
		}
	}

	private static void Close()
	{
		if (panel != null)
		{
			panel.SetActive(false);
		}
	}

	// same layout and colours as the logbook window (ModGuide.BuildPanel), one page, Close only
	private static void BuildPanel(Transform parent, Vector3[] corners, Font font, int fontSize)
	{
		// dim overlay covering the whole screen, blocks clicks on the menu behind it
		RectTransform overlay = NewRect("ChangeLogWindow", parent, new Vector2(0.5f, 0.5f));
		float s = parent.lossyScale.x;
		if (s <= 0f)
		{
			s = 1f;
		}
		overlay.position = (corners[0] + corners[2]) * 0.5f;
		overlay.sizeDelta = new Vector2((corners[2].x - corners[0].x) / s, (corners[2].y - corners[0].y) / s);
		overlay.gameObject.AddComponent<Image>().color = new Color(0f, 0f, 0f, 0.35f);
		panel = overlay.gameObject;

		RectTransform window = NewRect("Window", overlay, new Vector2(0.5f, 0.5f));
		window.anchorMin = new Vector2(0.25f, 0.12f);
		window.anchorMax = new Vector2(0.75f, 0.88f);
		window.offsetMin = Vector2.zero;
		window.offsetMax = Vector2.zero;
		window.gameObject.AddComponent<Image>().color = gold;
		RectTransform back = NewRect("Back", window, new Vector2(0.5f, 0.5f));
		Stretch(back, 2f, 2f, 2f, 2f);
		Image backImage = back.gameObject.AddComponent<Image>();
		backImage.color = dark;
		backImage.raycastTarget = false;

		RectTransform title = NewRect("Title", window, new Vector2(0.5f, 1f));
		title.anchorMin = new Vector2(0f, 1f);
		title.anchorMax = new Vector2(1f, 1f);
		title.anchoredPosition = new Vector2(0f, -14f);
		title.sizeDelta = new Vector2(-40f, 40f);
		NewText(title, font, fontSize + 10, TextAnchor.MiddleCenter, Color.white).text = ChangelogTitle.ToUpper();

		RectTransform line = NewRect("Line", window, new Vector2(0.5f, 1f));
		line.anchorMin = new Vector2(0f, 1f);
		line.anchorMax = new Vector2(1f, 1f);
		line.anchoredPosition = new Vector2(0f, -58f);
		line.sizeDelta = new Vector2(-50f, 2f);
		Image lineImage = line.gameObject.AddComponent<Image>();
		lineImage.color = gold;
		lineImage.raycastTarget = false;

		RectTransform scroll = NewRect("Scroll", window, new Vector2(0.5f, 0.5f));
		Stretch(scroll, 30f, 80f, 30f, 72f);
		ScrollRect scrollRect = scroll.gameObject.AddComponent<ScrollRect>();
		RectTransform viewport = NewRect("Viewport", scroll, new Vector2(0.5f, 0.5f));
		Stretch(viewport, 0f, 0f, 22f, 0f);
		viewport.gameObject.AddComponent<Image>().color = new Color(0f, 0f, 0f, 0f);
		viewport.gameObject.AddComponent<RectMask2D>();
		contentRect = NewRect("Content", viewport, new Vector2(0.5f, 1f));
		contentRect.anchorMin = new Vector2(0f, 1f);
		contentRect.anchorMax = new Vector2(1f, 1f);
		contentRect.anchoredPosition = Vector2.zero;
		contentRect.sizeDelta = Vector2.zero;
		Text body = NewText(contentRect, font, fontSize + 1, TextAnchor.UpperLeft, bodyColour);
		body.lineSpacing = 1.1f;
		body.text = ChangelogBody;
		contentRect.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;

		RectTransform bar = NewRect("Scrollbar", scroll, new Vector2(1f, 1f));
		bar.anchorMin = new Vector2(1f, 0f);
		bar.anchorMax = new Vector2(1f, 1f);
		bar.anchoredPosition = Vector2.zero;
		bar.sizeDelta = new Vector2(12f, 0f);
		bar.gameObject.AddComponent<Image>().color = new Color(0.03f, 0.06f, 0.1f, 1f);
		RectTransform sliding = NewRect("Sliding Area", bar, new Vector2(0.5f, 0.5f));
		Stretch(sliding, 0f, 0f, 0f, 0f);
		RectTransform handle = NewRect("Handle", sliding, new Vector2(0.5f, 0.5f));
		handle.anchorMin = Vector2.zero;
		handle.anchorMax = Vector2.one;
		handle.sizeDelta = Vector2.zero;
		Image handleImage = handle.gameObject.AddComponent<Image>();
		handleImage.color = gold;
		Scrollbar scrollbar = bar.gameObject.AddComponent<Scrollbar>();
		scrollbar.direction = Scrollbar.Direction.BottomToTop;
		scrollbar.handleRect = handle;
		scrollbar.targetGraphic = handleImage;
		scrollRect.content = contentRect;
		scrollRect.viewport = viewport;
		scrollRect.horizontal = false;
		scrollRect.vertical = true;
		scrollRect.movementType = ScrollRect.MovementType.Clamped;
		scrollRect.scrollSensitivity = 30f;
		scrollRect.verticalScrollbar = scrollbar;
		scrollRect.verticalScrollbarVisibility = ScrollRect.ScrollbarVisibility.Permanent;

		RectTransform close = NewRect("Btn Close", window, new Vector2(0.5f, 0f));
		close.anchorMin = new Vector2(0.5f, 0f);
		close.anchorMax = new Vector2(0.5f, 0f);
		close.anchoredPosition = new Vector2(0f, 18f);
		close.sizeDelta = new Vector2(150f, 40f);
		MakeButton(close, font, fontSize + 2, "Close", new UnityAction(Close));

		panel.SetActive(false);
	}

	// logbook-style button: gold edge, dark blue fill, white label
	private static void MakeButton(RectTransform rt, Font font, int size, string label, UnityAction action)
	{
		Image edge = rt.gameObject.AddComponent<Image>();
		edge.color = gold;
		Button button = rt.gameObject.AddComponent<Button>();
		button.targetGraphic = edge;
		button.onClick.AddListener(action);
		RectTransform back = NewRect("Back", rt, new Vector2(0.5f, 0.5f));
		Stretch(back, 2f, 2f, 2f, 2f);
		Image backImage = back.gameObject.AddComponent<Image>();
		backImage.color = buttonBack;
		backImage.raycastTarget = false;
		RectTransform text = NewRect("Text", rt, new Vector2(0.5f, 0.5f));
		Stretch(text, 0f, 0f, 0f, 0f);
		NewText(text, font, size, TextAnchor.MiddleCenter, Color.white).text = label;
	}

	private static RectTransform NewRect(string name, Transform parent, Vector2 pivot)
	{
		GameObject go = new GameObject(name, new Type[1] { typeof(RectTransform) });
		go.transform.SetParent(parent, false);
		RectTransform rt = go.GetComponent<RectTransform>();
		rt.anchorMin = pivot;
		rt.anchorMax = pivot;
		rt.pivot = pivot;
		return rt;
	}

	private static void Stretch(RectTransform rt, float left, float bottom, float right, float top)
	{
		rt.anchorMin = Vector2.zero;
		rt.anchorMax = Vector2.one;
		rt.offsetMin = new Vector2(left, bottom);
		rt.offsetMax = new Vector2(0f - right, 0f - top);
	}

	private static Text NewText(RectTransform rt, Font font, int size, TextAnchor anchor, Color colour)
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
}
