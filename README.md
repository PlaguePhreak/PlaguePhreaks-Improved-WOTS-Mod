PLAGUE'S BETTER WOTS MOD
=========================

Everything here is a work in progress and still in testing.
This is for game version 1.09a (the newest version of the game).
Current mod version: v0.28.11 (see the Change Log for everything that is in it, and the BOOK button in game for a plain-words version).

This build is the air combat update. Dogfights, the flight model, aircraft damage and fuel are new since v0.25, and that is what I most want tested right now (see TESTING NOTES below).

If there's something you'd like to use for your own mod, please give credit.

I don't know if some of the stuff I've worked on is also being worked on by someone else.
If it is, give them credit instead of me, since they had the idea first.

The events and the survivors system were inspired by Kiko. Fuel fires are Kiko's idea, and parts falling off a damaged plane is Avaricles' idea.
The Hitlog system is a 'copy' from the ADBA Mod Team's Hitlog system, so thanks to them for the inspiration for mine.

-------------------------------------------------
CREDITS - CUSTOM SHIPS AND AIRCRAFT
-------------------------------------------------

Almost all of the custom merchant ships currently in the game (merchants, transports, the hospital ship, and oilers)
come from the TTE mod team. They are NOT my own creation: I did not make the models, and all credit for them goes to the TTE team.

If any member of the TTE team wants their assets removed from this mod, I will remove them at their request.

I have also used RamZ's Catalogue for all the custom ships and aircraft in the mod, so all credit goes to him for those.

I have no experience in modding or coding, so I'm using an AI (Claude) to help me write the code.
I test everything myself in game and decide what goes in.

I currently have no plans to make the mod public, but I'm happy to share it with anyone who'd like to try it.

-------------------------------------------------
INSTALLING
-------------------------------------------------

Assembly-CSharp.dll goes into
...\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed

The Override folder goes into
...\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets

(For me that's E:\SteamLibrary\steamapps\common\War on the Sea\... yours might be on a different drive.)

Start a NEW campaign. Old saves might act weird.

Do NOT use Steam's "Verify integrity of game files". It will put the original files back and wipe the mod.

-------------------------------------------------
MAIN FEATURES
-------------------------------------------------

- Ships have to be ordered and built, with build times and deposits. Fuel, repair costs and home ports
- Bigger fleets: task forces of up to 20 ships, several task forces in one battle, and smarter AI that holds formation and coordinates torpedo attacks
- Lasting damage, listing and capsizing ships, and damage control that works on the most urgent job first
- Crews: real crew sizes, losses, veterancy from real fights, and survivors you can rescue
- Supply: troops use supplies every day, and the AI sends (and you can sink) supply convoys
- Historical torpedo dud rates, and glancing torpedo hits bounce off
- Custom ships and aircraft from RamZ's catalogue and the TTE mod, built like any other ship: 100+ ships and 115 aircraft
- A bigger map: the New Guinea front, ten new locations, every air base with its own historical mix of aircraft, and real-looking starting fleets
- Air rework: mixed strike packages, steep dive bombing, escorts that protect bombers, and aircraft with their own toughness
- Air combat (v0.26 to v0.28): a real flight model (dives gain speed, climbs lose it, stalls, flaps), every aircraft with its own performance table,
  pilots who judge energy and choose boom-and-zoom, turn fighting or disengaging, dogfight manoeuvres (yo-yos, Immelmann, split-S, scissors, Thach weave,
  wingman cover), pilot ranks, damage that changes how a plane flies (engine, wings, fuel leaks, fires, parts falling off), realistic fuel, and planes
  that leave the fight when out of ammunition, short of fuel or too damaged
- Battle UI: message log tabs, group orders, minimap layers, a fuel overlay on the campaign map, an in-game book, and a flight readout (F8)
- Darker nights, and battle speed up to x10

COMING NEXT (see the Roadmap file)
- More air combat tuning from your test logs (Wildcat tactics against Zeros, escort stations)
- v0.25.3: shorter aircraft range and realistic launch, landing and rearming times
- A settings menu to switch the mod's features on and off

The full list is in the Change Log. The rules pages at the start of a campaign explain it all in game.

-------------------------------------------------
TESTING NOTES FOR THIS BUILD
-------------------------------------------------

- Air combat is the thing to test. Fight some air battles (carrier CAP against a strike, fighters against fighters) and send me the log.
- Battle speed x8 to x10 is fine, the flight model runs on battle clock time.
- Plane-to-plane collisions are switched OFF in this build (they cost too many planes in testing). Planes pass through each other like in the stock game.
- A plane at bingo fuel (10%), out of ammunition, or too damaged leaves the battle on its own and flies to the edge of the area.
- Fighters do not chase a plane that is leaving while there are others still fighting.
- Your fire key works on the plane you have selected, for a short burst, as long as the nose is on the target.

-------------------------------------------------
FOUND A BUG?
-------------------------------------------------

Send me this file:
...\War on the Sea\WarOnTheSea_Data\output_log.txt

Send it BEFORE you start the game again. It gets wiped every time the game starts.
The mod writes notes into it (lines starting with things like [DOGFIGHT], [GUN], [BATTLE], [FLIGHT], [DAMAGE], [FUEL], [CREW], [RESCUE], [VET], [TORP],
[AIRAI], [TFJOIN], [HITLOG], [AIMOVE], [REPAIR], [TORPHIT], [TFOVERLAY], [SUPPLY], [CONVOY]) that help me find what went wrong.
Tell me the time compression you were running at and roughly what the fight was (how many planes of what type on each side).

Tester keys:
F9 - show all enemy task forces (campaign map)
F4 - create a "ship sunk, survivors adrift" event straight away (campaign map)
F3 - developer view (battle): enemy ships' distance, speed and what the AI is doing
F8 - flight readout (battle): speed, height, energy, damage, fuel and what the pilot is doing, for the selected plane

Other keys:
F11 - fuel overlay on / off (campaign map). In battle F11 switches the minimap layers on / off
F2 - switch message log tab (battle)
Ctrl+A / D / C / B and Ctrl+1-5 - group orders (battle)

-------------------------------------------------

PLEASE!! Back up your stuff. If you have other mods, back up their Override files and Assembly files.
I don't wanna be blamed if you want to change mods afterwards and something is broken.
