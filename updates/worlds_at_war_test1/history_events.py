# Historical events for Worlds at War, written per side by build_world.py into campaign/<id>/history.txt
# and language/english/campaign/<id>/event/h_*.txt. Dates are the real ones.
# kind: 'attack' = attacker lands if the defender has too few warships near; 'raid' = each side's own ships near
# the place earn command points; 'convoy' like raid but the defender is the one who must be there.
# (id, (d, m, y), location, attacker side, check, rangeKm, minCount, troops, cp, name, note)
EVENTS = [
    ("wake",      (23,12,1941), "wake",        'X', "ships",    500, 4,  2000, 100, "Wake Island",
     "The first Japanese landing on 11 December was beaten off by the island's guns and four Wildcats. The second, with two carriers in support, took the atoll on 23 December."),
    ("hongkong",  (25,12,1941), "hongkong",    'X', "ships",    300, 3,  3000, 50,  "Hong Kong",
     "The colony fell on Christmas Day 1941 after eighteen days of fighting."),
    ("manila",    (2,1,1942),   "manila",      'X', "ships",    500, 6,  6000, 150, "Manila",
     "Manila was declared an open city and occupied on 2 January 1942; the Asiatic Fleet fell back to Java."),
    ("rabaul",    (23,1,1942),  "rabaul",      'X', "ships",    500, 3,  3000, 100, "Rabaul",
     "The South Seas Force took Rabaul on 23 January 1942 and made it the great Japanese base of the South Pacific."),
    ("channeldash",(12,2,1942), "brest",       'X', "raid",     400, 3,  0,    100, "the Channel Dash",
     "Scharnhorst, Gneisenau and Prinz Eugen ran up the Channel from Brest to Germany in daylight on 12 February 1942."),
    ("singapore", (15,2,1942),  "singapore",   'X', "ships",    500, 6,  8000, 200, "Singapore",
     "The fortress surrendered on 15 February 1942 after Force Z had been lost and the Malayan campaign collapsed."),
    ("darwin",    (19,2,1942),  "darwin",      'X', "carriers", 600, 2,  0,    100, "the Darwin raid",
     "Four carriers of the Kido Butai struck Darwin on 19 February 1942, sinking eight ships in the harbour."),
    ("javasea",   (1,3,1942),   "surabaya",    'X', "ships",    400, 6,  5000, 150, "Java",
     "The ABDA fleet was destroyed in the Java Sea on 27 February 1942 and the Japanese landed on Java on 1 March."),
    ("batavia",   (8,3,1942),   "batavia",     'X', "ships",    400, 4,  4000, 100, "Batavia",
     "The Dutch East Indies surrendered on 8 March 1942."),
    ("rangoon",   (8,3,1942),   "rangoon",     'X', "ships",    400, 3,  3000, 100, "Rangoon",
     "Rangoon fell on 8 March 1942, closing the Burma Road."),
    ("ceylon",    (5,4,1942),   "colombo",     'X', "carriers", 700, 2,  0,    100, "the Indian Ocean raid",
     "Nagumo's carriers struck Colombo on 5 April 1942 and Trincomalee on the 9th, sinking Hermes, Cornwall and Dorsetshire."),
    ("doolittle", (18,4,1942),  "yokosuka",    'A', "carriers", 1500, 1, 0,    100, "the Doolittle raid",
     "Sixteen B-25s flew off Hornet on 18 April 1942 and bombed Tokyo."),
    ("coralsea",  (7,5,1942),   "portmoresby", 'X', "ships",    600, 4,  4000, 150, "Port Moresby",
     "The invasion force turned back after the Battle of the Coral Sea, 7 and 8 May 1942: the first carrier battle in history."),
    ("midway",    (4,6,1942),   "midway",      'X', "carriers", 800, 2,  5000, 200, "Midway",
     "Four Japanese fleet carriers were sunk off Midway on 4 June 1942."),
    ("kiska",     (6,6,1942),   "kiska",       'X', "ships",    400, 3,  1200, 50,  "Kiska",
     "The Japanese occupied Kiska and Attu on 6 and 7 June 1942 as the northern arm of the Midway operation."),
    ("attu",      (7,6,1942),   "attu",        'X', "ships",    400, 3,  1100, 50,  "Attu",
     "Attu was occupied on 7 June 1942."),
    ("pq17",      (4,7,1942),   "murmansk",    'X', "convoy",   800, 4,  0,    100, "convoy PQ 17",
     "Ordered to scatter on 4 July 1942 for fear of Tirpitz, PQ 17 lost 24 of its 35 merchant ships to aircraft and U-boats."),
    ("guadalcanal",(7,8,1942),  "tulagi",      'A', "ships",    500, 6,  6000, 150, "Tulagi and Guadalcanal",
     "The 1st Marine Division landed at Tulagi and Guadalcanal on 7 August 1942, the first Allied offensive of the Pacific war."),
    ("pedestal",  (13,8,1942),  "malta",       'X', "convoy",   400, 4,  3000, 150, "Malta and Operation Pedestal",
     "Five of fourteen merchant ships reached Malta on 13 August 1942, the tanker Ohio among them, at the cost of a carrier, two cruisers and a destroyer."),
    ("torch1",    (8,11,1942),  "casablanca",  'A', "ships",    600, 6,  10000, 150, "Casablanca",
     "Operation Torch landed at Casablanca, Oran and Algiers on 8 November 1942; the French fleet at Casablanca fought for two days."),
    ("torch2",    (8,11,1942),  "oran",        'A', "ships",    600, 6,  10000, 150, "Oran",
     "Oran was taken by the Centre Task Force on 10 November 1942 after the French battleships at Mers-el-Kebir had been silenced two years before."),
    ("tripoli",   (23,1,1943),  "tripoli",     'A', "ships",    500, 4,  5000, 100, "Tripoli",
     "The Eighth Army entered Tripoli on 23 January 1943."),
    ("bizerte",   (7,5,1943),   "bizerte",     'A', "ships",    400, 4,  6000, 100, "Bizerte",
     "Bizerte and Tunis fell on 7 May 1943; a quarter of a million Axis troops surrendered in Tunisia."),
    ("attu2",     (11,5,1943),  "attu",        'A', "ships",    400, 4,  3000, 100, "Attu",
     "The 7th Infantry Division landed on Attu on 11 May 1943 and retook the island in three weeks."),
    ("sicily",    (10,7,1943),  "messina",     'A', "ships",    500, 8,  12000, 200, "Sicily",
     "Operation Husky landed on Sicily on 10 July 1943; Messina fell on 17 August."),
    ("salerno",   (9,9,1943),   "naples",      'A', "ships",    500, 6,  8000, 150, "Naples",
     "The Fifth Army landed at Salerno on 9 September 1943, the day Italy's surrender was announced, and took Naples on 1 October."),
    ("taranto",   (9,9,1943),   "taranto",     'A', "ships",    500, 4,  5000, 150, "Taranto",
     "The 1st Airborne Division was landed at Taranto by warships on 9 September 1943, as the Italian fleet sailed for Malta."),
    ("tarawa",    (20,11,1943), "tarawa",      'A', "ships",    400, 6,  5000, 150, "Tarawa",
     "The 2nd Marine Division took Betio in 76 hours from 20 November 1943."),
    ("northcape", (26,12,1943), "narvik",      'X', "raid",     800, 3,  0,    150, "the Battle of the North Cape",
     "Scharnhorst sortied against convoy JW 55B and was sunk by Duke of York on 26 December 1943."),
    ("kwajalein", (31,1,1944),  "kwajalein",   'A', "ships",    500, 6,  6000, 150, "Kwajalein",
     "Kwajalein and Roi-Namur were taken between 31 January and 3 February 1944."),
    ("hailstone", (17,2,1944),  "truk",        'A', "carriers", 800, 3,  0,    150, "the Truk raid",
     "Operation Hailstone struck Truk on 17 and 18 February 1944, sinking some forty ships and ending its use as a fleet base."),
    ("normandy",  (6,6,1944),   "portsmouth",  'A', "convoy",   500, 8,  0,    300, "Normandy",
     "Nearly 7,000 vessels put the Allied armies ashore in Normandy on 6 June 1944."),
    ("saipan",    (15,6,1944),  "saipan",      'A', "carriers", 800, 4,  10000, 200, "Saipan",
     "The landing on Saipan on 15 June 1944 brought on the Battle of the Philippine Sea and the loss of three Japanese carriers."),
    ("guam2",     (21,7,1944),  "guam",        'A', "ships",    500, 6,  8000, 150, "Guam",
     "Guam was retaken from 21 July 1944."),
    ("peleliu",   (15,9,1944),  "palau",       'A', "ships",    500, 6,  8000, 150, "Peleliu",
     "The 1st Marine Division landed on Peleliu on 15 September 1944."),
    ("leyte",     (20,10,1944), "manila",      'A', "carriers", 800, 4,  12000, 300, "the Philippines",
     "The landing at Leyte on 20 October 1944 brought on the largest naval battle ever fought."),
    ("iwojima",   (19,2,1945),  "iwojima",     'A', "ships",    500, 8,  8000, 200, "Iwo Jima",
     "Three Marine divisions landed on Iwo Jima on 19 February 1945."),
    ("okinawa",   (1,4,1945),   "okinawa",     'A', "ships",    500, 10, 15000, 300, "Okinawa",
     "Operation Iceberg landed on Okinawa on 1 April 1945; the fleet fought off the kamikazes for three months."),
]

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
Y = '<color=#caa809>{}</color>'


