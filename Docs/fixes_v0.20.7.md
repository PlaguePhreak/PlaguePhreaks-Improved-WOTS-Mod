# v0.20.7 fixes: Wildcats actually attack, torpedo drop check tidied

## What the test showed (14 Oct, Wildcats against Zeros, Avengers and Dauntlesses against a fleet)
- **The Wildcats never really attacked.** Following one Wildcat (id -134048) through the log: "diving on Zero" and "pass on Zero done" came in the same second, over and over, while it climbed from 5,000 m to 5,900 m. The "pass done" check ended a run as soon as the target was behind the plane (more than 100 degrees off its nose). After a zoom climb the Zero is always behind, so every run ended the moment it started, and the next zoom climbed higher again. Wildcat runs: 648 "pass done" for 621 "diving on".
- The Zeros fought normally (turning, high yo-yos, slashing passes on the bombers), which is why it was one-sided.
- **Torpedo runs (v0.20.5) worked:** an Avenger astern of Shokaku flew round to get ahead, and drop points closer than 600 m were moved out. The "drop point was 0 m" lines were from far out, where the set-up code parks the aim point on the ship; harmless, but now skipped.

## Pitch and height (your question)
Yes: in this game a plane's pitch comes only from its height. `UnitAir.ApplyFlightControls` pitches the nose by the difference between the height it wants and the height it is at, limited to the plane's dive and climb angles (Wildcat 23.5 degrees down, 13.5 up), and smoothed. Planes can't point their nose at a target above or below them; they change height and their guns follow. So a dive from far above is a gentle slope, not a steep dive, and the gun run happens near the target's height. That is why our setup keeps the height advantage to a sensible 400-500 m.

## What changes
**ModDogfight**
- A run can only end after the target has been in front of the fighter (within 45 degrees of its nose) during that run. So after a zoom climb the fighter turns back, gets the enemy in front, makes its firing pass, and only then breaks away.
- If a run never gets the target in front within 20 s, the fighter gives up and sets up again.
- Zoom climbs go no more than 1 km above the target, so fighters stop climbing away from the fight.

**ModTorpRun**
- The 600 m drop check only works inside 2.5 km (the run in), not further out.
- A flight counts as "ahead" again only once it is 15 degrees inside the astern line (105 degrees), so the astern / ahead messages don't flick back and forth at the edge.

