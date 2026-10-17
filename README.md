Everything here is a WIP and still in testing.
This is for game version 1.09a (the newest version of the game).
Current mod version: v0.24.2 (see the change log for everything that's in it)
The supply convoy event (v0.22.4) appears but does not sail to your home port by itself yet (fix planned). The TTE ships (v0.23 to v0.23.2) are not fully tested yet. v0.20.9 failed its test, so work on aircraft is on hold.

If there's something you'd like to use for your own mod, please give credit.

I don't know if some of the stuff I've worked on is also being worked on by someone else.
If it is, give them credit instead of me, since they had the idea first.

The events and the survivors system were inspired by Kiko. 
The Hitlog system is a 'copy' from the ADBA Mod Teams Hitlog system, so thanks to them for the inspiration for mine

-------------------------------------------------
CREDITS - CUSTOM SHIPS (TTE)
-------------------------------------------------

ALL custom merchant ships currently in the game (merchants, transports, the hospital ship, oilers and the destroyer escort / transport)
come from the TTE mod team. They are NOT my own creation: I did not make the models, and
all credit for them goes to the TTE team.
I have used the TTE team's assets and credit them for it. The TTE mod is about 4 years old and the team is no longer active.
If any member of the TTE team wants their assets removed from this mod, I will remove them at their request.

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
WHAT'S IN IT (short version)
-------------------------------------------------

- Ships have to be ordered and built, with build times and deposits
- Fuel system, repair costs and home ports
- Both sides start with the same forces: a carrier group, a cruiser group, destroyer patrols and subs
- Task forces of up to 20 ships, new formations, and bigger AI fleets
- Several task forces can join the same battle (pincers)
- Lasting damage: knocked-out equipment stays broken until you get to a port
- Damaged ships slow their task force, ships can list and capsize, counter-flooding
- Damage control works on the most urgent job first, and fires being fought can't spread
- Smarter AI: AI fleets hold formation, coordinate torpedo attacks, think before chasing you,
  retreat away from you (not into you), and subs ambush from further out and come back for more
- Air: up to 72 planes per side, mixed strike packages, strikes arrive in one wave,
  real steep dive bombing, bombers attack on their own, hammer and anvil torpedo attacks,
  escorts that protect their bombers, CAP that follows its carrier
- Air rework: every plane type has its own toughness and armour, guns do damage by calibre
- Darker nights, and burning ships are easier to spot
- Battle speed up to x10
- Troops use supplies every day and the AI sends convoys to its low-supply outposts; you get an Admiralty supply convoy every 20-30 days
- Historical torpedo dud rates, and torpedoes that hit at a glancing angle bounce off
- 23 extra merchant ships, oilers and transports from the TTE team, in limited numbers (10-30 of each type)
- A book button on the campaign map that lists the features and the change log

NEW IN v0.18 - CREWS
- Veterancy only counts from real fights (an enemy has to be there, and something has to be sunk or shot down)
- Every ship has its real crew size (hover over a ship to see "Men")
- Ships lose men from hits, fires and flooding. Losing men costs progress towards the next rank
- Short-handed ships (below 80% crew) reload and repair slower and have fewer damage control parties
- Taking on new recruits at port (Rearm) resets your progress, or drops a rank
- Survivors: when a ship sinks, her crew go into the water. Stop near them (within 300 m, 5 knots or less) to pick them up.
  Your own men refill your crews without losing experience. Enemy survivors become prisoners (command points)
- Events: every few days a ship is reported sunk somewhere on the campaign map.
  Sail a task force to the lifebuoy marker within 24 hours to save the survivors (or take enemy ones prisoner)

NEW IN v0.19 - UI
- Message log tabs: the battle message log now has three tabs, General, Hit log and Crew. Press F2 or click a tab to switch.
  Hit log lists every hit on a ship, e.g. "Monaghan hit Dale with an HE shell: armour held, fire".
  Crew lists your casualties, short-handed ships, survivors and rescues.
- Group orders: Ctrl+A all ships, Ctrl+D destroyers, Ctrl+C cruisers, Ctrl+B battleships and carriers.
  Ctrl+Shift+1-5 saves the ticked ships as a group (the number shows on the roster), Ctrl+1-5 selects it again.
  Speed, rudder and waypoints now go to every ticked ship.
- Minimap: torpedo tracks, smoke screens, lookout and radar range rings, and a red X where an enemy was last seen.
  Switch each on or off with the buttons above the map toolbar (bottom right), or all of them with F11.
- Damage control colours: yellow light damage, orange heavy damage, red knocked out (fixable at sea),
  black destroyed or needs a port, grey patched as far as it can go (needs a port).
  Engine rooms can always be repaired at sea, but only back to 50% health and half power until a port repair.
- Torpedoes that hit high on a ship now always do damage (this was a bug in the base game)

NEW IN v0.20 - AI
- AI task forces that start far away no longer sail in circles: a ship that isn't closing in steers straight at you
  for a few minutes (but never into land or shallows)

NEW IN v0.21 - TORPEDOES AND CAMPAIGN MAP
- Faster ship buying: after you order a ship, the name list moves on to the next ship of that class you can still buy
- Torpedo dud rates are historical (US Mark 13/14/15 fail often, Mark 18 about 10%, Japanese torpedoes 3-6%).
  Only active when the game's "dud torpedoes" option is on
- Torpedoes that hit a ship at a glancing angle (under 15 degrees) bounce off and keep running. The early US torpedoes
  also dud more on a square 90 degree hit and less on angled hits. Bounces show in the Hit log
- Hit log: torpedo and bomb hit lines no longer clutter the General tab
- Fuel overlay: click the fuel barrel button at the top left of the campaign map, or press F11. Every task force of yours gets a label
  (days of fuel left, speed) and the selected one gets a ring showing how far it sails in 1 day
- Rules popups: new pages Torpedoes, Extra UI Parts and Extra Features at the start of a campaign

NEW IN v0.22 - SUPPLY
- Troops use supplies: each location with troops spends supplies every day (3% of the troop number). A garrison that runs dry slowly loses troops.
  The location panel shows how many days of supply are left
- The AI sends supply convoys to its outposts that are running low. You can sink them
- Weekly supplies at home ports went from 4,000 to 6,000, and outposts start with 1 supply per troop (was 2)
- Admiralty supply convoy (v0.22.4, not tested yet): every 20-30 days a convoy of 3 transports, 1 oiler and destroyers appears on the northern edge
  of the map and sails to your home port. The enemy knows where it is for the first 6 hours. Ships that are sunk take their cargo with them

NEW IN v0.22.5 - IN-GAME BOOK
- A book button at the top left of the campaign map (the fuel barrel is now under it). Click it to read what's new and the features of the mod, page by page

NEW IN v0.24 - SHIPS AND AIRCRAFT FROM RamZ'S CATALOGUE (by RamZ, not by me)
- Thank you to RamZ, whose Unit Catalog is public use: 84 warships (v0.24.1) and 93 aircraft (v0.24.2) for Japan, USA and Australia. They are RamZ's work. He is also credited for the TTE merchant ships, which are believed to be his.
- 20 more warships (v0.24.1) and 22 aircraft (v0.24.2) from the TTE team, credited to them.
- Costs and dates are my estimates and it is not fully tested yet. Steps: Docs/new_ships_v0.24.md

NEW IN v0.23 - TTE SHIPS (by the TTE team, not by me)
- 23 merchant ships, transports, a hospital ship, an oiler (Patapsco) and a destroyer escort (Manley) from the TTE mod, used with credit to the TTE team
- Allied: Heywood, President Jackson, Attack Transport, Hospital Ship, Arcturus, Harris, Mount Hood, McCawley, Patapsco, Manley.
  Japanese: Generic Maru, Type 1B, 1C, 1K, 2TL, 3A, Type A Merchant, Ural Maru, Akita Maru, Kasagisan Maru, Taihosan Maru, Hakushika Maru, Aratama Maru
- The AI uses them in its convoys (a random mix), and you can buy them
- Limited numbers (v0.23.1): each type has a pool of 10-30 ships for each side. A ship that is built or sunk is gone for good. The three stock merchants stay unlimited
- The Manley sits between the submarines and the destroyers in the ship list (v0.23.2)
- Install: the ship models (3D files) are not in this repo. See Docs/tte_merchants.md

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
