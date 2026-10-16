# v0.20.9 fixes: aimed gun runs, formations keep combing torpedoes

## What the test showed (14 Oct)
- **Wildcats still couldn't shoot.** 15 Wildcats were lost for 2 Zeros (and you're right that the earlier Zero losses were mostly to ships' AA). The reason is how this game flies planes:
  - A plane's nose only tilts up or down by the height difference it is chasing (`UnitAir.ApplyFlightControls`): wanting to be 10 game units lower gives 10 degrees nose down, up to the plane's dive angle (Wildcat 23.5 degrees, plus 4 when its guns are lined up).
  - The game's gun run (`UnitAIAir.DogfightApproach`) only fires when the target is within 5 degrees of the nose (`IsInFiringCone`), and holds the target's height.
  - So a diving Wildcat never had the Zero in front of its nose and never fired. It reached the Zero's height, the run timed out, and it climbed again. The Zeros fought level, where the game's aim works, so they got their shots.
- **Spreading worked** (no more than 4 on a plane, `[FIGHTRULE]`), but it wrote 1,861 log lines.
- **Ships turned into torpedoes.** When Enterprise switched from combing the planes to combing the actual torpedo tracks, her formation (Portland, Atlanta, the destroyers) read that as "leader finished evading" and went back to station, across the tracks.

## What changes
**ModDogfight: our own gun run (both sides)**
- The fighter aims at where the target will be when the bullets arrive (lead), and points its nose **up or down** at it as well as left and right, by setting the height it chases to exactly the pitch it needs.
- While lining up a shot (target within 20 degrees of the nose) it may dive at up to 45 degrees.
- It fires when the aim point is within 5 degrees of the nose and in gun range (300-500 m), the same rule as the game. Guns stop between runs.
- **A pass ends when the fighter has flown past its target**, not after a fixed time: once it has come within 600 m and the range is opening again by 150 m. Before, a US pass ended after 8 s, which was before a diving Wildcat even reached gun range, so it levelled out at the Zero's height, gave up and climbed away (your "dive down, reach their height, break off and go back up"). A run that never gets close gives up after 30 s.
- The boom and zoom, turn fighting, yo-yo, Thach Weave and so on stay the same; they now end in a gun run that can actually hit.

**ModFighterRules**
- The "already has 4 attackers" line is only written when a fighter's choice changes.

**ModAAEvade**
- Formation ships also turn together while the leader is combing torpedo tracks.
- When the leader is done, they keep their evasive heading for the rest of the hold time (15-40 s, the torpedoes may still be running) before going back to station.

