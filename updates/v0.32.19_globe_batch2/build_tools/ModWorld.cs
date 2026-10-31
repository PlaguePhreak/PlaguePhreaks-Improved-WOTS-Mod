using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using UnityEngine;
using WorldMapStrategyKit;

// Worlds at War extras, driven by two optional files in the campaign folder (Override/campaign/<id>/):
//   convoys.txt  one JSON line per convoy route (ConvoyRoute): scripted convoys that sail the route on a timetable and score points
//   score.txt    one JSON line (ScoreRules): the campaign end date and the victory-point weights
// Campaigns without the files are untouched. State is saved in CampaignData.modWorld (a field the patcher adds).
// Hooks (patcher HooksWorld): CheckDaily -> ModWorld.Daily(), Check1Min -> ModWorld.Tick(), GetCampaignDataString -> ModWorld.Save(campaignData).

[Serializable]
public class ConvoyRoute
{
    public string id = "";              // short id, e.g. "hx"
    public string name = "";            // "HX" -> the convoys are named "Convoy HX-160", "Convoy HX-161", ...
    public int faction = 0;             // 0 = the player's side sails it (yellow, steers itself), 1 = the enemy sails it (the AI steers it)
    public string from = "";            // port id it sails from (must be held by its side)
    public string to = "";              // port id it sails to (must be held by its side)
    public List<string> via = new List<string>();   // sea waypoint names it must pass, optional
    public int everyDays = 10;          // a new convoy this often
    public int firstDay = 0;            // days after the campaign start for the first one
    public int firstNumber = 100;       // numbering starts here
    public int merchants = 6;
    public int oilers = 1;
    public int escorts = 3;
    public int points = 10;             // victory points for getting through (the other side gets them if it is wiped out)
    public string cargo = "supplies";   // supplies | fuel | troops: what the merchants carry (oilers always carry fuel)
    public string note = "";            // one line shown in the arrival pop-up
}

[Serializable]
public class ScoreRules
{
    public int endDay = 2;
    public int endMonth = 9;
    public int endYear = 1945;
    public int warnDays = 30;           // pop-up this many days before the end
    public int portPoints = 15;         // per port that changed hands since the start
    public int submarine = 3, destroyerEscort = 2, destroyer = 3, lightCruiser = 5, heavyCruiser = 7, battlecruiser = 9, battleship = 12;
    public int lightCarrier = 9, carrier = 14, oiler = 2, merchant = 2;
    public string side0 = "Allies";     // the player's side
    public string side1 = "Axis";
}

public static class ModWorld
{
    public static bool On = true;

    public static void Daily()
    {
        if (!On) return;
        try { ModRoutes.Daily(); } catch (Exception ex) { Debug.LogError("[WORLD] routes daily: " + ex); }
        try { ModScore.Daily(); } catch (Exception ex) { Debug.LogError("[WORLD] score daily: " + ex); }
    }

    public static void Tick()
    {
        if (!On) return;
        try { ModRoutes.Tick(); } catch (Exception ex) { Debug.LogError("[WORLD] routes tick: " + ex); }
    }

    private static FieldInfo SaveField()
    {
        return typeof(CampaignData).GetField("modWorld", BindingFlags.Instance | BindingFlags.Public);
    }

    public static void Save(CampaignData data)
    {
        try
        {
            if (data == null) return;
            FieldInfo f = SaveField();
            if (f == null) return;
            List<string> list = new List<string>();
            ModRoutes.Write(list);
            ModScore.Write(list);
            f.SetValue(data, list);
        }
        catch (Exception ex) { Debug.LogError("[WORLD] save failed: " + ex.Message); }
    }

    public static List<string> Saved()
    {
        try
        {
            FieldInfo f = SaveField();
            CampaignManager cm = CampaignManager.instance;
            if (f == null || cm == null || cm.campaignData == null) return null;
            return f.GetValue(cm.campaignData) as List<string>;
        }
        catch (Exception) { return null; }
    }

    public static bool Ready()
    {
        CampaignManager cm = CampaignManager.instance;
        return cm != null && cm.campaignData != null && CampaignInterface.instance != null && cm.landMapLocations != null && cm.landMapLocations.Count > 0 && cm.playerMobile != null;
    }

    public static DateTime Start(CampaignData d)
    {
        try
        {
            int[] s = d.startDate;
            if (s != null && s.Length >= 6) return new DateTime(s[5], s[4], s[3]);
        }
        catch (Exception) { }
        return CampaignInterface.instance.dateTime.Date;
    }
}

public static class ModRoutes
{
    public static string Prefix = "Convoy ";
    public static int MaxAtSea = 2;         // per route
    public static float ArriveKm = 60f;
    public static int ResendMinutes = 30;   // a stopped convoy of ours is sent on again after this
    public static List<ConvoyRoute> routes = new List<ConvoyRoute>();

    private class Live
    {
        public MobileMapObject mmo;
        public ConvoyRoute route;
        public int startMerchants;
        public bool awarded;
        public int idle;
    }

    private static readonly Dictionary<MobileMapObject, Live> live = new Dictionary<MobileMapObject, Live>();
    private static readonly Dictionary<string, int> nextNumber = new Dictionary<string, int>();
    private static readonly Dictionary<string, string[]> saved = new Dictionary<string, string[]>();
    private static object owner;
    private static string loadedFor;
    private static DateTime lastDay = DateTime.MinValue;

