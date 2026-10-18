# v0.26.4 Pilot skill and fighter acrobatics (flight_0.26.4.md)

**Status: written, not compiled, not tested.** Back up the DLL first. Needs 0.26.3 installed. If a compile error appears, send me the exact text. This one needs the Mod Options class (`ModOptions.Crew`, v0.27) to be in your DLL.

## What changes
1. **Pilot rank.** Every fighter pilot is Green, Trained, Veteran or Elite. Until air crew experience exists the rank comes from nation and year, fixed for each plane: 1942 Japanese pilots are mostly Veteran or Elite and get worse in 1943 and 1944, US pilots start mostly Trained and get better. **With the Crew system switched off in Mod Options, every pilot is Elite**, so all manoeuvres can be tested. The log prints `pilot is Veteran` once per plane and adds `pilot X` to its flight lines.
2. **What each rank may do.**
   - **Green:** straight pursuit, notices a plane on its tail after 2 seconds, plain break turn (no dive or climb), under-leads its shots (60% lead), does not climb to set up a pass and turns straight back in after a pass.
   - **Trained:** notices after 0.8 s, 85% lead, boom and zoom (US) or turn fight (Japanese), zoom climb after a pass.
   - **Veteran:** instant reaction, the high yo-yo (Japanese), the Thach Weave (US pairs), a **defensive barrel roll** whenever it breaks away, and the **roll-over attack**.
   - **Elite:** all of the above, a higher chance of the roll-over attack, and the **split-S escape**.
