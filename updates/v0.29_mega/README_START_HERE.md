# v0.29 mega change: ships blow up, break in two and sink for real

This is everything for 0.29 in one go: the sinking rework, the broken destroyer models made in Blender, and the new explosion.
It builds on 0.28.18 + the hotfix (your current build). It replaces the earlier `v0.29_sinking` pack: use this one only.

Back up `Assembly-CSharp.dll` first. I can't run the game here, but I test-compiled all three new classes against your DLL (with stand-in Unity files), so the names and types match your build.

## Part A: copy the art folder (no dnSpy)

Copy the folder **`mod_wreck`** from this pack into:

`E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets\override\`

so you end up with `...\StreamingAssets\override\mod_wreck\units.txt` (plus `boom.png`, `burnt.png` and 138 `.brk` files, about 135 MB).

## Part B: dnSpy, in this order

1. **ModSinkFx** (NEW class): in the tree, right-click the `-` (empty) namespace under Assembly-CSharp > **Add Class (C#)...**, select all, delete, paste all of `1_NEW_ModSinkFx.cs.txt`, **Compile**.
2. **ModWreckArt** (NEW class): same way, **Add Class (C#)...**, paste all of `2_NEW_ModWreckArt.cs.txt`, **Compile**.
3. **ModSinking** (NEW class): same way, **Add Class (C#)...**, paste all of `3_NEW_ModSinking.cs.txt`, **Compile**. (Steps 1 and 2 must be in first.)
4. **Three one-line additions in DamageableSea**, exact places in `4_DamageableSea_three_lines.txt`:
   - A) `DamageableSea.SinkShip`: last line `ModSinking.Begin(this);`
   - B) `DamageableSea.ApplyMagazineExplosion`: last line `ModSinking.AfterMagazine(this, cv);`
   - C) `DamageableSea.ApplyDamage`: in the torpedo break-back part, `ModSinking.TorpedoBreakBack(this, text);`
5. **ModVersion**: right-click ModVersion > Edit Class (C#)..., paste all of `5_ModVersion.cs.txt` (menu shows 0.29 and the new changelog), **Compile**.
6. **File > Save Module**.

If a Compile shows a red error, don't save: send me the error text.

## What it does

**1. Torpedo breaks a destroyer's back.** The stock game has a "break-back" roll for a torpedo hit under a ship with no torpedo protection (config `torpBreakBackValues`). Now on a destroyer or destroyer escort it sets off the new explosion: a white flash, an orange fireball bursting out of the sea, black smoke with fire glowing through it, climbing on a column into a mushroom cloud about 250 m high (two smaller blasts go off next to it). The ship breaks in two and both halves sink in a V, bow and stern rising out of the water, in about 1.5 minutes. Message log: "... breaks in two!".

**2. The broken ends look broken.** Every destroyer and escort (all 50, including the modded 1942-45 ones) has three pre-made breaks made in Blender: forward, midships and aft. The game picks the one nearest the hit. The break is torn and jagged, the plating is crumpled and bent outwards, the edges are burnt black, and you can see into the dark, burnt hull with its torn decks and a bulkhead. Turrets, guns and directors are never cut in half: each one goes down whole with the half it stands on. If a hit is far from all three (or a ship isn't a destroyer), the ship is cut straight at the hit as before.

**3. Lethal magazine explosions.** When a magazine blows (stock: 1% chance per damaging hit on a magazine square), the mod counts the squares the blast covers. More than 9 = lethal: the new explosion, and the ship is sunk. 3 times in 4 it also breaks: a magazine near midships splits it in half, one near the bow blows the bow off, one near the stern blows the stern off. The rest of the time it plunges fast by the end that blew up. 9 squares or fewer stays as in the stock game. Message log: "... blows up!".

**4. Realistic sinking for every ship** (not submarines). How it goes depends on where it flooded:
- flooded on one side, or already listing over 25 degrees: it **capsizes**, floats keel-up for a while, then goes.
- flooded at one end: it **plunges** by that end, the other end rising out of the water.
- flooded evenly, or scuttled: it **settles** slowly and level, then goes down by one end.

Times for a 2000 t destroyer: break in two 1.5 min, plunge 6 min, capsize 5 min, settle 10 min (battle time). Big ships take up to 2.5 x longer. In shallow water the wreck comes to rest on the seabed.

**5. Debris and oil.** Wreckage floats up where a ship sinks (planks, crates, barrels, plates, rafts, burnt timber), an explosion throws half of it into the air, and an oil slick spreads and fades after about 45 minutes. An oiler's slick is bigger and burns 60% of the time; a ship that blew up has a 25% chance of burning oil.

## What dnSpy can't do, and what I did instead

dnSpy can't add models to the game's asset bundles, so the broken parts are files the mod reads itself (`.brk`, in `mod_wreck`), and the explosion is a 64-frame picture (`boom.png`) played on a card that always faces the camera. Only the torn middle part of each break is in the files; the rest of each half is the ship's own model cut exactly where the torn part starts, so it always has the right paint and damage marks. If the `mod_wreck` folder is missing, everything still works the old way (straight cut, the game's own explosions).

## What to test

1. Look in `output_log.txt` for `[WRECK] break kits folder ...\mod_wreck/, 50 ships listed`. If it says `units.txt NOT FOUND`, the folder is in the wrong place.
2. Torpedo a destroyer (Long Lances do it best). Log: `[SINK] ... torpedo BROKE ITS BACK`, then `[WRECK] loaded fletcher_mid.brk ...` and `[SINK] ... pre-made break fletcher_mid.brk: torn parts N on the ship, N on the broken-off half`. Look at the broken ends close up.
3. The explosion: log `[WRECK] explosion picture loaded (2048 x 2048, shader Sprites/Default)`. Tell me if it is too big, too small, too fast or too slow (`BoomSize`, `BoomTime` at the top of ModWreckArt), and whether it shows in front of or behind the sea properly (`BoomQueue`).
4. Magazine explosions are rare. To test, set `"magazineExplosionProbability":0.5` in your Override `config.txt` for one battle (it is 0.01), then shell a destroyer or cruiser. Put it back to 0.01 afterwards.
5. Sink ships by flooding: `[SINK] ... sinks: capsizes ...` or `plunges ...` or `settles ...`.
6. Look for debris and the dark oil slick. If you can't see the slick at all, tell me: it's one number (`OilQueue` 3100 to 4000).
7. Send me `output_log.txt` and say how it all looks.

All the numbers are knobs at the top of ModSinking and ModWreckArt. `ModSinking.On = false` switches the whole thing off; `ModWreckArt.UseKits` / `UseBoom = false` switch off just the new models or just the new explosion.

If anything goes wrong inside the mod, it writes `[SINK] ... failed` once and hands every sinking ship back to the stock game.
