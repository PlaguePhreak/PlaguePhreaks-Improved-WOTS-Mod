# 0.29.6: torpedo hits use the game's own splash

This is built on your tested 0.29.5 DLL and keeps everything in it. The only change: a torpedo hit no longer makes the white smoke "tower of water". It plays the game's own big splash (`splashLarge`) at the hit instead, made 2.5 times bigger (give or take 15%). That comes on top of the normal splash the game already plays there.

Nothing else changed. Magazine blasts, both magazines on a broken back, the smoke rules, plane parts and parachutes all work as in 0.29.5.

## Install

1. Close the game.
2. Go to `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`.
3. Rename `Assembly-CSharp.dll` to `Assembly-CSharp_0.29.5.dll` as a backup.
4. Copy `Assembly-CSharp.dll` from this folder into `Managed\`.
5. Start the game. The menu should say **Version 0.29.6**.

In the log, each torpedo hit shows `[SINK] <ship> torpedo hit: the game's big splash, x2.4`.

## Knob

`ModSinking.TorpedoSplash` = 2.5 sets how many times bigger the game's splash is. Set it to 0 and you only get the game's normal splash.

## Checks

- The DLL verifier lists the same harmless stock warnings as 0.29.5.
- Every patched method matches what was compiled.
- It's not tested in the game yet.

## dnSpy (only if doing it by hand)

1. `ModSinking`: Edit Class with `01_ModSinking.cs.txt`. The changes are the new `TorpedoSplash` knob and `TorpedoHit`.
2. `ModWreckArt`: only the comments changed, so you can skip it.
3. `ModVersion`: change the strings in `03_ModVersion_strings.txt` (0.29.5 to 0.29.6).
