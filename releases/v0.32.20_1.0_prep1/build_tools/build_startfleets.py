# Writes Override/campaign/<id>/startfleets.txt (read by ModStartFleets, 0.32.20+) for the Pacific War and both Worlds at War
# campaigns. Positions are lat/lon (snapped to the nearest open-sea grid waypoint of that campaign) or a port waypoint name.
# Usage: python3 build_startfleets.py <worldWaypoints.txt> <pacificWaypoints.txt> <outOverrideDir>
import json, math, os, sys

MAPS = {'world': (260.0, -90.0, 360.0, 180.0), 'pacific': (117.0, -8.0, 136.0, 68.0)}

def lon360(lon, lon0):
    while lon < lon0: lon += 360
    while lon >= lon0 + 360: lon -= 360
    return lon

def load(path):
    return [json.loads(l) for l in open(path, encoding='utf-8-sig') if l.strip().startswith('{')]

def snap(wps, mp, where):
    if isinstance(where, str):
        if not any(w['waypointName'] == where for w in wps): raise SystemExit('no waypoint ' + where)
        return where
    lat, lon = where; lon0, lat0, wd, hd = mp
    x, y = (lon360(lon, lon0) - lon0) / wd - 0.5, (lat - lat0) / hd - 0.5
    if not (-0.5 <= x <= 0.5 and -0.5 <= y <= 0.5): return None
    best = min((w for w in wps if not w['isLocation']), key=lambda w: (float(w['pos'][0]) - x) ** 2 + (float(w['pos'][1]) - y) ** 2)
    return best['waypointName']

