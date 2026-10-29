import json
b=json.load(open('bodies_old.json'))
old=list(b)
def H(t): return '<color=#E0B030><b>'+t+'</b></color>\n'
def rep(i,a,c):
    assert a in b[i], (i,a[:40]); b[i]=b[i].replace(a,c)

# ---------- page 1 WHAT'S NEW ----------
p1 = (
H('VERSION 0.30: MEGA PATCH 01')+
"The biggest update so far. In short: friendly RAN task forces that fight on their own, a much smarter enemy that scales with the difficulty, downed airmen you can rescue, real fires, ships that handle like the real thing, and ships that break up and sink on real physics. Each part has its own page in this book.\n\n"
+H('Allied AI (Allied campaign)')+
"Royal Australian Navy groups sail and fight on your side, shown in yellow. They patrol, attack enemy ships they can beat, escort your exposed merchants and the supply convoy, and RAN merchants carry supplies from Cooktown to your ports that run short. The RAN force you start with is handed to them. You can't give them orders. Click one to see its ships and job. See ENEMY AND ALLIED AI.\n\n"
+H('Enemy AI rework')+
"The enemy now follows the difficulty settings (Very Easy, Easy, Balanced, Hard, Elite). Floatplanes and flying boats fan out from every enemy airfield on scout patrols, and a pop-up tells you when one has spotted you. Strikes gather and arrive together, sized to the ships they go for. On the map the enemy hunts you harder; in battle its ships press home, spread their fire and finish cripples. On Elite it fights like a real commander. New campaigns give enemy airfields more aircraft types. Switches are in Mod Options. See ENEMY AND ALLIED AI.\n\n"
+H('Bail-outs and rescues')+
"Airmen who bail out over the sea show up on the campaign map as an orange aircrew marker. Send a flying boat, a floatplane or a ship to pick them up, or switch on auto rescue with the new button under the fuel button. See EVENTS.\n\n"
+H('Fires')+
"Burning ships show real 3D animated flames and a smoke column. One burning compartment is a small fire; more grow it into a roaring blaze that lights up the ship and the sea. Shell and bomb hits burst in 3D fire, smoke and sparks. See REPAIR AND DAMAGE.\n\n"
+H('Ship handling')+
"Every ship turns on a real turning circle, the rudder takes time to bite, and ships carry their way: cut the engines and she coasts on for minutes. See FUEL AND SHIPS.\n\n"
+H('Break-up and sinking')+
"A magazine blast can now tear any ship apart, even a battleship, and every surface ship has torn, burnt break pieces. Wrecks and broken halves sink on real physics: water floods in, and they list, roll over, or stand on end before they go. Torpedo hits use the game's own big splash. See SINKING AND EXPLOSIONS.\n\n"
+H('Also in 0.30')+
"The supply convoy now really sails to your port (it used to sit still) and is shown in yellow. The battle message log starts empty in every new battle. The air auto resolve window matches the game's look, and a new sea auto resolve covers battles of your allies. The main menu has a CHANGE LOG button. Nebraska (1944) is gone from the ship lists. The Pacific War campaign is in as an early test, named \"Experimental. WIP might not work\".\n\n"
+H('VERSION 0.29: SHIPS GO DOWN FOR REAL')+
"Ships sink the way their flooding takes them. A torpedo can break a destroyer's back, magazine blasts are as big as what is in them, with new HMS Barham style explosions, floating wreckage and oil slicks. Shot-down planes shed their real wings, tails and engines, and crews bail out by parachute. Your ships answer your controls again with enemy planes near, fewer planes blow up in the air, and torpedo bombers stay at 800 m until the attack.\n\n"
+H('VERSION 0.28: AIR COMBAT UPDATE')+
"All 135 aircraft have their own flight, toughness, guns, armour and real fuel. New manoeuvres, formation flying, damage that changes how a plane flies, and planes that leave at bingo fuel or when out of ammunition. Fly your own plane with G and a chase camera with C. Air auto resolve with points and dice. The flight model runs on battle time, so x8 and x10 fly the same as x1.\n\n"
+H('VERSION 0.26 AND 0.27: THE FLIGHT MODEL')+
"Dives gain speed and climbs lose it, planes stall, flaps come out for hard turns. Pilot ranks from Green to Elite, real dogfight moves, and pilots who judge energy: boom and zoom, turn fight or disengage.\n\n"
+H('VERSION 0.25: THE NEW GUINEA FRONT')+
"Ten new map locations along Papua New Guinea, a historical aircraft mix at every base, much bigger starting fleets, 10 new formations, and new campaign names and win conditions. See MAP AND AIR BASES and STARTING FORCES.\n\n"
+H('VERSION 0.21 TO 0.24')+
"0.24: 84 RamZ warships and 93 RamZ aircraft, plus 20 ships and 22 aircraft from the TTE team. 0.23: a limited merchant fleet from the TTE team. 0.22: garrisons eat supplies, the Admiralty supply convoy, and this book. 0.21: faster ship buying, torpedo duds, glancing hits and the fuel overlay.\n\n"
+H('ON THE WAY (planned, NOT in the game yet)')+
"The Pacific War: finishing the new, bigger campaign map.\n"
"Free flight: planes that do not always fly along their nose, so loops, inverted flight and real spins.\n"
"Plane-to-plane collisions back on, retuned.\n"
"Pilots who keep their experience from battle to battle in a campaign.\n"
"Air auto resolve: a beaten bomber strike turns back.\n"
"Enemy bombers that press on through losses, and enemy fighters that cover their bombers first.\n"
"Enemy flying boats that rescue their own airmen.\n"
"Air range and timers: realistic launch, landing and rearming times so an airfield or carrier cannot launch non-stop.\n"
"A rule so a merchant or oiler in first place does not make a whole task force retreat.\n"
"Towing: crippled ships taken in tow, in battle and on the map.\n"
"More ships: Aegon's CTM pack of 86 Japanese ships.\n"
"Being looked at: crash and ditching effects for planes, and hit marks and scorching on ship models.\n\n"
"The full list is in the Change Log file."
)
b[0]=p1