    // ---------- data ----------
    private static void Sync()
    {
        CampaignManager cm = CampaignManager.instance;
        if (owner != cm.landMapLocations)
        {
            owner = cm.landMapLocations;
            live.Clear();
            nextNumber.Clear();
            saved.Clear();
            lastDay = DateTime.MinValue;
            Load(cm.campaignData.campaignID);
            Restore();
        }
        // drop convoys that left the map
        List<MobileMapObject> gone = null;
        foreach (KeyValuePair<MobileMapObject, Live> kv in live)
        {
            MobileMapObject m = kv.Key;
            if (m == null || m.gameObjectAnimator == null || (!cm.playerMobile.Contains(m.gameObjectAnimator) && !cm.otherMobile.Contains(m.gameObjectAnimator)))
            {
                if (gone == null) gone = new List<MobileMapObject>();
                gone.Add(m);
            }
        }
        if (gone != null)
        {
            for (int i = 0; i < gone.Count; i++)
            {
                Live l = live[gone[i]];
                live.Remove(gone[i]);
                if (!l.awarded)
                {
                    // vanished before it arrived: wiped out (or disbanded) -> the other side scores
                    Debug.Log("[CONVOYS] " + l.route.name + " convoy gone from the map before arrival");
                    Lost(l, null);
                }
            }
        }
        // adopt convoys that are on the map but not tracked (after a load)
        Adopt(cm.playerMobile);
        Adopt(cm.otherMobile);
    }

    private static void Adopt(List<GameObjectAnimator> list)
    {
        if (list == null) return;
        for (int i = 0; i < list.Count; i++)
        {
            GameObjectAnimator goa = list[i];
            if (goa == null || goa.mobileMapObject == null || live.ContainsKey(goa.mobileMapObject)) continue;
            string n = goa.mobileMapObject.mobileName;
            if (string.IsNullOrEmpty(n) || !n.StartsWith(Prefix)) continue;
            ConvoyRoute r = RouteOf(n);
            if (r == null) continue;
            Live l = new Live();
            l.mmo = goa.mobileMapObject;
            l.route = r;
            l.startMerchants = Merchants(l.mmo);
            string[] s;
            if (saved.TryGetValue(n, out s) && s.Length >= 4)
            {
                l.awarded = s[2] == "1";
                int.TryParse(s[3], NumberStyles.Integer, CultureInfo.InvariantCulture, out l.startMerchants);
            }
            live[l.mmo] = l;
            Debug.Log("[CONVOYS] tracking " + n + " (" + Merchants(l.mmo) + " merchants, " + (goa.mobileMapObject.currentFaction == 0 ? "ours" : "enemy") + ")");
        }
    }

    private static ConvoyRoute RouteOf(string mobileName)
    {
        ConvoyRoute best = null;
        for (int i = 0; i < routes.Count; i++)
        {
            string p = Prefix + routes[i].name + "-";
            if (mobileName.StartsWith(p) && (best == null || routes[i].name.Length > best.name.Length)) best = routes[i];
        }
        return best;
    }

    private static void Load(string campaignID)
    {
        loadedFor = campaignID;
        routes.Clear();
        string path = "campaign/" + campaignID + "/convoys.txt";
        if (!Utilities.DoesGameFileExist(path)) return;
        string[] lines = AssetLoader.instance.ImportText(path);
        if (lines == null) return;
        for (int i = 0; i < lines.Length; i++)
        {
            string t = lines[i].Trim();
            if (t.Length == 0 || t.StartsWith("//")) continue;
            try
            {
                ConvoyRoute r = new ConvoyRoute();
                JsonUtility.FromJsonOverwrite(t, r);
                if (r.via == null) r.via = new List<string>();
                if (string.IsNullOrEmpty(r.id)) r.id = r.name.ToLower();
                if (r.everyDays < 1) r.everyDays = 1;
                routes.Add(r);
            }
            catch (Exception ex) { Debug.Log("[CONVOYS] bad line " + (i + 1) + ": " + ex.Message); }
        }
        Debug.Log("[CONVOYS] " + routes.Count + " convoy routes loaded for " + campaignID);
    }

    private static void Restore()
    {
        List<string> list = ModWorld.Saved();
        if (list == null) return;
        int n = 0;
        for (int i = 0; i < list.Count; i++)
        {
            string[] a = list[i].Split('|');
            if (a.Length >= 3 && a[0] == "N")
            {
                int v;
                if (int.TryParse(a[2], NumberStyles.Integer, CultureInfo.InvariantCulture, out v)) nextNumber[a[1]] = v;
            }
            else if (a.Length >= 4 && a[0] == "L")
            {
                saved[a[1]] = a;
                n++;
            }
        }
        Debug.Log("[CONVOYS] state restored: " + nextNumber.Count + " route counters, " + n + " convoys at sea");
    }

