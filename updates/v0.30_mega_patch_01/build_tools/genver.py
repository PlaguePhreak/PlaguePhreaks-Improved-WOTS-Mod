import json
d=json.load(open('dump/ModVersion.json'))
oldlog=[x['s'] for x in d if x['s'].startswith('<color=#E0B030><b>0.31.14')][0]
oldlab=[x['s'] for x in d if 'Version 0.31.14' in x['s']][0]
G=lambda t:'<color=#E0B030><b>'+t+'</b></color>'
S=lambda t:'<color=#E0B030>'+t+'</color>'
L=[G('0.30 Mega Patch 01'),
S('New'),
"- Allied AI: RAN task forces (yellow) patrol, fight, escort your merchants and supply your ports",
"- Your starting RAN force in the Allied campaign sails under RAN command",
"- Sea auto resolve for battles your allies fight",
"- Enemy AI rework, scaled by difficulty from Very Easy to Elite (switches in Mod Options)",
"- Enemy floatplanes and flying boats scout from every airfield; a pop-up names the force they spot",
"- Enemy strikes gather and attack together, sized to the ships they go for",
"- The enemy hunts you harder on the map; in battle it presses home and finishes cripples",
"- More aircraft types at every enemy airfield (new campaigns)",
"- Downed airmen show on the map; flying boats, floatplanes and ships pick them up",
"- Auto rescue button on the campaign map",
"- Real 3D animated ship fires that grow with every burning compartment and light up the sea",
"- Shell and bomb hits burst in 3D fire, smoke and sparks",
"- Every surface ship has torn, burnt break pieces",
"- Wrecks and broken halves sink on real physics: they flood, list, roll over or stand on end",
"- Real turning circles, rudder lag and momentum for every ship",
"- CHANGE LOG button in the main menu",
S('Changes'),
"- A magazine blast can tear any ship apart, even a battleship",
"- Torpedo break-back stays for destroyers and escorts",
"- The Pacific War campaign is in as \"Experimental. WIP might not work\"",
"- Nebraska (1944) removed from the ship lists",
S('Fixes'),
"- The supply convoy sat still; it now sails to your port and unloads",
"- The battle message log carried over from the last battle",
"",
G('0.29'),
"- Ships capsize, plunge by the bow or stern, or settle, by their flooding",
"- Torpedoes can break a destroyer's back: two magazine blasts, then she splits",
"- Magazine blasts sized by what is in them, in a new HMS Barham style",
"- Torpedo hits throw up a huge splash (the game's own, made bigger)",
"- Floating wreckage and spreading oil slicks where ships sink",
"- Shot planes shed real wings, tails, engines; crews bail out by parachute",
"- Air auto resolve window restyled to match the game",
"- Mod models now live in StreamingAssets/override/ModAssets",
"- Your ships answer your controls again; fewer planes explode",
"- Plus the 0.28 air combat update (0.28.18 and hotfix)"]
new='\n'.join(L)
m=[{"type":"ModVersion","old":oldlog,"new":new},
   {"type":"ModVersion","old":oldlab,"new":"Plague's Better WOTS mod\n<color=#E0B030>Version 0.30 Mega Patch 01</color>"}]
json.dump(m,open('map_ver.json','w')); print(len(oldlog),len(new)); print(new)
