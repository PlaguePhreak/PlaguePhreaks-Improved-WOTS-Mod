using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
using UnityEngine.UI;
using WorldMapStrategyKit;
using System.Reflection;

// 0.32.11 Globe phase 2+3+4+5 (+ main menu): the campaign map as a spinning Earth, with the flat map's own icons and names on it.
// GLOBE button (row 5 of the mod buttons, top left) or F10 swaps the flat campaign map for a 3D globe drawn by its own
// camera far away from everything else in the scene. The globe shows the whole Earth (override/ModAssets/globe/earth.jpg),
// the day/night line worked out from the campaign clock, a gold outline of the current theatre, and simple dots for bases,
// your task forces and spotted enemy forces. Drag to spin, wheel to zoom, arrows to turn. Zooming in past the closest point
// drops you back onto the flat map at the spot in the middle of the view.
// Phase 4: clicks on the globe do what they do on the flat map. Click an icon to select it (tooltips on hover), use the
// game's own Plot Course button, then click waypoints on the globe and right-click to finish. The route lines the game
// draws on the hidden flat map are mirrored onto the globe.
// Phase 5: base range rings (MapRadii), the weather cells and sea states, and map notes drawn on the globe. The mouse's
// map point is fed to WMSK.cursorLocation so the ruler and map-note keys work on the globe.
// Main menu: a second, look-only copy of the globe spins slowly and is drawn into the menu's video picture (MenuSystem.Start).
public class ModGlobe : MonoBehaviour
{
    // ===== knobs =====
    public static bool Enabled = true;         // false = no button, no key
    public static KeyCode Key = (KeyCode)291;  // F10
    public static float Radius = 100f;         // globe size in scene units
    public static float ZoomMin = 1.3f;        // closest camera distance, in radii
    public static float ZoomMax = 4.5f;        // farthest
    public static float ZoomStart = 2.8f;      // where the camera starts
    public static float ZoomStep = 0.12f;      // one wheel notch
    public static float DragSpeed = 0.22f;     // degrees per pixel dragged
    public static float KeySpeed = 45f;        // degrees per second on the arrow keys
    public static float Night = 0.16f;         // how dark the night side is (0 black, 1 no night)
    public static float Twilight = 0.10f;      // width of the day/night blend
    public static bool MenuGlobe = false;       // the globe spins in the main menu where the video used to be (off: Aaron prefers the video)
    public static float MenuSpin = 1.5f;        // degrees per second
    public static float MenuLat = 18f;          // latitude the menu camera looks from
    public static float MenuZoom = 2.4f;        // menu camera distance in globe radii
    public static float UtcOffsetHours = 99f;  // 99 = work it out from the theatre centre (campaign clock is local time)
    public static float MarkerSize = 0.014f;   // dots, in radii
    public static bool AutoDropToMap = true;   // zoom in past the closest point = back to the flat map
    public static bool ShowMarkers = true;      // the icons and names
    public static float IconPx = 22f;           // icon size on screen at ZoomStart
    public static float LabelZoom = 2.2f;       // names show when the camera is closer than this (radii)
    public static int LabelPx = 12;             // name text size
    public static bool OpenOnScrollOut = true;  // on the flat map, scrolling out past the farthest zoom opens the globe

    public static bool on;
    private static ModGlobe inst;
    private static bool menuPending;              // set while the menu copy is being added, so it does not become `inst`
    private bool menu;                            // this copy is the main-menu one
    private RenderTexture menuRt;
    private RawImage menuRaw;
    private MenuSystem menuSys;

    private const float Far = -300000f;        // the globe lives down here, away from the campaign scene

    private Camera cam;
    private GameObject root, globeObj, starsObj, haloObj, ribbonObj, blocker;
    private Mesh globeMesh;
    private Vector3[] globeNormals;
    private int[] globeTris;                 // every triangle of the sphere
    private List<int> frontTris = new List<int>();
    private Vector3 lastCamPos = new Vector3(1e9f, 0f, 0f);
    private Color[] globeColors;
    private Shader shader;
    private Texture2D white;
    private Material ribbonMat;
    private List<Vector3> ribbonDirs = new List<Vector3>();
    private Color[] ribbonColors;
    private class Entry { public Vector3 dir; public RectTransform rect; public Image icon; public Text label, shadow; public GameObject go; public GameObjectAnimator goa; public Vector2 screen; public bool shown; }
    private List<Entry> entries = new List<Entry>();
    private RectTransform overlay;
    private Font font;
    private float dist, viewLat, viewLon;
    private Vector3 lastMouse;
    private bool dragging;
    private float lastSwitch = -10f;              // time of the last globe<->map switch (cooldown)
    public static float SwitchCooldown = 0.8f;    // seconds before the wheel can switch views again
    public static float DropZoom = 0.4f;          // 0 = closest flat-map zoom, 1 = farthest; where a zoom-in from the globe lands
    private float sunTimer, markerTimer;
    // phase 4: clicks, hover, routes
    public static bool Clicks = true;             // clicks on the globe select icons and plot courses like the flat map
    public static float PickPx = 16f;             // a click within this many screen pixels of an icon hits it
    public static float RouteWidth = 0.005f;      // route line width as a fraction of the globe radius (at the start zoom)
    private int downButton = -1;
    private Vector3 downPos;
    private Entry hover;
    private GameObject routeObj;
    private Mesh routeMesh;
    private int routeSig = -1;
    private Vector2 lastRouteMouse = new Vector2(9f, 9f);
    private static MethodInfo miRoute;
    // phase 5: rings, weather, notes
    public static bool Theatre = true;            // yellow outline of the campaign map's area (skipped when the map goes right round the world)
    public static bool Rings = true;              // base range rings (the flat map's MapRadii) on the globe
    public static bool Weather = true;            // weather cells and sea states on the globe
    public static bool Notes = true;              // map notes (markers) on the globe
    public static float RingWidth = 0.003f;       // ring line width as a fraction of the globe radius (at the start zoom)
    public static float WeatherAlpha = 0.7f;      // how strong the weather patches are drawn
    private GameObject ringObj;
    private Mesh ringMesh;
    private int ringSig = -1;
    private GameObject weatherRoot;
    private List<MeshRenderer> weatherPatches = new List<MeshRenderer>();
    private List<Vector3> weatherDirs = new List<Vector3>();
    private int weatherSig = -1;
    private float weatherTimer;
    private bool built, reported, buttonReported;
    private GameObject buttonObject;
    private Image buttonBack;
    private bool savedDrag, savedZoom, savedKeys, savedOk;
    private Vector3 centre { get { return new Vector3(menu ? 80000f : 0f, Far, 0f); } }

    public static void Ensure(Component host)
    {
        try
        {
            if (host != null && host.gameObject.GetComponent<ModGlobe>() == null) host.gameObject.AddComponent<ModGlobe>();
        }
        catch (Exception ex) { Debug.LogError("[GLOBE] could not add: " + ex.Message); }
    }

    private void Awake() { if (menuPending) { menu = true; menuPending = false; } else inst = this; }

    private void OnDisable()
    {
        try
        {
            if (menu) { if (cam != null) cam.enabled = false; if (root != null) root.SetActive(false); return; }
            if (on) Off();
        }
        catch (Exception) { }
    }

    // a campaign ended (scene change): drop everything this copy made, so the next campaign starts clean
    private void OnDestroy()
    {
        try
        {
            if (root != null) Destroy(root);
            if (blocker != null) Destroy(blocker);
            if (buttonObject != null) Destroy(buttonObject);
            if (menuRt != null) { menuRt.Release(); Destroy(menuRt); }
            if (inst == this) inst = null;
        }
        catch (Exception) { }
    }

    private void OnEnable()
    {
        try { if (menu && built) { if (root != null) root.SetActive(true); if (cam != null) cam.enabled = true; } } catch (Exception) { }
    }

    // ---------- main menu copy ----------