    public static void Write(List<string> list)
    {
        if (owner == null || CampaignManager.instance == null || owner != CampaignManager.instance.landMapLocations) return;
        foreach (KeyValuePair<string, int> kv in nextNumber) list.Add("N|" + kv.Key + "|" + kv.Value.ToString(CultureInfo.InvariantCulture));
        foreach (Live l in live.Values)
        {
            if (l.mmo != null) list.Add("L|" + l.mmo.mobileName.Replace("|", "/") + "|" + (l.awarded ? "1" : "0") + "|" + l.startMerchants.ToString(CultureInfo.InvariantCulture));
        }
    }

    // ---------- timetable ----------
    public static void Daily()
    {
        if (!ModWorld.Ready()) return;
        Sync();
        if (routes.Count == 0) return;
        CampaignData d = CampaignManager.instance.campaignData;
        DateTime date = CampaignInterface.instance.dateTime.Date;
        if (date == lastDay) return;
        lastDay = date;
        int day = (int)(date - ModWorld.Start(d)).TotalDays;
        for (int i = 0; i < routes.Count; i++)
        {
            ConvoyRoute r = routes[i];
            if (day < r.firstDay || (day - r.firstDay) % r.everyDays != 0) continue;
            int atSea = 0;
            foreach (Live l in live.Values) if (l.route == r && !l.awarded) atSea++;
            if (atSea >= MaxAtSea) { Debug.Log("[CONVOYS] " + r.name + ": " + atSea + " already at sea, none sailed today"); continue; }
            try { Spawn(r); }
            catch (Exception ex) { Debug.LogError("[CONVOYS] " + r.name + " spawn failed: " + ex); }
        }
    }

    private static void Spawn(ConvoyRoute r)
    {
        CampaignManager cm = CampaignManager.instance;
        MapLocation from = cm.GetMapLocationObject(r.from);
        MapLocation to = cm.GetMapLocationObject(r.to);
        if (from == null || to == null) { Debug.Log("[CONVOYS] " + r.name + ": port '" + (from == null ? r.from : r.to) + "' is not in this campaign"); return; }
        if (from.currentFaction != r.faction || to.currentFaction != r.faction)
        {
            Debug.Log("[CONVOYS] " + r.name + " not sailing: " + (from.currentFaction != r.faction ? from.locationName : to.locationName) + " is no longer held by its side");
            return;
        }
        int number;
        if (!nextNumber.TryGetValue(r.id, out number)) number = r.firstNumber;
        string name = Prefix + r.name + "-" + number;
        GameObjectAnimator goa = r.faction == 0 ? SpawnOurs(r, name, from, to) : SpawnEnemy(r, name, from, to);
        if (goa == null) return;
        nextNumber[r.id] = number + 1;
        Live l = new Live();
        l.mmo = goa.mobileMapObject;
        l.route = r;
        l.startMerchants = Merchants(l.mmo);
        live[l.mmo] = l;
        Debug.Log("[CONVOYS] " + name + " sailed from " + from.locationName + " for " + to.locationName + ": " + l.mmo.unitPrefabs.Count + " ships, " + l.startMerchants + " merchants (" + (r.faction == 0 ? "ours" : "enemy") + ")");
        if (r.faction == 0)
        {
            Notify("Convoys", name + " has sailed from " + from.locationName + " for " + to.locationName + " with " + l.startMerchants + " merchant ships. It steers itself; escort it if you can.");
        }
    }

    // our side: a yellow, self-steering group like the RAN forces
    private static GameObjectAnimator SpawnOurs(ConvoyRoute r, string name, MapLocation from, MapLocation to)
    {
        List<string> merchants = Ships(UnitSubType.Merchant);
        List<string> oilers = Ships(UnitSubType.Oiler);
        List<string> escorts = Ships(UnitSubType.Destroyer);
        if (escorts.Count == 0) escorts = Ships(UnitSubType.Destroyer_Escort);
        if (escorts.Count == 0) escorts = Ships(UnitSubType.Light_Cruiser);
        if (merchants.Count == 0 && oilers.Count == 0) { Debug.Log("[CONVOYS] " + r.name + ": no merchant ship classes in service for our side"); return null; }
        List<string> prefabs = new List<string>();
        List<string> cargo = new List<string>();
        int cargoIndex = r.cargo == "fuel" ? 3 : (r.cargo == "troops" ? 0 : 1);
        for (int i = 0; i < r.merchants && merchants.Count > 0; i++)
        {
            string p = merchants[UnityEngine.Random.Range(0, merchants.Count)];
            prefabs.Add(p);
            cargo.Add(CargoString(p, cargoIndex));
        }
        for (int i = 0; i < r.oilers && oilers.Count > 0; i++)
        {
            string p = oilers[UnityEngine.Random.Range(0, oilers.Count)];
            prefabs.Add(p);
            cargo.Add(CargoString(p, 3));
        }
        for (int i = 0; i < r.escorts && escorts.Count > 0; i++)
        {
            prefabs.Add(escorts[UnityEngine.Random.Range(0, escorts.Count)]);
            cargo.Add("0|0|0|0");
        }
        GameObjectAnimator goa = Create(name, prefabs, cargo, from);
        if (goa == null) return null;
        Paint(goa);
        ModAllied.SendTo(goa, ModAllied.Sea(to));
        return goa;
    }

