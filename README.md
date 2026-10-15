Everything here is a WIP and still in testing.
This is for game version 1.09a (the newest version of the game).
Current mod version: v0.20 (see the change log for everything that's in it)

If there's something you'd like to use for your own mod, please give credit.

I don't know if some of the stuff I've worked on is also being worked on by someone else.
If it is, give them credit instead of me, since they had the idea first.

The events and the survivors system were inspired by Kiko. 
The Hitlog system is a 'copy' from the ADBA Mod Teams Hitlog system, so thanks to them for the inspiration for mine

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
- Battle speed up to x10battle

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

The full list is in the change log. The rules pages at the start of a campaign explain it all in game.

-------------------------------------------------
FOUND A BUG?
-------------------------------------------------

Send me this file:
...\War on the Sea\WarOnTheSea_Data\output_log.txt

Send it BEFORE you start the game again. It gets wiped every time the game starts.
The mod writes notes into it (lines starting with things like [CREW], [RESCUE], [VET], [TORP], [AIRAI], [TFJOIN], [HITLOG], [AIMOVE], [REPAIR])
that help me find what went wrong.

Tester keys:
F9 - show all enemy task forces (campaign map)
F4 - create a "ship sunk, survivors adrift" event straight away (campaign map)
F3 - developer view (battle): enemy ships' distance, speed and what the AI is doing

-------------------------------------------------

PLEASE!! Back up your stuff. If you have other mods, back up their Override files and Assembly files.
I don't wanna be blamed if you want to change mods afterwards and something is broken.