# ---------- page 2 EVENTS ----------
rep(1,"It appears on the northern edge of the map and sails to your home port by itself. If it stops, it is told to sail again.",
 "It appears on the northern edge of the map and sails to your home port by itself, shown in yellow. You can't move it. If it stops, it is told to sail again. When it has unloaded it leaves the map.")
b[1]+=("\n\n"+H('Downed airmen')+
"Airmen who bail out over the sea show up on the campaign map as an orange aircrew marker, and they last about 36 hours. Send a flying boat (PBY, PBM, Mavis, Emily, Sunderland: 10 seats) or a floatplane (1 seat) to the marker. It picks them up and flies home. A ship that sails to the marker picks them up too. Each airman saved gives 0.25 command points. Enemy airmen are taken prisoner by ships, like ship survivors.\n\n"
+H('Auto rescue')+
"The 4th button in the top-left column of the campaign map (under BOOK, BELL and FUEL) switches auto rescue on or off; it is lit orange when on, and starts off. When on, the nearest of your airfields with a free flying boat in range sends one (two for a crew over 10 men) to each new aircrew marker, during flying hours only. Floatplanes, ship survivors and enemy airmen are still up to you.")

# ---------- page 4 CUSTOM SHIPS ----------
rep(3,"Iowa (1945), Nebraska, Nevada","Iowa (1945), Nevada")
rep(3,"84 ships from RamZ's public Unit Catalog (thank you, RamZ!), listed by ship class.","84 ships from RamZ's public Unit Catalog (thank you, RamZ!), listed by ship class. Nebraska (1944) was taken out in 0.30: a carrier-battleship hybrid did not fit the mod's realism.")

# ---------- page 7 STARTING FORCES ----------
rep(6,"Australia Surface Force: HMAS Australia, Canberra and Hobart with destroyers, near Port Moresby.",
 "Australia Surface Force: HMAS Australia, Canberra and Hobart with destroyers, near Port Moresby. Since 0.30 it is handed to the Allied AI in the first 2 days and sails as RAN CRUISER FORCE (yellow).")

# ---------- page 8 REPAIR AND DAMAGE ----------
b[7]+=("\n\n"+H('Fires')+
"Fires burn in real 3D: animated flames from the side, round ragged blazes when seen from above, and a smoke plume. A single burning compartment is a small fire. The more compartments burn, the bigger it grows, up to a roaring blaze that glows, lights up the ship and the sea around it, and sends up a black smoke column.\n\n"
+H('Hits')+"Shell and bomb hits on ships burst in 3D fire, smoke, flying chunks and sparks, sized by the damage they do. Bombs make bigger bursts, armour-piercing shells smaller ones.")