    private static string CargoString(string prefab, int index)
    {
        int[] c = new int[4];
        try
        {
            List<int> cap = EngagementManager.instance.unitDataDictionary[prefab].cargo;
            if (cap != null && cap.Count == 4)
            {
                c[index] = cap[index];
                if (c[index] <= 0) c[index] = index == 0 ? 500 : (index == 3 ? 50 : 1000);
            }
        }
        catch (Exception) { }
        return c[0] + "|" + c[1] + "|" + c[2] + "|" + c[3];
    }

    private static List<string> Ships(UnitSubType type)
    {
        List<string> result = new List<string>();
        List<string> nations = CampaignManager.instance.campaignData.nations0;
        foreach (KeyValuePair<string, UnitListData> item in EngagementManager.instance.unitSeaDictionary)
        {
            if (nations != null && !nations.Contains(item.Value.nation)) continue;
            UnitData u;
            if (!EngagementManager.instance.unitDataDictionary.TryGetValue(item.Key, out u) || u.unitSubtype != type) continue;
            if (!InService(item.Key)) continue;
            result.Add(item.Key);
        }
        return result;
    }

    private static bool InService(string prefab)
    {
        try { return UnitReference.instance == null || UnitReference.instance.IsShipClassAvailable(prefab) == string.Empty; }
        catch (Exception) { return true; }
    }

    private static GameObjectAnimator Create(string name, List<string> prefabs, List<string> cargo, MapLocation at)
    {
        CampaignManager cm = CampaignManager.instance;
        MobileMapObject tf = CampaignAI.instance.newTaskForce;
        CampaignInterface.instance.ClearNewGroupData(tf);
        tf.unitPrefabs = new List<string>();
        for (int i = 0; i < prefabs.Count; i++)
        {
            string p = prefabs[i];
            UnitData u = EngagementManager.instance.unitDataDictionary[p];
            int inst = FreeInstance(p, tf);
            if (inst < 0) continue;
            tf.unitPrefabs.Add(p);
            tf.unitInstances.Add(inst);
            tf.unitDisplayNames.Add((u.namesInClass != null && u.namesInClass.Count > inst) ? u.namesInClass[inst] : u.unitName);
            tf.cellVariables.Add(string.Empty);
            tf.ammunitionRemaining.Add(string.Empty);
            tf.aircraftCooldown.Add(string.Empty);
            tf.cargo.Add(i < cargo.Count ? cargo[i] : "0|0|0|0");
            tf.bombardments.Add(0);
            tf.paint.Add(0);
            tf.speedModifier.Add(1f);
            tf.currentAircraft.Add((u.aircraftTotal != null && u.aircraftTotal.Count > 0) ? cm.SetIntListToString(u.aircraftTotal) : string.Empty);
        }
        if (tf.unitPrefabs.Count == 0) { Debug.Log("[CONVOYS] no free ship names left for " + name); return null; }
        tf.formation = 2;
        tf.formationSpacing = 0;
        tf.mobileName = name;
        tf.customName = true;
        cm.SetMobileMapObjectSensors(tf);
        tf.currentFaction = 0;
        GameObjectAnimator keep = CampaignInterface.instance.currentMapObject;
        GameObjectAnimator goa = CampaignInterface.instance.CreateNewMobileObject(CampaignObjectType.Sea, tf, ModAllied.Sea(at), false, null, string.Empty);
        CampaignInterface.instance.currentMapObject = keep;
        if (goa == null) return null;
        goa.mobileMapObject.mobileName = name;
        goa.mobileMapObject.customName = true;
        return goa;
    }

    private static int FreeInstance(string prefab, MobileMapObject building)
    {
        CampaignManager cm = CampaignManager.instance;
        UnitData u = EngagementManager.instance.unitDataDictionary[prefab];
        int count = (u.namesInClass == null || u.namesInClass.Count <= 0) ? 1 : u.namesInClass.Count;
        List<int> order = new List<int>();
        for (int i = 0; i < count; i++) order.Insert(UnityEngine.Random.Range(0, order.Count + 1), i);
        for (int j = 0; j < order.Count; j++)
        {
            int k = order[j];
            if (cm.IsPlayerShipInstanceAvailable(prefab, k) != -1 || cm.GetGameObjectAnimatorContainingShip(cm.playerMobile, prefab, k) != null) continue;
            bool used = false;
            for (int m = 0; m < building.unitPrefabs.Count; m++) if (building.unitPrefabs[m] == prefab && building.unitInstances[m] == k) used = true;
            if (!used) return k;
        }
        return -1;
    }