## Install
1. Right-click class **ModDogfight** > **Edit Class (C#)**, select everything (Ctrl+A), paste the new `ModDogfight.cs` below over it, **Compile**, then **File > Save Module**.
2. Right-click class **ModTorpRun** > **Edit Class (C#)**, select everything (Ctrl+A), paste the new `ModTorpRun.cs` below over it, **Compile**, then **File > Save Module**.
Nothing else changes.

## Testing
1. Wildcats against Zeros: after each zoom climb the Wildcats should turn back, dive on a Zero and shoot, then climb away. In the log, "diving on" and "pass done" should now be several seconds apart, with heights staying within about 1 km of the Zeros.
2. Zeros should start falling as well as Wildcats.

## ModDogfight.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.4 / v0.20.6 / v0.20.7: fighter manoeuvres. The game's dogfight is pure pursuit at the target's height, so fighters look like they
// are on rails. This flies everything around the gun pass, following real WW2 doctrine:
//   US fighters (boom and zoom): climb above the enemy, dive in for one firing pass, zoom climb away, repeat.
//     Never turn-fight a Zero. Under attack: break towards the threat and dive away. A wingman nearby turns in on the
//     attacker (the Thach Weave).
//   Japanese fighters (turn fighting): stay in the turning fight. If they are about to overshoot, pull up into a
//     high yo-yo and drop back behind. Under attack: a hard climbing break turn. The Zero gets heavy controls at high
//     speed, so it turns poorly in a fast dive.
//   Against bombers, both sides make slashing passes from above and to the side, then pull away from the gunners.
// The game's own code still flies the actual gun run (aiming and firing); this class flies the rest.
// Planes dive faster than their level top speed and lose speed in a zoom climb (a simple energy model).
public class ModDogfight
{
	public class State
	{
		public int phase;           // 0 attack (game's gun run), 1 position (get above and to the side), 2 zoom / extend, 3 high yo-yo, 4 defend
		public float phaseUntil;
		public float phaseStart;
		public float attackStart;
		public float turnSign;
		public float targetHeight;
		public float side;          // which side of the target to set up on
		public float nextThreatCheck;
		public float defendCooldown;
		public Unit threat;
		public Unit lastTarget;
		public float wobble;
		public float nextRepick;
		// v0.20.7: the target has been in front of us during this run (a pass can only end after that)
		public bool sawAhead;
	}

	// distances and heights in battle code are metres x 0.1
	public const float ThreatRange = 600f * 0.1f;
	public const float OvershootRange = 120f * 0.1f;
	public const float USHeightAdvantage = 500f * 0.1f;
	public const float BomberHeightAdvantage = 400f * 0.1f;
	public const float SetupOffset = 800f * 0.1f;
	public const float ZoomHeight = 500f * 0.1f;
	public const float YoYoHeight = 150f * 0.1f;
	public const float SplitSDrop = 400f * 0.1f;
	public const float MinHeight = 200f * 0.1f;
	public const float MaxHeight = 8000f * 0.1f;
	public const float WingmanRange = 1500f * 0.1f;
	// dive speed limits (share of level top speed) and the Zero's heavy controls at high speed
	public const float USDiveSpeed = 1.2f;
	public const float JapanDiveSpeed = 1.1f;
	public const float HeavyControlsSpeed = 1.05f;
	public const float HeavyControlsTurn = 0.55f;
	// how long a US fighter stays in one gun run before zooming away (seconds)
	public const float USPassTime = 8f;
	public const float BomberPassTime = 6f;
	// v0.20.6: how often a fighter may look for a better target (seconds), and how long a turning fight
	// goes on before it looks again
	public const float RepickSeconds = 5f;
	public const float TurnFightRepick = 12f;
	// v0.20.7: give up a run that never got the target in front after this long (seconds),
	// and never zoom higher than this above the target
	public const float RunGiveUp = 20f;
	public const float MaxAbove = 1000f * 0.1f;

	public static Dictionary<int, ModDogfight.State> states = new Dictionary<int, ModDogfight.State>();

	public static ModDogfight.State GetState(Unit u)
	{
		int id = u.GetInstanceID();
		ModDogfight.State s;
		if (!ModDogfight.states.TryGetValue(id, out s))
		{
			s = new ModDogfight.State();
			s.wobble = Random.Range(0f, 100f);
			s.side = (Random.value < 0.5f) ? -1f : 1f;
			ModDogfight.states[id] = s;
		}
		return s;
	}

	public static bool IsJapanese(Unit u)
	{
		return u.unitData != null && u.unitData.nationIndex == 3;
	}

	public static bool IsFighter(Unit u)
	{
		return u != null && u.unitData != null && u.unitData.unitSubtype == UnitSubType.Fighter;
	}

	// First line of UnitAIAir.DogfightApproach. Returns true when this class has flown the aircraft this tick
	// (the game's pursuit and firing are then skipped); false lets the game fly the gun run as usual.
	public static bool Fly(UnitAIAir ai)
	{
		try
		{
			Unit u = ai.parentUnit;
			Unit target = ai.focusedUnit;
			if (!ModDogfight.IsFighter(u) || u.unitAir == null || target == null || target.isDestroyed || target.unitAir == null || u.isDestroyed)
			{
				return false;
			}
			ModDogfight.State s = ModDogfight.GetState(u);
			float now = Time.time;
			bool japanese = ModDogfight.IsJapanese(u);
			bool targetIsFighter = ModDogfight.IsFighter(target);
			float dist = Vector3.Distance(u.transform.position, target.transform.position);
			if (target != s.lastTarget)
			{
				s.lastTarget = target;
				ModDogfight.StartAttack(u, target, s, japanese, targetIsFighter, dist, now);
			}
			// someone on my tail?
			if (now >= s.nextThreatCheck)
			{
				s.nextThreatCheck = now + 0.5f;
				s.threat = ModDogfight.FindThreat(u);
				if (s.threat != null && s.phase != 4 && now >= s.defendCooldown)
				{
					ModDogfight.StartDefend(u, s, japanese, now);
				}
			}
			switch (s.phase)
			{
			case 0:
				return ModDogfight.Attack(u, target, s, japanese, targetIsFighter, dist, now);
			case 1:
				return ModDogfight.Position(u, target, s, japanese, targetIsFighter, dist, now);
			case 2:
				return ModDogfight.Zoom(u, target, s, japanese, targetIsFighter, dist, now);
			case 3:
				return ModDogfight.YoYo(u, target, s, japanese, targetIsFighter, dist, now);
			default:
				return ModDogfight.Defend(u, target, s, japanese, targetIsFighter, dist, now);
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[DOGFIGHT] fly failed: " + ex.Message);
			return false;
		}
	}

	// A new target: US fighters (and anyone against bombers) first get above it unless they already are
	public static void StartAttack(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		float adv = u.transform.position.y - target.transform.position.y;
		float want = targetIsFighter ? (japanese ? 0f : ModDogfight.USHeightAdvantage) : ModDogfight.BomberHeightAdvantage;
		if (want > 0f && adv < want * 0.6f && dist > 1000f * 0.1f)
		{
			ModDogfight.SetPhase(u, s, 1, now, 25f, "climbing to get above " + ModDogfight.Name(target) + " before attacking (" + (adv * 10f).ToString("F0") + " m height advantage)");
		}
		else
		{
			ModDogfight.SetPhase(u, s, 0, now, 0f, null);
		}
	}

	// Phase 0: the game's own gun run. Leave it when it is time to break off.
	public static bool Attack(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		ModDogfight.Energy(u, japanese);
		Vector3 to = target.transform.position - u.transform.position;
		float ata = Vector3.Angle(u.transform.forward, to);
		float inRun = now - s.attackStart;
		if (ata < 45f)
		{
			s.sawAhead = true;
		}
		// about to fly past the target
		if (dist < ModDogfight.OvershootRange && ata < 60f)
		{
			if (japanese && targetIsFighter)
			{
				ModDogfight.SetPhase(u, s, 3, now, 3f, "about to overshoot " + ModDogfight.Name(target) + ", high yo-yo");
			}
			else
			{
				ModDogfight.SetPhase(u, s, 2, now, 7f, "passing " + ModDogfight.Name(target) + ", zoom climb away");
			}
			return true;
		}
		// US fighters make one pass and climb away; everyone does against bombers
		if (!targetIsFighter && ((s.sawAhead && (inRun > ModDogfight.BomberPassTime || ata > 100f)) || inRun > ModDogfight.RunGiveUp))
		{
			ModDogfight.SetPhase(u, s, 2, now, 7f, "slashing pass on " + ModDogfight.Name(target) + " done, pulling away from the gunners");
			return true;
		}
		if (targetIsFighter && !japanese && ((s.sawAhead && (inRun > ModDogfight.USPassTime || (ata > 100f && dist > 300f * 0.1f))) || inRun > ModDogfight.RunGiveUp))
		{
			ModDogfight.SetPhase(u, s, 2, now, 7f, "pass on " + ModDogfight.Name(target) + " done, zoom climb (no turning fight)");
			return true;
		}
		// a long turning fight: see whether someone else needs attacking more (spreads fighters out)
		if (inRun > ModDogfight.TurnFightRepick && dist > 300f * 0.1f && ModDogfight.Repick(u, s, now))
		{
			s.attackStart = now;
			s.sawAhead = false;
		}
		return false;
	}

	// Phase 1: get above the target and out to one side, then dive in
	public static bool Position(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		float want = targetIsFighter ? ModDogfight.USHeightAdvantage : ModDogfight.BomberHeightAdvantage;
		Vector3 tp = target.transform.position;
		Vector3 right = target.transform.right;
		right.y = 0f;
		Vector3 aim = tp + right.normalized * ModDogfight.SetupOffset * s.side;
		ModDogfight.Steer(u, aim, 1f, s, japanese);
		ModDogfight.SetHeight(u, tp.y + want, s);
		float adv = u.transform.position.y - tp.y;
		if ((adv > want * 0.8f && dist < 2000f * 0.1f) || now > s.phaseUntil)
		{
			ModDogfight.SetPhase(u, s, 0, now, 0f, "diving on " + ModDogfight.Name(target) + " from " + (adv * 10f).ToString("F0") + " m above");
		}
		return true;
	}

	// Phase 2: zoom climb / extend away after a pass, then set up again
	public static bool Zoom(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		// mostly straight, a gentle turn to the setup side
		u.wantedTurnRate = s.side * u.unitData.maxTurnRate * 0.25f;
		// v0.20.7: zoom up, but not more than 1 km above the target (they were climbing higher with every loop)
		ModDogfight.SetHeight(u, Mathf.Min(s.targetHeight, target.transform.position.y + ModDogfight.MaxAbove), s);
		ModDogfight.Energy(u, japanese);
		if (now > s.phaseUntil)
		{
			s.side = -s.side;
			// v0.20.6: between passes, pick the best target again (spreads fighters out as more enemies are seen)
			ModDogfight.Repick(u, s, now);
			target = u.unitAI.focusedUnit;
			targetIsFighter = ModDogfight.IsFighter(target);
			if (japanese && targetIsFighter)
			{
				ModDogfight.SetPhase(u, s, 0, now, 0f, "turning back in on " + ModDogfight.Name(target));
			}
			else
			{
				ModDogfight.SetPhase(u, s, 1, now, 25f, "setting up another pass on " + ModDogfight.Name(target));
			}
		}
		return true;
	}

	// Phase 3: high yo-yo - pull up and ease the turn so as not to overshoot, then drop back in behind
	public static bool YoYo(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		ModDogfight.Steer(u, target.transform.position, 0.5f, s, japanese);
		ModDogfight.SetHeight(u, s.targetHeight, s);
		u.wantedSpeed = u.unitData.maxSpeed * 0.85f;
		if (now > s.phaseUntil)
		{
			ModDogfight.SetPhase(u, s, 0, now, 0f, "dropping back in behind " + ModDogfight.Name(target));
		}
		return true;
	}

	// Phase 4: defend - break hard towards the threat (and dive away if US, climbing turn if Japanese)
	public static bool Defend(Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		u.wantedTurnRate = s.turnSign * u.unitData.maxTurnRate * ModDogfight.ControlFactor(u, japanese);
		ModDogfight.SetHeight(u, s.targetHeight, s);
		ModDogfight.Energy(u, japanese);
		if (now > s.phaseUntil)
		{
			s.defendCooldown = now + 3f;
			if (japanese)
			{
				ModDogfight.SetPhase(u, s, 0, now, 0f, "back on the attack");
			}
			else
			{
				ModDogfight.SetPhase(u, s, 1, now, 25f, "clear, climbing back to attack");
			}
		}
		return true;
	}

	public static void StartDefend(Unit u, ModDogfight.State s, bool japanese, float now)
	{
		Unit threat = s.threat;
		float a = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, threat.transform.position);
		s.turnSign = (a >= 0f) ? 1f : -1f;
		string how;
		if (japanese)
		{
			s.targetHeight = u.transform.position.y + 60f * 0.1f;
			how = "hard climbing break turn";
		}
		else
		{
			s.targetHeight = u.transform.position.y - ModDogfight.SplitSDrop;
			how = "breaking and diving away";
			// Thach Weave: turn towards a wingman, who turns in on the attacker
			Unit wing = ModDogfight.FindWingman(u, threat);
			if (wing != null)
			{
				float wa = Utilities.GetSignedAngleToPosition(u.transform.forward, u.transform.position, wing.transform.position);
				s.turnSign = (wa >= 0f) ? 1f : -1f;
				wing.unitAI.focusedUnit = threat;
				ModDogfight.State ws = ModDogfight.GetState(wing);
				ws.lastTarget = threat;
				ModDogfight.SetPhase(wing, ws, 0, now, 0f, null);
				how = "Thach Weave, turning towards " + wing.unitData.unitName + " who turns in on the attacker";
			}
		}
		ModDogfight.SetPhase(u, s, 4, now, Random.Range(4f, 6f), ModDogfight.Name(threat) + " on her tail at " + (Vector3.Distance(u.transform.position, threat.transform.position) * 10f).ToString("F0") + " m, " + how);
	}

	// v0.20.6: ask the game's target choice (our v0.17 fighter AI, which spreads fighters out) for the best target now.
	// Returns true if the target changed.
	public static bool Repick(Unit u, ModDogfight.State s, float now)
	{
		if (now < s.nextRepick || EngagementAI.instance == null || u.unitAI == null)
		{
			return false;
		}
		s.nextRepick = now + ModDogfight.RepickSeconds;
		List<Unit> enemies = (u.faction == Faction.Player) ? EngagementAI.instance.otherAir : EngagementAI.instance.playerAir;
		if (enemies == null)
		{
			return false;
		}
		Unit old = u.unitAI.focusedUnit;
		Unit pick = EngagementAI.instance.GetBestDogfightTarget(u, enemies);
		if (pick == null || pick == old || pick.isDestroyed)
		{
			return false;
		}
		u.unitAI.focusedUnit = pick;
		s.lastTarget = pick;
		UnityEngine.Debug.Log("[DOGFIGHT] " + u.unitData.unitName + " id " + u.GetInstanceID() + " (" + (u.faction == Faction.Player ? "ours" : "enemy") + "): switching from " + ModDogfight.Name(old) + " to " + ModDogfight.Name(pick) + " id " + pick.GetInstanceID());
		return true;
	}

	// An enemy fighter behind us, close, pointing at us and targeting us
	public static Unit FindThreat(Unit u)
	{
		if (EngagementManager.instance == null || EngagementManager.instance.allAirUnits == null)
		{
			return null;
		}
		List<Unit> air = EngagementManager.instance.allAirUnits;
		Unit best = null;
		float bestDist = ModDogfight.ThreatRange;
		for (int i = 0; i < air.Count; i++)
		{
			Unit e = air[i];
			if (e == null || e.isDestroyed || e.faction == u.faction || !ModDogfight.IsFighter(e) || e.unitAI == null || e.unitAI.focusedUnit != u)
			{
				continue;
			}
			float d = Vector3.Distance(e.transform.position, u.transform.position);
			if (d > bestDist)
			{
				continue;
			}
			// it is behind us, and we are in front of its nose
			if (Vector3.Angle(-u.transform.forward, e.transform.position - u.transform.position) < 70f && Vector3.Angle(e.transform.forward, u.transform.position - e.transform.position) < 25f)
			{
				bestDist = d;
				best = e;
			}
		}
		return best;
	}

	// A friendly fighter close by that is free to help
	public static Unit FindWingman(Unit u, Unit threat)
	{
		List<Unit> air = EngagementManager.instance.allAirUnits;
		Unit best = null;
		float bestDist = ModDogfight.WingmanRange;
		for (int i = 0; i < air.Count; i++)
		{
			Unit w = air[i];
			if (w == null || w == u || w.isDestroyed || w.faction != u.faction || !ModDogfight.IsFighter(w) || w.unitAIAir == null || w.unitAIAir.aiAttack != AIAttack.Dogfight || w.unitAI.focusedUnit == threat)
			{
				continue;
			}
			if (ModDogfight.GetState(w).phase == 4)
			{
				continue;
			}
			float d = Vector3.Distance(w.transform.position, u.transform.position);
			if (d < bestDist)
			{
				bestDist = d;
				best = w;
			}
		}
		return best;
	}

	// Turn towards a point (scale = share of full rudder), with a little pilot wobble so it isn't on rails
	public static void Steer(Unit u, Vector3 point, float scale, ModDogfight.State s, bool japanese)
	{
		Vector3 fwd = u.transform.forward;
		fwd.y = 0f;
		Vector3 pos = u.transform.position;
		point.y = pos.y;
		float angle = Utilities.GetSignedAngleToPosition(fwd, pos, point);
		float max = u.unitData.maxTurnRate * ModDogfight.ControlFactor(u, japanese);
		float wob = Mathf.Sin((Time.time + s.wobble) * 0.7f) * 0.1f * max;
		u.wantedTurnRate = Mathf.Clamp(angle + wob, -max, max) * scale;
	}

	public static void SetHeight(Unit u, float h, ModDogfight.State s)
	{
		float wob = Mathf.Sin((Time.time + s.wobble) * 0.4f) * 30f * 0.1f;
		u.wantedHeight = Mathf.Clamp(h + wob, ModDogfight.MinHeight, ModDogfight.MaxHeight);
	}

	// Diving builds speed past level top speed, climbing costs it
	public static void Energy(Unit u, bool japanese)
	{
		float max = u.unitData.maxSpeed;
		float dh = u.wantedHeight - u.transform.position.y;
		if (dh < -50f * 0.1f)
		{
			u.wantedSpeed = max * (japanese ? ModDogfight.JapanDiveSpeed : ModDogfight.USDiveSpeed);
		}
		else if (dh > 50f * 0.1f)
		{
			u.wantedSpeed = max * 0.8f;
		}
		else
		{
			u.wantedSpeed = max;
		}
	}

	// The Zero's controls stiffen at high speed
	public static float ControlFactor(Unit u, bool japanese)
	{
		if (japanese && u.currentSpeed > u.unitData.maxSpeed * ModDogfight.HeavyControlsSpeed)
		{
			return ModDogfight.HeavyControlsTurn;
		}
		return 1f;
	}

	public static void SetPhase(Unit u, ModDogfight.State s, int phase, float now, float duration, string why)
	{
		s.phase = phase;
		s.phaseStart = now;
		s.phaseUntil = now + duration;
		if (phase == 0)
		{
			s.attackStart = now;
			s.sawAhead = false;
		}
		else if (phase == 2)
		{
			s.targetHeight = u.transform.position.y + ModDogfight.ZoomHeight;
		}
		else if (phase == 3)
		{
			s.targetHeight = u.transform.position.y + ModDogfight.YoYoHeight;
		}
		if (why != null)
		{
			UnityEngine.Debug.Log("[DOGFIGHT] " + u.unitData.unitName + " id " + u.GetInstanceID() + " (" + (u.faction == Faction.Player ? "ours" : "enemy") + ", " + Time.time.ToString("F0") + " s, " + (u.transform.position.y * 10f).ToString("F0") + " m): " + why);
		}
	}

	public static string Name(Unit t)
	{
		return (t != null && t.unitData != null) ? t.unitData.unitName : "the enemy";
	}
}
```

## ModTorpRun.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.5 / v0.20.7: torpedo bomber runs.
// 1. Torpedo planes that find themselves astern of their target fly round to get ahead of her before going in,
//    instead of chasing her from behind. Only if they still can't get ahead after 2 minutes do they attack from astern.
// 2. A torpedo is never dropped closer than 600 m from the ship (the game's aim could put the drop point right on top
//    of a fast ship being chased from behind). Real torpedoes needed a few hundred metres to arm and settle.
public class ModTorpRun
{
	// distances in battle code are metres x 0.1
	public const float MinDrop = 600f * 0.1f;
	// "astern" = more than this many degrees off the ship's bow
	public const float SternAngle = 120f;
	// only counts as stuck astern inside this range
	public const float SternRange = 4000f * 0.1f;
	// seconds of trying to get ahead before attacking from astern anyway
	public const float SternGiveUp = 120f;
	// v0.20.7: only check the drop point on the run in (further out the set-up code moves the aim point around),
	// and count as "ahead" only once 15 degrees inside the astern line, so it doesn't flicker at the edge
	public const float DropCheckRange = 2500f * 0.1f;
	public const float AheadMargin = 15f;

	public static Dictionary<int, float> sternSince = new Dictionary<int, float>();
	public static HashSet<int> gaveUp = new HashSet<int>();

	// From UnitAIAir.ModTorpedoSetup: true = this flight is astern and should keep flying round to get ahead (don't commit yet)
	public static bool Astern(UnitAIAir ai, Unit target, float angleOffBow, float dist)
	{
		try
		{
			int id = ai.GetInstanceID();
			bool wasAstern = ModTorpRun.sternSince.ContainsKey(id);
			float line = wasAstern ? ModTorpRun.SternAngle - ModTorpRun.AheadMargin : ModTorpRun.SternAngle;
			if (angleOffBow < line || dist > ModTorpRun.SternRange)
			{
				if (angleOffBow < line && wasAstern)
				{
					ModTorpRun.sternSince.Remove(id);
					UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " is ahead of " + target.unitInstanceName + "'s beam now (" + angleOffBow.ToString("F0") + " deg off her bow, " + (dist * 10f).ToString("F0") + " m), turning in");
				}
				return false;
			}
			if (ModTorpRun.gaveUp.Contains(id))
			{
				return false;
			}
			float t0;
			if (!ModTorpRun.sternSince.TryGetValue(id, out t0))
			{
				ModTorpRun.sternSince[id] = Time.time;
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " is astern of " + target.unitInstanceName + " (" + angleOffBow.ToString("F0") + " deg off her bow, " + (dist * 10f).ToString("F0") + " m), flying round to get ahead before attacking");
				return true;
			}
			if (Time.time - t0 > ModTorpRun.SternGiveUp)
			{
				ModTorpRun.gaveUp.Add(id);
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + " couldn't get ahead of " + target.unitInstanceName + " in " + ModTorpRun.SternGiveUp.ToString("F0") + " s, attacking from astern");
				return false;
			}
			return true;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[TORPRUN] astern check failed: " + ex.Message);
			return false;
		}
	}

	// Second line of UnitAIAir.TorpedoApproach: move the drop point out if it is too close to the ship
	public static void KeepDropOut(UnitAIAir ai)
	{
		try
		{
			Unit target = ai.focusedUnit;
			if (target == null || target.isDestroyed || target.unitSea == null || ai.parentUnit == null)
			{
				return;
			}
			Vector3 tPos = target.transform.position;
			if (Utilities.GetXZDistance(ai.parentUnit.transform.position, tPos) > ModTorpRun.DropCheckRange)
			{
				return;
			}
			Vector3 ap = ai.attackPosition;
			Vector3 v = ap - tPos;
			v.y = 0f;
			if (v.magnitude >= ModTorpRun.MinDrop)
			{
				return;
			}
			// push it out towards the side the plane is coming from
			Vector3 dir = ai.parentUnit.transform.position - tPos;
			dir.y = 0f;
			if (dir.sqrMagnitude < 0.01f)
			{
				return;
			}
			dir.Normalize();
			Vector3 moved = tPos + dir * ModTorpRun.MinDrop;
			moved.y = ap.y;
			ai.attackPosition = moved;
			int id = ai.GetInstanceID();
			if (!ModTorpRun.logged.Contains(id))
			{
				ModTorpRun.logged.Add(id);
				UnityEngine.Debug.Log("[TORPRUN] " + ModTorpRun.Name(ai.parentUnit) + ": drop point was " + (v.magnitude * 10f).ToString("F0") + " m from " + target.unitInstanceName + ", moved out to " + (ModTorpRun.MinDrop * 10f).ToString("F0") + " m");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[TORPRUN] drop check failed: " + ex.Message);
		}
	}

	public static HashSet<int> logged = new HashSet<int>();

	public static string Name(Unit u)
	{
		return (u != null && u.unitData != null) ? u.unitData.unitName : "torpedo plane";
	}
}
```

Tags: `[DOGFIGHT]`, `[TORPRUN]`. I could not compile or run this.
