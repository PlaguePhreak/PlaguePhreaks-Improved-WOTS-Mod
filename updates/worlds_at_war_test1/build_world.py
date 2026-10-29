"""Build the two Worlds at War campaigns (wawallies, wawaxis) as Override data.

Usage: python3 build_world.py <out Override dir> <maps dir from render_world.py> <stock examplePacific campaign dir> <mod campaign001 dir> <pacific Override dir>
Map: whole world, 100W eastwards round to 100W, pole to pole. Map coords -0.5..0.5, +y = north. 240 px per degree.
"""
import json, math, os, sys, shutil
from PIL import Image

OUT, MAPS, STOCK, MODCAMP, PAC = sys.argv[1:6]
LON0, LAT0, WDEG, HDEG = 260.0, -90.0, 360.0, 180.0
MASK = Image.open(os.path.join(MAPS, 'worldWatermask.png')).convert('RGBA')
MW, MH = MASK.size
mpx = MASK.load()
START = [0, 0, 6, 8, 12, 1941]


def lon360(lon):
    while lon < LON0: lon += 360
    while lon >= LON0 + 360: lon -= 360
    return lon


def to_map(lat, lon):
    return ((lon360(lon) - LON0) / WDEG - 0.5, (lat - LAT0) / HDEG - 0.5)


def is_land(lat, lon):
    x = int((lon360(lon) - LON0) / WDEG * MW) % MW
    y = int((LAT0 + HDEG - lat) / HDEG * MH)
    if y < 0 or y >= MH:
        return True
    return mpx[x, y][3] > 128


def clear_line(a, b, skip_ends=0.0):
    la0, lo0 = a[0], lon360(a[1]); la1, lo1 = b[0], lon360(b[1])
    if lo1 - lo0 > 180: lo1 -= 360
    if lo0 - lo1 > 180: lo1 += 360
    n = max(8, int(math.hypot(la1 - la0, lo1 - lo0) / 0.05))
    for i in range(n + 1):
        t = i / n
        if t < skip_ends or t > 1 - skip_ends:
            continue
        if is_land(la0 + (la1 - la0) * t, lo0 + (lo1 - lo0) * t):
            return False
    return True