    // enemy side: borrow one of the campaign's own Convoy missions for a moment so the AI builds and steers it
    private static GameObjectAnimator SpawnEnemy(ConvoyRoute r, string name, MapLocation from, MapLocation to)
    {
        CampaignAI ai = CampaignAI.instance;
        CampaignManager cm = CampaignManager.instance;
        if (ai == null || ai.seaMissions == null) return null;
        if (!cm.seaNavigationIndexes.ContainsKey(r.from) || !cm.seaNavigationIndexes.ContainsKey(r.to)) { Debug.Log("[CONVOYS] " + r.name + ": no sea waypoint for " + r.from + " or " + r.to); return null; }
        int idx = ai.GetMissionByType(MissionType.Convoy);
        if (idx < 0) { Debug.Log("[CONVOYS] " + r.name + ": this campaign has no Convoy mission for the enemy AI to borrow"); return null; }
        MissionData md = ai.seaMissions[idx];
        string spawn = md.spawnLocation, first = md.firstWaypoint, last = md.lastWaypoint;
        List<string> units = md.units, must = md.mustUseWaypoints;
        bool noCost = md.noCost, aggressive = md.aggressive, construction = md.construction, troops = md.troops, destIsLocation = md.destIsLocation;
        int[] delay = md.delayAIDays;
        int before = cm.otherMobile.Count;
        bool ok = false;
        try
        {
            md.spawnLocation = r.from;
            md.firstWaypoint = r.from;
            md.lastWaypoint = r.to;
            List<string> u = new List<string>();
            for (int i = 0; i < r.escorts; i++) u.Add(i == 0 && r.escorts >= 3 ? "Light_Cruiser" : "Destroyer");
            for (int i = 0; i < r.oilers; i++) u.Add("Oiler");
            for (int i = 0; i < r.merchants; i++) u.Add("Transport");
            md.units = u;
            md.mustUseWaypoints = new List<string>(r.via);
            md.noCost = true;
            md.aggressive = false;
            md.construction = r.cargo != "troops";
            md.troops = r.cargo == "troops";
            md.destIsLocation = true;
            md.delayAIDays = new int[4];
            ok = ai.CreateAIMobileSea(idx, r.to, false);
        }
        finally
        {
            md.spawnLocation = spawn; md.firstWaypoint = first; md.lastWaypoint = last;
            md.units = units; md.mustUseWaypoints = must;
            md.noCost = noCost; md.aggressive = aggressive; md.construction = construction; md.troops = troops; md.destIsLocation = destIsLocation;
            md.delayAIDays = delay;
        }
        if (!ok || cm.otherMobile.Count <= before) { Debug.Log("[CONVOYS] " + r.name + ": the AI could not form the convoy (no merchant classes free?)"); return null; }
        GameObjectAnimator goa = cm.otherMobile[cm.otherMobile.Count - 1];
        if (goa == null || goa.mobileMapObject == null || goa.mobileMapObject.currentFaction != 1) return null;
        goa.mobileMapObject.mobileName = name;
        goa.mobileMapObject.customName = true;
        return goa;
    }

    // ---------- every game minute ----------
    public static void Tick()
    {
        if (!ModWorld.Ready()) return;
        Sync();
        if (live.Count == 0) return;
        CampaignManager cm = CampaignManager.instance;
        List<Live> list = new List<Live>(live.Values);
        for (int i = 0; i < list.Count; i++)
        {
            Live l = list[i];
            MobileMapObject m = l.mmo;
            if (m == null || m.gameObjectAnimator == null) continue;
            GameObjectAnimator goa = m.gameObjectAnimator;
            MapLocation to = cm.GetMapLocationObject(l.route.to);
            if (l.awarded)
            {
                continue;   // an enemy convoy that got through: the AI takes it home
            }
            if (Merchants(m) == 0)
            {
                live.Remove(m);
                Lost(l, goa);
                continue;
            }
            if (to == null) continue;
            bool near = ModAllied.Near(goa, to.gameObjectAnimator.currentMap2DLocation, ArriveKm);
            if (m.currentFaction == 0)
            {
                m.fuelUsedDays = 0f;
                Paint(goa);
                if (to.currentFaction != 0)
                {
                    // destination fell: turn for home
                    MapLocation home = cm.GetMapLocationObject(l.route.from);
                    if (home != null && home.currentFaction == 0 && !ModAllied.Near(goa, home.gameObjectAnimator.currentMap2DLocation, ArriveKm))
                    {
                        if (!goa.isMoving && ++l.idle >= ResendMinutes) { l.idle = 0; ModAllied.SendTo(goa, ModAllied.Sea(home)); }
                    }
                    else if (home != null && home.currentFaction == 0)
                    {
                        live.Remove(m);
                        Notify("Convoys", m.mobileName + " turned back to " + home.locationName + ": " + to.locationName + " has fallen.");
                        CampaignInterface.instance.DestroyMapMobileObject(goa);
                    }
                    continue;
                }
                if (!near || (goa.isMoving && !ModAllied.Near(goa, to.gameObjectAnimator.currentMap2DLocation, 15f)))
                {
                    if (goa.isMoving) l.idle = 0;
                    else if (++l.idle >= ResendMinutes)
                    {
                        l.idle = 0;
                        Debug.Log("[CONVOYS] " + m.mobileName + " stopped short, sent on again");
                        ModAllied.SendTo(goa, ModAllied.Sea(to));
                    }
                    continue;
                }
                Arrived(l, goa, to);
            }
            else if (near)
            {
                // an enemy convoy reached its port: their points
                l.awarded = true;
                int pts = PointsFor(l);
                ModScore.AddConvoy(1, pts);
                Debug.Log("[CONVOYS] enemy " + m.mobileName + " reached " + to.locationName + ": " + Merchants(m) + "/" + l.startMerchants + " merchants, " + pts + " points to the enemy");
                Notify("Convoys", "Intelligence: " + m.mobileName + " has reached " + to.locationName + " (" + Merchants(m) + " of " + l.startMerchants + " merchant ships). " + pts + " points to the " + ModScore.SideName(1) + ".");
            }
        }
    }

