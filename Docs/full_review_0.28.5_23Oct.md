# Full mod review, 23 October (code as of 0.28.5)

What I read: the 0.28.5 code (`Docs/flight_0.28_*.cs.txt`, the same files as `v0.28.5_update/`), the other mod classes in the decompiled `Assembly-CSharp.dll`, the game code they hook into, the log reviews up to the multi-battle 0.28.5 log, and that log itself (`bb823e24`). Nothing here was run in the game. Every fix below is a small edit; nothing changes at x1 time compression for fix 1.

The `Assembly-CSharp.dll` in the project folder is from 20 Oct 05:29, before 0.28.5 (it has no `ModPlayerOverride`). Upload the current DLL next time so the 0.28.5 hooks can be checked in it too.

## Findings, most serious first

| # | Severity | Problem | Where |
|---|---|---|---|
| 1 | High | Time compression makes the flight physics run 2, 5 or 10 times too fast | `ModFlight.End`, `Pitch`, `Roll`, `TurnRate` |
| 2 | High | Friendly "right of way" can leave nobody avoiding | `ModAirCollide.Avoid` |
| 3 | Medium | The fighter you have selected never stops firing once the AI starts a burst | `ModDogfight.StopGuns` |
| 4 | Medium | Scissors cannot work: cut off after 4 s, and turn reversals are too quick | `ModDogfight.Fly`, `Move`, `StartDefend` |
| 5 | Medium | Chase power switches on in the wrong cases (head-on, slow) | `ModDogfight.GunRun` |
| 6 | Low | Log limits and counters never reset between battles | many classes |
| 7 | Low | Formation yield almost never gets a case | `ModAirFormation` (design) |
| 8 | Low | Wildcats at 3000 m always think they can run from a Zero | `ModDogfight.Decide` (tactics) |
| 9 | Low | Wingman cover search gets slow in very big air battles | `ModDogfight.FindAttackerOfFriend` |

### 1. Time compression speeds up the flight physics (High)

**What is wrong.** The game calls `UnitAir.UpdateMovementData` with `updateTimer * Time.timeScale` (`Unit.Update`), but `updateTimer` already adds up scaled frame time. So at x10 the `duration` the mod gets is 10 times the battle seconds that really passed. 0.28.4 fixed this for fuel only (`ModAirDamage.Tick`). Everything else in `ModFlight` still uses the inflated number, while the plane still moves at the real rate:
* speed from thrust, drag and gravity changes 10 times too fast: a climb loses speed 10 times faster than it gains height, a dive gains 10 times the speed it should (energy is no longer conserved);
* pitch, roll and the rudder slip move 10 times too fast;
* the collision check looks 10 frames ahead instead of 1, so a near miss that the avoidance would still fix counts as a hit.

**Why it matters.** It fits the open problems: the Wildcat in battle 2 of the multi log sat at 60% of top speed while climbing and diving, Wildcats "cannot regain energy", and 5 of 7 collisions were friendly near misses at 150 to 184 m/s. I cannot see the compression used in the log, but the 0.28.4 log showed testing at x8. At x1 all these edits change nothing.

**Fix (Edit Method in dnSpy, one method at a time, Compile, then File > Save Module):**
1. Class `ModFlight`, method `End`: the first line inside `try {` is `bool bombing = Bombing(ua);`. Add this line above it:
   `duration = duration / Mathf.Max(1f, Time.timeScale);`
2. Same method: find `float boost = ModAirFlight.ChaseFactor(ua, duration / Mathf.Max(1f, Time.timeScale));` and change it to
   `float boost = ModAirFlight.ChaseFactor(ua, duration);`
3. Class `ModAirDamage`, method `Tick`: delete the line `dt = dt / Mathf.Max(1f, Time.timeScale);` (step 1 already does it; leaving it would make fuel last 10 times too long).
4. Class `ModFlight`, method `Pitch`: add `duration = duration / Mathf.Max(1f, Time.timeScale);` as the first line of the method (above `try`).
5. Class `ModFlight`, method `Roll`: add the same line as the first line.
6. Class `ModFlight`, method `TurnRate`: add the same line as the first line, then in the two lines that contain `duration * ua.unitData.turnRate * Time.timeScale` delete ` * Time.timeScale`.
7. Test: the same 1v1 Wildcat against Zero once at x1 and once at x10. The [ENERGY] and [FLIGHT] lines should now look alike.

### 2. Friendly right of way can leave nobody avoiding (High)