# ------------------------------------------------------------------ locations
# id, name, lat, lon, side (A = Allies, X = Axis, N = neutral), port, airfield, troops, shipyard
L = [
    # --- Pacific: Japan and mandates
    ("yokosuka", "YOKOSUKA", 35.28, 139.67, 'X', 5, 5, 10000, True),
    ("kure", "KURE", 34.24, 132.55, 'X', 5, 3, 4000, True),
    ("sasebo", "SASEBO", 33.16, 129.72, 'X', 4, 2, 2000, False),
    ("ominato", "OMINATO", 41.25, 141.15, 'X', 2, 2, 1000, False),
    ("paramushiro", "PARAMUSHIRO", 50.40, 156.00, 'X', 1, 2, 800, False),
    ("okinawa", "OKINAWA", 26.21, 127.68, 'X', 2, 2, 1000, False),
    ("takao", "TAKAO", 22.62, 120.27, 'X', 3, 3, 2000, False),
    ("chichijima", "CHICHI JIMA", 27.08, 142.20, 'X', 2, 1, 800, False),
    ("iwojima", "IWO JIMA", 24.78, 141.32, 'X', 0, 2, 500, False),
    ("marcus", "MARCUS ISLAND", 24.29, 153.98, 'X', 0, 1, 300, False),
    ("saipan", "SAIPAN", 15.18, 145.75, 'X', 3, 3, 2000, False),
    ("palau", "PALAU", 7.34, 134.48, 'X', 3, 2, 1000, False),
    ("truk", "TRUK", 7.42, 151.78, 'X', 5, 4, 6000, True),
    ("ponape", "PONAPE", 6.96, 158.21, 'X', 1, 1, 500, False),
    ("kwajalein", "KWAJALEIN", 8.72, 167.73, 'X', 3, 3, 2000, False),
    ("jaluit", "JALUIT", 5.92, 169.64, 'X', 2, 1, 500, False),
    ("shanghai", "SHANGHAI", 31.23, 121.49, 'X', 3, 2, 3000, False),
    ("hainan", "HAINAN", 20.02, 110.35, 'X', 2, 2, 1500, False),
    ("camranh", "CAM RANH BAY", 11.92, 109.17, 'X', 3, 2, 2000, False),
    ("saigon", "SAIGON", 10.76, 106.70, 'X', 3, 2, 2000, False),
    # --- Pacific: Allies
    ("guam", "GUAM", 13.44, 144.79, 'A', 1, 0, 550, False),
    ("wake", "WAKE ISLAND", 19.28, 166.65, 'A', 1, 2, 450, False),
    ("pearlharbor", "PEARL HARBOR", 21.35, -157.97, 'A', 5, 4, 10000, True),
    ("midway", "MIDWAY", 28.21, -177.38, 'A', 1, 3, 2000, False),
    ("johnston", "JOHNSTON ISLAND", 16.73, -169.53, 'A', 0, 1, 300, False),
    ("palmyra", "PALMYRA", 5.88, -162.08, 'A', 1, 1, 300, False),
    ("canton", "CANTON ISLAND", -2.80, -171.70, 'A', 0, 1, 300, False),
    ("dutchharbor", "DUTCH HARBOR", 53.89, -166.54, 'A', 2, 1, 1000, False),
    ("seattle", "SEATTLE", 47.56, -122.63, 'A', 4, 3, 3000, True),
    ("sanfrancisco", "SAN FRANCISCO", 37.80, -122.40, 'A', 5, 4, 5000, True),
    ("sandiego", "SAN DIEGO", 32.70, -117.17, 'A', 5, 5, 8000, True),
    ("manila", "MANILA", 14.58, 120.97, 'A', 4, 3, 6000, False),
    ("davao", "DAVAO", 7.07, 125.61, 'A', 1, 1, 500, False),
    ("hongkong", "HONG KONG", 22.28, 114.16, 'A', 3, 1, 2000, False),
    ("singapore", "SINGAPORE", 1.26, 103.84, 'A', 5, 4, 8000, True),
    ("batavia", "BATAVIA", -6.10, 106.80, 'A', 3, 2, 2000, False),
    ("surabaya", "SURABAYA", -7.20, 112.73, 'A', 4, 2, 3000, False),
    ("balikpapan", "BALIKPAPAN", -1.27, 116.83, 'A', 2, 1, 800, False),
    ("ambon", "AMBON", -3.70, 128.18, 'A', 1, 1, 500, False),
    ("darwin", "DARWIN", -12.46, 130.84, 'A', 3, 3, 3000, False),
    ("portmoresby", "PORT MORESBY", -9.44, 147.18, 'A', 2, 2, 1500, False),
    ("rabaul", "RABAUL", -4.20, 152.17, 'A', 2, 2, 1400, False),
    ("tulagi", "TULAGI", -9.10, 160.15, 'A', 1, 0, 200, False),
    ("noumea", "NOUMEA", -22.27, 166.44, 'A', 3, 2, 2000, False),
    ("suva", "SUVA", -18.14, 178.44, 'A', 2, 2, 1500, False),
    ("pagopago", "PAGO PAGO", -14.28, -170.69, 'A', 2, 1, 800, False),
    ("brisbane", "BRISBANE", -27.38, 153.17, 'A', 4, 3, 4000, True),
    ("sydney", "SYDNEY", -33.85, 151.23, 'A', 5, 4, 6000, True),
    ("melbourne", "MELBOURNE", -37.85, 144.93, 'A', 4, 2, 3000, False),
    ("fremantle", "FREMANTLE", -32.05, 115.74, 'A', 4, 2, 2500, False),
    ("auckland", "AUCKLAND", -36.84, 174.77, 'A', 3, 2, 2000, False),
    ("townsville", "TOWNSVILLE", -19.25, 146.82, 'A', 2, 3, 1500, False),
    # --- Indian Ocean
    ("colombo", "COLOMBO", 6.94, 79.84, 'A', 4, 3, 4000, False),
    ("trincomalee", "TRINCOMALEE", 8.57, 81.23, 'A', 4, 2, 2000, False),
    ("bombay", "BOMBAY", 18.95, 72.84, 'A', 5, 3, 5000, True),
    ("calcutta", "CALCUTTA", 22.55, 88.33, 'A', 3, 2, 3000, False),
    ("rangoon", "RANGOON", 16.77, 96.17, 'A', 2, 2, 1500, False),
    ("portblair", "PORT BLAIR", 11.67, 92.75, 'A', 1, 1, 300, False),
    ("aden", "ADEN", 12.79, 45.03, 'A', 3, 2, 2000, False),
    ("mombasa", "MOMBASA", -4.06, 39.67, 'A', 3, 2, 1500, False),
    ("durban", "DURBAN", -29.87, 31.03, 'A', 4, 2, 2000, False),
    ("capetown", "CAPE TOWN", -33.90, 18.42, 'A', 5, 3, 3000, True),
    ("diegosuarez", "DIEGO SUAREZ", -12.28, 49.29, 'X', 2, 1, 800, False),
    ("portlouis", "PORT LOUIS", -20.16, 57.50, 'A', 1, 1, 300, False),
    # --- Atlantic, Europe and the Mediterranean
    ("scapaflow", "SCAPA FLOW", 58.90, -3.05, 'A', 5, 3, 5000, True),
    ("rosyth", "ROSYTH", 56.02, -3.44, 'A', 4, 2, 2000, True),
    ("liverpool", "LIVERPOOL", 53.40, -3.00, 'A', 4, 2, 3000, False),
    ("plymouth", "PLYMOUTH", 50.37, -4.14, 'A', 4, 3, 3000, True),
    ("portsmouth", "PORTSMOUTH", 50.80, -1.09, 'A', 4, 3, 3000, True),
    ("gibraltar", "GIBRALTAR", 36.14, -5.35, 'A', 4, 3, 3000, False),
    ("malta", "MALTA", 35.90, 14.52, 'A', 4, 4, 3000, False),
    ("alexandria", "ALEXANDRIA", 31.20, 29.92, 'A', 5, 3, 6000, False),
    ("haifa", "HAIFA", 32.82, 34.99, 'A', 2, 2, 1000, False),
    ("freetown", "FREETOWN", 8.49, -13.23, 'A', 3, 1, 1500, False),
    ("reykjavik", "REYKJAVIK", 64.15, -21.94, 'A', 3, 3, 2000, False),
    ("murmansk", "MURMANSK", 68.97, 33.08, 'A', 3, 2, 3000, False),
    ("archangel", "ARCHANGEL", 64.54, 40.52, 'A', 2, 1, 1500, False),
    ("halifax", "HALIFAX", 44.65, -63.57, 'A', 4, 3, 3000, True),
    ("stjohns", "ST JOHN'S", 47.56, -52.71, 'A', 2, 2, 1000, False),
    ("newyork", "NEW YORK", 40.65, -74.02, 'A', 5, 4, 8000, True),
    ("norfolk", "NORFOLK", 36.95, -76.33, 'A', 5, 5, 8000, True),
    ("charleston", "CHARLESTON", 32.78, -79.93, 'A', 3, 2, 2000, False),
    ("bermuda", "BERMUDA", 32.30, -64.78, 'A', 2, 2, 800, False),
    ("guantanamo", "GUANTANAMO", 19.90, -75.15, 'A', 3, 2, 1500, False),
    ("sanjuan", "SAN JUAN", 18.47, -66.11, 'A', 3, 2, 1500, False),
    ("trinidad", "TRINIDAD", 10.65, -61.52, 'A', 2, 2, 1000, False),
    ("colon", "COLON", 9.36, -79.90, 'A', 3, 3, 3000, False),
    ("balboa", "BALBOA", 8.95, -79.57, 'A', 3, 3, 3000, False),
    ("wilhelmshaven", "WILHELMSHAVEN", 53.52, 8.11, 'X', 5, 3, 5000, True),
    ("kiel", "KIEL", 54.32, 10.14, 'X', 5, 2, 4000, True),
    ("bergen", "BERGEN", 60.39, 5.32, 'X', 3, 2, 2000, False),
    ("trondheim", "TRONDHEIM", 63.43, 10.40, 'X', 3, 2, 2000, False),
    ("narvik", "NARVIK", 68.44, 17.43, 'X', 2, 1, 1500, False),
    ("brest", "BREST", 48.39, -4.49, 'X', 4, 3, 3000, False),
    ("lorient", "LORIENT", 47.75, -3.37, 'X', 3, 1, 1500, False),
    ("stnazaire", "ST NAZAIRE", 47.27, -2.20, 'X', 4, 1, 1500, False),
    ("bordeaux", "BORDEAUX", 44.84, -0.58, 'X', 2, 1, 1000, False),
    ("toulon", "TOULON", 43.12, 5.93, 'X', 5, 2, 3000, False),
    ("laspezia", "LA SPEZIA", 44.10, 9.82, 'X', 5, 3, 4000, True),
    ("naples", "NAPLES", 40.84, 14.25, 'X', 4, 3, 3000, False),
    ("taranto", "TARANTO", 40.47, 17.24, 'X', 5, 3, 5000, True),
    ("messina", "MESSINA", 38.19, 15.55, 'X', 2, 2, 1000, False),
    ("tripoli", "TRIPOLI", 32.90, 13.18, 'X', 3, 3, 3000, False),
    ("benghazi", "BENGHAZI", 32.12, 20.07, 'X', 2, 2, 2000, False),
    ("piraeus", "PIRAEUS", 37.94, 23.65, 'X', 3, 2, 2000, False),
    ("crete", "CRETE", 35.34, 25.14, 'X', 2, 3, 2000, False),
    ("rhodes", "RHODES", 36.44, 28.23, 'X', 2, 2, 1000, False),
    ("dakar", "DAKAR", 14.69, -17.44, 'X', 4, 2, 3000, False),
    ("casablanca", "CASABLANCA", 33.60, -7.62, 'X', 4, 2, 3000, False),
    ("oran", "ORAN", 35.71, -0.64, 'X', 3, 2, 2000, False),
    ("bizerte", "BIZERTE", 37.27, 9.87, 'X', 3, 2, 2000, False),
    # --- neutral
    ("lisbon", "LISBON", 38.70, -9.14, 'N', 0, 0, 0, False),
    ("azores", "AZORES", 38.65, -27.22, 'N', 0, 0, 0, False),
    ("ferrol", "FERROL", 43.48, -8.24, 'N', 0, 0, 0, False),
    ("canaries", "CANARY ISLANDS", 28.13, -15.43, 'N', 0, 0, 0, False),
    ("capeverde", "CAPE VERDE", 14.92, -23.51, 'N', 0, 0, 0, False),
    ("gothenburg", "GOTHENBURG", 57.70, 11.97, 'N', 0, 0, 0, False),
    ("recife", "RECIFE", -8.05, -34.87, 'N', 0, 0, 0, False),
    ("riodejaneiro", "RIO DE JANEIRO", -22.90, -43.17, 'N', 0, 0, 0, False),
    ("montevideo", "MONTEVIDEO", -34.90, -56.16, 'N', 0, 0, 0, False),
    ("buenosaires", "BUENOS AIRES", -34.60, -58.37, 'N', 0, 0, 0, False),
    ("valparaiso", "VALPARAISO", -33.05, -71.62, 'N', 0, 0, 0, False),
    ("callao", "CALLAO", -12.05, -77.14, 'N', 0, 0, 0, False),
    ("acapulco", "ACAPULCO", 16.85, -99.88, 'N', 0, 0, 0, False),
    ("veracruz", "VERACRUZ", 19.19, -96.14, 'N', 0, 0, 0, False),
    ("tarawa", "TARAWA", 1.42, 172.98, 'N', 0, 0, 0, False),
    ("nauru", "NAURU", -0.53, 166.93, 'N', 0, 0, 0, False),
    ("attu", "ATTU", 52.90, 173.20, 'N', 0, 0, 0, False),
    ("kiska", "KISKA", 51.98, 177.50, 'N', 0, 0, 0, False),
    ("tahiti", "TAHITI", -17.53, -149.57, 'A', 1, 0, 200, False),
]