    public static void Menu(MenuSystem ms)
    {
        try
        {
            if (ms == null || !MenuGlobe) return;
            if (ms.gameObject.GetComponent<ModGlobe>() != null) return;
            menuPending = true;
            ModGlobe g = ms.gameObject.AddComponent<ModGlobe>();
            menuPending = false;
            g.menu = true;
            g.menuSys = ms;
            Debug.Log("[GLOBE] main menu globe added");
        }
        catch (Exception ex) { menuPending = false; Debug.LogError("[GLOBE] menu copy could not be added: " + ex.Message); }
    }

    private void DriveMenu()
    {
        if (!MenuGlobe || menuSys == null) return;
        if (!built)
        {
            Build(null);
            int w = Mathf.Max(256, Mathf.RoundToInt(Screen.width * 0.6f)), h = Mathf.Max(256, Screen.height);
            menuRt = new RenderTexture(w, h, 16);
            menuRt.Create();
            cam.targetTexture = menuRt;
            cam.depth = -50f;
            viewLat = MenuLat; viewLon = 150f; dist = MenuZoom * Radius;
            root.SetActive(true);
            cam.enabled = true;
            Place();
            Shade(DateTime.UtcNow, 0f);
            Debug.Log("[GLOBE] menu globe drawing into a " + w + "x" + h + " picture");
        }
        // the menu's own video picture shows our globe; the video and the still image stay off
        try
        {
            if (menuRaw == null && menuSys.menuStaticBackground != null) menuRaw = menuSys.menuStaticBackground.transform.parent.GetComponent<RawImage>();
            if (menuRaw != null)
            {
                if (menuRaw.texture != menuRt) menuRaw.texture = menuRt;
                if (!menuRaw.enabled) menuRaw.enabled = true;
                if (menuRaw.color != Color.white) menuRaw.color = Color.white;
            }
            if (menuSys.videoPlayer != null && menuSys.videoPlayer.gameObject.activeSelf) menuSys.videoPlayer.gameObject.SetActive(false);
            if (menuSys.menuStaticBackground != null && menuSys.menuStaticBackground.gameObject.activeSelf) menuSys.menuStaticBackground.gameObject.SetActive(false);
        }
        catch (Exception) { }
        if (!root.activeSelf) root.SetActive(true);
        if (!cam.enabled) cam.enabled = true;
        float dt = Time.unscaledDeltaTime;
        viewLon += MenuSpin * dt;
        while (viewLon >= 360f) viewLon -= 360f;
        viewLat = MenuLat; dist = MenuZoom * Radius;
        Place();
        sunTimer -= dt;
        if (sunTimer <= 0f) { sunTimer = 2f; Shade(DateTime.UtcNow, 0f); }
        Facing();
    }

    private void Update()
    {
        try
        {
            if (menu) { DriveMenu(); return; }
            CampaignInterface ci = CampaignInterface.instance;
            if (ci == null || CampaignManager.instance == null || !Enabled) return;
            if (buttonObject == null) BuildButton(ci);
            if (Input.GetKeyDown(Key)) Toggle();
            if (buttonBack != null) buttonBack.color = on ? new Color(0.5f, 0.3f, 0.08f, 0.95f) : new Color(0.07f, 0.12f, 0.19f, 0.92f);
            if (on) Drive(ci);
            else if (OpenOnScrollOut) ScrollOut(ci);
        }
        catch (Exception ex)
        {
            if (!reported) { reported = true; Debug.LogError("[GLOBE] failed: " + ex.ToString()); }
            try { if (on) Off(); } catch (Exception) { }
        }
    }

    public static void Toggle()
    {
        if (inst == null) return;
        if (on) inst.Off(); else inst.On();
    }

    // ---------- on / off ----------

    private void On() { On(float.NaN, float.NaN); }

    private void On(float startLat, float startLon)
    {
        CampaignInterface ci = CampaignInterface.instance;
        CampaignData d = CampaignManager.instance.campaignData;
        if (ci == null || d == null || d.mapOriginXY == null || d.mapOriginXY.Length < 2) { Debug.Log("[GLOBE] no campaign map"); return; }
        if (!built) Build(d);
        // start over the theatre centre, or where the flat map is looking? The centre is simpler and always right.
        viewLat = float.IsNaN(startLat) ? (float)ModGeo.Lat(d, 0f) : startLat;
        viewLon = float.IsNaN(startLon) ? (float)ModGeo.Lon(d, 0f) : startLon;
        dist = Mathf.Clamp(ZoomStart, ZoomMin, ZoomMax) * Radius;
        WMSK map = ci.map;
        if (map != null)
        {
            savedDrag = map.allowUserDrag; savedZoom = map.allowUserZoom; savedKeys = map.allowUserKeys; savedOk = true;
            map.allowUserDrag = false; map.allowUserZoom = false; map.allowUserKeys = false;
        }
        root.SetActive(true);
        cam.enabled = true;
        if (blocker != null) blocker.SetActive(true);
        on = true;
        sunTimer = 0f; markerTimer = 0f;
        lastCamPos = new Vector3(1e9f, 0f, 0f);
        Place();
        Debug.Log("[GLOBE] on, view " + viewLat.ToString("0.0") + " " + viewLon.ToString("0.0") + ", map zoom level " + (map != null ? map.GetZoomLevel().ToString("0.000") : "?")
            + " (min " + (map != null ? map.zoomMinDistance.ToString("0.000") : "?") + " max " + (map != null ? map.zoomMaxDistance.ToString("0.000") : "?") + ")");
    }

    private void Off()
    {
        on = false;
        dragging = false;
        downButton = -1;
        try { SetHover(null, CampaignInterface.instance); } catch (Exception) { }
        routeSig = -1; ringSig = -1; weatherSig = -1;
        if (cam != null) cam.enabled = false;
        if (root != null) root.SetActive(false);
        if (blocker != null) blocker.SetActive(false);
        CampaignInterface ci = CampaignInterface.instance;
        if (savedOk && ci != null && ci.map != null)
        {
            ci.map.allowUserDrag = savedDrag; ci.map.allowUserZoom = savedZoom; ci.map.allowUserKeys = savedKeys;
        }
        Debug.Log("[GLOBE] off");
    }