# Kido Butai: Akagi, Kaga, Soryu and Hiryu only exist with the CTM pack; '?' makes them optional (left out when CTM is not installed).
# (name, at, to, formation, ships). at/to: (lat, lon) or a port id. Ships: class:ship (a free ship of the class is used if the name is not found).
US_PACIFIC = [
    ("Enterprise Carrier Force", (22.0, -164.5), None, 12, ["yorktown:enterprise", "northampton:northampton", "northampton:chester", "pensacola:salt lake city",
        "porter:balch", "gridley:maury", "gridley:craven", "benham:benham", "benham:ellet", "mahan:dunlap"]),
    ("Lexington Carrier Force", (24.5, -172.0), None, 12, ["lexington:lexington", "northampton:chicago", "portland:portland", "new_orleans:astoria",
        "porter:porter", "mahan:drayton", "mahan:flusser", "mahan:lamson", "mahan:mahan"]),
    ("Saratoga Carrier Force", "sandiego", None, 12, ["lexington:saratoga", "farragut:dewey", "farragut:macdonough", "farragut:worden"]),
    ("Pearl Harbor Cruiser Force", (20.6, -158.2), None, 17, ["new_orleans:minneapolis", "brooklyn:phoenix", "brooklyn:st. louis", "omaha:detroit",
        "farragut:aylwin", "farragut:dale", "farragut:monaghan", "porter:phelps"]),
    ("Asiatic Fleet", (10.4, 122.3), None, 13, ["northampton:houston", "omaha:marblehead", "clemson:paul jones", "clemson:john d. ford", "clemson:pope", "clemson:peary"]),
    ("", (19.6, 166.2), None, 0, ["tambor:tambor"]),
    ("", (19.0, 167.2), None, 0, ["tambor:triton"]),
]
US_ATLANTIC = [
    ("Iceland Battle Force", "reykjavik", None, 17, ["new_mexico:new mexico", "new_mexico:mississippi", "new_mexico:idaho", "wichita:wichita", "new_orleans:tuscaloosa",
        "gleaves:gleaves", "gleaves:niblack", "benson:benson", "benson:mayo"]),
    ("Yorktown Carrier Force", "norfolk", None, 12, ["yorktown:yorktown", "ranger42:ranger", "sims:sims", "sims:hammann", "sims:anderson", "sims:russell"]),
    ("Wasp Carrier Force", "bermuda", None, 12, ["wasp:wasp", "gleaves:livermore", "gleaves:kearny"]),
    ("North Carolina Battle Force", "norfolk", None, 17, ["north_carolina:north carolina", "north_carolina:washington", "brooklyn:savannah", "benson:madison", "benson:lansdale"]),
    ("Australian Squadron", "sydney", None, 9, ["kent:australia", "kent:canberra", "amphion:perth", "amphion:hobart"]),
]
JAPAN = [
    ("Kido Butai", (31.0, -158.0), "kure", 15, ["?ctm_akagi42:akagi", "?ctm_kaga:kaga", "?ctm_soryu:soryu", "?ctm_hiryu:hiryu", "shokaku:shokaku", "shokaku:zuikaku", "kongo:hiei", "kongo:kirishima", "tone:tone", "tone:chikuma", "nagara:abukuma",
        "kagero:tanikaze", "kagero:urakaze", "kagero:isokaze", "kagero:hamakaze", "kagero:kagero"]),
    ("Southern Force", (7.5, 105.5), None, 17, ["kongo:kongo", "kongo:haruna", "takao:atago", "takao:takao", "asashio:asashio", "asashio:oshio", "shiratsuyu:shiratsuyu", "shiratsuyu:shigure"]),
    ("Malaya Cruiser Force", (6.8, 102.8), None, 13, ["takao:chokai", "mogami:mogami", "mogami:mikuma", "mogami:suzuya", "mogami:kumano", "sendai:sendai",
        "fubuki:fubuki", "fubuki:shirayuki", "fubuki:hatsuyuki", "fubuki:murakumo"]),
    ("Philippines Force", (21.0, 121.5), None, 13, ["myoko:ashigara", "kuma:kuma", "nagara:natori", "akatsuki:ikazuchi", "akatsuki:inazuma", "hatsuharu:hatsuharu"]),
    ("Ryujo Carrier Force", (7.0, 128.5), None, 12, ["ryujo:ryujo", "myoko:myoko", "myoko:nachi", "myoko:haguro", "sendai:jintsu", "shiratsuyu:yudachi", "shiratsuyu:murasame"]),
    ("Main Body", "kure", None, 17, ["nagato:nagato", "nagato:mutsu", "fuso:fuso", "fuso:yamashiro", "ise:ise", "ise:hyuga", "hosho:hosho", "akatsuki:akatsuki", "akatsuki:hibiki"]),
    ("Wake Invasion Force", "kwajalein", None, 13, ["yubari:yubari", "tenryu:tenryu", "tenryu:tatsuta", "mutsuki:mutsuki", "mutsuki:kisaragi", "mutsuki:yayoi", "mutsuki:mochizuki"]),
    ("", (21.8, -157.2), None, 0, ["type_b1:i-15"]),
    ("", (20.8, -156.8), None, 0, ["type_b1:i-17"]),
    ("", (21.6, -158.9), None, 0, ["type_b1:i-19"]),
]

def write(out, cid, wps, mp, forces):
    lines = ["// Historical start fleets, 8 December 1941 (read by ModStartFleets in 0.32.20+, new campaigns only).",
             "// One task force per line: name (empty = named after its ship), at (waypoint), to (waypoint, optional), formation, ships (class:ship).",
             "// If a ship name is not found in its class, the first free ship of that class is used instead (see the [STARTFLEET] log lines)."]
    n = 0
    for name, at, to, form, ships in forces:
        a = snap(wps, mp, at)
        if a is None: continue
        d = {"name": name, "at": a, "to": snap(wps, mp, to) if to else "", "formation": form, "ships": ships}
        lines.append(json.dumps(d, ensure_ascii=False)); n += 1
    p = os.path.join(out, 'campaign', cid); os.makedirs(p, exist_ok=True)
    open(os.path.join(p, 'startfleets.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(cid, n, 'task forces')

world, pac = load(sys.argv[1]), load(sys.argv[2])
out = sys.argv[3]
write(out, 'wawallies', world, MAPS['world'], US_PACIFIC + US_ATLANTIC)
write(out, 'wawaxis', world, MAPS['world'], JAPAN)
write(out, 'pacificwar', pac, MAPS['pacific'], US_PACIFIC)