# helper sea points for narrow waters (name, lat, lon)
HELPERS = [
    ("TokyoBay", 34.90, 139.80), ("Bungo", 32.70, 132.30), ("Kii", 33.40, 135.20), ("Tsushima", 33.60, 129.20),
    ("Tsugaru", 41.45, 141.00), ("Kyushu", 31.00, 131.60), ("Formosa", 24.50, 122.50), ("Luzon", 20.00, 121.50),
    ("Tonkin", 18.50, 108.00), ("SChina", 15.00, 114.00), ("Malacca", 3.00, 100.50), ("Sunda", -6.50, 105.00),
    ("Lombok", -9.00, 115.80), ("Makassar", -2.50, 118.50), ("Banda", -5.50, 128.00), ("Torres", -10.20, 143.50),
    ("Coral", -13.00, 150.00), ("Bass", -39.50, 146.50), ("Cook", -41.20, 174.50),
    ("PugetSd", 48.25, -124.90), ("GoldenGt", 37.70, -123.10), ("Coronado", 32.55, -117.50), ("Unimak", 54.20, -166.80),
    ("Kurils", 49.80, 156.80), ("Oahu", 21.20, -158.40), ("Panama", 8.70, -79.40), ("Colon2", 9.60, -79.90),
    ("Windward", 19.90, -73.80), ("Florida", 24.50, -80.50), ("Chesapeake", 36.95, -75.60), ("Sandy", 40.40, -73.60),
    ("Fundy", 44.40, -63.20), ("Avalon", 47.20, -52.30), ("Denmark", 66.00, -27.00), ("Faroe", 61.50, -4.00),
    ("Pentland", 58.90, -2.50), ("Forth", 56.10, -2.60), ("Irish", 53.60, -4.00), ("Channel", 50.20, -3.50),
    ("Dover", 50.60, 0.80), ("Spithead", 50.60, -1.10), ("Ushant", 48.40, -5.20), ("Biscay", 46.50, -3.50),
    ("Gironde", 45.50, -1.50), ("Finisterre", 43.30, -9.50), ("Tagus", 38.60, -9.50), ("Straits", 36.00, -5.60),
    ("Alboran", 36.00, -2.50), ("Lion", 42.80, 5.00), ("Ligurian", 43.60, 9.00), ("Tyrrhenian", 40.00, 12.50),
    ("Sicily", 37.00, 12.00), ("Ionian", 37.50, 18.00), ("Otranto", 40.00, 18.80), ("Aegean", 37.00, 25.00),
    ("Levant", 33.50, 31.50), ("Sirte", 33.00, 17.00), ("Cyrenaica", 33.00, 21.00), ("Nile", 31.80, 29.50),
    ("Jade", 53.80, 7.80), ("Skagerrak", 57.80, 9.50), ("Kattegat", 56.80, 11.60), ("Bergen2", 60.30, 4.60),
    ("Trond", 63.60, 9.00), ("Vest", 68.20, 14.00), ("Barents", 70.50, 34.00), ("White", 65.50, 38.00),
    ("Kola", 69.60, 33.50), ("Hormuz", 26.50, 56.50), ("Mandeb", 12.60, 44.00), ("Hooghly", 21.00, 88.50),
    ("Martaban", 15.80, 96.00), ("Andaman", 11.50, 93.50), ("Palk", 7.50, 80.50), ("Arabian", 18.50, 71.50),
    ("Mozambique", -16.00, 42.00), ("Agulhas", -35.50, 19.50), ("Natal", -30.50, 32.00), ("Mombasa2", -4.20, 40.20),
    ("Dakar2", 14.60, -17.90), ("Casa", 33.70, -8.20), ("Freetown2", 8.30, -13.80), ("Recife2", -8.00, -34.30),
    ("Plate", -35.20, -55.50), ("Rio", -23.20, -42.80), ("Valpo", -33.00, -72.20), ("Lima", -12.20, -77.80),
    ("Moresby", -9.90, 147.00), ("Rabaul2", -4.00, 152.60), ("Darwin2", -12.00, 130.50), ("Fremantle2", -32.20, 115.20),
    ("PortJackson", -33.80, 151.60), ("Moreton", -27.20, 153.60), ("Hauraki", -36.50, 175.20), ("Suva2", -18.30, 178.80),
    ("Noumea2", -22.50, 166.20), ("Manila2", 14.50, 120.50), ("Davao2", 6.80, 125.80), ("HK", 22.10, 114.40),
    ("Yangtze", 31.00, 122.40), ("Hainan2", 19.80, 111.00), ("Camranh2", 12.00, 109.60), ("Saigon2", 10.20, 107.20),
    ("Surabaya2", -7.00, 113.00), ("Batavia2", -5.80, 106.70), ("Balik", -1.20, 117.30), ("Ambon2", -3.60, 128.50),
    ("Ceylon", 7.00, 80.50), ("Trinco", 8.60, 81.70), ("Blair", 11.70, 93.00), ("Aden2", 12.60, 45.30),
    ("Haifa2", 32.80, 34.70), ("Piraeus2", 37.80, 23.40), ("Heraklion", 35.50, 25.20), ("Rhodes2", 36.30, 28.50),
    ("Benghazi2", 32.30, 20.00), ("Tripoli2", 33.10, 13.20), ("Bizerte2", 37.40, 9.90), ("Oran2", 35.90, -0.70),
    ("Taranto2", 40.30, 17.30), ("Naples2", 40.70, 14.10), ("Spezia", 44.00, 9.70), ("Toulon2", 42.90, 6.00),
    ("Messina2", 38.30, 15.70), ("Halifax2", 44.50, -63.40), ("Charleston2", 32.60, -79.70), ("Bermuda2", 32.20, -64.60),
    ("Gitmo", 19.80, -75.20), ("SanJuan2", 18.60, -66.10), ("Trinidad2", 10.80, -61.30), ("Liverpool2", 53.50, -3.40),
    ("Plymouth2", 50.20, -4.20), ("Rosyth2", 56.10, -3.00), ("Scapa", 58.95, -3.20), ("Reyk", 64.20, -22.40),
    ("Arch", 64.70, 40.00), ("Murm", 69.20, 33.50), ("Narvik2", 68.40, 16.00), ("Kiel2", 54.50, 10.30),
    ("Wilh", 53.70, 8.10), ("Brest2", 48.40, -4.80), ("Lorient2", 47.60, -3.40), ("Nazaire", 47.10, -2.40),
    ("Bordeaux2", 45.50, -1.20), ("Gib", 36.10, -5.40), ("Malta2", 35.80, 14.60), ("Alex", 31.40, 29.90),
    ("Colombo2", 6.90, 79.70), ("Bombay2", 18.90, 72.70), ("Calcutta2", 21.50, 88.30), ("Rangoon2", 16.30, 96.30),
    ("Durban2", -29.90, 31.30), ("CapeT", -33.90, 18.30), ("DiegoS", -12.20, 49.40), ("Louis", -20.10, 57.40),
    ("Capetown2", -34.20, 18.00), ("Takao2", 22.50, 120.10), ("Okinawa2", 26.20, 127.50), ("Chichi", 27.10, 142.30),
    ("Iwo", 24.70, 141.40), ("Guam2", 13.40, 144.60), ("Saipan2", 15.20, 145.60), ("Palau2", 7.30, 134.30),
    ("Truk2", 7.40, 151.60), ("Kwaj", 8.70, 167.60), ("Midway2", 28.20, -177.20), ("Wake2", 19.30, 166.50),
    ("Dutch", 53.90, -166.40), ("Seattle2", 47.80, -124.00), ("SF", 37.75, -122.70), ("SD", 32.65, -117.30),
    ("Pearl", 21.30, -158.00), ("Tahiti2", -17.50, -149.70), ("Pago", -14.30, -170.80), ("Canton2", -2.80, -171.60),
    ("Palmyra2", 5.90, -162.20), ("Johnston2", 16.70, -169.60), ("Tulagi2", -9.00, 160.20), ("Townsville2", -19.10, 147.00),
    ("Melbourne2", -38.30, 144.80), ("Auckland2", -36.70, 174.90), ("Brisbane2", -27.30, 153.40), ("Sydney2", -33.90, 151.40),
    ("Acapulco2", 16.70, -99.90), ("Veracruz2", 19.30, -96.00), ("Lisbon2", 38.60, -9.40), ("Ferrol2", 43.50, -8.40),
    ("Azores2", 38.60, -27.00), ("Canaries2", 28.20, -15.20), ("CapeV", 14.90, -23.40), ("Goth", 57.60, 11.70),
    ("Recife3", -8.10, -34.70), ("Rio2", -23.00, -43.10), ("Monte", -35.00, -56.00), ("BsAs", -34.70, -58.00),
    ("Callao2", -12.10, -77.30), ("Tarawa2", 1.40, 172.80), ("Nauru2", -0.50, 166.80), ("Attu2", 52.90, 173.00),
    ("Kiska2", 51.90, 177.40), ("Ominato2", 41.30, 141.30), ("Sasebo2", 33.10, 129.60), ("Kure2", 34.10, 132.50),
    ("Shanghai2", 31.10, 122.00), ("Paramushiro2", 50.40, 156.20), ("Marcus2", 24.30, 153.90), ("Ponape2", 6.90, 158.30),
    ("Jaluit2", 5.90, 169.50), ("Haiphong", 20.80, 107.00),
]

