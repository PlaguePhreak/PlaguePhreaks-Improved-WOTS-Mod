# v0.29: ships blow up, break in two and sink for real

Builds on 0.28.18 + the hotfix (your current build). Nothing from the Pacific War pack is needed.
Not compiled in the game by me: back up `Assembly-CSharp.dll` first. I did test-compile the two new classes against your DLL here (with stand-in Unity files), so names and types match your build.

## dnSpy steps, in this order

1. **ModSinkFx** (NEW class): in the tree, right-click the `-` (empty) namespace under Assembly-CSharp > **Add Class (C#)...**, select all, delete, paste all of `1_NEW_ModSinkFx.cs.txt`, **Compile**.
2. **ModSinking** (NEW class): same way, **Add Class (C#)...**, paste all of `2_NEW_ModSinking.cs.txt`, **Compile**. (Step 1 must be in first.)
3. **Three one-line additions in DamageableSea**, exact places in `3_DamageableSea_three_lines.txt`:
   - A) `DamageableSea.SinkShip`: last line `ModSinking.Begin(this);`
   - B) `DamageableSea.ApplyMagazineExplosion`: last line `ModSinking.AfterMagazine(this, cv);`
   - C) `DamageableSea.ApplyDamage`: in the torpedo break-back part, `ModSinking.TorpedoBreakBack(this, text);`
4. **ModVersion**: Edit Class, paste all of `4_ModVersion.cs.txt` (menu shows 0.29 and the new changelog), **Compile**.
5. **File > Save Module**.

## What it does

**1. Torpedo breaks a destroyer's back.** The stock game already has a "break-back" roll for a torpedo hit under a ship with no torpedo protection (config `torpBreakBackValues`): it destroys the keel squares. Now on a destroyer or destroyer escort it also sets off a huge explosion at the hit: the game's own `explosionMagazine` effect (it is in the game files but the stock game never uses it) made 3 times bigger, 3 to 5 more blasts along the hull over the next few seconds, a water column and a smoke pillar. The ship breaks in two at the hit and is sunk. Both halves sink in a V: the bow half rises bow-up, the stern half stern-up, they drift apart and slide under in about 1.5 minutes. Message log: "... breaks in two!".

**2. Lethal magazine explosions.** When a magazine blows (stock: 1% chance per damaging hit on a magazine square), the mod counts the squares the blast covers. More than 9 = lethal: a big explosion (2.2 x the magazine effect) and the ship is sunk. 3 times in 4 it also breaks: a magazine near midships splits it in half, one near the bow blows the bow off, one near the stern blows the stern off. The rest of the time it plunges fast by the end that blew up. A blast of 9 squares or fewer stays as in the stock game. Message log: "... blows up!".

**3. Realistic sinking for every ship** (not submarines, they keep the stock sinking). The stock game made the ship roll over on a physics joint. Now the way it goes depends on where it flooded:
- flooded on one side, or already listing over 25 degrees: it **capsizes**, rolls right over, floats keel-up for a while, then goes.
- flooded at one end: it **plunges** by that end; it settles by the bow (or stern), the other end rises out of the water, then it slides under.
- flooded evenly, or scuttled: it **settles** slowly and level, then goes down by one end at the last.

Times for a 2000 t destroyer: break in two 1.5 min, plunge 6 min, capsize 5 min, settle 10 min (battle time, so about a tenth of that at x10). Big ships take up to 2.5 x longer. In shallow water the wreck hits the seabed and stays there, and in very shallow water it can stick out of the sea.

**4. Debris and oil.** Where a ship sinks, wreckage floats up as it goes under: planks, crates, barrels, steel plates, rafts and burnt timber (20 to 40 pieces, they bob on the waves and drift), and an explosion throws half of it into the air. An oil slick spreads out from the wreck for 10 to 20 minutes and fades after about 45. An oiler's slick is 2.5 x bigger and burns 60% of the time; a ship that blew up has a 25% chance of burning oil.

## What dnSpy can't do, and what I did instead

There are no models of half ships, and dnSpy can't make new models. So the half that breaks off is a copy of the ship's own meshes made while the game runs: every part of the ship (turrets, funnels, masts...) goes to the half it is on, and the hull mesh is cut in two at the break. If the game won't let the mod read a mesh, both halves keep the whole hull and the missing half is simply pushed under the water as it tilts, so you still see a V. The log says which happened ("meshes cut 3, copied whole 0"). The cut edge is open (you might see into the hull), but it sits in the water and the smoke. Debris pieces are simple shapes (boxes and drums), and the oil slick is flat, so in a heavy sea wave crests can poke through it.

## What to test

1. Torpedo a destroyer (Long Lances do it best): it should blow up and break in two. Log: `[SINK] ... torpedo BROKE ITS BACK` and `[SINK] ... breaks in two: cut ... meshes cut N, copied whole M`.
2. Magazine explosions are rare. To test, set `"magazineExplosionProbability":0.5` in your Override `config.txt` for one battle (it is 0.01), then shell a cruiser. Log: `[SINK] ... magazine explosion ... the blast covers N squares`. Put it back to 0.01 afterwards.
3. Sink ships by flooding and watch how they go. Log: `[SINK] ... sinks: capsizes to port ...` or `plunges bow first ...` or `settles low in the water ...`.
4. Sink something near land (shallow water): `[SINK] ... hits the seabed at ... m`.
5. Look for debris and the dark oil slick where ships went down. **If you can't see the slick at all**, tell me: it's one number to change (`OilQueue` 3100 to 4000).
6. Send me `output_log.txt` and say how the explosions look (too big or small) and how long the sinking takes. All the numbers are knobs at the top of ModSinking (`BreakFxScale`, `MagFxScale`, `LethalCells`, `LethalSplitChance`, `BreakTime`, `PlungeTime`, `CapsizeTime`, `SettleTime`, `DebrisMax`, `OilSize`, `OilLife`...). `On = false` switches the whole thing off.

If anything goes wrong inside the mod, it writes `[SINK] ... failed` once and hands every sinking ship back to the stock game.