# ---------- page 9 SINKING ----------
rep(8,"A ship goes down the way its flooding takes it. It capsizes and floats keel-up for a while, plunges by the bow or stern with the other end rising out of the water, or settles slowly and level. In shallow water the wreck comes to rest on the seabed. Submarines keep the game's own sinking.",
 "Since 0.30 wrecks sink on real physics, not a script. The hull is made of cells that float, fill with water and pass it on. A ship holed on one side takes water on that side, lists and can roll over. A ship holed at one end goes down by that end while the other end rises. A ship that floods evenly settles lower and lower, then goes. In shallow water the wreck comes to rest on the seabed and can stick out of the water. No two sinkings look the same. Submarines keep the game's own sinking.")
rep(8,"The middle kicks up and smashes back down, and the two halves sink in a V with bow and stern rising. All 50 destroyers and escorts (the modded 1942-45 ones too) have torn, crumpled and burnt break models, and turrets and guns go down whole with their half.",
 "The middle kicks up and smashes back down. Then each half floods through its torn end on the same physics: the broken ends go down, bow and stern rise, and they stand on end before they slide under. Torpedo break-back is for destroyers and escorts only.\n\n"+H('Break pieces')+
 "Every surface ship has torn, crumpled and burnt break pieces: near the bow, midships and near the stern (137 bigger ships plus the 50 destroyers and escorts). Turrets and guns go down whole with their piece.")
rep(8,"A big blast sinks the ship, and most of the time blows it in half or blows off the bow or stern.",
 "A magazine at least a quarter full is lethal to any ship, even a battleship: it sinks her, and most of the time blows her in half or blows off the bow or stern. The fuller the magazine, the likelier the break.")
rep(8,"A torpedo hit makes a 100 m tower of water, not a fireball.","A torpedo hit throws up the game's own big splash, made larger, not a fireball.")

# ---------- page 11 FUEL AND SHIPS ----------
b[10]+=("\n\n"+H('Ship handling')+
"Every ship turns on a real WW2 turning circle for its type: destroyers turn tight, battleships and carriers swing slowly and wide. The rudder and the swing take time to build, and hard turns cost speed. Ships carry their way: cut the engines and a big ship coasts on for minutes. Judge turns at x1 or x2 speed, because x10 makes a one minute turn look like six seconds.")

