# v0.28.9 update (not run in the game yet)

You have 0.28.8 installed. This update edits 1 class. Save the module after.

| Step | What | File |
|---|---|---|
| 1 | Edit Class `ModDogfight` | 1_ModDogfight.cs.txt |

In dnSpy right-click `ModDogfight` > Edit Class (C#), select all, paste the whole file, Compile, File > Save Module.

## What the 0.28.8 log (27 Oct, 1v1 + 4v4) showed
0.28.8 is in and clean: no error lines, no collisions, the "too slow to zoom: extending level" lines appear (6 times).

**Why a Wildcat with a firing line did not shoot.** Two things, both fixed:
1. **The mod cancelled bursts it had not started.** Any burst switched on by the fire key on the selected plane (or by the mod's own wingman-cover and barrel-roll code) was turned off on the next tick, because the mod judged it by the start time of the plane's *previous* burst and called it too long. The log has a Wildcat at 281 m, 1.9 deg off, whose guns went on and off 8 times in 4 s without a single second of fire. Each cancel also blocked the AI's own fire for 2 s. Now a burst the mod did not start is adopted as a new burst from that moment (`ModDogfight.GunsOn`, `GunRun`).
2. **The Wildcats seldom got within 300 m.** Their guns were in the cone 50% of the time but in range 8% (the [GUNSTAT] lines). Three behaviour causes:
   * The energy mode flipped every 4 s (boom and zoom / turn with flaps / "it is running away, straight pursuit"). A Zero chasing a wingman counted as running away the moment it was passed, and the zoom was dropped for a straight chase. Now a plane busy with someone else only counts as running beyond 800 m (`Fleeing`), and a plane already in boom and zoom stays there down to 90% of corner speed (`Decide`).
   * A slow Wildcat that cannot outrun a Zero turned with flaps out, which bled it further: 85 to 97% of the last three minutes were spent below corner speed. The worse turner now keeps the flaps in and turns at the sustained rate, except for a snap shot inside 400 m (`GunRun`).
   * A Zero on the tail at 260 to 300 m was never a threat (threat range 250 m) while Zeros open fire at 270 to 300 m: Wildcats were shot from behind with no defence. Threat range is now 400 m, and 320 m for a plane that is not aimed at us by its AI (`ThreatRange`, `TailCloseRange`).

**Also:** no Immelmann or barrel roll attack with an enemy on the tail (a Wildcat died in phase 5, mid barrel roll, with a Zero behind it), and the doubled "collisions collisions" word in the [BATTLE] line.

## How to tell it is installed (next log)
* Press the fire key on a selected plane whose nose is on a target: it fires for up to 2.5 s.
* "[DOGFIGHT] ... sustained turns, flaps in, building speed" lines instead of "turn with flaps out".
* "on her tail at 3xx m" lines (before, never above 249 m).
* [GUNSTAT]: US "in range" and "both" counts a bigger share of "total".

## Not compiled
Edits by exact text replacement against the 0.28.8 source, checked by diff, not compiled. Paste any red line here.