FIXED = [("kure", "Bungo"), ("Bungo", "Kyushu"), ("sasebo", "Tsushima"), ("yokosuka", "TokyoBay"), ("ominato", "Tsugaru"),
         ("seattle", "PugetSd"), ("sanfrancisco", "GoldenGt"), ("sandiego", "Coronado"), ("dutchharbor", "Unimak"),
         ("paramushiro", "Kurils"), ("colon", "Colon2"), ("balboa", "Panama"), ("Straits", "Gib"), ("Alboran", "Straits"),
         ("gibraltar", "Gib"), ("Dover", "Channel"), ("Dover", "Jade"), ("Skagerrak", "Kattegat"), ("Kattegat", "Kiel2"),
         ("kiel", "Kiel2"), ("wilhelmshaven", "Wilh"), ("Wilh", "Jade"), ("Malacca", "singapore"), ("Malacca", "Andaman"),
         ("Sunda", "Batavia2"), ("Sunda", "Malacca"), ("Torres", "Coral"), ("Torres", "Banda"), ("Bass", "Melbourne2"),
         ("Mandeb", "Aden2"), ("Hooghly", "calcutta"), ("Martaban", "rangoon"), ("Forth", "rosyth"), ("Pentland", "scapaflow"),
         ("Spithead", "portsmouth"), ("Nile", "alexandria"), ("Levant", "Haifa2"), ("Kola", "murmansk"), ("White", "archangel"),
         ("Barents", "White"), ("Vest", "narvik"), ("Trond", "trondheim"), ("Bergen2", "bergen"), ("Yangtze", "shanghai"),
         ("Tonkin", "Haiphong"), ("Tonkin", "Hainan2"), ("Sicily", "Malta2"), ("Otranto", "Taranto2"), ("Lion", "Toulon2"),
         ("Ligurian", "Spezia"), ("Tyrrhenian", "Naples2"), ("Messina2", "Tyrrhenian"), ("Messina2", "Ionian"),
         ("Aegean", "Piraeus2"), ("Sirte", "Tripoli2"), ("Cyrenaica", "Benghazi2"), ("Gironde", "bordeaux"),
         ("Chesapeake", "norfolk"), ("Sandy", "newyork"), ("Fundy", "halifax"), ("Avalon", "stjohns"), ("Irish", "liverpool"),
         ("Plymouth2", "plymouth"), ("Ushant", "Brest2"), ("Lorient2", "lorient"), ("Nazaire", "stnazaire"), ("Florida", "Windward"),
         ("Windward", "Gitmo"), ("Hormuz", "Arabian"), ("Palk", "Ceylon"), ("Agulhas", "CapeT"), ("Natal", "Durban2"),
         ("Mozambique", "Mombasa2"), ("Mozambique", "DiegoS"), ("Cook", "auckland"), ("Hauraki", "auckland"),
         ("Moresby", "portmoresby"), ("Rabaul2", "rabaul"), ("Darwin2", "darwin"), ("Fremantle2", "fremantle"),
         ("PortJackson", "sydney"), ("Moreton", "brisbane"), ("Makassar", "Balik"), ("Balik", "balikpapan"),
         ("Banda", "Ambon2"), ("Lombok", "Surabaya2"), ("Surabaya2", "surabaya"), ("Manila2", "manila"), ("Davao2", "davao"),
         ("HK", "hongkong"), ("Formosa", "Takao2"), ("Luzon", "Formosa"), ("SChina", "Camranh2"), ("Saigon2", "saigon"),
         ("Camranh2", "camranh"), ("Haiphong", "Hainan2"), ("Okinawa2", "okinawa"), ("Oahu", "Pearl"), ("Pearl", "pearlharbor"),
         ("Denmark", "Reyk"), ("Reyk", "reykjavik"), ("Faroe", "Pentland"), ("Tagus", "lisbon"), ("Finisterre", "Ferrol2"),
         ("Casa", "casablanca"), ("Dakar2", "dakar"), ("Freetown2", "freetown"), ("Oran2", "oran"), ("Bizerte2", "bizerte"),
         ("Heraklion", "crete"), ("Rhodes2", "rhodes"), ("Plate", "Monte"), ("Monte", "montevideo"), ("BsAs", "buenosaires"),
         ("Plate", "BsAs"), ("Rio2", "riodejaneiro"), ("Recife3", "recife"), ("Valpo", "valparaiso"), ("Lima", "callao"),
         ("Toulon2", "toulon"), ("Goth", "gothenburg"), ("Kattegat", "Goth"), ("Liverpool2", "liverpool"), ("Irish", "Liverpool2"),
         ("Ceylon", "colombo"), ("Trinco", "trincomalee"), ("Palk", "Trinco"), ("Arch", "archangel"), ("White", "Arch"),
         ("Narvik2", "narvik"), ("Vest", "Narvik2"), ("Seattle2", "seattle"), ("PugetSd", "Seattle2"), ("Kure2", "kure"), ("Bungo", "Kure2"),
         ("Channel", "Irish"), ("Scapa", "scapaflow"), ("Pentland", "Scapa"), ("Rosyth2", "rosyth"), ("Forth", "Rosyth2")]