    private static int PointsFor(Live l)
    {
        int now = Merchants(l.mmo);
        if (l.startMerchants <= 0) return l.route.points;
        if (now * 2 < l.startMerchants) return Mathf.Max(1, l.route.points / 2);   // more than half lost: half points
        return l.route.points;
    }

    private static void Arrived(Live l, GameObjectAnimator goa, MapLocation to)
    {
        MobileMapObject m = goa.mobileMapObject;
        int[] sum = new int[4];
        for (int i = 0; i < m.cargo.Count; i++)
        {
            string[] a = m.cargo[i].Split('|');
            for (int j = 0; j < 4 && j < a.Length; j++) { int v; if (int.TryParse(a[j], out v)) sum[j] += v; }
            m.cargo[i] = "0|0|0|0";
        }
        to.troops[0] += sum[0];
        to.supplies[0] += sum[1];
        to.engineering[0] += sum[2];
        to.fuel[0] += sum[3];
        int pts = PointsFor(l);
        l.awarded = true;
        live.Remove(m);
        ModScore.AddConvoy(0, pts);
        string text = m.mobileName + " has reached " + to.locationName + " with " + Merchants(m) + " of " + l.startMerchants + " merchant ships.\n\n<b>Delivered:</b> " + sum[0] + " troops, " + sum[1] + " supplies, " + sum[2] + " engineering, " + sum[3] + " fuel.\n<b>Victory points:</b> +" + pts + " to the " + ModScore.SideName(0) + ".";
        if (!string.IsNullOrEmpty(l.route.note)) text += "\n\n<i>" + l.route.note + "</i>";
        Debug.Log("[CONVOYS] " + m.mobileName + " arrived at " + to.locationName + ": +" + pts);
        CampaignInterface.instance.DestroyMapMobileObject(goa);
        Popup("wconvoy_arrived", "Convoy arrived", text);
    }

    private static void Lost(Live l, GameObjectAnimator goa)
    {
        int pts = Mathf.Max(1, l.route.points);
        string name = l.mmo != null ? l.mmo.mobileName : (Prefix + l.route.name);
        if (l.route.faction == 0)
        {
            ModScore.AddConvoy(1, pts);
            if (goa != null && goa.mobileMapObject != null)
            {
                goa.mobileMapObject.mobileName = "Escort of " + name;
                goa.mobileMapObject.customName = true;
            }
            Debug.Log("[CONVOYS] " + name + " lost: " + pts + " points to the enemy");
            Popup("wconvoy_lost", "Convoy lost", "Every merchant ship of " + name + " has been sunk" + (goa != null ? "; the escorts are on their own." : ".") + "\n\n<b>Victory points:</b> +" + pts + " to the " + ModScore.SideName(1) + ".");
        }
        else
        {
            ModScore.AddConvoy(0, pts);
            Debug.Log("[CONVOYS] enemy " + name + " destroyed: " + pts + " points to us");
            Popup("wconvoy_sunk", "Enemy convoy destroyed", "Every merchant ship of the enemy's " + name + " has been sunk before it could reach " + PortName(l.route.to) + ".\n\n<b>Victory points:</b> +" + pts + " to the " + ModScore.SideName(0) + ".");
        }
    }

    private static string PortName(string id)
    {
        MapLocation ml = CampaignManager.instance.GetMapLocationObject(id);
        return ml != null ? ml.locationName : id;
    }

    public static int Merchants(MobileMapObject m)
    {
        if (m == null || m.unitPrefabs == null) return 0;
        int n = 0;
        for (int i = 0; i < m.unitPrefabs.Count; i++)
        {
            UnitData u;
            if (EngagementManager.instance.unitDataDictionary.TryGetValue(m.unitPrefabs[i], out u) && (u.unitSubtype == UnitSubType.Merchant || u.unitSubtype == UnitSubType.Oiler)) n++;
        }
        return n;
    }

    private static void Paint(GameObjectAnimator goa)
    {
        SpriteRenderer sr = goa.GetComponentInChildren<SpriteRenderer>();
        if (sr != null && !(sr.color == (Color)ModAllied.Yellow)) sr.color = ModAllied.Yellow;
    }

    public static int AtSea(int faction)
    {
        int n = 0;
        foreach (Live l in live.Values) if (l.mmo != null && l.mmo.currentFaction == faction && !l.awarded) n++;
        return n;
    }

    private static void Notify(string header, string text)
    {
        Debug.Log("[CONVOYS] " + text);
        try { ModNotify.AddEvent("wconvoy", header, text); } catch (Exception) { }
    }

    // pop-up through the campaign's event box; the event file gives the frame, the text is filled in here
    public static void Popup(string eventName, string header, string text)
    {
        try
        {
            CampaignEvent ce = CampaignEvent.instance;
            if (ce == null) { Notify(header, text); return; }
            string path = "language/campaign/" + CampaignManager.instance.campaignData.campaignID + "/event/" + eventName + ".txt";
            if (!Utilities.DoesGameFileExist(path)) { Notify(header, text); return; }
            ce.CreateEvent(eventName);
            if (ce.headerText != null && !string.IsNullOrEmpty(header)) ce.headerText.text = header.ToUpper();
            if (ce.contentText != null) ce.contentText.text = text;
            try { ModNotify.AddEvent(eventName, header, text); } catch (Exception) { }
        }
        catch (Exception ex) { Debug.Log("[CONVOYS] popup failed: " + ex.Message); Notify(header, text); }
    }
}