**What is wrong.** Since 0.28.5, of two friends on a collision course only one gives way (the lower id; the code comment says higher, the code does the opposite). The other holds course and assumes the first will move. But the first plane often cannot move: it is in an acrobatic move or a scripted manoeuvre, the player is flying it, it is below 30 m, or it is already dodging a third plane. Then nobody avoids. Also, two friends closing fast only count as a "real" collision inside 8 m and 1 s, which is too late at 150 m/s.

**Fix (class `ModAirCollide`, Edit Class):**
1. Add this new method just above `private static string Side(Unit u)`:
```
	// v0.28.6: can this plane give way? If not, the other plane must not hold course.
	private static bool CanGiveWay(Unit o)
	{
		if (o == null || o.unitAir == null || o.unitAI == null || ModPlayerOverride.IsManual(o) || ModFlight.AcroActive(o.unitAir))
		{
			return false;
		}
		Maneuvre m = o.unitAI.currentManeuvre;
		if (m != Maneuvre.None && m != Maneuvre.Break_Left && m != Maneuvre.Break_Right)
		{
			return false;
		}
		float busy;
		if (avoidUntil.TryGetValue(o.GetInstanceID(), out busy) && Time.time < busy)
		{
			return false;
		}
		return o.transform.position.y >= MinHeight * 2f;
	}
```
2. In method `Avoid`, find
   `bool real = worstSep.magnitude < (me.radius + worst.radius) && worstT < 1f;`
   and change it to
   `bool real = (worstSep.magnitude < (me.radius + worst.radius) && worstT < 1f) || (worst.vel - me.vel).magnitude * 10f > 100f;`
   (two friends closing faster than 100 m/s both break, as before 0.28.5.)
3. In the same method, find
   `if (friends && !real && !SameFlight(meUnit, worst.u) && id > worst.id)`
   and change it to
   `if (friends && !real && !SameFlight(meUnit, worst.u) && id > worst.id && CanGiveWay(worst.u))`
4. Compile, Save Module. In the next log, friendly [COLLIDE] lines should drop (do fix 1 too; it is part of the same problem).

### 3. The selected fighter never stops firing (Medium)

**What is wrong.** `ModDogfight.StopGuns` does nothing for the unit selected in the combat interface. When you select one of your fighters while the AI flies it, the first AI burst never ends: the guns run until the ammunition is gone and the plane then leaves the battle "OUT OF AMMO". The defend, extend and leave moves also call `StopGuns` and are skipped the same way.

**Fix:**
1. Class `ModDogfight`, method `StopGuns`: change the `if` line to
   `if (u.weaponParticle != null && u.weaponParticle.enabled)`
2. Compile, Save Module. (`Fly` only runs while the AI flies the plane, so this does not stop a plane you fly yourself.)

### 4. Scissors cannot work (0 of 5 in the multi log) (Medium)

**What is wrong.** Two things.
* The scissors lasts 9 s, but the attacker is close (inside 200 m), so the threat check in `Fly` starts a new defence 4 s in (`DefendRepeat`) and ends the scissors.
* The turn is reversed every 1.4 to 2.2 s, but rolling from one hard bank to the other takes about that long. The log shows it: Zero -17042 at 334 s was turning -5.2 deg/s while asking for +28. The plane spends the scissors rolling, not turning, so the attacker never overshoots.

**Fix (class `ModDogfight`):**
1. Method `Fly`: find
   `if (s.threat != null && s.phase != 4 && s.phase != 5 && coolOk && now - s.threatSince >= reaction)`
   and change it to
   `if (s.threat != null && s.phase != 4 && s.phase != 5 && !(s.phase == 6 && s.move == 7) && coolOk && now - s.threatSince >= reaction)`
2. Method `Move`: change `s.scissorFlip = now + UnityEngine.Random.Range(1.4f, 2.2f);` to `s.scissorFlip = now + UnityEngine.Random.Range(2.8f, 3.6f);`
3. Method `StartDefend`: change `s.scissorFlip = now + 1.5f;` to `s.scissorFlip = now + 2.5f;`
4. Compile, Save Module. Look for "scissors worked" lines.

### 5. Chase power switches on in the wrong cases (Medium)

**What is wrong.** `GunRun` asks for emergency power whenever the target is farther than 300 m and we are not 12% faster than it. That includes a target coming at us head-on, and our own plane being slow in a climb (the extra thrust only helps near top speed). The multi log had 828 starts. Each one spends the 240 s budget and burns fuel 1.8 times faster, so by the time a real stern chase comes the power may be used up. It may also be part of why three Zeros ditched with empty tanks in the last battle (not proven).