NATIONS = {'A': ["usa", "australia"], 'X': ["japan"]}
AIRCRAFT = {'A': ["wildcat", "dauntless", "b17f"], 'X': ["zero", "val", "betty"]}
MUST = {'A': ["truk", "kwajalein", "saipan", "rabaul", "singapore", "manila", "taranto", "brest", "tripoli", "wilhelmshaven"],
        'X': ["pearlharbor", "midway", "singapore", "colombo", "darwin", "alexandria", "malta", "gibraltar", "scapaflow", "newyork"]}
HOLD = {'A': ["pearlharbor", "sandiego", "sydney", "scapaflow", "norfolk", "alexandria"],
        'X': ["yokosuka", "truk", "wilhelmshaven", "taranto", "toulon", "saigon"]}

CAMPS = {
    'wawallies': dict(player='A', name="Worlds at War: Allies", title="WORLDS AT WAR: THE ALLIES",
                      blurb="December 1941. The war is now truly a world war. Hold the sea lanes in every ocean, break the Axis fleets and carry the war to Truk, Taranto and Wilhelmshaven."),
    'wawaxis': dict(player='X', name="Worlds at War: Axis", title="WORLDS AT WAR: THE AXIS",
                    blurb="December 1941. Japan has struck Pearl Harbor and the Axis fleets hold Europe's coasts. Cut the Allied sea lanes in every ocean and take their great bases before their shipyards outbuild you."),
}


def faction(side, player):
    if side == 'N': return 2
    return 0 if side == player else 1


def build_locations(player):
    land, names = [], []
    for lid, name, lat, lon, side, port, af, troops, cs in L:
        x, y = to_map(lat, lon)
        fac = faction(side, player)
        own = [troops, 0] if fac == 0 else ([0, troops] if fac == 1 else [0, 0])
        sup = [v * 2 for v in own]
        big = 200 if cs else 0
        d = {"locationID": lid, "currentFaction": fac, "locationPosition": {"x": round(x, 5), "y": round(y, 5)}}
        if cs: d["createShips"] = True
        d.update({"portLevel": port, "airfieldLevel": af, "aircraftPrefabs": [], "integrity": 100,
                  "troops": own, "supplies": sup,
                  "fuel": [big, 0] if fac == 0 else [0, big], "engineering": [big, 0] if fac == 0 else [0, big],
                  "inTheAir": [0, 0, 0], "destroyedAir": [0, 0, 0]})
        land.append(json.dumps(d, separators=(',', ':')))
        names.append(name)
    return land, names


