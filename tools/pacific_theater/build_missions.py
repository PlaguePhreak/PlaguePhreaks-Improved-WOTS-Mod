"""AI (Japan) sea missions, nav aids, setup and support files for the pacificwar campaign.
Run after build_pacific.py (reads its graph.json)."""
import json, math, os, sys, shutil

OUT = sys.argv[1]           # .../Override
STOCK = sys.argv[2]         # examplePacific_stock/campaign
g = json.load(open('/tmp/claude-0/test/graph.json'))
camp = os.path.join(OUT, 'campaign', 'pacificwar')
lang = os.path.join(OUT, 'language', 'english', 'campaign', 'pacificwar')


def wp(lat, lon):
    """Nearest open-ocean grid waypoint to a lat/lon."""
    lon = lon + 360 if lon < 0 else lon
    best = None
    for n, la, lo, isloc in g['nodes']:
        if isloc or not n.startswith('G'):
            continue
        lo2 = lo + 360 if lo < 0 else lo
        d = math.hypot(la - lat, (lo2 - lon) * math.cos(math.radians(lat)))
        if best is None or d < best[0]:
            best = (d, n)
    return best[1]


Z = {  # patrol and staging zones
    'offHawaii': wp(22.5, -160), 'northHawaii': wp(27.5, -157.5), 'offMidway': wp(27.5, -177.5),
    'offWake': wp(17.5, 167.5), 'offJohnston': wp(17.5, -167.5), 'offPalmyra': wp(7.5, -162.5),
    'offSanFran': wp(37.5, -127.5), 'offLA': wp(32.5, -122.5), 'offSeattle': wp(47.5, -127.5),
    'offDutch': wp(52.5, -167.5), 'offGuam': wp(12.5, 147.5), 'offMarshalls': wp(12.5, 167.5),
    'offGilberts': wp(2.5, 172.5), 'eastJapan': wp(32.5, 147.5), 'midPacific': wp(27.5, 167.5),
    'offAleutW': wp(47.5, 177.5), 'offCanton': wp(-2.5, -172.5),
}
print(Z)

M = []


def mission(kind, spawn, units, last='', must=None, prohib=None, **kw):
    d = {"missionString": kind, "spawnLocation": spawn, "firstWaypoint": spawn, "lastWaypoint": last,
         "units": units, "mustUseWaypoints": must or ([last] if last and kind == 'Patrol' else []),
         "prohibitedWaypoints": prohib or [], "directPath": kind != 'Patrol',
         "destIsLocation": kind not in ('Patrol', 'Intercept', 'DefendArea', 'PrimaryLost')}
    d.update(kw)
    M.append(json.dumps(d, separators=(',', ':')))


