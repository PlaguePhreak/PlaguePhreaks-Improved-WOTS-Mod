# Debris and oil slick art for sinking ships (add-on to the 0.29 mega pack)

This goes in **together with the v0.29 mega pack**. It adds one new class, ModDebrisArt, and gives you a new ModSinking that **replaces** `3_NEW_ModSinking.cs.txt` from the mega pack. Use this ModSinking, not that one. Everything else in the mega pack stays as it is.

I can't run the game, so back up `Assembly-CSharp.dll` first. I did test-compile the new classes together with the mega pack's ModSinkFx and ModWreckArt against your DLL (with stand-in Unity files), and there were no errors.

## Part A: copy the art folder (no dnSpy)
Copy the folder **`mod_debris`** from this pack into the same place as the mega pack's `mod_wreck`:

`E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets\override\`

so you end up with `...\StreamingAssets\override\mod_debris\debris_atlas.png` (21 files: 14 models, the debris texture, 3 oil shapes and 3 sheens, about 2 MB).

## Part B: dnSpy, in this order (this replaces mega pack steps 1 to 3)
1. **ModSinkFx** (NEW): right-click the `-` (empty) namespace under Assembly-CSharp > **Add Class (C#)...**, select all, delete, paste all of the mega pack's `1_NEW_ModSinkFx.cs.txt`, **Compile**.
2. **ModWreckArt** (NEW): same way, paste all of the mega pack's `2_NEW_ModWreckArt.cs.txt`, **Compile**.
3. **ModDebrisArt** (NEW): same way, paste all of `1_NEW_ModDebrisArt.cs.txt` from this pack, **Compile**.
4. **ModSinking** (NEW): same way, paste all of `2_NEW_ModSinking.cs.txt` from this pack, **Compile**. Steps 1 to 3 must be in first.
5. Then carry on with the mega pack from its step 4: the three lines in `DamageableSea`, then `ModVersion`, then **File > Save Module**.

If a Compile shows a red error, don't save: send me the error text.

## What it does
- **Real wreckage.** The plain boxes and cylinders are replaced by the Blender models: planks, broken deck planking, crates, oil drums, ammo boxes, Carley floats, life rings, life vests, a hatch cover, bent steel plate, a broken spar, burnt timber and now and then a capsized ship's boat. An explosion still throws some of it into the air (only the pieces that look right flying: no rafts or boats in the air).
- **Oil that looks like oil.** Each slick is built from the three Blender oil shapes, turned and sized at random, so no two look alike. They have ragged edges and patches of open water, with a faint rainbow sheen on the thin edges. They still spread out, darken and fade the same way, and oilers still burn.
- Without the `mod_debris` folder, everything works as before (plain boxes, round slick).

## In the log (output_log.txt)
- `[DEBRIS] art loaded from ...mod_debris/: debris models 14, oil slick shapes 3`: all found.
- `[DEBRIS] folder ... NOT FOUND`: the folder is in the wrong place.

## Knobs
At the top of ModDebrisArt: `Scale` (model size, 1.2 = a little over real size; try 2 if they're hard to see), `SheenAlpha` (rainbow sheen, 0 = off), `UseModels`, `UseOilArt`. The amount of debris and the slick size, darkness and life are still the old knobs at the top of ModSinking (`DebrisMax`, `OilSize`, `OilAlpha`, `OilLife`, `OilQueue`).

## What to look at when you test
Sink a few ships and look at the wreckage and slick close up and from the normal camera. Tell me if the pieces are too small, the slick too dark or too faint, or the sheen too strong.