# ---------- page 12 SMARTER AI ----------
b[11]=(H('Difficulty')+
"The enemy follows the game's two difficulty settings, with the steps Very Easy, Easy, Balanced, Hard and Elite. Campaign Difficulty (set when the campaign starts) sets how the enemy acts on the map; Combat Difficulty sets how it fights in battle. Every step changes something, and Elite fights like a real commander who coordinates and attacks without mercy or hesitation. Mod Options has a section Enemy AI with a switch for the whole rework (off = the old enemy) and one for the scout pop-up.\n\n"
+H('Enemy scouts')+
"Every enemy airfield sends floatplanes and flying boats out on scout patrols, many single planes fanned out, at the first flying hour and at midday. Bases get floatplane scouts added, saved campaigns too. When a scout spots you, a pop-up names the force, and enemy HQ reacts after a delay: shoot the scout down first and the report is lost. On the lower steps scouts stay home in rain and storms.\n\n"
+H('Enemy strikes')+
"Strike groups gather at a rally point and attack together, and waves from different bases time their arrival. The size of a strike follows its target: a few planes for a destroyer, a whole wing for a battleship group. Fighter cover over enemy ships is sized to the group. Search planes are never sent on strikes. New campaigns give every enemy airfield more aircraft types.\n\n"
+H('Enemy on the map')+
"It chases further and with less of a size advantage, remembers you for longer and searches where it last saw you. On Elite it sends a surface group straight at any force it spots.\n\n"
+H('Enemy in battle')+
"AI fleets hold formation and coordinate torpedo attacks. Ships rethink more often and, from Balanced up, no longer turn away after the first hit. Fire is spread over your ships, and from Hard up cripples are finished first. Retreating ships lay smoke. Some enemy pilots are one rank better. On Elite the whole force only runs when it is down to a third of your strength. Far-away task forces head straight for you instead of sailing in circles. Subs ambush from further out and come back for more.\n\n"
+H('Allied AI (Allied campaign only)')+
"Royal Australian Navy groups sail on your side, shown in yellow: RAN CRUISER FORCE, RAN DESTROYER FORCE and, from 3 months in, sometimes RAN CARRIER FORCE (Colossus). The first comes 3 to 7 days in from Cooktown (or Port Moresby or Milne Bay), with at most 2 at a time and a new one 15 to 25 days after one is lost. They patrol, attack enemy ships within 250 km they can beat, send carrier strikes, escort the supply convoy and your exposed merchant groups, and go home to refit when damaged or after 12 days at sea.\n\n"
+H('RAN merchants')+
"When one of your ports is short of supplies or fuel, RAN MERCHANTS (borrowed US transports and oilers with a RAN destroyer) load cargo from Cooktown's stock, sail there and unload. They never carry troops or take a port.\n\n"
+H('Your allies and you')+
"You can't give orders to a yellow group. Click it to see its ships, damage, job, days at sea, planes and cargo. When it meets the enemy you choose ENGAGE (you command the RAN ships in that battle) or AUTO RESOLVE, which opens the sea resolve window with a chance bar. Battles your allies fight give no command points. Their messages appear in the Admiralty tab.")
b[11] # keep
# ---------- page 13 AIR ----------
rep(12,"The crew bail out and drift down into the sea under a parachute.","The crew bail out and drift down into the sea under a parachute, and can be rescued from the campaign map (see EVENTS).")
rep(12,"An air meeting can be settled from a window that shows your chance of victory, using points and dice.","An air meeting can be settled from a window in the game's own style that shows your chance of victory, using points and dice.")

# ---------- page 14 TORPEDOES ----------
rep(13,H('Water towers')+"A torpedo hit throws up a white tower of water about 100 m high that falls back as foam and drifting mist.",
 H('Splash')+"A torpedo hit throws up the game's own big splash, made two and a half times larger.")
rep(13,"A torpedo that breaks the keel of a destroyer or escort sets off both magazines and splits the ship in two.","A torpedo that breaks the keel of a destroyer or escort sets off both magazines and splits the ship in two. Bigger ships do not break from torpedoes, but a magazine blast can tear any ship apart.")

# ---------- page 15 BATTLE UI ----------
rep(14,"General, Hit log and Crew. Press F2 or click a tab.","General, Hit log and Crew. Press F2 or click a tab. All three start empty in every new battle.")
b[14]=b[14].replace(H('Keys'), H('Main menu')+"The CHANGE LOG button at the top right opens the list of what changed in this version.\n\n"+H('Keys'))

# ---------- page 16 CREDITS ----------
rep(15,"The broken ship ends, floating wreckage, oil slicks, parachutes and airmen were made for the mod in Blender.","The broken ship ends, floating wreckage, oil slicks, parachutes and airmen were made for the mod in Blender. The fire animation comes from a fire simulation made for the mod.")

titles_old=["SMARTER AI"]; titles_new=["ENEMY AND ALLIED AI"]
json.dump(b,open('bodies_new.json','w'))
for i,(o,n) in enumerate(zip(old,b)): print(i+1,len(o),'->',len(n))
# map
m=[{"type":"ModGuide","old":o,"new":n} for o,n in zip(old,b) if o!=n]
m.append({"type":"ModGuide","old":"SMARTER AI","new":"ENEMY AND ALLIED AI"})
json.dump(m,open('map_guide.json','w'))
# preview
import re
with open('book_text_preview_0.30.txt','w') as f:
    t=["WHAT'S NEW","EVENTS","SUPPLY","CUSTOM SHIPS","CUSTOM AIRCRAFT","MAP AND AIR BASES","STARTING FORCES","REPAIR AND DAMAGE","SINKING AND EXPLOSIONS","CREWS AND VETERANCY","FUEL AND SHIPS","ENEMY AND ALLIED AI","AIR","TORPEDOES","BATTLE UI AND KEYS","CREDITS"]
    for i,x in enumerate(b): f.write(f"=== PAGE {i+1}: {t[i]} ===\n"+re.sub(r'<[^>]+>','',x)+"\n\n")