    // on the flat map: one more wheel notch outwards at the farthest zoom opens the globe at the spot the map shows
    private void ScrollOut(CampaignInterface ci)
    {
        WMSK map = ci.map;
        if (map == null || !map.allowUserZoom) return;
        if (Time.unscaledTime - lastSwitch < SwitchCooldown) return;
        float axis = Outward(map);
        if (axis <= 0.0001f) return;                         // not an outward notch
        if (map.GetZoomLevel() < map.zoomMaxDistance - 0.02f) return;
        try { if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject()) return; } catch (Exception) { }
        CampaignData d = CampaignManager.instance.campaignData;
        Vector3 loc;
        float lat = float.NaN, lon = float.NaN;
        if (map.GetCurrentMapLocation(out loc)) { lat = (float)ModGeo.Lat(d, loc.y); lon = (float)ModGeo.Lon(d, loc.x); }
        lastSwitch = Time.unscaledTime;
        On(lat, lon);
    }

    // wheel movement in the flat map's own sense: positive = zoom out (farther), negative = zoom in. Same sense on the globe.
    private static float Outward(WMSK map)
    {
        float axis = Input.GetAxis("Mouse ScrollWheel");
        if (map == null || !map.invertZoomDirection) return axis;
        return -axis;
    }

    // ---------- every frame while on ----------

    private void Drive(CampaignInterface ci)
    {
        // the campaign screen went away (battle, menu): hide
        if (!CampaignManager.instance.gameObject.activeInHierarchy) { Off(); return; }
        bool overUi = OverGameUi();
        // spin by dragging
        if (!overUi && (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1)))
        {
            dragging = true; lastMouse = Input.mousePosition;
            downButton = Input.GetMouseButtonDown(0) ? 0 : 1; downPos = Input.mousePosition;
        }
        if (downButton >= 0 && Input.GetMouseButtonUp(downButton))
        {
            bool click = (Input.mousePosition - downPos).magnitude < 6f;
            int b = downButton; downButton = -1;
            if (click && Clicks && !overUi) Click(ci, b);
        }
        if (!Input.GetMouseButton(0) && !Input.GetMouseButton(1)) dragging = false;
        if (dragging)
        {
            Vector3 m = Input.mousePosition;
            float scale = DragSpeed * dist / (ZoomStart * Radius);
            viewLon -= (m.x - lastMouse.x) * scale;
            viewLat -= (m.y - lastMouse.y) * scale;
            lastMouse = m;
        }
        float dt = Time.unscaledDeltaTime;
        if (Input.GetKey(KeyCode.LeftArrow)) viewLon -= KeySpeed * dt;
        if (Input.GetKey(KeyCode.RightArrow)) viewLon += KeySpeed * dt;
        if (Input.GetKey(KeyCode.UpArrow)) viewLat += KeySpeed * dt;
        if (Input.GetKey(KeyCode.DownArrow)) viewLat -= KeySpeed * dt;
        viewLat = Mathf.Clamp(viewLat, -85f, 85f);
        while (viewLon < 0f) viewLon += 360f;
        while (viewLon >= 360f) viewLon -= 360f;
        // zoom with the wheel
        float wheel = overUi ? 0f : Outward(ci.map);
        if (wheel < -0.0001f)
        {
            if (dist <= ZoomMin * Radius + 0.01f && AutoDropToMap && Time.unscaledTime - lastSwitch >= SwitchCooldown) { DropToMap(ci); return; }
            dist *= 1f - ZoomStep;
        }
        else if (wheel > 0.0001f) dist *= 1f + ZoomStep;
        dist = Mathf.Clamp(dist, ZoomMin * Radius, ZoomMax * Radius);
        Place();
        sunTimer -= dt;
        if (sunTimer <= 0f) { sunTimer = 0.5f; Shade(ci); }
        markerTimer -= dt;
        if (markerTimer <= 0f) { markerTimer = 1f; Markers(ci); }
        Facing();
        if (Clicks)
        {
            Hover(ci, overUi);
            RouteMouse(ci, overUi);
            RouteLines(ci);
            Cursor(ci, overUi);
        }
        if (Rings) RingLines(ci);
        if (Weather) WeatherPatches(ci);
    }

    // ---------- phase 5: rings, weather, notes ----------

    // tell WMSK where the mouse is on the map, so the game's ruler and map-note keys work on the globe
    private void Cursor(CampaignInterface ci, bool overUi)
    {
        if (overUi || ci.map == null) return;
        CampaignData d = CampaignManager.instance.campaignData;
        Vector2 p; Vector3 dir;
        if (!MouseMapPoint(d, out p, out dir) || !InMap(p)) return;
        ci.map.cursorLocation = new Vector3(p.x, p.y, 0f);
    }

    // a ribbon ring around a point on the sphere, angular radius ang (radians)
    private void AddRing(List<Vector3> v, List<Color> col, List<int> tri, Vector3 c, float ang, float w, float lift, Color color, Vector3 camDir, float limit)
    {
        Vector3 u = Vector3.Cross(c, Vector3.up); if (u.sqrMagnitude < 1e-6f) u = Vector3.Cross(c, Vector3.right);
        u.Normalize();
        Vector3 vv = Vector3.Cross(c, u).normalized;
        float ca = Mathf.Cos(ang), sa = Mathf.Sin(ang);
        int n = Mathf.Clamp(Mathf.RoundToInt(ang * Mathf.Rad2Deg * 6f), 24, 160);
        int start = v.Count;
        for (int k = 0; k <= n; k++)
        {
            float t = (float)k / n * Mathf.PI * 2f;
            Vector3 dir = (c * ca + (u * Mathf.Cos(t) + vv * Mathf.Sin(t)) * sa).normalized;
            v.Add(dir * (lift + w)); v.Add(dir * (lift - w));
            // a thin ring: offset along the surface instead of radially looks the same at this width and is simpler
            Color cc = color; cc.a = Vector3.Dot(dir, camDir) > limit ? color.a : 0f;
            col.Add(cc); col.Add(cc);
        }
        for (int k = 0; k < n; k++)
        {
            int a = start + k * 2, b = a + 1, cI = a + 2, dI = a + 3;
            tri.Add(a); tri.Add(cI); tri.Add(b); tri.Add(b); tri.Add(cI); tri.Add(dI);
        }
    }

    // base range rings: same size and visibility as the flat map's MapRadii discs
    private void RingLines(CampaignInterface ci)
    {
        MapRadii mr = MapRadii.instance;
        CampaignManager cm = CampaignManager.instance;
        List<MeshRenderer> list = mr != null ? mr.mapRadiiMeshRenderers : null;
        int sig = 23;
        if (list != null)
            for (int i = 0; i < list.Count; i++)
            {
                MeshRenderer r = list[i];
                if (r == null) { sig = sig * 31; continue; }
                bool vis = r.enabled && r.gameObject.activeInHierarchy;
                sig = sig * 31 + (vis ? 1 : 0);
                sig = sig * 31 + Mathf.RoundToInt(r.transform.localScale.y * 100f);
            }
        sig = sig * 31 + Mathf.RoundToInt(viewLat * 4f);
        sig = sig * 31 + Mathf.RoundToInt(viewLon * 4f);
        sig = sig * 31 + Mathf.RoundToInt(dist);
        if (sig == ringSig) return;
        ringSig = sig;
        if (ringMesh == null)
        {
            ringMesh = new Mesh();
            ringMesh.MarkDynamic();
            ringObj = MeshObj("Rings", ringMesh, white, Color.white, 3004);
        }
        if (list == null || cm.landMapLocations == null || cm.landMapLocations.Count == 0) { ringMesh.Clear(); ringObj.SetActive(false); return; }
        CampaignData d = cm.campaignData;
        Vector3 camDir = (cam.transform.position - centre).normalized;
        float limit = Radius / dist;
        float w = Radius * RingWidth * Mathf.Clamp(dist / (ZoomStart * Radius), 0.25f, 1.5f);
        float lift = Radius * 1.0035f;
        double earth = ModGeo.Radius(d);
        List<Vector3> v = new List<Vector3>(); List<int> tri = new List<int>(); List<Color> col = new List<Color>();
        int bases = cm.landMapLocations.Count;
        for (int i = 0; i < list.Count; i++)
        {
            MeshRenderer r = list[i];
            if (r == null || !r.enabled || !r.gameObject.activeInHierarchy) continue;
            float scale = r.transform.localScale.y;
            if (scale <= 0.0001f) continue;
            MapLocation loc = cm.landMapLocations[i % bases];
            if (loc == null) continue;
            float metres = scale / 400f * d.mapWidthMetres;        // the disc is scale wide on a 200-unit map
            float ang = (float)(metres / earth);
            Color color = new Color(1f, 1f, 1f, 0.5f);
            try { if (r.sharedMaterial != null && r.sharedMaterial.HasProperty("_Color")) color = r.sharedMaterial.color; } catch (Exception) { }
            if (color.a < 0.35f) color.a = 0.35f;
            if (i >= bases) color = new Color(color.r, color.g, color.b, color.a * 0.6f);
            Vector3 c = Dir((float)ModGeo.Lat(d, loc.locationPosition.y), (float)ModGeo.Lon(d, loc.locationPosition.x));
            AddRing(v, col, tri, c, ang, w, lift, color, camDir, limit);
        }
        ringMesh.Clear();
        if (v.Count == 0) { ringObj.SetActive(false); return; }
        ringMesh.vertices = v.ToArray();
        ringMesh.colors = col.ToArray();
        ringMesh.triangles = tri.ToArray();
        ringMesh.RecalculateBounds();
        ringObj.SetActive(true);
    }

    // weather cells: a textured patch per cell on the sphere, same texture and tint as the flat map's cell, plus the sea state text
    private void WeatherPatches(CampaignInterface ci)
    {
        WeatherManager wm = WeatherManager.instance;
        if (wm == null || wm.weatherMeshes == null || wm.weatherMeshes.Count == 0) { if (weatherRoot != null) weatherRoot.SetActive(false); return; }
        CampaignData d = CampaignManager.instance.campaignData;
        if (weatherRoot == null)
        {
            weatherRoot = new GameObject("Weather");
            weatherRoot.transform.SetParent(root.transform, false);
        }
        // one patch per cell, built once
        while (weatherPatches.Count < wm.weatherMeshes.Count)
        {
            int i = weatherPatches.Count;
            MeshRenderer src = wm.weatherMeshes[i];
            Vector3 lp = src != null ? src.transform.localPosition : Vector3.zero;
            float cx = lp.x / 200f, cy = lp.y / 100f, half = 0.05f;
            Mesh m = new Mesh();
            List<Vector3> v = new List<Vector3>(); List<Vector2> uv = new List<Vector2>(); List<int> tri = new List<int>();
            int g = 4;
            for (int yy = 0; yy <= g; yy++)
                for (int xx = 0; xx <= g; xx++)
                {
                    float mx = cx - half + 2f * half * xx / g, my = cy - half + 2f * half * yy / g;
                    Vector3 dir = Dir((float)ModGeo.Lat(d, my), (float)ModGeo.Lon(d, mx));
                    v.Add(dir * Radius * 1.0025f);
                    uv.Add(new Vector2((float)xx / g, (float)yy / g));
                }
            for (int yy = 0; yy < g; yy++)
                for (int xx = 0; xx < g; xx++)
                {
                    int a = yy * (g + 1) + xx, b = a + 1, c = a + g + 1, dd = c + 1;
                    tri.Add(a); tri.Add(c); tri.Add(b); tri.Add(b); tri.Add(c); tri.Add(dd);
                }
            m.vertices = v.ToArray(); m.uv = uv.ToArray(); m.triangles = tri.ToArray(); m.RecalculateBounds();
            GameObject go = MeshObj("Cell" + i, m, null, Color.white, 3003);
            go.transform.SetParent(weatherRoot.transform, false);
            weatherPatches.Add(go.GetComponent<MeshRenderer>());
            weatherDirs.Add(Dir((float)ModGeo.Lat(d, cy), (float)ModGeo.Lon(d, cx)));
        }
        // copy texture and tint when the game changes them (checked every second)
        weatherTimer -= Time.unscaledDeltaTime;
        if (weatherTimer <= 0f)
        {
            weatherTimer = 1f;
            int sig = 29;
            for (int i = 0; i < wm.weatherMeshes.Count; i++)
            {
                MeshRenderer src = wm.weatherMeshes[i];
                bool vis = src != null && src.enabled && src.gameObject.activeInHierarchy;
                sig = sig * 31 + (vis ? 1 : 0);
                sig = sig * 31 + (vis && src.sharedMaterial != null ? src.sharedMaterial.GetInstanceID() : 0);
            }
            if (sig != weatherSig)
            {
                weatherSig = sig;
                for (int i = 0; i < wm.weatherMeshes.Count && i < weatherPatches.Count; i++)
                {
                    MeshRenderer src = wm.weatherMeshes[i];
                    MeshRenderer dst = weatherPatches[i];
                    bool vis = src != null && src.enabled && src.gameObject.activeInHierarchy && src.sharedMaterial != null;
                    dst.enabled = vis;
                    if (!vis) continue;
                    Material sm = src.sharedMaterial;
                    Material dm = dst.sharedMaterial;
                    dm.mainTexture = sm.mainTexture;
                    Color c = Color.white;
                    try { if (sm.HasProperty("_Color")) c = sm.color; } catch (Exception) { }
                    c.a *= WeatherAlpha;
                    Tinted(dm, c);
                }
            }
        }
        // hide the far side
        Vector3 camDir = (cam.transform.position - centre).normalized;
        float limit = Radius / dist - 0.08f;
        for (int i = 0; i < weatherPatches.Count; i++)
        {
            bool front = Vector3.Dot(weatherDirs[i], camDir) > limit;
            if (weatherPatches[i].gameObject.activeSelf != front) weatherPatches[i].gameObject.SetActive(front);
        }
        if (!weatherRoot.activeSelf) weatherRoot.SetActive(true);
    }

    // ---------- phase 4: clicks, hover and routes ----------

    // where the mouse ray meets the globe, as a map point (-0.5..0.5); false when the mouse is off the Earth
    private bool MouseMapPoint(CampaignData d, out Vector2 p, out Vector3 dir)
    {
        p = Vector2.zero; dir = Vector3.zero;
        if (cam == null) return false;
        Ray ray = cam.ScreenPointToRay(Input.mousePosition);
        Vector3 oc = ray.origin - centre;
        float b = Vector3.Dot(oc, ray.direction);
        float c = Vector3.Dot(oc, oc) - Radius * Radius;
        float disc = b * b - c;
        if (disc < 0f) return false;
        float t = -b - Mathf.Sqrt(disc);
        if (t < 0f) return false;
        dir = (ray.origin + ray.direction * t - centre).normalized;
        float lat = Mathf.Asin(Mathf.Clamp(dir.y, -1f, 1f)) * Mathf.Rad2Deg;
        float lon = Mathf.Atan2(dir.z, dir.x) * Mathf.Rad2Deg; if (lon < 0f) lon += 360f;
        p = MapPoint(d, lat, lon);
        return true;
    }

    private static bool InMap(Vector2 p) { return p.x >= -0.5f && p.x <= 0.5f && p.y >= -0.5f && p.y <= 0.5f; }

    // the icon nearest the mouse, within PickPx
    private Entry EntryUnderMouse()
    {
        Entry best = null; float bestD = PickPx * PickPx;
        Vector2 m = Input.mousePosition;
        for (int i = 0; i < entries.Count; i++)
        {
            Entry e = entries[i];
            if (!e.shown || e.goa == null) continue;
            float dd = (e.screen - m).sqrMagnitude;
            if (dd < bestD) { bestD = dd; best = e; }
        }
        return best;
    }

    // same as hovering an icon on the flat map: the game's own tooltip
    private void Hover(CampaignInterface ci, bool overUi)
    {
        Entry e = (overUi || dragging) ? null : EntryUnderMouse();
        if (e != hover) SetHover(e, ci);
    }

    private void SetHover(Entry e, CampaignInterface ci)
    {
        WMSK map = ci != null ? ci.map : null;
        if (hover != null && hover.goa != null && map != null && map.OnVGOPointerExit != null) map.OnVGOPointerExit(hover.goa);
        hover = e;
        if (hover != null && hover.goa != null && map != null && map.OnVGOPointerEnter != null) map.OnVGOPointerEnter(hover.goa);
    }

    // a click on the globe, doing what the flat map's OnClick / OnVGOPointerDown handlers do (CampaignInterface.Awake)
    private void Click(CampaignInterface ci, int button)
    {
        WMSK map = ci.map;
        if (map == null) return;
        CampaignData d = CampaignManager.instance.campaignData;
        Vector2 p; Vector3 dir;
        bool onEarth = MouseMapPoint(d, out p, out dir);
        if (button == 1)
        {
            if (ci.enablePlotCourse)
            {
                ci.enablePlotCourse = false;
                ci.SetCampaignCursor();
                if (TooltipManager.instance != null) TooltipManager.instance.ClearToolTip();
                ci.PlotMobileCourse();
            }
            return;
        }
        if (!ci.enablePlotCourse)
        {
            Entry e = EntryUnderMouse();
            if (e != null && e.goa != null)
            {
                if (map.OnVGOPointerDown != null) map.OnVGOPointerDown(e.goa);
                markerTimer = 0f;
                return;
            }
        }
        if (ci.enablePlotCourse && ci.currentMapObject != null && onEarth && InMap(p))
        {
            ci.MoveMobileToDestination(ci.currentMapObject, p);
            lastRouteMouse = new Vector2(9f, 9f);
        }
    }

    // while plotting a course or using the ruler, feed the mouse's map point to the game so it draws the route preview
    private void RouteMouse(CampaignInterface ci, bool overUi)
    {
        if (overUi) return;
        if (!ci.enablePlotCourse && !ci.enablePlotRuler) return;
        if (!ci.enablePlotRuler && ci.currentMapObject == null) return;
        CampaignData d = CampaignManager.instance.campaignData;
        Vector2 p; Vector3 dir;
        if (!MouseMapPoint(d, out p, out dir) || !InMap(p)) return;
        if ((p - lastRouteMouse).sqrMagnitude < 1e-10f) return;
        lastRouteMouse = p;
        if (miRoute == null) miRoute = typeof(CampaignInterface).GetMethod("UpdateRoutePathLine", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
        if (miRoute != null) miRoute.Invoke(ci, new object[] { p.x, p.y });
    }

    // mirror the game's route lines (CampaignInterface.pathlines, drawn on the hidden flat map) onto the globe
    private void RouteLines(CampaignInterface ci)
    {
        List<LineMarkerAnimator> lines = ci.pathlines;
        int sig = 17;
        int count = 0;
        if (lines != null)
            for (int i = 0; i < lines.Count; i++)
            {
                LineMarkerAnimator l = lines[i];
                if (l == null || l.path == null || l.path.Length < 2) continue;
                count++;
                sig = sig * 31 + l.path.Length;
                sig = sig * 31 + Mathf.RoundToInt(l.path[0].x * 20000f) ;
                sig = sig * 31 + Mathf.RoundToInt(l.path[l.path.Length - 1].y * 20000f);
                sig = sig * 31 + Mathf.RoundToInt(l.color.r * 10f + l.color.g * 100f + l.color.b * 1000f);
            }
        sig = sig * 31 + Mathf.RoundToInt(viewLat * 4f);
        sig = sig * 31 + Mathf.RoundToInt(viewLon * 4f);
        sig = sig * 31 + Mathf.RoundToInt(dist);
        if (sig == routeSig) return;
        routeSig = sig;
        if (routeMesh == null)
        {
            routeMesh = new Mesh();
            routeMesh.MarkDynamic();
            routeObj = MeshObj("Routes", routeMesh, white, Color.white, 3004);
        }
        if (count == 0) { routeMesh.Clear(); routeObj.SetActive(false); return; }
        CampaignData d = CampaignManager.instance.campaignData;
        Vector3 camDir = (cam.transform.position - centre).normalized;
        float limit = Radius / dist;
        float w = Radius * RouteWidth * Mathf.Clamp(dist / (ZoomStart * Radius), 0.25f, 1.5f);
        float lift = Radius * 1.004f;
        List<Vector3> v = new List<Vector3>(); List<int> tri = new List<int>(); List<Color> col = new List<Color>();
        List<Vector3> dirs = new List<Vector3>();
        for (int i = 0; i < lines.Count; i++)
        {
            LineMarkerAnimator l = lines[i];
            if (l == null || l.path == null || l.path.Length < 2) continue;
            dirs.Clear();
            for (int k = 0; k < l.path.Length; k++)
            {
                Vector3 nd = Dir((float)ModGeo.Lat(d, l.path[k].y), (float)ModGeo.Lon(d, l.path[k].x));
                if (dirs.Count > 0)
                {
                    Vector3 pd = dirs[dirs.Count - 1];
                    float ang = Vector3.Angle(pd, nd);
                    int sub = Mathf.Min(64, Mathf.FloorToInt(ang / 1.5f));
                    for (int q = 1; q <= sub; q++) dirs.Add(Vector3.Slerp(pd, nd, (float)q / (sub + 1)).normalized);
                }
                dirs.Add(nd);
            }
            Color c = l.color; c.a = 1f;
            int start = v.Count;
            for (int k = 0; k < dirs.Count; k++)
            {
                Vector3 dir = dirs[k];
                Vector3 next = dirs[Mathf.Min(k + 1, dirs.Count - 1)];
                Vector3 prev = dirs[Mathf.Max(k - 1, 0)];
                Vector3 tangent = (next - prev);
                if (tangent.sqrMagnitude < 1e-12f) tangent = Vector3.Cross(dir, Vector3.up);
                Vector3 side = Vector3.Cross(dir, tangent.normalized).normalized;
                v.Add(dir * lift + side * w); v.Add(dir * lift - side * w);
                Color cc = c; cc.a = Vector3.Dot(dir, camDir) > limit ? 1f : 0f;
                col.Add(cc); col.Add(cc);
            }
            for (int k = 0; k < dirs.Count - 1; k++)
            {
                int a = start + k * 2, b = a + 1, cI = a + 2, dI = a + 3;
                tri.Add(a); tri.Add(cI); tri.Add(b); tri.Add(b); tri.Add(cI); tri.Add(dI);
            }
        }
        routeMesh.Clear();
        routeMesh.vertices = v.ToArray();
        routeMesh.colors = col.ToArray();
        routeMesh.triangles = tri.ToArray();
        routeMesh.RecalculateBounds();
        routeObj.transform.position = centre;
        routeObj.SetActive(true);
    }

    private void Place()
    {
        Vector3 dir = Dir(viewLat, viewLon);
        cam.transform.position = centre + dir * dist;
        cam.transform.LookAt(centre, Vector3.up);
        if (haloObj != null) { haloObj.transform.position = centre; haloObj.transform.rotation = cam.transform.rotation; }
        if (starsObj != null) starsObj.transform.position = centre;
    }

    // true when the mouse is over one of the game's own panels (our invisible blocker does not count)
    private bool OverGameUi()
    {
        try
        {
            EventSystem es = EventSystem.current;
            if (es == null) return false;
            PointerEventData pd = new PointerEventData(es);
            pd.position = Input.mousePosition;
            List<RaycastResult> hits = new List<RaycastResult>();
            es.RaycastAll(pd, hits);
            for (int i = 0; i < hits.Count; i++)
            {
                if (hits[i].gameObject == null) continue;
                if (hits[i].gameObject == blocker) continue;
                return true;
            }
            return false;
        }
        catch (Exception) { return false; }
    }

    private void DropToMap(CampaignInterface ci)
    {
        CampaignData d = CampaignManager.instance.campaignData;
        Vector2 p = MapPoint(d, viewLat, viewLon);
        Off();
        lastSwitch = Time.unscaledTime;
        if (ci.map != null && p.x >= -0.5f && p.x <= 0.5f && p.y >= -0.5f && p.y <= 0.5f)
        {
            float z = Mathf.Lerp(ci.map.zoomMinDistance, ci.map.zoomMaxDistance, Mathf.Clamp01(DropZoom));
            ci.map.FlyToLocation(p, 0.6f, z);
            Debug.Log("[GLOBE] dropped to map at " + p.x.ToString("0.000") + " " + p.y.ToString("0.000"));
        }
    }

    // ---------- geometry ----------

    // unit direction from the globe centre for a latitude/longitude (east to the right when seen from outside)
    public static Vector3 Dir(float lat, float lon)
    {
        float la = lat * Mathf.Deg2Rad, lo = lon * Mathf.Deg2Rad;
        return new Vector3(Mathf.Cos(la) * Mathf.Cos(lo), Mathf.Sin(la), Mathf.Cos(la) * Mathf.Sin(lo));
    }

    // map point (-0.5..0.5) of a latitude/longitude, using the campaign's own origin
    public static Vector2 MapPoint(CampaignData d, float lat, float lon)
    {
        double lonW = ModGeo.Lon(d, -0.5f);                 // west edge, 0..360
        double l = lon; while (l < lonW) l += 360.0; while (l >= lonW + 360.0) l -= 360.0;
        float x = (float)((l * ModGeo.PxPerDeg - d.mapOriginXY[0]) / d.mapPixelWidth - 0.5);
        float y = (float)(((lat + 90.0) * ModGeo.PxPerDeg - d.mapOriginXY[1]) / (d.mapPixelWidth * 0.5) - 0.5);
        return new Vector2(x, y);
    }

    private Vector3 SunDir(CampaignInterface ci)
    {
        float offset = UtcOffsetHours;
        if (offset > 24f || offset < -24f)
        {
            CampaignData d = CampaignManager.instance.campaignData;
            double lon = ModGeo.Lon(d, 0f); if (lon > 180.0) lon -= 360.0;
            offset = Mathf.Round((float)(lon / 15.0));
        }
        return SunDir(ci.dateTime, offset);
    }

    private static Vector3 SunDir(DateTime t, float offset)
    {
        float utc = (float)t.TimeOfDay.TotalHours - offset;
        float decl = 23.44f * Mathf.Sin(2f * Mathf.PI * (284f + t.DayOfYear) / 365f);
        float sunLon = 180f - 15f * utc;
        return Dir(decl, sunLon);
    }

    // day/night as vertex colours (no lights needed, nothing else in the scene is touched)
    private void Shade(CampaignInterface ci) { if (globeMesh != null) ShadeBy(SunDir(ci)); }
    private void Shade(DateTime t, float offset) { if (globeMesh != null) ShadeBy(SunDir(t, offset)); }

    private void ShadeBy(Vector3 s)
    {
        if (globeMesh == null || globeNormals == null) return;
        float lo = -Twilight, hi = Twilight;
        for (int i = 0; i < globeNormals.Length; i++)
        {
            float k = Mathf.InverseLerp(lo, hi, Vector3.Dot(globeNormals[i], s));
            float v = Mathf.Lerp(Night, 1f, k * k * (3f - 2f * k));
            globeColors[i] = new Color(v, v, v, 1f);
        }
        globeMesh.colors = globeColors;
    }

    // hide dots and outline on the far side of the globe
    private void Facing()
    {
        Vector3 v = (cam.transform.position - centre).normalized;
        float limit = Radius / dist; // cos of the angle to the horizon
        // The particle shader draws both faces and writes no depth, so the far side of the sphere would paint over the near
        // side wherever it is drawn later. Keep only the triangles that face the camera (rebuilt when the camera moves).
        if (globeTris != null && (cam.transform.position - lastCamPos).sqrMagnitude > 0.0001f)
        {
            lastCamPos = cam.transform.position;
            frontTris.Clear();
            Vector3 camLocal = cam.transform.position - centre;
            for (int t = 0; t < globeTris.Length; t += 3)
            {
                int a = globeTris[t], b = globeTris[t + 1], c = globeTris[t + 2];
                Vector3 n = globeNormals[a] + globeNormals[b] + globeNormals[c];
                Vector3 p = (globeNormals[a] + globeNormals[b] + globeNormals[c]) * (Radius / 3f);
                if (Vector3.Dot(n, camLocal - p) > 0f) { frontTris.Add(a); frontTris.Add(b); frontTris.Add(c); }
            }
            globeMesh.SetTriangles(frontTris, 0);
        }
        PlaceEntries(v, limit);
        if (ribbonObj != null && ribbonColors != null)
        {
            bool changed = false;
            for (int i = 0; i < ribbonDirs.Count; i++)
            {
                float a = Vector3.Dot(ribbonDirs[i], v) > limit ? 1f : 0f;
                int k = i * 2;
                if (ribbonColors[k].a != a) { ribbonColors[k].a = a; ribbonColors[k + 1].a = a; changed = true; }
            }
            if (changed) ribbonObj.GetComponent<MeshFilter>().sharedMesh.colors = ribbonColors;
        }
    }

    // ---------- icons and names (UI objects placed over the globe) ----------

    private void Markers(CampaignInterface ci)
    {
        for (int i = 0; i < entries.Count; i++) if (entries[i].go != null) Destroy(entries[i].go);
        entries.Clear();
        hover = null;
        if (!ShowMarkers || overlay == null) return;
        CampaignManager cm = CampaignManager.instance;
        CampaignData d = cm.campaignData;
        if (cm.landMapLocations != null)
            for (int i = 0; i < cm.landMapLocations.Count; i++)
            {
                MapLocation loc = cm.landMapLocations[i];
                if (loc == null) continue;
                AddEntry(d, loc.locationPosition, loc.GetComponentInChildren<SpriteRenderer>(), loc.locationName, 1f, loc.gameObjectAnimator);
            }
        if (cm.playerMobile != null)
            for (int i = 0; i < cm.playerMobile.Count; i++)
            {
                GameObjectAnimator g = cm.playerMobile[i];
                if (g == null || g.mobileMapObject == null || g.mobileMapObject.unitPrefabs == null || g.mobileMapObject.unitPrefabs.Count == 0) continue;
                AddEntry(d, g.currentMap2DLocation, g.GetComponentInChildren<SpriteRenderer>(), g.mobileMapObject.mobileName, 1.1f, g);
            }
        if (cm.spottedContacts != null)
            for (int i = 0; i < cm.spottedContacts.Count; i++)
            {
                MobileMapObject m = cm.spottedContacts[i];
                if (m == null || m.gameObjectAnimator == null) continue;
                AddEntry(d, m.gameObjectAnimator.currentMap2DLocation, m.gameObjectAnimator.GetComponentInChildren<SpriteRenderer>(), m.mobileName, 1.1f, m.gameObjectAnimator);
            }
        if (Notes && ci.mapMarkerParent != null)
        {
            MapLocation[] notes = ci.mapMarkerParent.GetComponentsInChildren<MapLocation>();
            for (int i = 0; i < notes.Length; i++)
            {
                MapLocation n = notes[i];
                if (n == null || n.gameObjectAnimator == null) continue;
                AddEntry(d, n.locationPosition, n.GetComponentInChildren<SpriteRenderer>(), n.locationName, 0.9f, n.gameObjectAnimator);
            }
        }
        if (Weather && WeatherManager.instance != null && WeatherManager.instance.seaStateMeshes != null)
        {
            List<TextMesh> sea = WeatherManager.instance.seaStateMeshes;
            for (int i = 0; i < sea.Count; i++)
            {
                TextMesh t = sea[i];
                if (t == null || string.IsNullOrEmpty(t.text) || !t.gameObject.activeInHierarchy) continue;
                Vector3 lp = t.transform.localPosition;
                AddEntry(d, new Vector2(lp.x / 200f, lp.y / 100f), null, t.text, 0.01f, null);
                Entry e = entries[entries.Count - 1];
                e.icon.enabled = false;
                if (e.label != null) { e.label.color = new Color(0.8f, 0.9f, 1f, 0.9f); e.label.fontSize = LabelPx - 1; e.shadow.fontSize = LabelPx - 1; }
            }
        }
        Vector3 v = (cam.transform.position - centre).normalized;
        PlaceEntries(v, Radius / dist);
    }

    private void AddEntry(CampaignData d, Vector2 mapPos, SpriteRenderer src, string name, float size, GameObjectAnimator goa)
    {
        Entry e = new Entry();
        e.goa = goa;
        e.dir = Dir((float)ModGeo.Lat(d, mapPos.y), (float)ModGeo.Lon(d, mapPos.x));
        e.go = new GameObject("GlobeIcon", typeof(RectTransform));
        e.go.transform.SetParent(overlay, false);
        e.rect = e.go.GetComponent<RectTransform>();
        e.rect.anchorMin = e.rect.anchorMax = new Vector2(0.5f, 0.5f);
        e.rect.pivot = new Vector2(0.5f, 0.5f);
        e.rect.sizeDelta = new Vector2(IconPx * size, IconPx * size);
        e.icon = e.go.AddComponent<Image>();
        e.icon.raycastTarget = false;
        e.icon.preserveAspect = true;
        if (src != null && src.sprite != null) { e.icon.sprite = src.sprite; Color ic = src.color; ic.a = 1f; e.icon.color = ic; }   // the flat map may have faded its icon out; ours is always solid
        else e.icon.color = Color.white;
        if (!string.IsNullOrEmpty(name))
        {
            e.shadow = MakeLabel(e.rect, name, new Vector2(1f, -1f), new Color(0f, 0f, 0f, 0.9f));
            e.label = MakeLabel(e.rect, name, Vector2.zero, Color.white);
        }
        entries.Add(e);
    }

    private Text MakeLabel(RectTransform parent, string name, Vector2 offset, Color c)
    {
        GameObject g = new GameObject("Name", typeof(RectTransform));
        g.transform.SetParent(parent, false);
        RectTransform r = g.GetComponent<RectTransform>();
        r.anchorMin = new Vector2(0.5f, 0f); r.anchorMax = new Vector2(0.5f, 0f);
        r.pivot = new Vector2(0.5f, 1f);
        r.anchoredPosition = new Vector2(offset.x, -2f + offset.y);
        r.sizeDelta = new Vector2(220f, LabelPx + 6);
        Text t = g.AddComponent<Text>();
        t.font = font;
        t.fontSize = LabelPx;
        t.alignment = TextAnchor.UpperCenter;
        t.color = c;
        t.raycastTarget = false;
        t.text = name;
        return t;
    }

    private void PlaceEntries(Vector3 v, float limit)
    {
        if (overlay == null) return;
        Canvas canvas = overlay.GetComponentInParent<Canvas>();
        Camera uiCam = (canvas != null && canvas.renderMode != RenderMode.ScreenSpaceOverlay) ? canvas.worldCamera : null;
        float scale = Mathf.Clamp(ZoomStart * Radius / dist, 0.6f, 2.4f);
        bool labels = dist < LabelZoom * Radius;
        GameObjectAnimator selected = CampaignInterface.instance != null ? CampaignInterface.instance.currentMapObject : null;
        for (int i = 0; i < entries.Count; i++)
        {
            Entry e = entries[i];
            if (e.go == null) continue;
            bool front = Vector3.Dot(e.dir, v) > limit;
            e.shown = false;
            if (!front) { if (e.go.activeSelf) e.go.SetActive(false); continue; }
            Vector3 sp = cam.WorldToScreenPoint(centre + e.dir * Radius * 1.002f);
            e.screen = new Vector2(sp.x, sp.y);
            Vector2 local;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(overlay, new Vector2(sp.x, sp.y), uiCam, out local)) continue;
            if (!e.go.activeSelf) e.go.SetActive(true);
            e.shown = true;
            e.rect.anchoredPosition = local;
            float s2 = scale;
            if (e.goa != null && (e == hover || e.goa == selected)) s2 *= 1.3f;
            e.rect.localScale = new Vector3(s2, s2, 1f);
            if (e.label != null) { e.label.enabled = labels; e.shadow.enabled = labels; }
        }
    }

    // ---------- build once ----------

    private void Build(CampaignData d)
    {
        built = true;
        shader = Shader.Find("Particles/Alpha Blended");
        if (shader == null) { shader = Shader.Find("Sprites/Default"); Debug.Log("[GLOBE] Particles/Alpha Blended not found, using Sprites/Default"); }
        white = new Texture2D(2, 2, TextureFormat.RGBA32, false);
        white.SetPixels(new Color[] { Color.white, Color.white, Color.white, Color.white }); white.Apply();

        root = new GameObject("ModGlobeRoot");
        root.transform.position = centre;
        DontDestroyOnLoad(root);

        GameObject camObj = new GameObject("ModGlobeCamera");
        camObj.transform.SetParent(root.transform, false);
        cam = camObj.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = Color.black;
        cam.nearClipPlane = 1f;
        cam.farClipPlane = 60000f;
        cam.fieldOfView = 40f;
        Camera main = Camera.main;
        cam.depth = (main != null ? main.depth : 0f) + 5f;
        cam.cullingMask = -1;
        cam.enabled = false;

        // the Earth
        globeMesh = Sphere(96, 192, Radius, out globeNormals);
        globeTris = globeMesh.triangles;
        globeMesh.MarkDynamic();
        globeColors = new Color[globeNormals.Length];
        for (int i = 0; i < globeColors.Length; i++) globeColors[i] = Color.white;
        globeMesh.colors = globeColors;
        globeObj = MeshObj("Globe", globeMesh, EarthTexture(), Color.white, 3002);
        // stars behind everything (a big sphere seen from inside; the particle shader draws both faces)
        Vector3[] dummy;
        starsObj = MeshObj("Stars", Sphere(24, 48, 30000f, out dummy), StarTexture(), Color.white, 3000);
        // a soft blue halo on a quad that always faces the camera
        haloObj = MeshObj("Halo", Quad(Radius * 2.6f), HaloTexture(), new Color(0.45f, 0.65f, 1f, 1f), 3001);
        // gold outline of the theatre
        if (d != null) { BuildRibbon(d); BuildBlocker(); }
        root.SetActive(false);
        Debug.Log("[GLOBE] built: " + globeNormals.Length + " vertices, shader " + (shader != null ? shader.name : "none"));
    }

    private Material Unlit(Color c, int queue)
    {
        Material m = new Material(shader);
        m.mainTexture = white;
        if (m.HasProperty("_TintColor")) m.SetColor("_TintColor", new Color(0.5f, 0.5f, 0.5f, 0.5f));
        if (m.HasProperty("_Color")) m.color = Color.white;
        m.renderQueue = queue;
        // colour comes from the vertices, so set them
        return Tinted(m, c);
    }

    private Material Tinted(Material m, Color c)
    {
        if (m.HasProperty("_TintColor")) m.SetColor("_TintColor", new Color(c.r * 0.5f, c.g * 0.5f, c.b * 0.5f, c.a * 0.5f));
        else if (m.HasProperty("_Color")) m.color = c;
        return m;
    }

    private GameObject MeshObj(string name, Mesh mesh, Texture2D tex, Color tint, int queue)
    {
        GameObject g = new GameObject(name);
        g.transform.SetParent(root.transform, false);
        g.AddComponent<MeshFilter>().sharedMesh = mesh;
        MeshRenderer r = g.AddComponent<MeshRenderer>();
        Material m = new Material(shader);
        m.mainTexture = tex;
        m.renderQueue = queue;
        Tinted(m, tint);
        r.sharedMaterial = m;
        r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        r.receiveShadows = false;
        return g;
    }

    private Texture2D EarthTexture()
    {
        Texture2D t = null;
        try { t = AssetLoader.instance.ImportTexture2D("ModAssets/globe/earth.jpg"); } catch (Exception ex) { Debug.Log("[GLOBE] earth.jpg: " + ex.Message); }
        if (t != null && t.width > 64) { t.wrapMode = TextureWrapMode.Repeat; t.anisoLevel = 4; Debug.Log("[GLOBE] earth.jpg " + t.width + "x" + t.height); return t; }
        Debug.Log("[GLOBE] override/ModAssets/globe/earth.jpg not found, drawing a plain globe");
        int w = 1024, h = 512;
        t = new Texture2D(w, h, TextureFormat.RGB24, false);
        Color sea = new Color(0.16f, 0.26f, 0.38f), line = new Color(0.4f, 0.5f, 0.6f);
        Color[] px = new Color[w * h];
        for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) px[y * w + x] = ((x % (w / 24) == 0) || (y % (h / 12) == 0)) ? line : sea;
        t.SetPixels(px); t.Apply();
        return t;
    }

    private Texture2D StarTexture()
    {
        int w = 1024, h = 512;
        Texture2D t = new Texture2D(w, h, TextureFormat.RGBA32, false);
        Color[] px = new Color[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = new Color(0f, 0f, 0f, 1f);
        System.Random rnd = new System.Random(7);
        for (int i = 0; i < 1800; i++)
        {
            int x = rnd.Next(w), y = rnd.Next(h);
            float b = 0.35f + 0.65f * (float)rnd.NextDouble();
            px[y * w + x] = new Color(b, b, b * 0.95f + 0.05f, 1f);
        }
        t.SetPixels(px); t.Apply();
        return t;
    }

    private Texture2D HaloTexture()
    {
        int n = 256;
        Texture2D t = new Texture2D(n, n, TextureFormat.RGBA32, false);
        Color[] px = new Color[n * n];
        float inner = Radius / (Radius * 1.3f), outer = 1f; // in units of the quad half size
        for (int y = 0; y < n; y++) for (int x = 0; x < n; x++)
        {
            float dx = (x + 0.5f) / n * 2f - 1f, dy = (y + 0.5f) / n * 2f - 1f;
            float r = Mathf.Sqrt(dx * dx + dy * dy);
            float a = 0f;
            if (r > inner * 0.98f && r < outer) { float k = (r - inner * 0.98f) / (outer - inner * 0.98f); a = 0.55f * (1f - k) * (1f - k); }
            px[y * n + x] = new Color(1f, 1f, 1f, a);
        }
        t.SetPixels(px); t.Apply();
        t.wrapMode = TextureWrapMode.Clamp;
        return t;
    }

    private static Mesh Sphere(int rings, int segs, float r, out Vector3[] normals)
    {
        int nv = (rings + 1) * (segs + 1);
        Vector3[] v = new Vector3[nv]; Vector3[] n = new Vector3[nv]; Vector2[] uv = new Vector2[nv];
        int k = 0;
        for (int i = 0; i <= rings; i++)
        {
            float lat = -90f + 180f * i / rings;
            for (int j = 0; j <= segs; j++)
            {
                float lon = -180f + 360f * j / segs;
                Vector3 dir = Dir(lat, lon);
                v[k] = dir * r; n[k] = dir; uv[k] = new Vector2((float)j / segs, (float)i / rings);
                k++;
            }
        }
        int[] tri = new int[rings * segs * 6];
        int t = 0;
        for (int i = 0; i < rings; i++)
            for (int j = 0; j < segs; j++)
            {
                int a = i * (segs + 1) + j, b = a + 1, c = a + segs + 1, d = c + 1;
                tri[t++] = a; tri[t++] = c; tri[t++] = d;
                tri[t++] = a; tri[t++] = d; tri[t++] = b;
            }
        Mesh m = new Mesh();
        m.name = "GlobeSphere";
        m.vertices = v; m.normals = n; m.uv = uv; m.triangles = tri;
        m.RecalculateBounds();
        normals = n;
        return m;
    }

    private static Mesh Quad(float size)
    {
        float h = size * 0.5f;
        Mesh m = new Mesh();
        m.vertices = new Vector3[] { new Vector3(-h, -h, 0f), new Vector3(h, -h, 0f), new Vector3(-h, h, 0f), new Vector3(h, h, 0f) };
        m.uv = new Vector2[] { new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(0f, 1f), new Vector2(1f, 1f) };
        m.triangles = new int[] { 0, 2, 3, 0, 3, 1, 0, 3, 2, 0, 1, 3 };
        m.RecalculateBounds();
        return m;
    }

    private void BuildRibbon(CampaignData d)
    {
        float lat0 = (float)ModGeo.Lat(d, -0.5f), lat1 = (float)ModGeo.Lat(d, 0.5f);
        float lon0 = (float)ModGeo.Lon(d, -0.5f);
        float wdeg = d.mapPixelWidth / ModGeo.PxPerDeg;
        if (!Theatre || wdeg > 359f) { ribbonObj = null; ribbonColors = null; return; }   // a world-wide map has no edge worth drawing
        List<Vector2> pts = new List<Vector2>();
        int n = Mathf.Max(8, Mathf.RoundToInt(wdeg));
        for (int i = 0; i <= n; i++) pts.Add(new Vector2(lat0, lon0 + wdeg * i / n));
        int m2 = Mathf.Max(4, Mathf.RoundToInt(lat1 - lat0));
        for (int i = 1; i <= m2; i++) pts.Add(new Vector2(lat0 + (lat1 - lat0) * i / m2, lon0 + wdeg));
        for (int i = n - 1; i >= 0; i--) pts.Add(new Vector2(lat1, lon0 + wdeg * i / n));
        for (int i = m2 - 1; i >= 0; i--) pts.Add(new Vector2(lat0 + (lat1 - lat0) * i / m2, lon0));
        float w = Radius * 0.004f, lift = Radius * 1.003f;
        List<Vector3> v = new List<Vector3>(); List<int> tri = new List<int>(); List<Vector2> uv = new List<Vector2>();
        ribbonDirs.Clear();
        for (int i = 0; i < pts.Count; i++)
        {
            Vector3 dir = Dir(pts[i].x, pts[i].y);
            Vector3 next = Dir(pts[(i + 1) % pts.Count].x, pts[(i + 1) % pts.Count].y);
            Vector3 prev = Dir(pts[(i - 1 + pts.Count) % pts.Count].x, pts[(i - 1 + pts.Count) % pts.Count].y);
            Vector3 tangent = (next - prev).normalized;
            Vector3 side = Vector3.Cross(dir, tangent).normalized;
            v.Add(dir * lift + side * w); v.Add(dir * lift - side * w);
            uv.Add(Vector2.zero); uv.Add(Vector2.one);
            ribbonDirs.Add(dir);
        }
        int cnt = pts.Count;
        for (int i = 0; i < cnt; i++)
        {
            int a = i * 2, b = a + 1, c = ((i + 1) % cnt) * 2, dd = c + 1;
            Vector3 nrm = Vector3.Cross(v[c] - v[a], v[b] - v[a]);
            if (Vector3.Dot(nrm, v[a]) > 0f) { tri.Add(a); tri.Add(c); tri.Add(b); tri.Add(b); tri.Add(c); tri.Add(dd); }
            else { tri.Add(a); tri.Add(b); tri.Add(c); tri.Add(b); tri.Add(dd); tri.Add(c); }
        }
        Mesh mesh = new Mesh();
        mesh.vertices = v.ToArray(); mesh.uv = uv.ToArray(); mesh.triangles = tri.ToArray();
        ribbonColors = new Color[v.Count];
        for (int i = 0; i < ribbonColors.Length; i++) ribbonColors[i] = new Color(1f, 0.8f, 0.25f, 1f);
        mesh.colors = ribbonColors;
        mesh.RecalculateBounds();
        ribbonObj = MeshObj("Theatre", mesh, white, Color.white, 3003);
        ribbonMat = ribbonObj.GetComponent<MeshRenderer>().sharedMaterial;
    }

    // an invisible full-screen panel behind the game's panels, so clicks on the globe do not reach the flat map
    private void BuildBlocker()
    {
        try
        {
            CampaignInterface ci = CampaignInterface.instance;
            if (ci == null || ci.pauseButtonImage == null || ci.pauseButtonImage.canvas == null) return;
            Transform rootCanvas = ci.pauseButtonImage.canvas.rootCanvas.transform;
            blocker = new GameObject("ModGlobeBlocker", typeof(RectTransform));
            blocker.transform.SetParent(rootCanvas, false);
            blocker.transform.SetAsFirstSibling();
            RectTransform rt = blocker.GetComponent<RectTransform>();
            rt.anchorMin = Vector2.zero; rt.anchorMax = Vector2.one; rt.offsetMin = Vector2.zero; rt.offsetMax = Vector2.zero;
            Image img = blocker.AddComponent<Image>();
            img.color = new Color(0f, 0f, 0f, 0f);
            img.raycastTarget = true;
            GameObject ov = new GameObject("ModGlobeOverlay", typeof(RectTransform));
            ov.transform.SetParent(blocker.transform, false);
            overlay = ov.GetComponent<RectTransform>();
            overlay.anchorMin = Vector2.zero; overlay.anchorMax = Vector2.one; overlay.offsetMin = Vector2.zero; overlay.offsetMax = Vector2.zero;
            font = null;
            try { if (TooltipManager.instance != null && TooltipManager.instance.toolTipText != null) font = TooltipManager.instance.toolTipText.font; } catch (Exception) { }
            if (font == null) font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            blocker.SetActive(false);
        }
        catch (Exception ex) { Debug.Log("[GLOBE] blocker: " + ex.Message); blocker = null; }
    }

    private void BuildButton(CampaignInterface ci)
    {
        if (ci.pauseButtonImage == null || ci.pauseButtonImage.canvas == null) return;
        Transform root = ci.pauseButtonImage.canvas.rootCanvas.transform;
        buttonObject = ModTFOverlay.MakeButton(root, 4, null, "3D", "Globe (F10). Drag to spin, wheel to zoom; zoom right in to return to the map, scroll out on the map to come back", new UnityAction(Toggle), out buttonBack);
        if (!buttonReported) { buttonReported = true; Debug.Log("[GLOBE] button added"); }
    }
}
