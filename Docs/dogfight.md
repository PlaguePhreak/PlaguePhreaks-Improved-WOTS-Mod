# Fighter manoeuvres (v0.20.4, AI super overhaul)

## What was wrong (found in the code)
`UnitAIAir.DogfightApproach` flies pure pursuit: it points the fighter at a lead point on the target, holds the target's height (`AdjustHeightToInterceptTarget`), fires when the target is in the gun cone, and makes a flat break turn when it gets very close (`BreakAwayFromUnit`). Nothing ever climbs, dives, extends or defends, so it looks like planes on rails. Planes also have no energy: diving doesn't make them faster, only turning slows them (`UnitAir.CalculateSpeedPenalty`).

## What changes
The game's own code still flies the actual gun run (aiming and firing). The new `ModDogfight` class flies everything around it, following real doctrine:

**US fighters (Wildcat, Hellcat and so on): boom and zoom**
- Against fighters they first climb to get about 500 m above the enemy and out to one side, then dive in for a firing pass.
- After one pass (at most 8 s) they zoom climb away instead of turning with the enemy, then set up again from the other side.
- **Under attack:** a break turn towards the attacker while diving away about 400 m.
- **Thach Weave:** if a friendly fighter is within 1.5 km, the one under attack turns towards it instead, and the wingman turns in on the attacker for a head-on shot.

**Japanese fighters (Zero): turn fighting**
- They stay in the turning fight (where the Zero is better).
- If about to overshoot, they pull up into a **high yo-yo** (about 150 m), ease the turn, and drop back in behind.
- **Under attack:** a hard climbing break turn towards the attacker.
- **Heavy controls at speed:** above 105% of level top speed the Zero only turns at 55% rate, as the real one did. So a Wildcat diving away really can escape.

**Against bombers (both sides): slashing passes**
- Get about 400 m above and out to one side, dive through for a pass of at most 6 seconds, then pull away from the gunners and set up again.

**Energy and feel**
- Diving now builds speed past level top speed (US up to 120%, Japanese up to 110%), and climbing costs speed.
- A small, slow wobble in heading and height so planes don't fly perfect lines.
- "Under attack" means an enemy fighter within 600 m, behind (within 70° of the tail), pointing at the plane (within 25°) and targeting it.

Crew experience (v0.18.6, next) will later change how quickly pilots react and how well they fly and shoot.

## Install (2 steps)
Back up the DLL first.