**Fix:**
1. Class `ModDogfight`, method `GunRun`: find
   `if (dist > ModDogfight.CatchUpRange && u.currentSpeed < target.currentSpeed * ModDogfight.ChaseOvertakeShare)`
   and change it to
   `if (dist > ModDogfight.CatchUpRange && u.currentSpeed < target.currentSpeed * ModDogfight.ChaseOvertakeShare && grow != null && u.currentSpeed >= ModDogfight.TopSpeedNow(grow) * 0.9f && Vector3.Angle(target.transform.forward, target.transform.position - pos) < 60f)`
   (only when the target is flying away from us and we are already near our top speed.)
2. Compile, Save Module. Expect far fewer [CHASE] starts.

### 6. Log limits and counters never reset between battles (Low)

Every log tag has a cap (`[AVOID]` 60 lines, `[COLLIDE]` 80, `[CHASE]` 40, `[PLAYER]` 30, `[FORMATION]` 40 and so on) and the [BATTLE] counters are cumulative, all for the whole game session. In a session with several battles the later battles have no `[AVOID]` evidence, which is why the multi log review could not explain the later collisions. Not harmful in play, only for testing. Workaround now: one battle per game start. A proper fix needs a small reset method called at the start of each battle; I can write it as part of 0.28.6.

### 7. Formation yield almost never gets a case (Low, design)

Combat spread starts when enemy fighters are within 12 km (`ModAirFormation.SpreadRange` = 1200), so in every test the flights spread within 3 s and are attacking soon after; the yield branch never has a formation to work on (0 yields in the multi log). When it does run, the slot shift steers at most 6 deg/s, too little to clear a conflict 2 s ahead, so fix 2 (both break above 100 m/s) is what actually protects formation mates. To test the yield on its own, start a battle with the enemy farther than 12 km, or set `SpreadRange` to 400 for one test build.

### 8. Wildcats at 3000 m always think they can run (Low, tactics)

In `ModDogfight.Decide`, `canRun` is true for any fighter above 2500 m (`u.transform.position.y > 2500f * 0.1f`), whatever the enemy. Every test starts at 3000 m, so a slow Wildcat at level energy against a Zero always picks "extend away" (35 + 10 such decisions in battle 3, and 4 of 4 losses had a Zero on the tail). This is a tactics choice, not a crash. If you want to try it: in `Decide` change `|| u.transform.position.y > 2500f * 0.1f` to `|| (u.transform.position.y > 2500f * 0.1f && u.currentSpeed >= rm.cornerSpeed * 1.2f)`, so only a Wildcat that is already fast dives away and a slow one turns with flaps (or gets help from the defensive split).

### 9. Big air battles: wingman cover search (Low, performance)

`FindAttackerOfFriend` runs once a second per fighter and, for every friend, calls `FindThreat` (all planes) and then counts all planes again. That grows with the cube of the number of planes. 12 against 12 is fine; with 72 a side (the config limit) it is about 3 million checks a second and could cause stutter. Nothing to do unless you see stutter in big battles; then it can be cached once a second for everyone.

## Checked and fine

* `ModPlayerOverride`: the game's own slider refresh when you select a unit runs with `lockSliderInput` on, so it is not taken for the player; the 1 s settle covers battle start. Hook D is in the right place in `ModAAEvade.Apply` (note: the AA-evasion "keep clear of the other ship" is also off for 30 s after you move a slider; you have the helm).
* Damage: the fire and kill paths call the game's damage method again from inside the hook; the `dead` flag stops a loop. Fuel, leaks, fire and break-up run on battle seconds.
* Auto-resolve hook in `CampaignManager` and `EngagementPanel.AutoResolve`: correct. (Scout against fighter now opens the mod window too, instead of the stock resolve.)
* Immelmann never starting is not a bug: it needs an overshoot in boom-and-zoom mode at 1.4 x corner speed, then 30% x 40% chance. Raise the 0.4 in `ModDogfight.Attack` if you want to see more.
* No error lines in the 0.28.5 multi log.

## Suggested order

Fixes 1 to 5 together as 0.28.6 (they touch `ModFlight`, `ModAirDamage`, `ModAirCollide`, `ModDogfight`), then the same tests as before: 1v1 at x1 and at x10, 4v4, 12 v 12. I can make the ready-to-paste class files for 0.28.6 if you want them.