3. **Roll-over attack (reworked 18 Oct after your first test).** Now only when the plane a Veteran or Elite fighter is chasing *suddenly* ends up well below it (it was roughly level or above three seconds ago and is now at least 150 m below, 300 to 1100 m away) and is off to the side or behind. The pilot half-rolls (about 2.5 s), pulls through the bottom of a loop so he comes out upright and diving on it from above, fires when lined up, then pulls out level, heading back the way he started. Needs 1000 m height. Never used on a target that has been below all along.
4. **Split-S escape.** US Elite pilots only (the Zero's controls stiffen in a fast dive and Japanese pilots did not dive away from a fight), 40% of the time, above 1100 m with an enemy within 450 m on their tail. Rolls inverted and pulls through into a dive away, finishing level on the opposite heading. At most once every 40 seconds.
5. **Barrel roll.** A 3.5 second full roll round the nose while the plane keeps its turn.
6. **Acrobatics are done in code, not by the game.** The game's own flight code only knows pitch and a bank angle, so during these moves `ModFlight.Acro` turns the plane itself and hands it back upright. It writes `acro roll-over-attack`, `acro split-S` or `acro barrel-roll` on the flight log lines.

## Update 18 Oct (second round)
Your second log (no errors) showed a bug: after a **split-S** the plane never gave control back. It finished the move and then flew dead straight and level for hundreds of seconds (about 500 s per plane in the log), which is also why the Zeros earlier did nothing. Fixed in `ModFlight` (the split-S now goes on to its pull-out and finishes, and any acrobatic move that runs longer than 30 seconds is cut off and the plane handed back level). Re-paste `ModFlight` only.

## Update 18 Oct (third round: Wildcats outnumbered)
Third log (Crew on, Wildcats against A6M2 Zeros and A8K1s, no errors from our code). The Wildcats were not stuck: Japanese fighters were aiming on 94% of their attack lines, the Wildcats only 34%, because the Wildcats were outnumbered about 2.5 to 1 and kept breaking away. There were 750 "on her tail" reactions (about 400 from A6M2s, 235 from A8K1s) and 623 "clear, climbing back to attack" restarts, against only 95 dives. A defence was triggered by any enemy within 600 m for even half a second, then a new one started 3 seconds after the last. Now a plane only counts as a threat inside **400 m** and a pilot does not react again for **8 seconds** after a defence or acrobatic move. Re-paste the `ModDogfight` class (`Docs/flight_0.26.4_ModDogfight.cs.txt`). The two `IndexOutOfRangeException` lines in the log come from `WeaponAAA.InitialiseAAA` (an anti-aircraft gun set up on some unit), not from the flight code; I will look at them separately.

## Update 18 Oct (fourth round: crew switch)
Your last log printed `pilot is Trained` although the save's Mod Options show Crew OFF. `ModOptions.Get` takes the campaign's locked copy only when it can see the running campaign; in a battle it may not, and then falls back to the main-menu setting. So the battle may have read the main-menu value (probably ON). `ModFlight` now writes one line `[FLIGHT] Mod Options crew system reads ON/OFF, campaign '...'` at the first pilot check, so the next log tells us for certain. Quick fix to test now: set **Crew system OFF in Mod Options from the main menu too** (not only in the save), then fly the battle again. Re-paste `ModFlight` (the class `Docs/flight_model_ModFlight.cs.txt`).

## Update 18 Oct (fifth round: wingman cover)
Your fourth log (quick battle, the crew line read OFF so every pilot was Elite, no errors from our code): 24 Wildcats against 72 Japanese fighters (24 each of A6M2 Mod 21, A6M3 Mod 22a and A8K1). The Wildcats lost 5 and shot none down; the Japanese lined up shots on 96% of their attack lines and the Wildcats on 36%, and the Wildcats spent most of the fight running (210 Thach Weaves, 202 breaks with a barrel roll, 192 split-S dives, 409 "clear, climbing back to attack").
New: **wingman cover** (Trained or better, in `ModDogfight`). Every second a pilot looks for a friendly fighter that has an enemy fighter on its tail within 400 m (the same test as the threat check). If one is within 1500 m of him, and fewer than two of our fighters are already after that enemy, he goes after that enemy: "covering a wingman: going after X on his tail". A pilot who is himself being chased keeps up his break turn (and barrel roll), fires at the enemy on his friend's tail if it crosses his nose, and when the break ends goes straight at that enemy instead of climbing away for another pass. Re-paste the `ModDogfight` class (`Docs/flight_0.26.4_ModDogfight.cs.txt`).

## Step 1 - replace ModFlight
1. Class **ModFlight** > **Edit Class (C#)...**, select all, paste the new `Docs/flight_model_ModFlight.cs.txt`. **Compile**.

## Step 2 - replace ModDogfight
1. Class **ModDogfight** > **Edit Class (C#)...**, select all, paste `Docs/flight_0.26.4_ModDogfight.cs.txt` (it already contains the 0.26.2 gun run and the 0.26.1 `Energy` change). **Compile**.

## Step 3 - UnitAir.ApplyUnitMovement
1. Class **UnitAir**, method **`ApplyUnitMovement`** > **Edit Method (C#)...**. At the very end of the method find this block:
```csharp
else if (unitAI.currentManeuvre == Maneuvre.None || unitAI.currentManeuvre == Maneuvre.Break_Left || unitAI.currentManeuvre == Maneuvre.Break_Right)
{
	Vector3 eulerAngles = ((Component)this).transform.eulerAngles;
	eulerAngles.x = currentPitch;
	eulerAngles.y += currentTurnRate * fixedDuration;
	eulerAngles.z = currentRoll;
	((Component)this).transform.eulerAngles = eulerAngles;
}
```
(dnSpy may show `base.transform` or `this.unitAI`; the lines are the same.) Replace that whole block with:
```csharp
else if (unitAI.currentManeuvre == Maneuvre.None || unitAI.currentManeuvre == Maneuvre.Break_Left || unitAI.currentManeuvre == Maneuvre.Break_Right)
{
	if (ModFlight.Acro(this, fixedDuration, currentPitch, currentRoll))
	{
		currentPitch = ModFlight.AcroPitch;
		currentRoll = ModFlight.AcroRoll;
	}
	else
	{
		Vector3 eulerAngles = ((Component)this).transform.eulerAngles;
		eulerAngles.x = currentPitch;
		eulerAngles.y += currentTurnRate * fixedDuration;
		eulerAngles.z = currentRoll;
		((Component)this).transform.eulerAngles = eulerAngles;
	}
}
```
2. **Compile**, then **File > Save Module**.

## Test
1. First with **Crew system off** in Mod Options (everyone Elite, all moves allowed): Wildcats vs Zeros, ideally with the fighters starting at different heights. Keep `Interval` at 1.
2. Watch for: a fighter rolling upside down and diving on a plane below it, a Zero rolling away when you get on its tail (split-S), planes doing a quick full roll when they break, and nothing flying into the sea.
3. Then switch **Crew system on** and fly the same battle: you should see more simple attacks and slower reactions from Green and Trained pilots.
4. Send me the output_log.txt. I will search for `pilot is`, `roll-over attack`, `split-S`, `acro`, kills, and any `failed and stopped` line.
5. If a move looks wrong (too fast a roll, too steep, pulls out too low) tell me which and I will change the numbers at the top of `ModFlight` (`RollOverRate` 70, `PullRate` 30, `PullOutHeight`, `BarrelTime` 3.5; all slowed down in the 18 Oct update).

## Still to come
- 0.26.5 Bombers and torpedo planes on the new model
- 0.26.6 Formation flying
- 0.26.7 Damage affects flight, altitude performance, per-aircraft flight file, flight readout, avoidance
- 0.26.8 Remove speed limit
- 0.26.9 Air auto resolve
- At the end: set the log `Interval` back to 10 or 20.
