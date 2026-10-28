"""Build mapLandLocations, mapLocationNames and seaWaypoints for the pacificwar campaign.

Map: lon 117E -> 253E (107W), lat 8S -> 60N. Map coords -0.5..0.5 both axes, +y = north.
"""
import json, math, os, sys
from PIL import Image

LON0, LAT0, WDEG, HDEG = 117.0, -8.0, 136.0, 68.0
OUT = sys.argv[1]
MASK = Image.open(sys.argv[2]).convert('RGBA')  # alpha 255 = land
MW, MH = MASK.size
mpx = MASK.load()


def lon360(lon):
    return lon + 360 if lon < 0 else lon


def to_map(lat, lon):
    return ((lon360(lon) - LON0) / WDEG - 0.5, (lat - LAT0) / HDEG - 0.5)


def is_land(lat, lon):
    x = int((lon360(lon) - LON0) / WDEG * MW)
    y = int((LAT0 + HDEG - lat) / HDEG * MH)
    if x < 0 or y < 0 or x >= MW or y >= MH:
        return True
    return mpx[x, y][3] > 128


def clear_line(a, b, skip_ends=0.0):
    """True if the straight line a->b (lat,lon) stays on water. skip_ends: fraction ignored at each end."""
    n = max(8, int(math.hypot(a[0] - b[0], lon360(a[1]) - lon360(b[1])) / 0.05))
    for i in range(n + 1):
        t = i / n
        if t < skip_ends or t > 1 - skip_ends:
            continue
        lat = a[0] + (b[0] - a[0]) * t
        lon = lon360(a[1]) + (lon360(b[1]) - lon360(a[1])) * t
        if is_land(lat, lon):
            return False
    return True


# id, display name, lat, lon, faction (0 US, 1 Japan, 2 neutral), port, airfield, troops, createShips
LOCS = [
    # Japan
    ("yokosuka", "YOKOSUKA", 35.28, 139.67, 1, 5, 5, 10000, True),
    ("kure", "KURE", 34.24, 132.55, 1, 5, 3, 4000, True),
    ("sasebo", "SASEBO", 33.16, 129.72, 1, 4, 2, 2000, False),
    ("ominato", "OMINATO", 41.25, 141.15, 1, 2, 2, 1000, False),
    ("paramushiro", "PARAMUSHIRO", 50.40, 156.00, 1, 1, 2, 800, False),
    ("okinawa", "OKINAWA", 26.21, 127.68, 1, 2, 2, 1000, False),
    ("chichijima", "CHICHI JIMA", 27.08, 142.20, 1, 2, 1, 800, False),
    ("iwojima", "IWO JIMA", 24.78, 141.32, 1, 0, 2, 500, False),
    ("marcus", "MARCUS ISLAND", 24.29, 153.98, 1, 0, 1, 300, False),
    ("saipan", "SAIPAN", 15.18, 145.75, 1, 3, 3, 2000, False),
    ("guam", "GUAM", 13.44, 144.79, 0, 1, 0, 550, False),  # ~550 Marines and Insular Force; fell 10 Dec
    ("palau", "PALAU", 7.34, 134.48, 1, 3, 2, 1000, False),
    ("truk", "TRUK", 7.42, 151.78, 1, 5, 4, 6000, True),
    ("ponape", "PONAPE", 6.96, 158.21, 1, 1, 1, 500, False),
    ("eniwetok", "ENIWETOK", 11.50, 162.30, 1, 1, 1, 500, False),
    ("kwajalein", "KWAJALEIN", 8.72, 167.73, 1, 3, 3, 2000, False),
    ("wotje", "WOTJE", 9.45, 170.24, 1, 0, 2, 500, False),
    ("maloelap", "MALOELAP", 8.72, 171.23, 1, 0, 2, 500, False),
    ("jaluit", "JALUIT", 5.92, 169.64, 1, 2, 1, 500, False),
    ("makin", "MAKIN", 3.07, 172.79, 2, 0, 0, 0, False),
    ("wake", "WAKE ISLAND", 19.28, 166.65, 0, 1, 2, 450, False),  # 1st Defense Bn detachment + VMF-211; held to 23 Dec
    # United States
    ("pearlharbor", "PEARL HARBOR", 21.35, -157.97, 0, 3, 1, 10000, True),  # wrecked by the 7 Dec raid
    ("midway", "MIDWAY", 28.21, -177.38, 0, 1, 3, 2000, False),
    ("frenchfrigate", "FRENCH FRIGATE SHOALS", 23.75, -166.20, 0, 0, 0, 200, False),
    ("johnston", "JOHNSTON ISLAND", 16.73, -169.53, 0, 0, 1, 300, False),
    ("palmyra", "PALMYRA", 5.88, -162.08, 0, 1, 1, 300, False),
    ("christmas", "CHRISTMAS ISLAND", 1.87, -157.40, 2, 0, 0, 0, False),
    ("canton", "CANTON ISLAND", -2.80, -171.70, 0, 0, 1, 300, False),
    ("dutchharbor", "DUTCH HARBOR", 53.89, -166.54, 0, 2, 1, 1000, False),
    ("seattle", "SEATTLE", 47.56, -122.63, 0, 4, 3, 3000, True),
    ("sanfrancisco", "SAN FRANCISCO", 37.80, -122.40, 0, 5, 4, 5000, True),
    ("losangeles", "LOS ANGELES", 33.74, -118.27, 0, 3, 3, 3000, False),
    ("sandiego", "SAN DIEGO", 32.70, -117.17, 0, 5, 5, 8000, True),
    # Neutral / unoccupied
    ("attu", "ATTU", 52.90, 173.20, 2, 0, 0, 0, False),
    ("kiska", "KISKA", 51.98, 177.50, 2, 0, 0, 0, False),
    ("adak", "ADAK", 51.88, -176.64, 2, 0, 0, 0, False),
    ("tarawa", "TARAWA", 1.42, 172.98, 2, 0, 0, 0, False),
    ("nauru", "NAURU", -0.53, 166.93, 2, 0, 0, 0, False),
    ("howland", "HOWLAND ISLAND", 0.81, -176.62, 2, 0, 0, 0, False),
]