### Step 1 - add the class
1. Right-click `Assembly-CSharp` > **Add Class (C#)**, delete what is there and paste all of `ModDogfight.cs` below.
2. **Compile**, then **File > Save Module**. Close dnSpy and open it again.

### Step 2 - UnitAIAir.DogfightApproach
1. Find class **UnitAIAir**, right-click the method **`DogfightApproach`** > **Edit Method (C#)**.
2. Click just after the method's first `{`, press Enter and paste:
```csharp
if (ModDogfight.Fly(this))
{
	return;
}
```
3. **Compile**, then **File > Save Module**.

### ModDogfight.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.4 / v0.20.6 / v0.20.7 / v0.20.9: fighter manoeuvres. The game's dogfight is pure pursuit at the target's height, so fighters look like they
// are on rails. This flies everything around the gun pass, following real WW2 doctrine:
//   US fighters (boom and zoom): climb above the enemy, dive in for one firing pass, zoom climb away, repeat.
//     Never turn-fight a Zero. Under attack: break towards the threat and dive away. A wingman nearby turns in on the
//     attacker (the Thach Weave).
//   Japanese fighters (turn fighting): stay in the turning fight. If they are about to overshoot, pull up into a
//     high yo-yo and drop back behind. Under attack: a hard climbing break turn. The Zero gets heavy controls at high
//     speed, so it turns poorly in a fast dive.
//   Against bombers, both sides make slashing passes from above and to the side, then pull away from the gunners.
// v0.20.9: this class now flies the gun run too, aiming the nose up and down as well as left and right.
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
		// v0.20.9: closest the fighter has been to its target during this run (a pass ends once it is past it)
		public float minDist;
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
	public const float RunGiveUp = 30f;
	// v0.20.9: a pass is over once the fighter got within this range and is now this much further away again
	public const float PassCloseRange = 600f * 0.1f;
	public const float PassOpening = 150f * 0.1f;
	public const float MaxAbove = 1000f * 0.1f;
	// v0.20.9: our own gun run. The game pitches a plane only by the height difference it is chasing (up to its dive
	// angle), and only fires when the target is within 5 degrees of the nose, so diving fighters never fired.
	// The gun run now points the nose at where the target will be (lead), up and down as well as left and right.
	public const float BulletSpeed = 800f * 0.1f;
	public const float GunCone = 5f;
	public const float AimDive = 45f;

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
			s.minDist = float.MaxValue;
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
			if (!ModDogfight.IsFighter(u) || u.unitAir == null || target == null || target.isDestroyed || target.unitAir == null || target.unitAir.shootDown || u.isDestroyed)
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
			if (s.phase != 0)
			{
				ModDogfight.StopGuns(u);
				ModDogfight.NormalPitch(u);
			}
			switch (s.phase)
			{
			case 0:
				return ModDogfight.Attack(ai, u, target, s, japanese, targetIsFighter, dist, now);
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
	public static bool Attack(UnitAIAir ai, Unit u, Unit target, ModDogfight.State s, bool japanese, bool targetIsFighter, float dist, float now)
	{
		ModDogfight.Energy(u, japanese);
		Vector3 to = target.transform.position - u.transform.position;
		float ata = Vector3.Angle(u.transform.forward, to);
		float inRun = now - s.attackStart;
		if (ata < 45f)
		{
			s.sawAhead = true;
		}
		if (dist < s.minDist)
		{
			s.minDist = dist;
		}
		// v0.20.9: the pass is over once the fighter has come in close and is now opening the range again (it has
		// flown past or through the target), not after a fixed time (that ended dives before they reached gun range)
		bool passed = s.sawAhead && s.minDist < ModDogfight.PassCloseRange && dist > s.minDist + ModDogfight.PassOpening;
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
		if (!targetIsFighter && (passed || inRun > ModDogfight.RunGiveUp))
		{
			ModDogfight.SetPhase(u, s, 2, now, 7f, "slashing pass on " + ModDogfight.Name(target) + " done, pulling away from the gunners");
			return true;
		}
		if (targetIsFighter && !japanese && (passed || inRun > ModDogfight.RunGiveUp))
		{
			ModDogfight.SetPhase(u, s, 2, now, 7f, "pass on " + ModDogfight.Name(target) + " done, zoom climb (no turning fight)");
			return true;
		}
		// a long turning fight: see whether someone else needs attacking more (spreads fighters out)
		if (inRun > ModDogfight.TurnFightRepick && dist > 300f * 0.1f && ModDogfight.Repick(u, s, now))
		{
			s.attackStart = now;
			s.sawAhead = false;
			s.minDist = float.MaxValue;
			return true;
		}
		ModDogfight.GunRun(ai, u, target, dist);
		return true;
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

	// v0.20.9: fly the gun run. Aim at the lead point (where the target will be when the bullets get there), with the
	// nose pointed up or down at it too: the game sets pitch from the height difference the plane is chasing,
	// so wanting a height N units below the plane gives N degrees nose down. Fire when the lead point is within
	// 5 degrees of the nose and in gun range, as the game does.
	public static void GunRun(UnitAIAir ai, Unit u, Unit target, float dist)
	{
		Vector3 pos = u.transform.position;
		float tof = dist / ModDogfight.BulletSpeed;
		Vector3 lead = target.transform.position + target.transform.forward * target.currentActualSpeed * tof;
		Vector3 d = lead - pos;
		Vector3 flat = d;
		flat.y = 0f;
		// left / right
		Vector3 fwd = u.transform.forward;
		fwd.y = 0f;
		float yaw = Utilities.GetSignedAngleToPosition(fwd, pos, new Vector3(lead.x, pos.y, lead.z));
		u.wantedTurnRate = Mathf.Clamp(yaw, -u.unitData.maxTurnRate, u.unitData.maxTurnRate);
		// up / down: allow a steeper aiming dive than normal flight while lining up a shot
		float down = Mathf.Atan2(-d.y, Mathf.Max(flat.magnitude, 1f)) * Mathf.Rad2Deg;
		float aim = Vector3.Angle(u.transform.forward, d);
		if (aim < 20f)
		{
			u.unitAir.maxDiveClimb = new Vector2(Mathf.Max(u.unitData.dive + 4f, ModDogfight.AimDive), u.unitData.climb + 4f);
		}
		else
		{
			ModDogfight.NormalPitch(u);
		}
		u.wantedHeight = Mathf.Clamp(pos.y - down, ModDogfight.MinHeight, ModDogfight.MaxHeight);
		// guns
		WeaponParticle wp = u.weaponParticle;
		if (wp == null)
		{
			return;
		}
		float range = (ai.attackRange > 0f) ? ai.attackRange : 400f * 0.1f;
		bool inCone = dist < range && aim < ModDogfight.GunCone;
		if (inCone && !wp.enabled)
		{
			wp.FireAll(true);
		}
		else if (!inCone && wp.enabled)
		{
			ModDogfight.StopGuns(u);
		}
	}

	public static void StopGuns(Unit u)
	{
		if (u.weaponParticle != null && u.weaponParticle.enabled && (CombatInterface.instance == null || CombatInterface.instance.currentUnit != u))
		{
			u.weaponParticle.FireAll(false);
		}
	}

	public static void NormalPitch(Unit u)
	{
		u.unitAir.maxDiveClimb = new Vector2(u.unitData.dive, u.unitData.climb);
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
			s.minDist = float.MaxValue;
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

## Testing
1. A battle with fighters on both sides (for example your Wildcats escorting a strike against a Zero CAP).
2. Watch the Wildcats: they should climb above the Zeros, dive through, then zoom back up instead of circling.
3. Watch the Zeros: tight turning, pulling up when they would overshoot.
4. When a Zero gets on a Wildcat's tail, the Wildcat should break and dive. With another Wildcat nearby, the two should cross (the weave).
5. Fighters attacking bombers should make diving passes from above and to the side, not sit behind the tail.
6. In `output_log.txt`, `[DOGFIGHT]` lines for each change, for example:
   - `[DOGFIGHT] Wildcat (ours, 4200 m): climbing to get above Zero before attacking (50 m height advantage)`
   - `[DOGFIGHT] Wildcat (ours, 4700 m): diving on Zero from 450 m above`
   - `[DOGFIGHT] Zero (enemy, 3900 m): about to overshoot Wildcat, high yo-yo`
   - `[DOGFIGHT] Wildcat (ours, 4100 m): Zero on her tail at 380 m, Thach Weave, turning towards Wildcat who turns in on the attacker`

## Tuning (top of ModDogfight)
- `USHeightAdvantage` 500 m, `BomberHeightAdvantage` 400 m, `SetupOffset` 800 m: where fighters set up before a pass.
- `ZoomHeight` 500 m, `YoYoHeight` 150 m, `SplitSDrop` 400 m.
- `USPassTime` 8 s and `BomberPassTime` 6 s: the longest gun run before breaking off.
- `ThreatRange` 600 m: how close an attacker has to be to make a fighter defend. `WingmanRange` 1,500 m.
- `USDiveSpeed` 1.2, `JapanDiveSpeed` 1.1, `HeavyControlsSpeed` 1.05, `HeavyControlsTurn` 0.55.

## Notes
- Only fighters change. Bombers fly as before (holding formation, which is what they did).
- True barrel rolls aren't possible: the game banks the model from the turn rate itself.
- Tag: `[DOGFIGHT]`. I could not compile or run this.


## v0.20.6
See fixes_v0.20.6.md: fighters pick their target again between passes, so they spread out. The code above is the v0.20.6 version.


## v0.20.7
See fixes_v0.20.7.md. The code above is the v0.20.7 version.


## v0.20.9
See fixes_v0.20.9.md. The code above is the v0.20.9 version.