SUB = ["Submarine"]
DD3 = ["Destroyer"] * 3
CRU = ["Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"]
KB = ["Aircraft_Carrier", "Aircraft_Carrier", "Battleship", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer", "Destroyer"]
BB = ["Battleship", "Battleship", "Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"]
pat = dict(patrolDestZone=True, patrolNeighbours=True, aggressive=True, autoRenew=True, noCost=True)

# submarine patrols (the I-boats off Hawaii and the US west coast, Dec 1941)
for z in ('offHawaii', 'northHawaii', 'offHawaii', 'offMidway', 'offSanFran', 'offLA', 'offSeattle', 'offDutch', 'offJohnston', 'offPalmyra'):
    mission('Patrol', 'kwajalein' if z not in ('offSeattle', 'offDutch', 'offSanFran') else 'yokosuka', SUB, Z[z], **pat)
# surface patrols
for z in ('offWake', 'offGuam', 'offMarshalls', 'offGilberts'):
    mission('Patrol', 'truk', DD3, Z[z], **pat)
for z in ('midPacific', 'offWake', 'offMarshalls'):
    mission('Patrol', 'truk', CRU, Z[z], formation=2, **pat)
mission('Patrol', 'yokosuka', CRU, Z['eastJapan'], formation=2, **pat)
mission('Patrol', 'paramushiro', DD3, Z['offAleutW'], **pat)
# intercepts and carrier strike forces
for spawn, units, delay in (('truk', CRU, [0, 1, 0, 1]), ('truk', BB, [0, 1, 1, 1]), ('yokosuka', BB, [1, 1, 0, 1]),
                            ('yokosuka', KB, [1, 1, 1, 3]), ('truk', KB, [1, 1, 1, 3]), ('kwajalein', CRU, [0, 1, 0, 1])):
    mission('Intercept', spawn, units, formation=4 if 'Aircraft_Carrier' in units else 2, aggressive=True, delayAIDays=delay)
# bombardment
for spawn, units in (('kwajalein', CRU), ('truk', BB), ('truk', CRU), ('yokosuka', BB)):
    mission('Bombard', spawn, units, formation=2, aggressive=True, bombard=True, delayAIDays=[0, 1, 1, 1])
# invasions (Wake, Guam, Gilberts, Aleutians, Midway, and later Hawaii)
mission('SubInvasion', 'kwajalein', SUB * 3, aggressive=False, troops=True)
mission('SubInvasion', 'truk', SUB * 3, aggressive=False, troops=True)
mission('SmallInvasion', 'kwajalein', ["Light_Cruiser", "Transport", "Transport", "Destroyer", "Destroyer", "Destroyer"], aggressive=False, troops=True, delayAIDays=[0, 1, 0, 0])
mission('SmallInvasion', 'saipan', ["Heavy_Cruiser", "Transport", "Transport", "Transport", "Destroyer", "Destroyer"], aggressive=False, troops=True, delayAIDays=[0, 1, 0, 0])
mission('SmallInvasion', 'paramushiro', ["Light_Cruiser", "Transport", "Transport", "Destroyer", "Destroyer"], aggressive=False, troops=True, delayAIDays=[0, 1, 0, 1])
mission('SmallInvasion', 'truk', ["Heavy_Cruiser", "Transport", "Transport", "Transport", "Light_Cruiser", "Destroyer", "Destroyer"], aggressive=False, troops=True, delayAIDays=[0, 1, 0, 1])
mission('LargeInvasion', 'truk', ["Battleship", "Heavy_Cruiser", "Heavy_Cruiser", "Transport", "Transport", "Transport", "Transport", "Destroyer", "Destroyer", "Destroyer"], formation=2, aggressive=False, troops=True, delayAIDays=[1, 1, 1, 3])
mission('LargeInvasion', 'yokosuka', ["Aircraft_Carrier", "Battleship", "Heavy_Cruiser", "Transport", "Transport", "Transport", "Transport", "Destroyer", "Destroyer", "Destroyer"], formation=2, aggressive=False, troops=True, delayAIDays=[1, 1, 1, 3])
# fast troop runs (destroyer transports)
mission('FastTroop', 'kwajalein', ["Destroyer"] * 6, aggressive=False, troops=True, delayAIDays=[0, 1, 0, 0])
mission('LargeFastTroop', 'truk', ["Light_Cruiser", "Light_Cruiser"] + ["Destroyer"] * 8, formation=2, aggressive=False, troops=True, delayAIDays=[0, 1, 0, 1])
# convoys (build airfields and ports)
for spawn in ('yokosuka', 'truk', 'truk', 'saipan'):
    mission('Convoy', spawn, ["Light_Cruiser", "Destroyer", "Destroyer", "Oiler", "Oiler", "Transport", "Transport", "Transport"], formation=2, aggressive=False, construction=True, delayAIDays=[0, 1, 0, 0])
# home, defence, last stand
mission('Home', '', [], last='truk', formation=2, aggressive=False)
for spawn in ('truk', 'kwajalein', 'yokosuka'):
    mission('DefendArea', spawn, SUB * 3, formation=2, aggressive=True, noCost=True)
mission('PrimaryLost', 'yokosuka', ["Battleship", "Battleship", "Aircraft_Carrier", "Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"],
        patrolDestZone=True, patrolNeighbours=True, formation=4, aggressive=False, autoRenew=False, noCost=True, delayAIDays=[1, 1, 0, 0])
open(os.path.join(camp, 'sea_missions.txt'), 'w').write('\n'.join(M))

nav = [{"missionString": "PrimaryLost", "mustUseWaypoints": [Z['eastJapan']], "prohibitedWaypoints": []}]
open(os.path.join(camp, 'sea_navigation_aid.txt'), 'w').write('\n'.join(json.dumps(n, separators=(',', ':')) for n in nav))

# copy unchanged support files
for f in ('sea_alts.txt', 'resupply.txt', 'strategicBombing.txt'):
    shutil.copy(os.path.join(STOCK, f), os.path.join(camp, f))
open(os.path.join(camp, 'ai1.txt'), 'w').write(json.dumps(
    {"subPatrol": [Z[k] for k in ('offHawaii', 'northHawaii', 'offMidway', 'offSanFran', 'offLA', 'offWake')], "carrierPatrol": []},
    separators=(',', ':')))

# sea and air units: the mod's full lists from campaign001 (dates in the files decide what is available in Dec 1941)
MODCAMP = '/home/claude/PlaguePhreaks-Improved-WOTS-Mod/Override/campaign/campaign001'
for f in ('seaUnits.txt', 'airUnits.txt'):
    shutil.copy(os.path.join(MODCAMP, f), os.path.join(camp, f))

# setup.txt
sp = os.path.join(camp, 'setup.txt')
s = json.loads(open(sp).read())
s.update({
    "startDate": [0, 0, 6, 8, 12, 1941], "currentDateTime": [0, 0, 6, 8, 12, 1941],
    "nations0": ["usa"], "nations1": ["japan"],
    "aircraft0": ["wildcat", "dauntless", "b17f"], "aircraft1": ["zero", "val", "betty"],
    "unavailableShipClasses": [], "unavailableShipInstanceNames": [],
    "maxAirAt": ["midway"], "maxPortAt": [],
    "mustControl": ["truk", "kwajalein", "saipan", "wake", "guam", "pearlharbor", "midway", "sandiego"],
    "mapZoomLevels": {"x": 0.05, "y": 1},
    "mapOriginXY": [28080, 19680], "mapPixelWidth": 32640, "mapWidthMetres": 32640 * 488.28125,
})
open(sp, 'w').write(json.dumps(s, separators=(',', ':')))

# language files
labels = [("PACIFIC OCEAN", 30, -160, 2.0, True), ("JAPAN", 36.5, 136, 1.0, False), ("UNITED STATES", 40, -118.5, 1.0, False),
          ("HAWAIIAN ISLANDS", 23.8, -160, 0.6, True), ("MARSHALL ISLANDS", 11.5, 169, 0.6, True),
          ("MARIANA ISLANDS", 17, 148.5, 0.6, True), ("CAROLINE ISLANDS", 4, 150, 0.6, True),
          ("ALEUTIAN ISLANDS", 50, -175, 0.6, True), ("GILBERT ISLANDS", -1, 176, 0.6, True), ("BONIN ISLANDS", 29, 144, 0.5, True)]
L = []
for t, lat, lon, size, it in labels:
    lo = lon + 360 if lon < 0 else lon
    L.append(json.dumps({"text": t, "size": {2.0: 0.12, 1.0: 0.07, 0.6: 0.04, 0.5: 0.035}[size], "position": {"x": round((lo - 117) / 136 - 0.5, 4), "y": round((lat + 8) / 68 - 0.5, 4)},
                         "shadow": False, "color": {"r": 255, "g": 255, "b": 255, "a": 160}, "italic": it}, separators=(',', ':')))
open(os.path.join(lang, 'mapLabels.txt'), 'w').write('\n'.join(L))

Y = '<color=#caa809>{}</color>'
obj = f"""
<b><size=18>THE PACIFIC WAR</size></b>

<b>December 8th 1941</b>
Yesterday the Imperial Japanese Navy struck the fleet at {Y.format('PEARL HARBOR')}. Japanese forces are moving on {Y.format('WAKE ISLAND')}, {Y.format('GUAM')} and the Gilbert Islands, and enemy submarines are already off Hawaii and the {Y.format('WEST COAST')}.

Using {Y.format('PEARL HARBOR')} and {Y.format('SAN DIEGO')} as home ports, hold the line, rebuild the fleet and carry the war across the Central Pacific to the enemy fleet base at {Y.format('TRUK')}.


You must:

1) Take control of:
   - {Y.format('TRUK')}
   - {Y.format('KWAJALEIN')}
   - {Y.format('SAIPAN')}

2) Retake or hold {Y.format('WAKE ISLAND')} and {Y.format('GUAM')}

3) Build a rank 5 airfield at {Y.format('MIDWAY')}

4) Maintain control of:
   - {Y.format('PEARL HARBOR')}
   - {Y.format('SAN DIEGO')}
   - {Y.format('MIDWAY')}

All of these must be held at the same time to win the campaign."""
open(os.path.join(lang, 'objectives.txt'), 'w').write(obj)

line = "pacificwar=The Pacific War=8,12,1941=December 1941. Recover from Pearl Harbor, hold Hawaii, Midway and the West Coast, and carry the war across the Central Pacific to Truk.=forceSettings=2,2,2,2,2,2,2,2,2,2"
open(os.path.join(OUT, '..', 'campaigns_line.txt'), 'w').write(line + '\n')
print('missions', len(M))