# helper sea points for narrow waters (name, lat, lon)
HELPERS = [
    ("TokyoBay", 34.90, 139.80),
    ("Bungo", 32.70, 132.30),
    ("Kii", 33.40, 135.20),
    ("Tsushima", 33.60, 129.20),
    ("Tsugaru", 41.45, 141.00),
    ("Sanriku", 39.50, 143.00),
    ("Kyushu", 31.00, 131.60),
    ("PugetSd", 48.25, -124.90),
    ("GoldenGt", 37.70, -123.10),
    ("SanPedro", 33.50, -118.50),
    ("Coronado", 32.55, -117.50),
    ("Unimak", 54.20, -166.80),
    ("Kurils", 49.80, 156.80),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    land, names = [], []
    for lid, name, lat, lon, fac, port, af, troops, cs in LOCS:
        x, y = to_map(lat, lon)
        own = [troops, 0] if fac == 0 else ([0, troops] if fac == 1 else [0, 0])
        sup = [v * 2 for v in own]
        big = 200 if cs else 0
        d = {"locationID": lid, "currentFaction": fac, "locationPosition": {"x": round(x, 4), "y": round(y, 4)}}
        if cs:
            d["createShips"] = True
        d.update({"portLevel": port, "airfieldLevel": af, "aircraftPrefabs": [], "integrity": 100,
                  "troops": own, "supplies": sup,
                  "fuel": [big, 0] if fac == 0 else [0, big], "engineering": [big, 0] if fac == 0 else [0, big],
                  "inTheAir": [0, 0, 0], "destroyedAir": [0, 0, 0]})
        land.append(json.dumps(d, separators=(',', ':')))
        names.append(name)

    # --- sea waypoints: 5 degree grid + helpers + locations
    nodes = []  # (name, lat, lon, radius, isLocation)
    for j, lat in enumerate([-5.5 + 5 * k for k in range(13)]):
        for i, lon in enumerate([119.5 + 5 * k for k in range(27)]):
            # keep only nodes with open water around them
            if any(is_land(lat + dy, lon + dx) for dx in (-0.6, 0, 0.6) for dy in (-0.6, 0, 0.6)):
                continue
            nodes.append(("G%02d_%02d" % (i, j), lat, lon if lon <= 180 else lon - 360, 0.02, False, (i, j)))
    for n, lat, lon in HELPERS:
        nodes.append((n, lat, lon, 0.005, False, None))
    for lid, name, lat, lon, *_ in LOCS:
        nodes.append((lid, lat, lon, 0.002, True, None))

    idx = {n[0]: k for k, n in enumerate(nodes)}
    links = {n[0]: set() for n in nodes}

    def link(a, b):
        links[a].add(b)
        links[b].add(a)

    grid = {n[5]: n for n in nodes if n[5] is not None}
    for (i, j), n in grid.items():
        for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
            m = grid.get((i + di, j + dj))
            if m and clear_line((n[1], n[2]), (m[1], m[2])):
                link(n[0], m[0])

    def dist(a, b):
        dlon = abs(lon360(a[2]) - lon360(b[2]))
        return math.hypot(a[1] - b[1], dlon * math.cos(math.radians((a[1] + b[1]) / 2)))

    # helpers and locations: link to nearest reachable sea nodes (ends may touch land)
    sea = [n for n in nodes if not n[4]]
    for n in nodes:
        if n[5] is not None:
            continue
        cands = sorted((dist(n, m), m) for m in sea if m[0] != n[0])
        got = 0
        for dd, m in cands:
            if dd > 9:
                break
            if clear_line((n[1], n[2]), (m[1], m[2]), skip_ends=0.12 if n[4] else 0.05):
                link(n[0], m[0])
                got += 1
                if got >= (2 if n[4] else 3):
                    break

    # fixed links for narrow waters the grid misses
    for a, b in [("kure", "Bungo"), ("Bungo", "Kyushu"), ("sasebo", "Tsushima"), ("yokosuka", "TokyoBay"),
                 ("ominato", "Tsugaru"), ("Tsugaru", "Sanriku"), ("seattle", "PugetSd"),
                 ("sanfrancisco", "GoldenGt"), ("losangeles", "SanPedro"), ("sandiego", "Coronado"),
                 ("SanPedro", "Coronado"), ("dutchharbor", "Unimak"), ("paramushiro", "Kurils")]:
        link(a, b)

    # connectivity check
    start = "pearlharbor"
    seen, todo = {start}, [start]
    while todo:
        c = todo.pop()
        for m in links[c]:
            if m not in seen:
                seen.add(m)
                todo.append(m)
    unreached = [n[0] for n in nodes if n[0] not in seen]
    lonely = [n[0] for n in nodes if not links[n[0]]]

    # drop sea nodes cut off from the main network (e.g. inner Philippine seas)
    nodes = [n for n in nodes if n[0] in seen or n[4]]
    idx = {n[0]: k for k, n in enumerate(nodes)}
    out = []
    for n in nodes:
        x, y = to_map(n[1], n[2])
        dirs = {"N": [], "S": [], "E": [], "W": []}
        for m in sorted(links[n[0]]):
            mm = nodes[idx[m]]
            mx, my = to_map(mm[1], mm[2])
            dx, dy = mx - x, (my - y)
            r = math.hypot(dx, dy) or 1
            if dy > 0.38 * r: dirs["N"].append(m)
            if dy < -0.38 * r: dirs["S"].append(m)
            if dx > 0.38 * r: dirs["E"].append(m)
            if dx < -0.38 * r: dirs["W"].append(m)
        out.append(json.dumps({"waypointName": n[0], "isLocation": n[4],
                               "pos": ["%.3f" % x, "%.3f" % y, "%.3f" % n[3]],
                               "sNorthWP": dirs["N"], "sSouthWP": dirs["S"], "sEastWP": dirs["E"], "sWestWP": dirs["W"]},
                              separators=(',', ':')))

    camp = os.path.join(OUT, 'campaign', 'pacificwar')
    lang = os.path.join(OUT, 'language', 'english', 'campaign', 'pacificwar')
    os.makedirs(camp, exist_ok=True)
    os.makedirs(lang, exist_ok=True)
    open(os.path.join(camp, 'mapLandLocations.txt'), 'w').write('\n'.join(land))
    open(os.path.join(camp, 'seaWaypoints.txt'), 'w').write('\n'.join(out))
    open(os.path.join(lang, 'mapLocationNames.txt'), 'w').write('\n'.join(names))
    print('locations', len(land), 'waypoints', len(out), 'links', sum(len(v) for v in links.values()) // 2)
    print('unreached', unreached)
    print('no links', lonely)
    on_water = [l[0] for l in LOCS if not is_land(l[2], l[3])]
    print('locations not on drawn land', on_water)
    json.dump({"nodes": [(n[0], n[1], n[2], n[4]) for n in nodes], "links": {k: sorted(v) for k, v in links.items()}},
              open('/tmp/claude-0/test/graph.json', 'w'))


main()
