using System;
using System.Collections.Generic;
using UnityEngine;

// 1.0 prep (S3): a merchant or oiler never leads a task force in battle while a warship is left.
// Stock merchants and oilers retreat when the enemy is sighted (EngagementAI.RetreatAllMerchants), and a leader takes its
// whole formation with it. Hooks: EngagementAI.RetreatAllMerchants calls BeforeRetreat(otherSea) first;
// EngagementAI.SwitchToNewLeader picks the new leader with Pick(list) instead of list[0].
public static class ModMerchantLead
{
	public const bool On = true;

	public static bool IsCargo(Unit u)
	{
		if (u != null && u.unitData != null)
		{
			if (u.unitData.unitSubtype != UnitSubType.Merchant)
			{
				return u.unitData.unitSubtype == UnitSubType.Oiler;
			}
			return true;
		}
		return false;
	}

	public static Unit Pick(List<Unit> list)
	{
		Unit unit = list[0];
		if (!On)
		{
			return unit;
		}
		try
		{
			if (!IsCargo(unit))
			{
				return unit;
			}
			for (int i = 1; i < list.Count; i++)
			{
				if (list[i] != null && !list[i].isDestroyed && list[i].unitSea != null && !IsCargo(list[i]))
				{
					Debug.Log("[MERCHANTLEAD] new leader is " + list[i].name + ", not the merchant " + unit.name);
					return list[i];
				}
			}
		}
		catch (Exception ex)
		{
			Debug.LogError("[MERCHANTLEAD] pick failed: " + ex.Message);
		}
		return unit;
	}

	public static void BeforeRetreat(List<Unit> sea)
	{
		if (!On || sea == null)
		{
			return;
		}
		try
		{
			for (int i = 0; i < sea.Count; i++)
			{
				Unit unit = sea[i];
				if (!IsCargo(unit) || unit.isDestroyed || unit.unitAI == null || unit.unitAI.followingUnit != null)
				{
					continue;
				}
				List<Unit> list = new List<Unit>();
				Unit unit2 = null;
				for (int j = 0; j < sea.Count; j++)
				{
					Unit unit3 = sea[j];
					if (unit3 != null && unit3 != unit && !unit3.isDestroyed && unit3.unitAI != null && unit3.unitAI.followingUnit == unit)
					{
						list.Add(unit3);
						if (unit2 == null && !IsCargo(unit3))
						{
							unit2 = unit3;
						}
					}
				}
				if (unit2 == null)
				{
					continue;
				}
				for (int k = 0; k < list.Count; k++)
				{
					if (list[k] != unit2)
					{
						list[k].unitAI.followingUnit = unit2;
					}
				}
				unit2.unitAI.followingUnit = null;
				ModLeaderFix.NewLeader(unit2);
				if (unit2.unitAI.currentAIAction == AIAction.Follow_Unit)
				{
					unit2.unitAI.currentAIAction = AIAction.Nothing;
				}
				if (unit2.unitAI.previousAIAction == AIAction.Follow_Unit)
				{
					unit2.unitAI.previousAIAction = AIAction.Nothing;
				}
				Debug.Log("[MERCHANTLEAD] " + unit2.name + " takes the lead from " + unit.name + " before the merchants turn away (" + list.Count + " ships followed it)");
			}
		}
		catch (Exception ex)
		{
			Debug.LogError("[MERCHANTLEAD] hand-over failed: " + ex.Message);
		}
	}
}