public static class ModScore
{
    public static ScoreRules rules;
    private static object owner;
    private static int convoy0, convoy1;          // convoy points, saved
    private static bool warned, ended;             // saved
    private static readonly Dictionary<string, int> startOwner = new Dictionary<string, int>();
    private static int cacheSig = int.MinValue;
    private static int cache0, cache1;

    [Serializable]
    private class LocStart { public string locationID = ""; public int currentFaction; }

    public static bool Active
    {
        get { Sync(); return rules != null; }
    }

    private static void Sync()
    {
        CampaignManager cm = CampaignManager.instance;
        if (cm == null || cm.campaignData == null || cm.landMapLocations == null) { return; }
        if (owner == cm.landMapLocations) return;
        owner = cm.landMapLocations;
        rules = null;
        convoy0 = convoy1 = 0;
        warned = ended = false;
        startOwner.Clear();
        cacheSig = int.MinValue;
        string id = cm.campaignData.campaignID;
        string path = "campaign/" + id + "/score.txt";
        if (Utilities.DoesGameFileExist(path))
        {
            try
            {
                string[] lines = AssetLoader.instance.ImportText(path);
                for (int i = 0; lines != null && i < lines.Length; i++)
                {
                    string t = lines[i].Trim();
                    if (t.Length == 0 || t.StartsWith("//")) continue;
                    ScoreRules r = new ScoreRules();
                    JsonUtility.FromJsonOverwrite(t, r);
                    rules = r;
                    break;
                }
            }
            catch (Exception ex) { Debug.Log("[SCORE] score.txt: " + ex.Message); }
        }
        if (rules == null) return;
        // who held each port at the start of the campaign
        try
        {
            string[] lines = AssetLoader.instance.ImportText("campaign/" + id + "/mapLandLocations.txt");
            for (int i = 0; lines != null && i < lines.Length; i++)
            {
                string t = lines[i].Trim();
                if (t.Length == 0 || t[0] != '{') continue;
                LocStart ls = new LocStart();
                JsonUtility.FromJsonOverwrite(t, ls);
                if (!string.IsNullOrEmpty(ls.locationID)) startOwner[ls.locationID] = ls.currentFaction;
            }
        }
        catch (Exception ex) { Debug.Log("[SCORE] mapLandLocations: " + ex.Message); }
        Restore();
        Debug.Log("[SCORE] scoring on for " + id + ": ends " + EndDate().ToString("d MMM yyyy", CultureInfo.InvariantCulture) + ", " + startOwner.Count + " ports");
    }

