# 0.31.14 ship break-up and physics sinking

Built on 0.31.13 animated fire (md5 5b0cac40), so it has everything up to 0.31.13.
DLL md5: dc4bd5151007a8b4200c6d0e149d141b. Not tested in game yet.

## Install

1. Close the game.
2. Back up `WarOnTheSea_Data\Managed\Assembly-CSharp.dll` by renaming it to `Assembly-CSharp.dll.0313`.
3. Copy `Assembly-CSharp.dll` from this folder into `WarOnTheSea_Data\Managed\`.
4. Open `WarOnTheSea_Data\StreamingAssets\override\mod_wreck\` (the folder that already holds the destroyer breaks from 0.29).
5. Copy everything inside this pack's `mod_wreck` folder into it. Say **yes** to replacing `units.txt`. Keep the files that are already there.
6. Start the game. The main menu should say **Version 0.31.14**.

## What changed

1. **Torn break pieces for every ship.**
   - Before, only destroyers and escorts had pre-made torn, burnt break pieces.
   - Now every surface ship has them: battleships, carriers, cruisers, merchants, oilers and transports (137 ships, 3 breaks each: near the bow, midships and near the stern).
   - A magazine blast near the bow of a battleship tears the whole bow off with jagged plating, burnt edges and the dark inside of the hull showing.
   - Submarines are left out, as before.
2. **Real sinking physics for every wreck.**
   - The old sinking was a script: each ship followed set moves.
   - Now each wreck is a hull made of cells that float, fill with water and pass it on to the next cells. Nothing is scripted.
   - A ship holed on one side takes water on that side, lists and can roll over.
   - A ship holed at one end goes down by that end while the other end rises.
   - A ship that floods evenly settles lower and lower, then goes.
   - Wrecks in shallow water come to rest on the seabed and can stick out of the water.
3. **Broken halves sink on the same physics, destroyers included.**
   - A torpedo that breaks a destroyer's back still kicks the break up first. Then each half floods through its torn end, the broken ends go down, bow and stern rise, and they stand on end before they slide under.
   - Each half moves on its own, so no two sinkings look the same.
4. Torpedo break-back is still for destroyers and escorts only. Magazine blasts can still break any ship.

See `previews/`: the Colorado with its bow blown off and broken at midships, a cargo ship broken in two, and a Colorado split by a magazine blast and sinking on the new physics (frames made from the mod's own physics code).

## What to test

1. Sink a destroyer with torpedoes until it breaks in two. Both halves should flood and go down on their own, not in step.
2. Blow up a battleship or cruiser magazine (the forward magazine is best). The bow should come off as a torn piece.
3. Sink a ship slowly with gunfire. It should list or go down by the bow or stern depending on where it was hit.
4. If anything looks wrong, send me `output_log.txt`. Look for lines that start with **`[SINK]`** and **`[WRECK]`**. They say which pre-made break was used and how each wreck is flooding.

## Settings (in ModSinking, for later tuning)

- `FSK` (0.3): how easily a flooded ship rolls over. Higher means more capsizes.
- `FreeboardK` (1.4): how much hull there is above the water. Lower means ships sink sooner.
- `BreakTime`, `MagTime`, `PlungeTime`, `CapsizeTime`, `SettleTime`: about how long each kind of sinking takes for a 2000 t ship.