def build_waypoints():
    nodes = []  # (name, lat, lon, radius, isLocation, gridkey)
    lats = [-62.5 + 5 * k for k in range(28)]       # -62.5 .. 72.5
    lons = [LON0 + 2.5 + 5 * k for k in range(72)]
    for j, lat in enumerate(lats):
        for i, lon in enumerate(lons):
            if any(is_land(lat + dy, lon + dx) for dx in (-0.6, 0, 0.6) for dy in (-0.6, 0, 0.6)):
                continue
            nodes.append(("G%02d_%02d" % (i, j), lat, lon, 0.01, False, (i, j)))
    for n, lat, lon in HELPERS:
        nodes.append((n, lat, lon, 0.003, False, None))
    for lid, name, lat, lon, *_ in L:
        nodes.append((lid, lat, lon, 0.001, True, None))
    links = {n[0]: set() for n in nodes}
    byname = {n[0]: n for n in nodes}

    def link(a, b):
        if a in links and b in links and a != b:
            links[a].add(b); links[b].add(a)

    grid = {n[5]: n for n in nodes if n[5] is not None}
    for (i, j), n in grid.items():
        for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
            m = grid.get(((i + di) % 72, j + dj))
            if m and clear_line((n[1], n[2]), (m[1], m[2])):
                link(n[0], m[0])

    def dist(a, b):
        dlon = abs(lon360(a[2]) - lon360(b[2]))
        if dlon > 180: dlon = 360 - dlon
        return math.hypot(a[1] - b[1], dlon * math.cos(math.radians((a[1] + b[1]) / 2)))

    sea = [n for n in nodes if not n[4]]
    for n in nodes:
        if n[5] is not None:
            continue
        cands = sorted((dist(n, m), m) for m in sea if m[0] != n[0])
        got = 0
        for dd, m in cands:
            if dd > 9: break
            if clear_line((n[1], n[2]), (m[1], m[2]), skip_ends=0.12 if n[4] else 0.05):
                link(n[0], m[0]); got += 1
                if got >= (2 if n[4] else 3): break
    for a, b in FIXED:
        link(a, b)
    # anything still unlinked (a port deep in a bay the straight-line test cannot reach): tie it to its 2 nearest sea nodes
    for n in nodes:
        if n[5] is None and not links[n[0]]:
            cands = sorted((dist(n, m), m) for m in sea if m[0] != n[0] and m[5] is not None)
            for dd, m in cands[:2]:
                if dd < 15: link(n[0], m[0])
    # connectivity from Pearl Harbor
    start = "pearlharbor"
    seen, todo = {start}, [start]
    while todo:
        c = todo.pop()
        for m in links[c]:
            if m not in seen:
                seen.add(m); todo.append(m)
    unreached = [n[0] for n in nodes if n[0] not in seen]
    for u in list(unreached):
        n = byname[u]
        if n[5] is not None: continue
        cands = sorted((dist(n, m), m) for m in sea if m[0] in seen and m[5] is not None)
        if cands and cands[0][0] < 15:
            link(u, cands[0][1][0]); seen.add(u)
    unreached = [n[0] for n in nodes if n[0] not in seen]
    nodes = [n for n in nodes if n[0] in seen or n[4]]
    idx = {n[0]: k for k, n in enumerate(nodes)}
    out = []
    for n in nodes:
        x, y = to_map(n[1], n[2])
        dirs = {"N": [], "S": [], "E": [], "W": []}
        for m in sorted(links[n[0]]):
            if m not in idx: continue
            mm = nodes[idx[m]]
            mx, my = to_map(mm[1], mm[2])
            dx, dy = mx - x, my - y
            r = math.hypot(dx, dy) or 1
            if dy > 0.38 * r: dirs["N"].append(m)
            if dy < -0.38 * r: dirs["S"].append(m)
            if dx > 0.38 * r: dirs["E"].append(m)
            if dx < -0.38 * r: dirs["W"].append(m)
        out.append(json.dumps({"waypointName": n[0], "isLocation": n[4],
                               "pos": ["%.4f" % x, "%.4f" % y, "%.4f" % n[3]],
                               "sNorthWP": dirs["N"], "sSouthWP": dirs["S"], "sEastWP": dirs["E"], "sWestWP": dirs["W"]},
                              separators=(',', ':')))
    graph = {"nodes": [(n[0], n[1], n[2], n[4]) for n in nodes], "links": {k: sorted(v) for k, v in links.items()}}
    return out, graph, unreached, sum(len(v) for v in links.values()) // 2


def nearest_grid(graph, lat, lon):
    lon = lon360(lon)
    best = None
    for n, la, lo, isloc in graph['nodes']:
        if isloc or not n.startswith('G'): continue
        lo2 = lon360(lo)
        dlon = abs(lo2 - lon); dlon = min(dlon, 360 - dlon)
        d = math.hypot(la - lat, dlon * math.cos(math.radians(lat)))
        if best is None or d < best[0]: best = (d, n)
    return best[1]


