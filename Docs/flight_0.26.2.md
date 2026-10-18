# v0.26.2 Aiming: real pitch control for fighters (flight_0.26.2.md)

**Status: written, not compiled, not tested.** Back up the DLL first. Needs 0.26.1 installed. If a compile error appears, send me the exact text.

## What was wrong
- The game pulls a plane's nose at most 10 degrees per second (`UnitAir.ApplyFlightControls` smooths the pitch with a 1 second delay and a 10 degree per second cap). A fighter lining up a shot needs 30 to 50 degrees, so the nose never got onto the target in time and the guns stayed silent.
- Our v0.20.9 gun run (`ModDogfight.GunRun`) worked out the right angle, but it could only ask for it through the "wanted height" wish, which goes through that slow pitch.

## What changes
- A fighter on a gun run now asks for the exact nose angle it needs, and the plane pulls to it at 40 degrees per second (other planes 20).
- Limit 60 degrees nose down, 50 degrees nose up. Near the sea the allowed dive angle shrinks (about 15 degrees at 200 m, none under 100 m), so planes do not fly into the water.
- A stalled plane (0.26.1) is forced to let the nose drop even in a gun run.
- Every other manoeuvre (climbing to get above, zoom, yo-yo, bombers) keeps the height-wish way, but pitch now changes faster (fighters 25, others 12 degrees per second instead of 10).
- The flight log gets ` aim 12.5` on a line while a pilot is lining up a shot (the nose angle he wants). Compare it with `pitch` on the same line.

## Step 1 - replace the ModFlight class
1. Class **ModFlight** > **Edit Class (C#)...**, select all, paste the new `Docs/flight_model_ModFlight.cs.txt`. **Compile**. (It will compile on its own; the logger below needs it.)

## Step 2 - replace the logger class
1. Class **ModFlightLog** > **Edit Class (C#)...**, select all, paste the new `Docs/flight_log_ModFlightLog.cs.txt`. `Interval` is 1 in this file (test setting). **Compile**.

## Step 3 - UnitAir.ApplyFlightControls
1. Class **UnitAir**, method **`ApplyFlightControls`** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
private void ApplyFlightControls(float duration)
{
	if (duration > 0f)
	{
		currentTurnRate = Mathf.MoveTowards(currentTurnRate, wantedTurnRate, duration * unitData.turnRate * Time.timeScale);
		currentRoll = Mathf.SmoothDampAngle(currentRoll, currentTurnRate * -5f, ref rollVelocity, 1f, float.PositiveInfinity, duration);
		altitudeDifference = ((Component)this).transform.position.y - wantedHeight;
		altitudeDifference = Mathf.Clamp(altitudeDifference, 0f - maxDiveClimb.y, maxDiveClimb.x);
		currentPitch = ModFlight.Pitch(this, currentPitch, altitudeDifference, duration);
	}
}
```
2. **Compile**.

## Step 4 - ModDogfight.GunRun
(Fixed 18 Oct: the first version of this method had `ref` and `(Object)(object)` casts copied from the decompiler, which dnSpy's compiler rejects.)
1. Class **ModDogfight**, method **`GunRun`** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
public static void GunRun(UnitAIAir ai, Unit u, Unit target, float dist)
{
	Vector3 position = u.transform.position;
	float num = dist / 80f;
	Vector3 val = target.transform.position + target.transform.forward * target.currentActualSpeed * num;
	Vector3 val2 = val - position;
	Vector3 val3 = val2;
	val3.y = 0f;
	Vector3 forward = u.transform.forward;
	forward.y = 0f;
	float signedAngleToPosition = Utilities.GetSignedAngleToPosition(forward, position, new Vector3(val.x, position.y, val.z));
	u.wantedTurnRate = Mathf.Clamp(signedAngleToPosition, 0f - u.unitData.maxTurnRate, u.unitData.maxTurnRate);
	float num2 = Mathf.Atan2(0f - val2.y, Mathf.Max(val3.magnitude, 1f)) * 57.29578f;
	float num3 = Vector3.Angle(u.transform.forward, val2);
	ModFlight.Aim(u.unitAir, num2);
	u.wantedHeight = Mathf.Clamp(position.y - num2, 20f, 800f);
	WeaponParticle weaponParticle = u.weaponParticle;
	if (weaponParticle != null)
	{
		float num4 = ((ai.attackRange > 0f) ? ai.attackRange : 40f);
		bool flag = dist < num4 && num3 < 5f;
		if (flag && !weaponParticle.enabled)
		{
			weaponParticle.FireAll(isOn: true);
		}
		else if (!flag && weaponParticle.enabled)
		{
			StopGuns(u);
		}
	}
}
```
2. **Compile**, then **File > Save Module**.

## Test
1. A fighter battle: Wildcats vs Zeros, plus fighters escorting bombers. Keep `Interval` at 1.
2. Send `output_log.txt`. I will check: lines with `aim` (does `pitch` follow `aim` within a few seconds?), how often guns reach the 5 degree cone, and kills.
3. To undo, restore your DLL backup.

## Still to come
- 0.26.3 Idle flight mode and bank-based turning
- 0.26.4 Fighter manoeuvres by pilot skill (crew toggle off = all manoeuvres)
- 0.26.5 Bombers and torpedo planes on the new model
- 0.26.6 Formation flying
- 0.26.7 Damage affects flight, altitude performance, per-aircraft flight file, flight readout, avoidance
- 0.26.8 Remove speed limit: overspeed break-up, wings snap off, falling wing pieces
- At the end: set the log `Interval` back to 10 or 20.
