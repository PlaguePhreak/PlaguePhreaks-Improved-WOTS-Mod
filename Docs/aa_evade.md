# Anti-air manoeuvres (v0.20.1 and v0.20.2, AI super overhaul)

## What was wrong (found in the code)
Ships never dodged air attacks. The game's "hazard evasion" toggle (`UnitAI.noNavEvade`, used in `UnitAISea.CheckNavigation`) only stops ships colliding with each other, and torpedoes spotted in the water are only put on the map. So ships held their course and speed and just soaked up the bombs and torpedoes.

## What changes
Ships, yours and the AI's, now take evasive action when aircraft start their attack run on them, before anything is released, the way real WW2 ships did:
- **Torpedo bombers** (and low-level bombers under 300 m) on their run inside 3 km: full speed, and the ship turns to point her bow at them (or her stern, if they are behind the beam). This is "combing", which gives the smallest target. She keeps that heading for 40 seconds after the drop, while the torpedoes are running.
- **Dive bombers** in their dive, or within about 1.3 km and about to push over: full speed and the rudder hard over, away from the side they come from, and she keeps turning for 20 seconds after.
- **High level bombers** inside 4 km: the same hard turn.
- Torpedo planes come first if both attack at once.
- Only aircraft actually attacking that ship count, and the reaction is checked once a second.
- **Your ships** only do this when their evasion toggle (the game's hazard evasion button) is on, so you can switch it off for any ship.
- Avoiding a collision with another ship always comes first.
- Afterwards the ship goes back to what she was doing: her waypoints, her attack, her place in the formation, or (your ships on manual) the speed and rudder you had set.
- Hammer and anvil still works: torpedo flights coming from both bows mean the ship can only comb one of them, as in real life.

## v0.20.2 - fixes after the first test (14 Oct)
**What the test showed (output_log):**
- Torpedo planes were only noticed at 0.7-1.5 km, because the check waited for them to get below 300 m, and the Avengers came down late. That left a cruiser about 10 seconds, far too little to turn.
- Dive bombers were only noticed as they pushed over (1.2 km). Their aim also allows for the ship's current turn, so a steady turn didn't help.
- Kako twice dropped her evasion when the game's collision avoidance cut in (another ship within 400 m ahead). In big formations that happens all the time, and two ships ended up stuck on each other.
- Hammer and anvil worked as intended: one ship can't comb torpedoes from both bows.
- No duds at all: the game's "dud bombs" and "dud torpedoes" options must be on for duds to happen.

**What changes:**
1. **Ships that are stuck come first:** a ship that is barely moving with another ship's hull right against hers for 4 seconds backs straight off at full astern for 10 seconds, then goes ahead at her old speed. This works for every ship, evasion on or off. Log: `[AAEVADE] X is stuck against Y, backing off`.
2. **Collision avoidance no longer cancels the evasion:** the game steers clear for its 1.5 seconds, then the evasion carries on.
3. **Formations turn together:** ships following a leader copy the leader's evasive turn, so the whole group swings the same way instead of into each other. When the leader is done, they are too (unless they have attackers of their own).
4. **Torpedo planes are noticed earlier:** from 4 km once they are heading in (within 60° of the ship), or inside 2.5 km whatever they are doing. Height no longer matters.
5. **Torpedoes in the water:** a ship that sees enemy torpedo tracks within 1 km that will pass close turns to run parallel to them (bow or stern on, whichever is quicker). This comes before everything else, so a ship caught by the second half of a hammer and anvil still has a chance.
6. **Dive bombers:** the ship starts turning hard when they are within 3 km, and when one pushes over she **reverses her rudder**. Their aim allowed for the old turn, so the bomb falls where she would have been. She reverses again for the next bomber, at most every 8 seconds ("snaking").
7. Night range reduction removed (the game has no night air attacks).

**Install v0.20.2 (1 step):**
1. Right-click the class **ModAAEvade** > **Edit Class (C#)**, select everything (Ctrl+A), paste the new `ModAAEvade.cs` below over it, **Compile**, then **File > Save Module**. The two `ModAAEvade.Apply(this);` lines from v0.20.1 stay as they are.

**New log lines:** `torpedo tracks in the water heading for her`, `turning together with <leader>`, `dive bombers pushing over, rudder reversed`, `is stuck against`, `is clear, going ahead again`.

## Install v0.20.1 (3 steps, already done)
Back up the DLL first.

### Step 1 - add the class
1. Right-click `Assembly-CSharp` > **Add Class (C#)**, delete what is there and paste all of `ModAAEvade.cs` below.
2. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 2 - UnitAI.FixedUpdate
1. Find class **UnitAI**, right-click the method **`FixedUpdate`** > **Edit Method (C#)**.
2. Click just before the method's **last** closing `}` (after everything else in it), press Enter and paste:
```csharp
ModAAEvade.Apply(this);
```
3. **Compile**, then **File > Save Module**.

### Step 3 - UnitAI.UpdateUnitAI
1. In class **UnitAI**, right-click the method **`UpdateUnitAI`** > **Edit Method (C#)**.
2. Find the line `this.navCurrentTicks++;` (near the end). Click at the start of that line, press Enter to make an empty line above it, and paste on the empty line:
```csharp
ModAAEvade.Apply(this);
```
3. **Compile**, then **File > Save Module**.

(The call is in both places so the evasion wins over the ship's normal steering whichever runs last.)

### ModAAEvade.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.1 / v0.20.2 / v0.20.6 / v0.20.9: anti-air manoeuvres. Ships (player and AI) take evasive action when aircraft start their attack run
// on them, the way real WW2 ships did:
//   torpedo bombers on their run inside 4 km  -> full speed, turn bow (or stern) on to them ("combing")
//   torpedoes seen in the water heading at us -> turn onto a course parallel to their tracks (comes first)
//   dive bombers closing inside 4.5 km       -> full speed, rudder hard over; when they push over, reverse the rudder
//   high level bombers inside 4 km            -> full speed, rudder hard over
// v0.20.2: ships in a formation turn together with their leader, the game's own collision avoidance is allowed to steer
// for a moment without cancelling the evasion, and two ships stuck against each other back off before anything else.
// Player ships only evade when their evasion toggle (the game's hazard evasion) is on. Unsticking works for every ship.
public class ModAAEvade
{
	public class State
	{
		public int mode;            // 0 none, 1 comb aircraft, 2 hard turn, 3 comb torpedo tracks
		public float until;         // keep evading until this time (seconds of battle time)
		public float nextCheck;
		public Unit threat;
		public Vector3 combDir;     // the way to point the ship while combing
		public float turnSign;
		public Unit reversedFor;    // the dive bomber the rudder was last reversed for
		public float lastReverse;
		public bool synced;         // turning together with the formation leader
		public bool restoreManual;  // player ship that was on manual speed and rudder
		public float savedSpeed;
		public float savedTurn;
		public int stuckChecks;
		public float unstickUntil;
		public bool unsticking;
		public float unstickSpeed;
		// v0.20.6: after unsticking, keep clear of the other ship for a while
		public float clearUntil;
		public float clearSign;
		public bool clearSlow;
		public Unit clearOf;
	}

	// distances in battle code are metres x 0.1
	public const float TorpedoPlaneRange = 4000f * 0.1f;
	public const float TorpedoCommitted = 2500f * 0.1f;
	public const float TorpedoTrackSight = 1000f * 0.1f;
	public const float TorpedoTrackMiss = 40f * 0.1f;
	public const float DiveRange = 4500f * 0.1f;
	public const float LevelRange = 4000f * 0.1f;
	public const float LowLevelAltitude = 300f * 0.1f;
	// how long to keep evading after the attack is over (seconds)
	public const float CombHold = 40f;
	public const float TrackHold = 15f;
	public const float TurnHold = 20f;
	public const float CheckSeconds = 1f;
	// stuck: barely moving with another ship right alongside for this many checks, then back off for this long
	public const int StuckChecks = 4;
	public const float UnstickSeconds = 10f;
	// v0.20.6: only one of the two ships backs off; afterwards both steer away from each other for this long
	public const float KeepClearSeconds = 20f;

	public static Dictionary<int, ModAAEvade.State> states = new Dictionary<int, ModAAEvade.State>();

	public static ModAAEvade.State GetState(Unit u)
	{
		int id = u.GetInstanceID();
		ModAAEvade.State s;
		if (!ModAAEvade.states.TryGetValue(id, out s))
		{
			s = new ModAAEvade.State();
			ModAAEvade.states[id] = s;
		}
		return s;
	}

	// Called at the end of UnitAI.FixedUpdate and in UnitAI.UpdateUnitAI, after the ship's normal steering is set
	public static void Apply(UnitAI ai)
	{
		try
		{
			Unit u = ai.parentUnit;
			if (u == null || u.unitSea == null || u.isDestroyed || u.unitData == null || u.unitData.unitSubtype == UnitSubType.Submarine)
			{
				return;
			}
			ModAAEvade.State s = ModAAEvade.GetState(u);
			bool allowed = !(u.faction == Faction.Player && ai.noNavEvade);
			if (Time.time >= s.nextCheck)
			{
				s.nextCheck = Time.time + ModAAEvade.CheckSeconds;
				ModAAEvade.CheckStuck(u, s);
				ModAAEvade.Check(ai, u, s, allowed);
			}
			// 1. stuck against another ship: back straight off first
			if (Time.time < s.unstickUntil)
			{
				if (!s.unsticking)
				{
					s.unsticking = true;
					s.unstickSpeed = u.wantedSpeed;
				}
				u.wantedSpeed = Config.instance.shipMaxReverse * u.unitData.maxSpeed;
				u.wantedTurnRate = 0f;
				return;
			}
			if (s.unsticking)
			{
				// clear: back to the speed she had before
				s.unsticking = false;
				u.wantedSpeed = s.unstickSpeed;
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + " is clear, going ahead again and keeping away from " + (s.clearOf != null ? s.clearOf.unitInstanceName : "the other ship"));
			}
			// v0.20.6: keep clear of the ship she was stuck to (turn away; the one that gave way also stays slow)
			if (Time.time < s.clearUntil)
			{
				if (s.clearOf != null && !s.clearOf.isDestroyed && Utilities.GetXZDistance(u.transform.position, s.clearOf.transform.position) > (u.unitData.length + s.clearOf.unitData.length) * 0.1f * 1.5f)
				{
					// far enough apart already
					s.clearUntil = 0f;
				}
				else
				{
					u.wantedTurnRate = s.clearSign * u.unitData.maxTurnRate * 0.6f;
					u.wantedSpeed = u.unitData.maxSpeed * (s.clearSlow ? 0.4f : 1f);
					return;
				}
			}
			if (s.mode == 0)
			{
				return;
			}
			if (!allowed)
			{
				ModAAEvade.Stop(ai, u, s, "evasion switched off");
				return;
			}
			u.wantedSpeed = u.unitData.maxSpeed;
			// 2. the game's collision avoidance steers for a moment (about 1.5 s), then the evasion carries on
			if (ai.currentAIAction == AIAction.Evade_Navigation)
			{
				return;
			}
			if (s.mode == 2)
			{
				u.wantedTurnRate = s.turnSign * u.unitData.maxTurnRate;
				return;
			}
			Vector3 dir = s.combDir;
			if (s.mode == 1 && s.threat != null && !s.threat.isDestroyed && Time.time < s.until - ModAAEvade.CombHold + ModAAEvade.CheckSeconds * 2f)
			{
				dir = ModAAEvade.CombDirection(u, s.threat.transform.position - u.transform.position);
				s.combDir = dir;
			}
			Vector3 aim = u.transform.position + dir * 100f;
			float angle = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, aim);
			u.wantedTurnRate = Mathf.Clamp(angle, -u.unitData.maxTurnRate, u.unitData.maxTurnRate);
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[AAEVADE] apply failed: " + ex.Message);
		}
	}

	// Once a second: is this ship stuck against another ship?
	public static void CheckStuck(Unit u, ModAAEvade.State s)
	{
		if (Time.time < s.unstickUntil || EngagementManager.instance == null || EngagementManager.instance.allSeaUnits == null)
		{
			return;
		}
		float wanted = Mathf.Abs(u.wantedSpeed);
		bool trying = wanted > Utilities.ConvertKnotToMetrePerSecond(4f) && Mathf.Abs(u.currentActualSpeed) < wanted * 0.25f;
		Unit other = trying ? ModAAEvade.Touching(u) : null;
		if (other == null)
		{
			s.stuckChecks = 0;
			return;
		}
		s.stuckChecks++;
		if (s.stuckChecks >= ModAAEvade.StuckChecks)
		{
			s.stuckChecks = 0;
			// v0.20.6: only one ship gives way (backs off), the other goes ahead; both then turn away from each other
			bool giveWay = ModAAEvade.GivesWay(u, other);
			float a = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, other.transform.position);
			s.clearSign = (a >= 0f) ? -1f : 1f;
			s.clearOf = other;
			s.clearSlow = giveWay;
			if (giveWay)
			{
				s.unstickUntil = Time.time + ModAAEvade.UnstickSeconds;
				s.clearUntil = s.unstickUntil + ModAAEvade.KeepClearSeconds;
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + " is stuck against " + other.unitInstanceName + ", she gives way: backing off for " + ModAAEvade.UnstickSeconds.ToString("F0") + " s, then keeping clear");
			}
			else
			{
				s.clearUntil = Time.time + ModAAEvade.KeepClearSeconds;
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + " is stuck against " + other.unitInstanceName + ", " + other.unitInstanceName + " gives way: going ahead and turning " + (s.clearSign > 0f ? "to starboard" : "to port") + " away from her");
			}
		}
	}

	// Which of two touching ships gives way: the one further astern, or if they are alongside each other, the smaller one
	// (the same answer whichever ship asks)
	public static bool GivesWay(Unit u, Unit o)
	{
		Vector3 d = u.transform.position - o.transform.position;
		d.y = 0f;
		float meBehind = -Vector3.Dot(o.transform.forward, d);
		float otherBehind = Vector3.Dot(u.transform.forward, d);
		float diff = meBehind - otherBehind;
		if (Mathf.Abs(diff) > 2f)
		{
			return diff > 0f;
		}
		float mine = (float)u.unitData.displacement_weight;
		float theirs = (float)o.unitData.displacement_weight;
		if (Mathf.Abs(mine - theirs) > 1f)
		{
			return mine < theirs;
		}
		return u.GetInstanceID() < o.GetInstanceID();
	}

	// Another ship so close her hull must be touching ours
	public static Unit Touching(Unit u)
	{
		List<Unit> ships = EngagementManager.instance.allSeaUnits;
		for (int i = 0; i < ships.Count; i++)
		{
			Unit o = ships[i];
			if (o == null || o == u || o.isDestroyed || o.unitData == null || o.unitData.unitSubtype == UnitSubType.Submarine)
			{
				continue;
			}
			float d = Utilities.GetXZDistance(o.transform.position, u.transform.position);
			if (d < (u.unitData.length + o.unitData.length) * 0.5f * 0.1f * 0.8f)
			{
				return o;
			}
		}
		return null;
	}

	// Once a second: what is attacking this ship?
	public static void Check(UnitAI ai, Unit u, ModAAEvade.State s, bool allowed)
	{
		if (!allowed || EngagementManager.instance == null || EngagementManager.instance.allAirUnits == null)
		{
			ModAAEvade.Expire(ai, u, s);
			return;
		}
		// 1. torpedoes already in the water and heading for us: steer parallel to their tracks
		Vector3 track;
		if (ModAAEvade.TorpedoInWater(u, out track))
		{
			bool fresh = s.mode != 3;
			if (s.mode == 0)
			{
				ModAAEvade.Begin(ai, u, s);
			}
			s.mode = 3;
			s.threat = null;
			s.until = Time.time + ModAAEvade.TrackHold;
			s.combDir = ModAAEvade.CombDirection(u, track);
			if (fresh)
			{
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": torpedo tracks in the water heading for her, turning to run parallel to them");
			}
			return;
		}
		if (s.mode == 3 && Time.time < s.until)
		{
			return;
		}
		// 2. formation ships turn together with their leader
		Unit leader = ai.followingUnit;
		if (leader != null && leader != u && !leader.isDestroyed && leader.unitSea != null)
		{
			ModAAEvade.State ls = ModAAEvade.GetState(leader);
			// v0.20.9: also while the leader is combing torpedo tracks (before, the formation went back to station then,
			// straight across the tracks)
			if (ls.mode == 1 || ls.mode == 2 || ls.mode == 3)
			{
				s.synced = true;
				if (s.mode == 0)
				{
					ModAAEvade.Begin(ai, u, s);
					UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": turning together with " + leader.unitInstanceName);
				}
				s.mode = ls.mode;
				s.threat = ls.threat;
				s.combDir = ls.combDir;
				s.turnSign = ls.turnSign;
				s.until = Time.time + ((ls.mode == 1) ? ModAAEvade.CombHold : ((ls.mode == 3) ? ModAAEvade.TrackHold : ModAAEvade.TurnHold));
				return;
			}
		}
		// 3. aircraft on their attack run
		Unit torp = null;
		float torpDist = float.MaxValue;
		Unit bomb = null;
		float bombDist = float.MaxValue;
		string bombKind = "";
		int torpCount = 0;
		int bombCount = 0;
		List<Unit> air = EngagementManager.instance.allAirUnits;
		for (int i = 0; i < air.Count; i++)
		{
			Unit p = air[i];
			if (p == null || p.isDestroyed || p.faction == u.faction || p.unitAIAir == null)
			{
				continue;
			}
			UnitAIAir pa = p.unitAIAir;
			if (pa.focusedUnit != u || pa.currentAIAction != AIAction.Attack_Unit)
			{
				continue;
			}
			float d = Utilities.GetXZDistance(p.transform.position, u.transform.position);
			float alt = p.transform.position.y;
			if (pa.aiAttack == AIAttack.Aerial_Torpedo || (pa.aiAttack == AIAttack.Level_Bomb && alt < ModAAEvade.LowLevelAltitude))
			{
				// inside 2.5 km they are committed; further out, only once they are heading in
				if (d < ModAAEvade.TorpedoCommitted || (d < ModAAEvade.TorpedoPlaneRange && ModAAEvade.HeadingAt(p, u, 60f)))
				{
					torpCount++;
					if (d < torpDist)
					{
						torpDist = d;
						torp = p;
					}
				}
			}
			else if (pa.aiAttack == AIAttack.Dive_Bomb || pa.aiAttack == AIAttack.Dive_Bomb_Approach || pa.currentManeuvre == Maneuvre.Roll_Over || pa.currentManeuvre == Maneuvre.Dive_Bomb || pa.currentManeuvre == Maneuvre.DiveBomb_Dive)
			{
				if (d < ModAAEvade.DiveRange)
				{
					bombCount++;
					if (d < bombDist)
					{
						bombDist = d;
						bomb = p;
						bombKind = "dive bombers";
					}
				}
			}
			else if (pa.aiAttack == AIAttack.Level_Bomb)
			{
				if (d < ModAAEvade.LevelRange)
				{
					bombCount++;
					if (d < bombDist)
					{
						bombDist = d;
						bomb = p;
						bombKind = "level bombers";
					}
				}
			}
		}
		// torpedoes do the most harm, so combing them comes first
		if (torp != null || bomb != null)
		{
			s.synced = false;
		}
		if (torp != null)
		{
			bool fresh = s.mode != 1 || s.threat != torp;
			if (s.mode == 0)
			{
				ModAAEvade.Begin(ai, u, s);
			}
			s.mode = 1;
			s.threat = torp;
			s.until = Time.time + ModAAEvade.CombHold;
			s.combDir = ModAAEvade.CombDirection(u, torp.transform.position - u.transform.position);
			if (fresh)
			{
				float a = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, torp.transform.position);
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": " + torpCount + " torpedo plane(s) on their run, nearest " + (torpDist * 10f / 1000f).ToString("F1") + " km " + ModAAEvade.Side(a) + ", full speed and turning " + (Mathf.Abs(a) < 90f ? "bow on" : "stern on") + " to comb the torpedoes");
			}
			return;
		}
		if (bomb != null && s.mode != 1)
		{
			bool fresh = s.mode != 2;
			if (s.mode == 0)
			{
				ModAAEvade.Begin(ai, u, s);
			}
			s.mode = 2;
			s.until = Time.time + ModAAEvade.TurnHold;
			if (fresh)
			{
				// turn away from the side the bombers are on, so the ship's track bends out of their aim
				float a = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, bomb.transform.position);
				s.turnSign = (a >= 0f) ? -1f : 1f;
				s.reversedFor = null;
				s.lastReverse = Time.time;
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": " + bombCount + " " + bombKind + " attacking, nearest " + (bombDist * 10f / 1000f).ToString("F1") + " km " + ModAAEvade.Side(a) + ", full speed and hard " + (s.turnSign > 0f ? "to starboard" : "to port"));
			}
			s.threat = bomb;
			// dive bombers aim for where she will be if she keeps turning: reverse the rudder when one pushes over
			// (again for the next one, but not more often than every 8 s)
			if (bomb != s.reversedFor && Time.time - s.lastReverse > 8f && bomb.unitAIAir != null && (bomb.unitAIAir.aiAttack == AIAttack.Dive_Bomb || bomb.unitAIAir.currentManeuvre == Maneuvre.DiveBomb_Dive || bomb.unitAIAir.currentManeuvre == Maneuvre.Dive_Bomb))
			{
				s.reversedFor = bomb;
				s.lastReverse = Time.time;
				s.turnSign = -s.turnSign;
				UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": dive bombers pushing over, rudder reversed " + (s.turnSign > 0f ? "to starboard" : "to port"));
			}
			return;
		}
		// v0.20.9: when the leader is done, hold the evasive heading for the rest of the hold time
		// (torpedoes may still be running) before going back to station
		if (s.synced && s.mode != 0)
		{
			if (Time.time >= s.until)
			{
				ModAAEvade.Stop(ai, u, s, "formation leader finished evading");
			}
			return;
		}
		ModAAEvade.Expire(ai, u, s);
	}

	// Is the aircraft flying towards the ship (within this many degrees)?
	public static bool HeadingAt(Unit p, Unit u, float degrees)
	{
		Vector3 to = u.transform.position - p.transform.position;
		Vector3 fwd = p.transform.forward;
		to.y = 0f;
		fwd.y = 0f;
		if (to.sqrMagnitude < 0.01f || fwd.sqrMagnitude < 0.0001f)
		{
			return true;
		}
		return Vector3.Angle(fwd, to) < degrees;
	}

	// An enemy torpedo within sight that will pass close to the ship if she holds on; returns its direction of travel
	public static bool TorpedoInWater(Unit u, out Vector3 track)
	{
		track = Vector3.zero;
		if (Map.instance == null || Map.instance.allMapTorpedoes == null)
		{
			return false;
		}
		float bestDist = float.MaxValue;
		float halfLength = u.unitData.length * 0.5f * 0.1f;
		for (int i = 0; i < Map.instance.allMapTorpedoes.Count; i++)
		{
			MapTorpedo mt = Map.instance.allMapTorpedoes[i];
			if (mt == null || mt.ammoTorpedo == null || !mt.ammoTorpedo.gameObject.activeInHierarchy || mt.ammoTorpedo.parentAmmunition == null)
			{
				continue;
			}
			if (ModAAEvade.TorpedoFaction(mt.ammoTorpedo) == (int)u.faction)
			{
				continue;
			}
			Vector3 p = mt.ammoTorpedo.transform.position;
			Vector3 f = mt.ammoTorpedo.transform.forward;
			f.y = 0f;
			if (f.sqrMagnitude < 0.0001f)
			{
				continue;
			}
			f.Normalize();
			Vector3 r = u.transform.position - p;
			r.y = 0f;
			float d = r.magnitude;
			float along = Vector3.Dot(r, f);
			if (d > ModAAEvade.TorpedoTrackSight || along <= 0f)
			{
				continue;
			}
			float miss = (r - f * along).magnitude;
			if (miss < halfLength + ModAAEvade.TorpedoTrackMiss && d < bestDist)
			{
				bestDist = d;
				track = f;
			}
		}
		return bestDist < float.MaxValue;
	}

	public static int TorpedoFaction(AmmunitionMoveTorpedo torp)
	{
		int id = torp.parentAmmunition.firedByUnitID;
		List<MapUnit> units = Map.instance.allMapUnits;
		if (units != null && id >= 0 && id < units.Count && units[id] != null && units[id].thisUnit != null)
		{
			return (int)units[id].thisUnit.faction;
		}
		return (int)torp.parentAmmunition.faction;
	}

	// Of the two ways along a line (towards / away), the one closer to the ship's heading
	public static Vector3 CombDirection(Unit u, Vector3 line)
	{
		line.y = 0f;
		if (line.sqrMagnitude < 0.0001f)
		{
			return u.transform.forward;
		}
		line.Normalize();
		Vector3 fwd = u.transform.forward;
		fwd.y = 0f;
		return (Vector3.Dot(fwd, line) >= 0f) ? line : -line;
	}

	public static string Side(float angle)
	{
		float a = Mathf.Abs(angle);
		string side = (angle >= 0f) ? "starboard" : "port";
		if (a < 30f)
		{
			return "ahead";
		}
		if (a > 150f)
		{
			return "astern";
		}
		return "off the " + side + (a < 70f ? " bow" : (a > 110f ? " quarter" : " beam"));
	}

	public static void Begin(UnitAI ai, Unit u, ModAAEvade.State s)
	{
		// a player ship on manual speed and rudder gets them back afterwards
		s.restoreManual = u.faction == Faction.Player && ai.currentAIAction == AIAction.Nothing;
		s.savedSpeed = u.wantedSpeed;
		s.savedTurn = u.wantedTurnRate;
	}

	// The hold time after the last attacker has run out
	public static void Expire(UnitAI ai, Unit u, ModAAEvade.State s)
	{
		if (s.mode != 0 && Time.time >= s.until)
		{
			ModAAEvade.Stop(ai, u, s, "attack over");
		}
	}

	public static void Stop(UnitAI ai, Unit u, ModAAEvade.State s, string why)
	{
		if (s.restoreManual && ai.currentAIAction == AIAction.Nothing)
		{
			u.wantedSpeed = s.savedSpeed;
			u.wantedTurnRate = s.savedTurn;
		}
		s.mode = 0;
		s.threat = null;
		s.synced = false;
		s.restoreManual = false;
		UnityEngine.Debug.Log("[AAEVADE] " + u.unitInstanceName + ": " + why + ", back to " + (u.faction == Faction.Player && ai.currentAIAction == AIAction.Nothing ? "her previous speed and rudder" : "her orders"));
	}
}
```

## Testing
1. Start a battle where enemy aircraft attack your ships, with hazard evasion on.
2. When torpedo planes are inside about 3 km on their run, the target ship should go to full speed and swing her bow (or stern) towards them before they drop.
3. When dive bombers push over, the target should go to full speed and turn hard.
4. Afterwards she should go back to her orders or formation.
5. Switch evasion off for one ship: she should hold her course.
6. Send your own strike at an AI ship: it should dodge the same way.
7. In `output_log.txt`:
   - `[AAEVADE] Hornet: 4 torpedo plane(s) on their run, nearest 2.8 km off the port bow, full speed and turning bow on to comb the torpedoes`
   - `[AAEVADE] Yorktown: 3 dive bombers attacking, nearest 1.2 km off the starboard beam, full speed and hard to port`
   - `[AAEVADE] Hornet: attack over, back to her orders`

## Tuning (top of ModAAEvade)
- `TorpedoPlaneRange` 4,000 m, `TorpedoCommitted` 2,500 m, `TorpedoTrackSight` 1,000 m, `DiveRange` 4,500 m (3,000 m before v0.20.3), `LevelRange` 4,000 m, `LowLevelAltitude` 300 m.
- `StuckChecks` 4 s and `UnstickSeconds` 10 s: when a stuck ship backs off, and for how long.
- `CombHold` 40 s, `TrackHold` 15 s and `TurnHold` 20 s: how long to keep evading after the attack.

## Notes
- Submarines are left out.
- Tag: `[AAEVADE]`. I could not compile or run this.


## v0.20.6
See fixes_v0.20.6.md: only one of two stuck ships gives way, then both turn apart. The code above is the v0.20.6 version.


## v0.20.9
See fixes_v0.20.9.md. The code above is the v0.20.9 version.