## Install
1. Right-click class **ModDogfight** > **Edit Class (C#)**, select everything (Ctrl+A), paste the new `ModDogfight.cs` below over it, **Compile**, then **File > Save Module**.
2. Same for class **ModFighterRules** with the new `ModFighterRules.cs`.
3. Same for class **ModAAEvade** with the new `ModAAEvade.cs`.
Nothing else changes.

## Testing
1. Wildcats against Zeros: Wildcats diving on a Zero should now open fire during the dive (watch for tracers), and Zeros should start going down to fighters, not only to AA.
2. Torpedo attack on a formation: when the leader turns to comb torpedo tracks, the ships around her should turn with her and not swing back into the tracks.

## ModDogfight.cs
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

## ModFighterRules.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

// v0.20.8 / v0.20.9: fighter rules.
// 1. Fighters fight enemy aircraft before ships. A fighter sent to strafe a ship goes for enemy planes instead while
//    there are any it can see within 20 km. Your own fighters still strafe when you order the selected one to.
// 2. No more than 4 fighters on one enemy plane (a division). If the best target already has 4 attackers, the fighter
//    takes the nearest other enemy plane that has fewer.
public class ModFighterRules
{
	// distances in battle code are metres x 0.1
	public const float AirSearchRange = 20000f * 0.1f;
	public const int MaxPerTarget = 4;
	public const float StrafeCheckSeconds = 5f;

	public static Dictionary<int, float> nextStrafeCheck = new Dictionary<int, float>();
	// v0.20.9: only log a spread decision when it changes (it was 1,861 lines in one battle)
	public static Dictionary<int, int> lastSpreadLog = new Dictionary<int, int>();

	public static bool IsFighter(Unit u)
	{
		return u != null && u.unitData != null && u.unitData.unitSubtype == UnitSubType.Fighter && u.unitAir != null;
	}

	public static List<Unit> Enemies(Unit u)
	{
		if (EngagementAI.instance == null)
		{
			return null;
		}
		return (u.faction == Faction.Player) ? EngagementAI.instance.otherAir : EngagementAI.instance.playerAir;
	}

	public static List<Unit> Friends(Unit u)
	{
		if (EngagementAI.instance == null)
		{
			return null;
		}
		return (u.faction == Faction.Player) ? EngagementAI.instance.playerAir : EngagementAI.instance.otherAir;
	}

	public static bool ValidAir(Unit e)
	{
		return e != null && !e.isDestroyed && !e.isParked && e.unitAir != null && !e.unitAir.shootDown && e.unitData != null;
	}

	// First line of EngagementAI.AttackUnit: a fighter given a ship as its target goes for enemy aircraft instead
	public static void PreferAir(Unit attacker)
	{
		try
		{
			if (!ModFighterRules.IsFighter(attacker) || attacker.unitAI == null)
			{
				return;
			}
			Unit target = attacker.unitAI.focusedUnit;
			if (target == null || target.unitSea == null)
			{
				return;
			}
			// your own orders win: the fighter you have selected and are commanding is left alone
			if (attacker.faction == Faction.Player && CombatInterface.instance != null && CombatInterface.instance.currentUnit == attacker)
			{
				return;
			}
			Unit air = ModFighterRules.FindAir(attacker);
			if (air != null)
			{
				attacker.unitAI.focusedUnit = air;
				UnityEngine.Debug.Log("[FIGHTRULE] " + attacker.unitData.unitName + " id " + attacker.GetInstanceID() + " (" + (attacker.faction == Faction.Player ? "ours" : "enemy") + ") was sent at " + target.unitInstanceName + ", enemy aircraft about: going for " + air.unitData.unitName + " id " + air.GetInstanceID() + " instead");
			}
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] prefer air failed: " + ex.Message);
		}
	}

	// First line of UnitAIAir.StrafeApproach: a fighter already strafing a ship looks up every 5 s for enemy aircraft.
	// Returns true if it has been switched to an air target (skip the strafing this tick).
	public static bool CheckStrafe(UnitAIAir ai)
	{
		try
		{
			Unit u = ai.parentUnit;
			if (!ModFighterRules.IsFighter(u) || ai.focusedUnit == null || ai.focusedUnit.unitSea == null)
			{
				return false;
			}
			if (u.faction == Faction.Player && CombatInterface.instance != null && CombatInterface.instance.currentUnit == u)
			{
				return false;
			}
			int id = u.GetInstanceID();
			float next;
			if (ModFighterRules.nextStrafeCheck.TryGetValue(id, out next) && Time.time < next)
			{
				return false;
			}
			ModFighterRules.nextStrafeCheck[id] = Time.time + ModFighterRules.StrafeCheckSeconds;
			Unit air = ModFighterRules.FindAir(u);
			if (air == null)
			{
				return false;
			}
			Unit ship = ai.focusedUnit;
			ai.focusedUnit = air;
			EngagementAI.instance.AttackUnit(u);
			UnityEngine.Debug.Log("[FIGHTRULE] " + u.unitData.unitName + " id " + id + " (" + (u.faction == Faction.Player ? "ours" : "enemy") + ") stops strafing " + ship.unitInstanceName + ": enemy aircraft about, going for " + air.unitData.unitName + " id " + air.GetInstanceID());
			return true;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] strafe check failed: " + ex.Message);
			return false;
		}
	}

	// The best enemy aircraft for this fighter within 20 km, or null if there is none it can see
	public static Unit FindAir(Unit u)
	{
		List<Unit> enemies = ModFighterRules.Enemies(u);
		if (enemies == null)
		{
			return null;
		}
		bool any = false;
		for (int i = 0; i < enemies.Count; i++)
		{
			Unit e = enemies[i];
			if (ModFighterRules.ValidAir(e) && e.detected && Vector3.Distance(e.transform.position, u.transform.position) < ModFighterRules.AirSearchRange)
			{
				any = true;
				break;
			}
		}
		if (!any)
		{
			return null;
		}
		Unit pick = EngagementAI.instance.GetBestDogfightTarget(u, enemies);
		if (!ModFighterRules.ValidAir(pick) || Vector3.Distance(pick.transform.position, u.transform.position) > ModFighterRules.AirSearchRange)
		{
			return null;
		}
		return pick;
	}

	// Last line of EngagementAI.GetBestDogfightTarget: if the chosen plane already has 4 attackers, take the nearest
	// other enemy plane with fewer
	public static Unit Spread(Unit unit, Unit best, List<Unit> units)
	{
		try
		{
			if (unit == null || best == null || units == null || !ModFighterRules.IsFighter(unit))
			{
				return best;
			}
			if (ModFighterRules.Attackers(unit, best) < ModFighterRules.MaxPerTarget)
			{
				return best;
			}
			Unit alt = null;
			float altDist = float.MaxValue;
			for (int i = 0; i < units.Count; i++)
			{
				Unit e = units[i];
				if (e == best || !ModFighterRules.ValidAir(e) || !e.detected)
				{
					continue;
				}
				float d = Vector3.Distance(e.transform.position, unit.transform.position);
				if (d < altDist && d < ModFighterRules.AirSearchRange && ModFighterRules.Attackers(unit, e) < ModFighterRules.MaxPerTarget)
				{
					altDist = d;
					alt = e;
				}
			}
			if (alt == null)
			{
				return best;
			}
			int uid = unit.GetInstanceID();
			int last;
			if (!ModFighterRules.lastSpreadLog.TryGetValue(uid, out last) || last != alt.GetInstanceID())
			{
				ModFighterRules.lastSpreadLog[uid] = alt.GetInstanceID();
				UnityEngine.Debug.Log("[FIGHTRULE] " + unit.unitData.unitName + " id " + uid + ": " + best.unitData.unitName + " id " + best.GetInstanceID() + " already has " + ModFighterRules.MaxPerTarget + " attackers, taking " + alt.unitData.unitName + " id " + alt.GetInstanceID() + " instead");
			}
			return alt;
		}
		catch (System.Exception ex)
		{
			UnityEngine.Debug.LogError("[FIGHTRULE] spread failed: " + ex.Message);
			return best;
		}
	}

	// How many of this fighter's side are attacking that plane (not counting this fighter)
	public static int Attackers(Unit unit, Unit target)
	{
		List<Unit> friends = ModFighterRules.Friends(unit);
		if (friends == null)
		{
			return 0;
		}
		int n = 0;
		for (int i = 0; i < friends.Count; i++)
		{
			Unit f = friends[i];
			if (f != null && f != unit && !f.isDestroyed && f.unitAI != null && f.unitAI.focusedUnit == target)
			{
				n++;
			}
		}
		return n;
	}
}
```

## ModAAEvade.cs
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

Tags: `[DOGFIGHT]`, `[FIGHTRULE]`, `[AAEVADE]`. I could not compile or run this.