    private static void Restore()
    {
        List<string> list = ModWorld.Saved();
        if (list == null) return;
        for (int i = 0; i < list.Count; i++)
        {
            string[] a = list[i].Split('|');
            if (a.Length >= 5 && a[0] == "S")
            {
                int.TryParse(a[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out convoy0);
                int.TryParse(a[2], NumberStyles.Integer, CultureInfo.InvariantCulture, out convoy1);
                warned = a[3] == "1";
                ended = a[4] == "1";
            }
        }
    }

    public static void Write(List<string> list)
    {
        if (owner == null || CampaignManager.instance == null || owner != CampaignManager.instance.landMapLocations) return;
        list.Add("S|" + convoy0.ToString(CultureInfo.InvariantCulture) + "|" + convoy1.ToString(CultureInfo.InvariantCulture) + "|" + (warned ? "1" : "0") + "|" + (ended ? "1" : "0"));
    }

    public static void AddConvoy(int faction, int points)
    {
        Sync();
        if (faction == 0) convoy0 += points; else convoy1 += points;
        cacheSig = int.MinValue;
    }

    public static string SideName(int faction)
    {
        Sync();
        if (rules != null) return faction == 0 ? rules.side0 : rules.side1;
        return faction == 0 ? "player" : "enemy";
    }

    public static DateTime EndDate()
    {
        try { return new DateTime(rules.endYear, rules.endMonth, rules.endDay); }
        catch (Exception) { return new DateTime(1945, 9, 2); }
    }

    private static int Weight(string prefab)
    {
        UnitData u;
        if (!EngagementManager.instance.unitDataDictionary.TryGetValue(prefab, out u)) return 2;
        switch (u.unitSubtype)
        {
            case UnitSubType.Submarine: return rules.submarine;
            case UnitSubType.Destroyer_Escort: return rules.destroyerEscort;
            case UnitSubType.Destroyer: return rules.destroyer;
            case UnitSubType.Light_Cruiser: return rules.lightCruiser;
            case UnitSubType.Heavy_Cruiser: return rules.heavyCruiser;
            case UnitSubType.Battlecruiser: return rules.battlecruiser;
            case UnitSubType.Battleship: return rules.battleship;
            case UnitSubType.Light_Carrier: return rules.lightCarrier;
            case UnitSubType.Aircraft_Carrier: return rules.carrier;
            case UnitSubType.Oiler: return rules.oiler;
            case UnitSubType.Merchant: return rules.merchant;
        }
        return 0;
    }

    // points of each side: ships sunk + ports taken + convoys
    public static void Totals(out int player, out int enemy)
    {
        player = enemy = 0;
        if (!Active) return;
        CampaignManager cm = CampaignManager.instance;
        CampaignData d = cm.campaignData;
        int sig = (d.sunkShipClasses != null ? d.sunkShipClasses.Count : 0) * 7919 + convoy0 * 31 + convoy1;
        for (int i = 0; i < cm.landMapLocations.Count; i++) if (cm.landMapLocations[i] != null) sig = sig * 31 + cm.landMapLocations[i].currentFaction;
        if (sig == cacheSig) { player = cache0; enemy = cache1; return; }
        int p = convoy0, e = convoy1;
        if (d.sunkShipClasses != null && d.factionSunk != null)
        {
            for (int i = 0; i < d.sunkShipClasses.Count && i < d.factionSunk.Count; i++)
            {
                int w = Weight(d.sunkShipClasses[i]);
                if (d.factionSunk[i] == 1) p += w; else if (d.factionSunk[i] == 0) e += w;
            }
        }
        for (int i = 0; i < cm.landMapLocations.Count; i++)
        {
            MapLocation ml = cm.landMapLocations[i];
            int start;
            if (ml == null || !startOwner.TryGetValue(ml.locationID, out start) || start == ml.currentFaction) continue;
            if (ml.currentFaction == 0) p += rules.portPoints; else if (ml.currentFaction == 1) e += rules.portPoints;
        }
        cacheSig = sig; cache0 = p; cache1 = e;
        player = p; enemy = e;
    }

    public static string Breakdown()
    {
        if (!Active) return "";
        CampaignManager cm = CampaignManager.instance;
        CampaignData d = cm.campaignData;
        int s0 = 0, s1 = 0, p0 = 0, p1 = 0;
        if (d.sunkShipClasses != null && d.factionSunk != null)
            for (int i = 0; i < d.sunkShipClasses.Count && i < d.factionSunk.Count; i++)
            {
                int w = Weight(d.sunkShipClasses[i]);
                if (d.factionSunk[i] == 1) s0 += w; else if (d.factionSunk[i] == 0) s1 += w;
            }
        for (int i = 0; i < cm.landMapLocations.Count; i++)
        {
            MapLocation ml = cm.landMapLocations[i];
            int start;
            if (ml == null || !startOwner.TryGetValue(ml.locationID, out start) || start == ml.currentFaction) continue;
            if (ml.currentFaction == 0) p0 += rules.portPoints; else if (ml.currentFaction == 1) p1 += rules.portPoints;
        }
        return rules.side0 + ": " + (s0 + p0 + convoy0) + " (ships sunk " + s0 + ", ports " + p0 + ", convoys " + convoy0 + ")\n" + rules.side1 + ": " + (s1 + p1 + convoy1) + " (ships sunk " + s1 + ", ports " + p1 + ", convoys " + convoy1 + ")";
    }

    // one or two lines for the globe
    public static string Summary()
    {
        if (!Active) return "";
        int p, e;
        Totals(out p, out e);
        DateTime end = EndDate();
        int days = (int)(end - CampaignInterface.instance.dateTime.Date).TotalDays;
        string when = days > 0 ? end.ToString("d MMM yyyy", CultureInfo.InvariantCulture) + ", " + days.ToString("N0", CultureInfo.InvariantCulture) + " days to go" : "the war is over";
        return rules.side0.ToUpper() + " " + p + "   " + rules.side1.ToUpper() + " " + e + "\nThe war ends " + when;
    }

    public static void Daily()
    {
        if (!ModWorld.Ready() || !Active) return;
        CampaignData d = CampaignManager.instance.campaignData;
        if (d.campaignEnded || ended) return;
        DateTime date = CampaignInterface.instance.dateTime.Date;
        DateTime end = EndDate();
        int p, e;
        if (!warned && rules.warnDays > 0 && date >= end.AddDays(-rules.warnDays) && date < end)
        {
            warned = true;
            Totals(out p, out e);
            ModRoutes.Popup("wscore_warn", "The end is in sight", "The war ends on " + end.ToString("d MMMM yyyy", CultureInfo.InvariantCulture) + ", in " + (int)(end - date).TotalDays + " days. The side with more victory points wins.\n\n<b>Standings</b>\n" + Breakdown());
        }
        if (date >= end)
        {
            ended = true;
            Totals(out p, out e);
            string tail = "\n\n<b>Final score, " + end.ToString("d MMMM yyyy", CultureInfo.InvariantCulture) + "</b>\n" + Breakdown();
            Debug.Log("[SCORE] campaign over: " + p + " to " + e);
            d.campaignEnded = true;
            CampaignEvent ce = CampaignEvent.instance;
            ce.CreateEvent(p > e ? "victory" : "defeat");
            if (ce.contentText != null) ce.contentText.text = (p > e ? "The war is over and the " + rules.side0 + " have the better of it at sea." : (p == e ? "The war is over. Neither side could claim the upper hand at sea." : "The war is over and the " + rules.side1 + " had the better of it at sea.")) + tail;
        }
    }
}