SUB = ["Submarine"]
DD3 = ["Destroyer"] * 3
CRU = ["Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"]
KB = ["Aircraft_Carrier", "Aircraft_Carrier", "Battleship", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer", "Destroyer"]
BB = ["Battleship", "Battleship", "Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"]
INV_S = ["Light_Cruiser", "Transport", "Transport", "Destroyer", "Destroyer", "Destroyer"]
INV_L = ["Battleship", "Heavy_Cruiser", "Heavy_Cruiser", "Transport", "Transport", "Transport", "Transport", "Destroyer", "Destroyer", "Destroyer"]
CONVOY = ["Light_Cruiser", "Destroyer", "Destroyer", "Oiler", "Oiler", "Transport", "Transport", "Transport"]

# AI theatre plan per side: (big bases, sub bases, patrol zones (lat, lon), intercept bases, invasion bases, home, last stand base)
AI_PLAN = {
    'X': dict(big=["truk", "yokosuka", "kwajalein", "wilhelmshaven", "taranto", "brest", "saigon"],
              subs=["kwajalein", "yokosuka", "lorient", "laspezia", "palau", "saigon"],
              zones=[(22.5, -160), (27.5, -177.5), (37.5, -127.5), (17.5, 167.5), (12.5, 167.5), (2.5, 172.5), (32.5, 147.5),
                     (-12.5, 157.5), (-17.5, 162.5), (7.5, 115), (2.5, 107.5), (-7.5, 102.5), (7.5, 85), (12.5, 92.5),
                     (57.5, -12.5), (62.5, -7.5), (47.5, -12.5), (42.5, -32.5), (37.5, 2.5), (35.5, 18), (33.5, 27.5),
                     (72.5, 27.5), (27.5, -62.5), (12.5, -57.5), (37.5, -72.5), (47.5, -42.5), (-32.5, 37.5), (-7.5, 47.5)],
              inv=["truk", "saipan", "kwajalein", "palau", "saigon", "takao", "tripoli", "piraeus", "trondheim", "dakar"],
              home="truk", last="yokosuka"),
    'A': dict(big=["pearlharbor", "sandiego", "singapore", "sydney", "scapaflow", "alexandria", "norfolk", "colombo"],
              subs=["pearlharbor", "manila", "fremantle", "portsmouth", "malta", "gibraltar"],
              zones=[(32.5, 147.5), (27.5, 142.5), (12.5, 147.5), (7.5, 152.5), (2.5, 157.5), (17.5, 132.5), (27.5, 127.5),
                     (12.5, 112.5), (-2.5, 132.5), (-7.5, 152.5), (22.5, -160), (57.5, 2.5), (62.5, 2.5), (47.5, -7.5),
                     (57.5, -12.5), (37.5, 7.5), (35.5, 18), (33.5, 22.5), (72.5, 22.5), (12.5, 62.5), (-2.5, 47.5),
                     (-32.5, 32.5), (37.5, -67.5), (17.5, -62.5), (47.5, -27.5), (-17.5, 172.5), (-22.5, 152.5), (2.5, 87.5)],
              inv=["pearlharbor", "noumea", "brisbane", "darwin", "colombo", "alexandria", "gibraltar", "scapaflow", "norfolk", "singapore"],
              home="pearlharbor", last="norfolk"),
}


def build_missions(graph, ai_side):
    P = AI_PLAN[ai_side]
    Z = [nearest_grid(graph, la, lo) for la, lo in P['zones']]
    M = []

    def mission(kind, spawn, units, last='', must=None, prohib=None, **kw):
        d = {"missionString": kind, "spawnLocation": spawn, "firstWaypoint": spawn, "lastWaypoint": last,
             "units": units, "mustUseWaypoints": must or ([last] if last and kind == 'Patrol' else []),
             "prohibitedWaypoints": prohib or [], "directPath": kind != 'Patrol',
             "destIsLocation": kind not in ('Patrol', 'Intercept', 'DefendArea', 'PrimaryLost')}
        d.update(kw); M.append(json.dumps(d, separators=(',', ':')))

    pat = dict(patrolDestZone=True, patrolNeighbours=True, aggressive=True, autoRenew=True, noCost=True)
    subs = P['subs']
    for k, z in enumerate(Z):
        mission('Patrol', subs[k % len(subs)], SUB, z, **pat)
    big = P['big']
    for k, z in enumerate(Z[::2]):
        mission('Patrol', big[k % len(big)], DD3 if k % 3 else CRU, z, formation=2 if k % 3 == 0 else 1, **pat)
    for k, b in enumerate(big):
        mission('Intercept', b, CRU if k % 2 else BB, formation=2, aggressive=True, delayAIDays=[0, 1, 0, 1])
        if k < 3:
            mission('Intercept', b, KB, formation=4, aggressive=True, delayAIDays=[1, 1, 1, 3])
        mission('Bombard', b, CRU, formation=2, aggressive=True, bombard=True, delayAIDays=[0, 1, 1, 1])
    for k, b in enumerate(P['inv']):
        mission('SmallInvasion', b, INV_S, aggressive=False, troops=True, delayAIDays=[0, 1, 0, 0])
        if k % 2 == 0:
            mission('LargeInvasion', b, INV_L, formation=2, aggressive=False, troops=True, delayAIDays=[1, 1, 1, 3])
    for b in subs[:3]:
        mission('SubInvasion', b, SUB * 3, aggressive=False, troops=True)
    for b in big[:4]:
        mission('FastTroop', b, ["Destroyer"] * 6, aggressive=False, troops=True, delayAIDays=[0, 1, 0, 0])
    for b in big:
        mission('Convoy', b, CONVOY, formation=2, aggressive=False, construction=True, delayAIDays=[0, 1, 0, 0])
    mission('Home', '', [], last=P['home'], formation=2, aggressive=False)
    for b in big[:4]:
        mission('DefendArea', b, SUB * 3, formation=2, aggressive=True, noCost=True)
    mission('PrimaryLost', P['last'], ["Battleship", "Battleship", "Aircraft_Carrier", "Heavy_Cruiser", "Heavy_Cruiser", "Light_Cruiser", "Destroyer", "Destroyer", "Destroyer"],
            patrolDestZone=True, patrolNeighbours=True, formation=4, aggressive=False, autoRenew=False, noCost=True, delayAIDays=[1, 1, 0, 0])
    nav = [{"missionString": "PrimaryLost", "mustUseWaypoints": [Z[0]], "prohibitedWaypoints": []}]
    ai1 = {"subPatrol": Z[:8], "carrierPatrol": []}
    return M, nav, ai1


LABELS = [("PACIFIC OCEAN", 10, -150, 0.12, True), ("NORTH PACIFIC", 40, -170, 0.07, True), ("SOUTH PACIFIC", -30, -140, 0.07, True),
          ("ATLANTIC OCEAN", 25, -40, 0.12, True), ("SOUTH ATLANTIC", -30, -20, 0.07, True), ("INDIAN OCEAN", -20, 80, 0.12, True),
          ("ARCTIC OCEAN", 78, 60, 0.07, True), ("SOUTHERN OCEAN", -58, 60, 0.07, True), ("MEDITERRANEAN", 34.5, 18, 0.04, True),
          ("CARIBBEAN SEA", 15, -75, 0.04, True), ("NORTH SEA", 56.5, 3.5, 0.035, True), ("ARABIAN SEA", 15, 62, 0.04, True),
          ("BAY OF BENGAL", 13, 88, 0.04, True), ("SOUTH CHINA SEA", 13, 114, 0.04, True), ("CORAL SEA", -16, 155, 0.04, True),
          ("TASMAN SEA", -38, 160, 0.04, True), ("NORWEGIAN SEA", 68, 2, 0.04, True), ("BARENTS SEA", 73, 38, 0.04, True),
          ("UNITED STATES", 39, -100 + 0.001, 0.07, False), ("CANADA", 55, -95, 0.07, False), ("BRAZIL", -10, -52, 0.07, False),
          ("EUROPE", 50, 15, 0.07, False), ("AFRICA", 5, 20, 0.07, False), ("ASIA", 50, 90, 0.07, False), ("AUSTRALIA", -25, 134, 0.07, False),
          ("JAPAN", 36.5, 136, 0.05, False), ("INDIA", 22, 78, 0.05, False), ("CHINA", 33, 105, 0.05, False),
          ("HAWAIIAN ISLANDS", 23.8, -160, 0.04, True), ("MARSHALL ISLANDS", 11.5, 169, 0.035, True), ("MARIANA ISLANDS", 17, 148.5, 0.035, True),
          ("CAROLINE ISLANDS", 4, 150, 0.035, True), ("ALEUTIAN ISLANDS", 50, -175, 0.035, True), ("SOLOMON ISLANDS", -8, 161, 0.035, True),
          ("DUTCH EAST INDIES", -4, 118, 0.035, True), ("PHILIPPINES", 12, 123.5, 0.035, True), ("NEW ZEALAND", -42, 172, 0.035, False),
          ("MADAGASCAR", -20, 47, 0.035, False), ("ICELAND", 65, -18, 0.035, False), ("GREENLAND", 72, -40, 0.05, False)]

Y = '<color=#caa809>{}</color>'


def write_campaign(cid, cfg, waypoints, graph, maps_rel):
    player = cfg['player']; ai = 'X' if player == 'A' else 'A'
    camp = os.path.join(OUT, 'campaign', cid)
    lang = os.path.join(OUT, 'language', 'english', 'campaign', cid)
    os.makedirs(camp, exist_ok=True); os.makedirs(os.path.join(lang, 'event'), exist_ok=True)
    land, names = build_locations(player)
    open(os.path.join(camp, 'mapLandLocations.txt'), 'w').write('\n'.join(land))
    open(os.path.join(camp, 'seaWaypoints.txt'), 'w').write('\n'.join(waypoints))
    open(os.path.join(lang, 'mapLocationNames.txt'), 'w').write('\n'.join(names))
    M, nav, ai1 = build_missions(graph, ai)
    open(os.path.join(camp, 'sea_missions.txt'), 'w').write('\n'.join(M))
    open(os.path.join(camp, 'sea_navigation_aid.txt'), 'w').write('\n'.join(json.dumps(n, separators=(',', ':')) for n in nav))
    open(os.path.join(camp, 'ai1.txt'), 'w').write(json.dumps(ai1, separators=(',', ':')))
    for f in ('sea_alts.txt', 'resupply.txt', 'strategicBombing.txt'):
        shutil.copy(os.path.join(STOCK, f), os.path.join(camp, f))
    for f in ('seaUnits.txt', 'airUnits.txt'):
        shutil.copy(os.path.join(MODCAMP, f), os.path.join(camp, f))
    # setup from the Pacific campaign's, with world numbers
    s = json.loads(open(os.path.join(PAC, 'campaign', 'pacificwar', 'setup.txt'), encoding='utf-8-sig').read())
    s.update({
        "mapImagePaths": [f"{maps_rel}/world{i}.png" for i in range(4)],
        "customWaterMask": True, "mapWaterMask": f"{maps_rel}/worldWatermask.png",
        "startDate": START, "currentDateTime": START,
        "nations0": NATIONS[player], "nations1": NATIONS[ai],
        "aircraft0": AIRCRAFT[player], "aircraft1": AIRCRAFT[ai],
        "mustControl": MUST[player] + HOLD[player],
        "maxAirAt": [], "maxPortAt": [],
        "mapZoomLevels": {"x": 0.02, "y": 1},
        "mapOriginXY": [int(LON0 * 240), 0], "mapPixelWidth": 86400, "mapWidthMetres": 86400 * 488.28125,
        "equatorYValue": 0.0, "interactionDistanceMetres": 12000,
        "minCampaignDetectionRange": 6.0, "maxCampaignDetectionRange": 35.0,
    })
    open(os.path.join(camp, 'setup.txt'), 'w').write(json.dumps(s, separators=(',', ':')))
    # labels
    Lb = []
    for t, lat, lon, size, it in LABELS:
        x, y = to_map(lat, lon)
        Lb.append(json.dumps({"text": t, "size": size, "position": {"x": round(x, 4), "y": round(y, 4)}, "shadow": False,
                              "color": {"r": 255, "g": 255, "b": 255, "a": 160}, "italic": it}, separators=(',', ':')))
    open(os.path.join(lang, 'mapLabels.txt'), 'w').write('\n'.join(Lb))
    # objectives
    must = MUST[player]; hold = HOLD[player]
    obj = f"""
<b><size=18>{cfg['title']}</size></b>

<b>December 8th 1941</b>
{cfg['blurb']}

You must:

1) Take control of:
""" + '\n'.join(f"   - {Y.format(dict((l[0], l[1]) for l in L)[m])}" for m in must) + """

2) Maintain control of:
""" + '\n'.join(f"   - {Y.format(dict((l[0], l[1]) for l in L)[m])}" for m in hold) + """

All of these must be held at the same time to win the campaign."""
    open(os.path.join(lang, 'objectives.txt'), 'w').write(obj)
    # events: copy the Pacific campaign's generic ones, then write our own start/victory/defeat
    pev = os.path.join(PAC, 'language', 'english', 'campaign', 'pacificwar', 'event')
    for f in os.listdir(pev):
        if f.startswith('modrules') or f.startswith('convoy') or f in ('shipsSunk.txt', 'defeatNoPort.txt', 'victoryNoPort.txt'):
            shutil.copy(os.path.join(pev, f), os.path.join(lang, 'event', f))
    side = "Allied" if player == 'A' else "Axis"
    open(os.path.join(lang, 'event', 'start.txt'), 'w').write(f"{cfg['title']}\n\n{cfg['blurb']}\n\nThis is a test build of the whole-world campaign. The Atlantic and Mediterranean are populated with placeholder ships until British, German and Italian units exist.")
    open(os.path.join(lang, 'event', 'victory.txt'), 'w').write(f"Victory\n\nThe {side} fleets hold every objective. The war at sea is won.")
    open(os.path.join(lang, 'event', 'defeat.txt'), 'w').write(f"Defeat\n\nThe {side} fleets have lost control of the oceans.")
    # rules.txt: copied from the mod campaign001 if present
    rules = os.path.join(os.path.dirname(MODCAMP), '..', 'language', 'english', 'campaign', 'campaign001', 'rules.txt')
    if os.path.exists(rules): shutil.copy(rules, os.path.join(lang, 'rules.txt'))
    return len(M)


def main():
    os.makedirs(OUT, exist_ok=True)
    maps_rel = "maps/worldsatwar"
    md = os.path.join(OUT, maps_rel); os.makedirs(md, exist_ok=True)
    for f in ('world0.png', 'world1.png', 'world2.png', 'world3.png', 'worldWatermask.png'):
        shutil.copy(os.path.join(MAPS, f), os.path.join(md, f))
    waypoints, graph, unreached, nlinks = build_waypoints()
    print('waypoints', len(waypoints), 'links', nlinks)
    print('unreached from Pearl Harbor:', [u for u in unreached if not u.startswith('G')])
    print('locations in water:', [l[0] for l in L if not is_land(l[2], l[3])])
    lines = []
    for cid, cfg in CAMPS.items():
        n = write_campaign(cid, cfg, waypoints, graph, maps_rel)
        print(cid, 'missions', n)
        lines.append(f"{cid}={cfg['name']}=8,12,1941={cfg['blurb']}=forceSettings=2,2,2,2,2,2,2,2,2,2")
    open(os.path.join(OUT, '..', 'campaigns_lines.txt'), 'w').write('\n'.join(lines) + '\n')
    json.dump(graph, open(os.path.join(OUT, '..', 'graph.json'), 'w'))


main()
