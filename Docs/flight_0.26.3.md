# v0.26.3 Banking turns and dive bomber fix (flight_0.26.3.md)

**Status: written, not compiled, not tested.** Back up the DLL first. Needs 0.26.2 installed. If a compile error appears, send me the exact text.

## From your 0.26.2 test
No errors in the log. The nose followed the aim angle almost exactly (median gap 0 degrees, 90% within 0.3 degrees). 6 Wildcats, 2 Zeros and 24 Vals were shot down.

## What changes
1. **Banking turns.** Before, the plane's bank was only a picture of its turn rate and the turn started the instant the AI asked. Now a plane rolls into a turn at a real roll rate (fighters 90 degrees per second, others 45) and the turn can only build as fast as the bank allows, so turns start and finish smoothly and a fighter reversing from a left to a right turn has to roll through level first. You will see `roll` on the log lines move before `turn` does.
2. **Idle flight.** The log already says `Idle` for planes with no job (since 0.26 test 1). Idle planes already cruise at about 75% speed in a gentle circle; with banking their gentle turns now show a gentle bank. No further idle behaviour yet.
3. **Dive bomber fix.** A dive bomber with no attack numbers in its data file (the 13 newer dive bombers and every loadout after the first) used old flat numbers (start the dive from height 85, range 120). They now use the same steep dive numbers as the Val (start height 400 to 450, range 250 to 270, bomb drop 60 to 70, lead 25 and 4, offset 3). Planes that have their own numbers in the data file are not changed.

## Step 1 - replace ModFlight
1. Class **ModFlight** > **Edit Class (C#)...**, select all, paste the new `Docs/flight_model_ModFlight.cs.txt`. **Compile**.

## Step 2 - UnitAir.ApplyFlightControls
1. Class **UnitAir**, method **`ApplyFlightControls`** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
private void ApplyFlightControls(float duration)
{
	if (duration > 0f)
	{
		currentTurnRate = ModFlight.TurnRate(this, currentTurnRate, wantedTurnRate, currentRoll, duration);
		currentRoll = ModFlight.Roll(this, currentRoll, currentTurnRate, wantedTurnRate, duration);
		altitudeDifference = ((Component)this).transform.position.y - wantedHeight;
		altitudeDifference = Mathf.Clamp(altitudeDifference, 0f - maxDiveClimb.y, maxDiveClimb.x);
		currentPitch = ModFlight.Pitch(this, currentPitch, altitudeDifference, duration);
	}
}
```
2. **Compile**.

## Step 3 - EngagementAI.DiveBombApproach
1. Class **EngagementAI**, method **`DiveBombApproach`** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
private void DiveBombApproach(Unit unit)
{
	if (unit.transform.position.y < 30f)
	{
		LevelBombTarget(unit, true);
		return;
	}
	if (unit.transform.position.y < 75f)
	{
		LevelBombTarget(unit);
		return;
	}
	unit.unitAI.weaponIndexToAttackWith = Utilities.GetIndexOfWeaponType(unit, WeaponType.Bomb);
	unit.unitAIAir.aiAttack = AIAttack.Dive_Bomb_Approach;
	if (unit.unitAIAir.customAirAttack == null)
	{
		unit.unitAIAir.attackHeight = Random.Range(400f, 450f);
		unit.unitAI.attackRange = Random.Range(250f, 270f);
		unit.unitAIAir.additionalLeadTime = 25f;
		unit.unitAI.attackOffset = SetAttackOffset(unit, 3f);
	}
	else
	{
		CustomAirAttack customAirAttack = unit.unitAIAir.customAirAttack;
		unit.unitAIAir.attackHeight = GetCustomAttackData(customAirAttack.attackHeight);
		unit.unitAI.attackRange = GetCustomAttackData(customAirAttack.attackRange);
		unit.unitAIAir.additionalLeadTime = GetCustomAttackData(customAirAttack.additionalLeadTime);
		unit.unitAI.attackOffset = SetAttackOffset(unit, GetCustomAttackData(customAirAttack.offset));
	}
	ChangeAIAction(unit, AIAction.Attack_Unit);
}
```
2. **Compile**. If it says `LevelBombTarget` has no overload `(Unit, bool)`, send me the text; the original call was `LevelBombTarget(unit, skip: true)` and I wrote it as a plain argument.

## Step 4 - EngagementAI.DiveBombTarget
1. Same class, method **`DiveBombTarget`** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
public void DiveBombTarget(Unit unit)
{
	unit.unitAI.weaponIndexToAttackWith = Utilities.GetIndexOfWeaponType(unit, WeaponType.Bomb);
	unit.unitAIAir.aiAttack = AIAttack.Dive_Bomb;
	if (unit.unitAIAir.customAirAttack == null)
	{
		unit.unitAIAir.additionalLeadTime = 4f;
		unit.unitAI.attackOffset = SetAttackOffset(unit, 3f + unit.unitAI.focusedUnit.currentSpeed + Mathf.Abs(unit.unitAI.focusedUnit.currentTurnRate));
		unit.unitAI.primaryEngageDistance = Random.Range(60f, 70f);
	}
	else
	{
		CustomAirAttack customAirAttack = unit.unitAIAir.customAirAttack;
		unit.unitAIAir.additionalLeadTime = GetCustomAttackData(customAirAttack.diveLead);
		unit.unitAI.attackOffset = SetAttackOffset(unit, GetCustomAttackData(customAirAttack.diveOffset) + unit.unitAI.focusedUnit.currentSpeed + Mathf.Abs(unit.unitAI.focusedUnit.currentTurnRate));
		unit.unitAI.primaryEngageDistance = GetCustomAttackData(customAirAttack.diveDropHeight);
	}
	unit.unitAIAir.currentManeuvre = Maneuvre.DiveBomb_Dive;
	if (unit.unitAir.diveBrakes != null && unit.unitAir.diveBrakes.Count > 0)
	{
		unit.unitAir.SetDiveBrakes(1);
	}
}
```
2. **Compile**, then **File > Save Module**.

## Test
1. Keep `Interval` at 1. Fly Wildcats vs Zeros again, and a strike with one of the newer dive bombers (any of the 13 that attacked flat) against a ship.
2. Check: dive bombers start their dive high and steep like the Val; the fighters' bank now builds before the turn; no `[FLIGHT] ... failed and stopped` line.
3. Send me the output_log.txt.

## Later
- 0.26.4 fighter manoeuvres by pilot skill (crews off = all manoeuvres)
- 0.26.5 bombers and torpedo planes on the new model
- 0.26.6 formation flying
- 0.26.7 damage affects flight, altitude performance, per-aircraft flight file
- 0.26.8 Remove speed limit
- 0.26.9 Air auto resolve
