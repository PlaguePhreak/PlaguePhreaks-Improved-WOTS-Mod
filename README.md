Everything here is a WIP and still in testing.
This is for game version 1.09a (the newest version of the game).
Current mod version: v0.24.2 (see the change log for everything that's in it)
The supply convoy event (v0.22.4) appears but does not sail to your home port by itself yet (fix planned).
v0.20.9 failed its tests, so work on aircraft is on hold.

If there's something you'd like to use for your own mod, please give credit.

I don't know if some of the stuff I've worked on is also being worked on by someone else.
If it is, give them credit instead of me, since they had the idea first.

The events and the survivors system were inspired by Kiko. 
The Hitlog system is a 'copy' from the ADBA Mod Teams Hitlog system, so thanks to them for the inspiration for mine

-------------------------------------------------
CREDITS - CUSTOM SHIPS 
-------------------------------------------------

Almost all of the custom merchant ships currently in the game (merchants, transports, the hospital ship, and oilers)
come from the TTE mod team. They are NOT my own creation: I did not make the models, and all credit for them goes to the TTE team.

If any member of the TTE team wants their assets removed from this mod, I will remove them at their request.

I have also used RamZ Catalogue for all the custom ships in the mod, so all credit goes to him for those.

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
- Air rework: mixed strike packages, steep dive bombing, escorts that protect bombers, and aircraft with their own toughness
- Supply: troops use supplies every day, and the AI sends (and you can sink) supply convoys
- Historical torpedo dud rates, and glancing torpedo hits bounce off
- Custom ships and aircraft from RamZ's catalogue and the TTE mod, built like any other ship
- Battle UI: message log tabs, group orders, minimap layers, a fuel overlay on the campaign map and an in-game book
- Darker nights, and battle speed up to x10

COMING NEXT (see the Roadmap file)
- v0.25: new map locations to fight for (planned, after v0.24.1 and v0.24.2 are tested)
- Fix for the Admiralty supply convoy so it sails to your home port by itself
- Small text fix: the Ship Orders rules page says light carriers take 30 days, but the game uses 42

The full list is in the change log. The rules pages at the start of a campaign explain it all in game.

-------------------------------------------------
FOUND A BUG?
-------------------------------------------------

Send me this file:
...\War on the Sea\WarOnTheSea_Data\output_log.txt

Send it BEFORE you start the game again. It gets wiped every time the game starts.
The mod writes notes into it (lines starting with things like [CREW], [RESCUE], [VET], [TORP], [AIRAI], [TFJOIN], [HITLOG], [AIMOVE], [REPAIR], [TORPHIT], [TFOVERLAY], [SUPPLY], [CONVOY])
that help me find what went wrong.

Tester keys:
F9 - show all enemy task forces (campaign map)
F4 - create a "ship sunk, survivors adrift" event straight away (campaign map)
F3 - developer view (battle): enemy ships' distance, speed and what the AI is doing

Other keys:
F11 - fuel overlay on / off (campaign map). In battle F11 switches the minimap layers on / off
F2 - switch message log tab (battle)
Ctrl+A / D / C / B and Ctrl+1-5 - group orders (battle)

-------------------------------------------------

PLEASE!! Back up your stuff. If you have other mods, back up their Override files and Assembly files.
I don't wanna be blamed if you want to change mods afterwards and something is broken.