def fmt_date(d):
    return f"{d[0]} {MONTHS[d[1]]} {d[2]}"


def write_history(camp, lang, player, owner_of, names, ev_json):
    """owner_of: locationID -> 'A'/'X'/'N' at the start. names: id -> NAME. ev_json(name, header, content)."""
    def side_index(s):            # faction index as the player sees it: 0 player, 1 enemy, 2 neutral
        return 2 if s == 'N' else (0 if s == player else 1)
    lines = ["// Historical events (read by ModHistory). One JSON line per event; see the Pacific War history.txt for the fields."]
    for (eid, date, loc, attacker, check, km, n, troops, cp, name, note) in EVENTS:
        if loc not in owner_of:
            continue
        # neutral places stay neutral until someone lands; otherwise the attacker needs the enemy to hold it, the defender needs to hold it
        own = 2 if owner_of[loc] == 'N' else (1 if attacker == player else 0)
        if check in ("raid", "convoy"): own = -1
        LOC = Y.format(names[loc]); when = fmt_date(date)
        day, month, year = date
        e = {"id": eid, "day": day, "month": month, "year": year, "location": loc, "ifOwner": own,
             "check": "carriers" if check == "carriers" else "ships", "rangeKm": km, "minCount": n,
             "passEvent": f"h_{eid}_pass", "failEvent": f"h_{eid}_fail", "warnEvent": f"h_{eid}_warn", "warnDays": 7}
        ships = "carriers" if check == "carriers" else "warships"
        if check in ("raid", "convoy"):
            # points for being there; the history note explains what happened
            mine = (attacker == player) if check == "raid" else (attacker != player)
            e["passCP"] = cp; e["failCP"] = 0 if mine else -cp // 2
            ev_json(f"h_{eid}_warn", f"{name}: one week".upper(),
                    f"<size=18><b>{when}</b></size>\nSomething is brewing around {LOC}. Have at least {n} {ships} within {km} km of it by {when} to make the most of it.")
            ev_json(f"h_{eid}_pass", name.upper(),
                    f"<size=18><b>{when}</b></size>\nOur {ships} were on hand at {LOC}. <b>+{cp} command points.</b>\n\n<i>{note}</i>")
            ev_json(f"h_{eid}_fail", name.upper(),
                    f"<size=18><b>{when}</b></size>\nWe had no {ships} within {km} km of {LOC} when it mattered." + ("" if mine else f" <b>{cp // 2} command points.</b>") + f"\n\n<i>{note}</i>")
        elif attacker == player:
            # the player is the attacker: enough ships near the place and it is taken
            e["passOwner"] = 0; e["passTroops"] = troops; e["passCP"] = cp
            ev_json(f"h_{eid}_warn", f"{name}: one week".upper(),
                    f"<size=18><b>{when}</b></size>\nThe landing force for {LOC} sails to arrive on {when}. It needs at least {n} {ships} within {km} km to cover it, or it will not go in.")
            ev_json(f"h_{eid}_pass", f"{name} taken".upper(),
                    f"<size=18><b>{when}</b></size>\nCovered by our {ships}, the landing force has taken {LOC}. <b>+{cp} command points.</b>\n\n<i>{note}</i>")
            ev_json(f"h_{eid}_fail", f"{name}: landing called off".upper(),
                    f"<size=18><b>{when}</b></size>\nWith fewer than {n} {ships} within {km} km of {LOC}, the landing force turned back.\n\n<i>{note}</i>")
        else:
            # the player holds (or the place is neutral) and the enemy comes for it
            e["failOwner"] = 1; e["failTroops"] = troops; e["passCP"] = cp; e["failCP"] = -cp // 2
            ev_json(f"h_{eid}_warn", f"{name} threatened".upper(),
                    f"<size=18><b>{when}</b></size>\nIntelligence expects an enemy move against {LOC} around {when}. Have at least {n} {ships} within {km} km by then, or it may fall.")
            ev_json(f"h_{eid}_pass", f"{name} held".upper(),
                    f"<size=18><b>{when}</b></size>\nOur {ships} off {LOC} turned the enemy landing force back. <b>+{cp} command points.</b>\n\n<i>{note}</i>")
            ev_json(f"h_{eid}_fail", f"{name} fallen".upper(),
                    f"<size=18><b>{when}</b></size>\nWith no {ships} to stop them, the enemy has landed at {LOC} and taken it. <b>{-cp // 2} command points.</b>\n\n<i>{note}</i>")
        lines.append(json.dumps(e, separators=(',', ':')))
    open(os.path.join(camp, 'history.txt'), 'w').write('\n'.join(lines) + '\n')
    return len(lines) - 1


import json, os
