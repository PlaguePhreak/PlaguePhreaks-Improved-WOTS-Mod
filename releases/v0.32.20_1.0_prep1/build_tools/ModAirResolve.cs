using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using WorldMapStrategyKit;

public static class ModAirResolve
{
	private class Craft
	{
		public string name;

		public bool armed;

		public bool alive;

		public float value;
	}

	private class Side
	{
		public List<Craft> craft = new List<Craft>();

		public bool player;

		public Dictionary<string, int> counts = new Dictionary<string, int>();

		public float points;

		public float mult;

		public int attacked;

		public int defended;

		public int shotDown;

		public float score;

		public int lost;

		public List<Group> groups = new List<Group>();

		public int unknown;

		public int Armed()
		{
			int num = 0;
			for (int i = 0; i < craft.Count; i++)
			{
				if (craft[i].armed)
				{
					num++;
				}
			}
			return num;
		}

		public int Count()
		{
			return craft.Count;
		}
	}

	private class Group
	{
		public MobileMapObject mmo;

		public List<Craft> craft = new List<Craft>();

		public bool known;
	}

	public const bool On = true;

	public static bool windowOpen;

	public static string resultText;

	public static float chance;

	public static bool noFight;

	public static float expectedLossPlayer;

	public static float expectedLossEnemy;

	private static Side player;

	private static Side enemy;

	private static GameObject host;

	public const float PointDivisor = 6f;

	public const float GunnerWeight = 3f;

	public const int Rehearsals = 1000;

	public const float WinnerLossMin = 0.5f;

	public const float WinnerLossMax = 0.75f;

	public const float ShotDownShare = 1f;

	public static string rollText;

	public const float JoinRange = 50000f;

	public const int ShotDownMin = 1;

	public static bool CanResolve(MobileMapObject a, MobileMapObject b)
	{
		try
		{
			if (a == null || b == null || a.type != 1 || b.type != 1 || a.unitPrefabs == null || b.unitPrefabs == null || a.unitPrefabs.Count == 0 || b.unitPrefabs.Count == 0)
			{
				return false;
			}
			UnitData value;
			UnitData value2;
			return EngagementManager.instance.unitDataDictionary.TryGetValue(a.unitPrefabs[0], out value) && EngagementManager.instance.unitDataDictionary.TryGetValue(b.unitPrefabs[0], out value2) && value.unitType == UnitType.Air && value2.unitType == UnitType.Air;
		}
		catch (Exception ex)
		{
			Debug.LogError("[AUTORESOLVE] check failed: " + ex.Message);
			return false;
		}
	}

	public static bool Open()
	{
		try
		{
			CampaignData campaignData = CampaignManager.instance.campaignData;
			if (campaignData.playerObjectEngaged < 0 || campaignData.otherObjectEngaged < 0)
			{
				return false;
			}
			GameObjectAnimator gameObjectAnimator = CampaignManager.instance.playerMobile[campaignData.playerObjectEngaged];
			GameObjectAnimator gameObjectAnimator2 = CampaignManager.instance.otherMobile[campaignData.otherObjectEngaged];
			if (!CanResolve(gameObjectAnimator.mobileMapObject, gameObjectAnimator2.mobileMapObject))
			{
				return false;
			}
			player = Build(gameObjectAnimator, gameObjectAnimator, CampaignManager.instance.playerMobile, isPlayer: true);
			enemy = Build(gameObjectAnimator2, gameObjectAnimator, CampaignManager.instance.otherMobile, isPlayer: false);
			resultText = null;
			rollText = null;
			Estimate();
			windowOpen = true;
			Ensure();
			Debug.Log("[AUTORESOLVE] window opened: ours " + Describe(player) + " (" + player.points.ToString("F0") + " points, " + player.mult.ToString("F3") + "x) against " + Describe(enemy) + " (" + enemy.points.ToString("F0") + " points, " + enemy.mult.ToString("F3") + "x)" + (noFight ? ", nobody is armed: the groups just pass" : (", chance of victory " + chance.ToString("F0") + "%, expected losses about " + expectedLossPlayer.ToString("F1") + " of ours, " + expectedLossEnemy.ToString("F1") + " of theirs")));
			return true;
		}
		catch (Exception ex)
		{
			Debug.LogError("[AUTORESOLVE] could not open: " + ex.Message + " " + ex.StackTrace);
			windowOpen = false;
			return false;
		}
	}

	public static void Close()
	{
		windowOpen = false;
	}

	private static void Ensure()
	{
		if (host == null)
		{
			host = new GameObject("ModAirResolveWindow");
			UnityEngine.Object.DontDestroyOnLoad(host);
			host.AddComponent<ModAirResolveWindow>();
		}
	}

	private static Craft MakeCraft(string prefab)
	{
		Craft craft = new Craft();
		string key = prefab.ToLowerInvariant();
		EngagementManager.instance.unitDataDictionary.TryGetValue(prefab, out var value);
		craft.name = ((value != null && !string.IsNullOrEmpty(value.unitName)) ? value.unitName : prefab);
		bool flag = value != null && value.unitSubtype == UnitSubType.Fighter;
		float[] array = ModAirStats.RowFor(key);
		float num = ((array != null && array[0] > 0f) ? array[0] : 25f);
		float num2 = ((array != null && array[1] > 0f) ? array[1] : (flag ? 10f : 0f));
		float num3 = Mathf.Clamp((array != null && array[2] >= 0f) ? array[2] : 0.1f, 0f, 0.6f);
		float num4 = ((array != null && array[3] > 0f) ? array[3] : ((array == null && !flag) ? 1f : 0f));
		craft.value = num2 + num * num3 + num4 * 3f;
		craft.armed = num2 > 0f || num4 > 0f;
		craft.alive = true;
		return craft;
	}

	private static string Describe(Side s)
	{
		string text = "";
		foreach (KeyValuePair<string, int> count in s.counts)
		{
			text = text + ((text.Length > 0) ? ", " : "") + count.Value + " x " + count.Key;
		}
		if (s.unknown > 0)
		{
			text = text + ((text.Length > 0) ? " + " : "") + s.unknown + " unknown aircraft";
		}
		return text + ((s.groups.Count > 1) ? (" (" + s.groups.Count + " groups)") : "");
	}

	public static string DescribeSide(bool playerSide)
	{
		Side side = (playerSide ? player : enemy);
		if (side == null)
		{
			return "";
		}
		string text = "";
		foreach (KeyValuePair<string, int> count in side.counts)
		{
			text = text + count.Value + " x " + count.Key + "\n";
		}
		if (side.unknown > 0)
		{
			text = text + "+ " + side.unknown + " unknown aircraft\n";
		}
		if (side.groups.Count > 1)
		{
			text = text + "(" + side.groups.Count + " groups, " + side.Count() + " aircraft)\n";
		}
		return text;
	}

	private static void Estimate()
	{
		noFight = player.Armed() == 0 && enemy.Armed() == 0;
		if (noFight)
		{
			chance = 50f;
			expectedLossPlayer = 0f;
			expectedLossEnemy = 0f;
			return;
		}
		int num = 0;
		float num2 = 0f;
		float num3 = 0f;
		for (int i = 0; i < 1000; i++)
		{
			Roll(player, enemy);
			if (Judge(player, enemy))
			{
				num++;
			}
			num2 += (float)player.lost;
			num3 += (float)enemy.lost;
		}
		chance = 100f * (float)num / 1000f;
		expectedLossPlayer = num2 / 1000f;
		expectedLossEnemy = num3 / 1000f;
		player.lost = 0;
		enemy.lost = 0;
	}

	public static string Band()
	{
		if (noFight)
		{
			return "No fight: nobody is armed";
		}
		if (chance >= 80f)
		{
			return "Very likely";
		}
		if (chance >= 60f)
		{
			return "Likely";
		}
		if (chance >= 40f)
		{
			return "Even";
		}
		if (chance >= 20f)
		{
			return "Unlikely";
		}
		return "Very unlikely";
	}

	public static void Resolve()
	{
		try
		{
			if (player == null || enemy == null)
			{
				Close();
				return;
			}
			bool flag = true;
			if (noFight)
			{
				player.lost = 0;
				enemy.lost = 0;
				rollText = null;
				resultText = "The groups passed each other. Nobody was hurt.";
			}
			else
			{
				Roll(player, enemy);
				flag = Judge(player, enemy);
				rollText = "Attacked!   " + player.attacked + "/6  --  " + enemy.attacked + "/6\nDefended   " + player.defended + "/6  --  " + enemy.defended + "/6\nShot down  " + player.shotDown + "/" + enemy.Count() + "  --  " + enemy.shotDown + "/" + player.Count() + "\nScore  " + player.score.ToString("F1") + " (" + (player.attacked + player.defended + player.shotDown) + " x " + player.mult.ToString("F3") + ")  --  " + enemy.score.ToString("F1") + " (" + (enemy.attacked + enemy.defended + enemy.shotDown) + " x " + enemy.mult.ToString("F3") + ")";
				KillPlanes(player, player.lost);
				KillPlanes(enemy, enemy.lost);
				string text = LostText(player);
				string text2 = LostText(enemy);
				resultText = (flag ? "VICTORY. " : "DEFEAT. ") + "You lost " + ((text.Length > 0) ? text : "nothing") + "; the enemy lost " + ((text2.Length > 0) ? text2 : "nothing") + ".";
			}
			List<GameObjectAnimator> list = new List<GameObjectAnimator>();
			if (!noFight)
			{
				string text3 = Beaten(player, !flag, list);
				string text4 = Beaten(enemy, flag, list);
				if (text3.Length > 0)
				{
					resultText = resultText + " Your " + text3 + " broke off the attack and turned for home.";
				}
				if (text4.Length > 0)
				{
					resultText = resultText + " The enemy's " + text4 + " broke off the attack and turned for home.";
				}
			}
			Debug.Log("[AUTORESOLVE] resolved (chance was " + chance.ToString("F0") + "%): " + ((rollText != null) ? (rollText.Replace("\n", " | ") + " | ") : "") + resultText);
			for (int i = 0; i < player.groups.Count; i++)
			{
				Finish(player.groups[i]);
			}
			for (int j = 0; j < enemy.groups.Count; j++)
			{
				Finish(enemy.groups[j]);
			}
			SendHome(list);
			if (EngagementPanel.instance != null)
			{
				EngagementPanel.instance.ClearEncounterData();
				EngagementPanel.instance.gameObject.SetActive(value: false);
			}
		}
		catch (Exception ex)
		{
			Debug.LogError("[AUTORESOLVE] resolve failed: " + ex.Message + " " + ex.StackTrace);
			resultText = "Auto resolve failed (see the log). Nothing was changed.";
		}
		player = null;
		enemy = null;
	}

	private static string LostText(Side s)
	{
		Dictionary<string, int> dictionary = new Dictionary<string, int>();
		for (int i = 0; i < s.craft.Count; i++)
		{
			if (!s.craft[i].alive)
			{
				dictionary.TryGetValue(s.craft[i].name, out var value);
				dictionary[s.craft[i].name] = value + 1;
			}
		}
		string text = "";
		foreach (KeyValuePair<string, int> item in dictionary)
		{
			text = text + ((text.Length > 0) ? ", " : "") + item.Value + " " + item.Key;
		}
		return text;
	}

	public static string PointsLine(bool playerSide)
	{
		Side side = (playerSide ? player : enemy);
		if (side == null)
		{
			return "";
		}
		return side.points.ToString("F0") + " points\n" + side.mult.ToString("F3") + "x";
	}

	private static int RollShotDown(Side me, Side them)
	{
		int num = Mathf.Min(them.Count(), Mathf.RoundToInt((float)me.Count() * 1f));
		float num2 = Mathf.Clamp(me.points / Mathf.Max(1f, them.points), 0.5f, 2f);
		float num3 = Mathf.Pow(UnityEngine.Random.value, 1f / num2);
		return Mathf.Clamp(Mathf.Max(1, Mathf.RoundToInt(num3 * (float)num)), 0, them.Count());
	}

	private static void Roll(Side a, Side b)
	{
		a.attacked = UnityEngine.Random.Range(1, 7);
		b.attacked = UnityEngine.Random.Range(1, 7);
		a.defended = UnityEngine.Random.Range(1, 7);
		b.defended = UnityEngine.Random.Range(1, 7);
		a.shotDown = ((a.Armed() > 0) ? RollShotDown(a, b) : 0);
		b.shotDown = ((b.Armed() > 0) ? RollShotDown(b, a) : 0);
		a.score = (float)(a.attacked + a.defended + a.shotDown) * a.mult;
		b.score = (float)(b.attacked + b.defended + b.shotDown) * b.mult;
	}

	private static bool Judge(Side p, Side e)
	{
		bool flag = (e.shotDown < p.Count() || p.shotDown >= e.Count()) && ((p.shotDown >= e.Count() && e.shotDown < p.Count()) || ((!(Mathf.Abs(p.score - e.score) < 0.001f)) ? (p.score > e.score) : (UnityEngine.Random.value < 0.5f)));
		Side side = (flag ? p : e);
		Side side2 = (flag ? e : p);
		side2.lost = Mathf.Clamp(side.shotDown, 0, side2.Count());
		float num = UnityEngine.Random.Range(0.5f, 0.75f);
		side.lost = Mathf.Clamp(Mathf.Max((side2.shotDown > 0) ? 1 : 0, Mathf.RoundToInt((float)side2.shotDown * num)), 0, side.Count());
		return flag;
	}

	private static void KillPlanes(Side s, int n)
	{
		List<int> list = new List<int>();
		for (int i = 0; i < s.craft.Count; i++)
		{
			s.craft[i].alive = true;
			list.Add(i);
		}
		for (int j = 0; j < n; j++)
		{
			if (list.Count <= 0)
			{
				break;
			}
			int index = UnityEngine.Random.Range(0, list.Count);
			s.craft[list[index]].alive = false;
			list.RemoveAt(index);
		}
	}

	private static Side Build(GameObjectAnimator engaged, GameObjectAnimator centre, List<GameObjectAnimator> all, bool isPlayer)
	{
		Side side = new Side();
		side.player = isPlayer;
		AddGroup(side, engaged, known: true);
		List<GameObjectAnimator> list = new List<GameObjectAnimator>();
		List<float> list2 = new List<float>();
		for (int i = 0; i < all.Count; i++)
		{
			GameObjectAnimator gameObjectAnimator = all[i];
			if (gameObjectAnimator == null || gameObjectAnimator == engaged || gameObjectAnimator.mobileMapObject == null || gameObjectAnimator.mobileMapObject.type != 1 || gameObjectAnimator.mobileMapObject.unitPrefabs == null || gameObjectAnimator.mobileMapObject.unitPrefabs.Count == 0 || !IsAir(gameObjectAnimator.mobileMapObject))
			{
				continue;
			}
			float distanceInMetresBetweenMapObjects = CampaignManager.instance.GetDistanceInMetresBetweenMapObjects(centre.currentMap2DLocation, gameObjectAnimator.currentMap2DLocation);
			if (!(distanceInMetresBetweenMapObjects >= 50000f))
			{
				int j;
				for (j = 0; j < list2.Count && list2[j] <= distanceInMetresBetweenMapObjects; j++)
				{
				}
				list.Insert(j, gameObjectAnimator);
				list2.Insert(j, distanceInMetresBetweenMapObjects);
			}
		}
		int num = ((Config.instance != null && Config.instance.maxAirPerSide > 0) ? Config.instance.maxAirPerSide : 9999);
		for (int k = 0; k < list.Count; k++)
		{
			MobileMapObject mobileMapObject = list[k].mobileMapObject;
			if (side.Count() + mobileMapObject.unitPrefabs.Count > num)
			{
				Debug.Log("[AUTORESOLVE] " + (isPlayer ? "our" : "enemy") + " air group of " + mobileMapObject.unitPrefabs.Count + " at " + (list2[k] / 1000f).ToString("F0") + " km left out: air limit " + num + " per side");
			}
			else
			{
				AddGroup(side, list[k], isPlayer || mobileMapObject.spottedTimer > 0f);
				Debug.Log("[AUTORESOLVE] " + (isPlayer ? "our" : "enemy") + " air group of " + mobileMapObject.unitPrefabs.Count + " at " + (list2[k] / 1000f).ToString("F0") + " km joins the fight" + ((isPlayer || mobileMapObject.spottedTimer > 0f) ? "" : " as unknown aircraft"));
			}
		}
		float num2 = 0f;
		for (int l = 0; l < side.craft.Count; l++)
		{
			num2 += side.craft[l].value;
		}
		side.points = num2 / 6f;
		side.mult = 1f + side.points / 1000f;
		return side;
	}

	private static void AddGroup(Side s, GameObjectAnimator goa, bool known)
	{
		Group group = new Group();
		group.mmo = goa.mobileMapObject;
		group.known = known;
		for (int i = 0; i < group.mmo.unitPrefabs.Count; i++)
		{
			Craft craft = MakeCraft(group.mmo.unitPrefabs[i]);
			group.craft.Add(craft);
			s.craft.Add(craft);
			if (known)
			{
				s.counts.TryGetValue(craft.name, out var value);
				s.counts[craft.name] = value + 1;
			}
			else
			{
				s.unknown++;
			}
		}
		s.groups.Add(group);
	}

	private static bool IsAir(MobileMapObject m)
	{
		if (EngagementManager.instance.unitDataDictionary.TryGetValue(m.unitPrefabs[0], out var value))
		{
			return value.unitType == UnitType.Air;
		}
		return false;
	}

	private static void Finish(Group g)
	{
		MobileMapObject mmo = g.mmo;
		if (!(mmo == null))
		{
			int count = mmo.unitPrefabs.Count;
			mmo.cellVariables = new List<string>();
			for (int i = 0; i < count; i++)
			{
				mmo.cellVariables.Add((i < g.craft.Count && !g.craft[i].alive) ? "DESTROYED" : string.Empty);
			}
			if (mmo.ammunitionRemaining == null)
			{
				mmo.ammunitionRemaining = new List<string>();
			}
			while (mmo.ammunitionRemaining.Count < count)
			{
				mmo.ammunitionRemaining.Add(string.Empty);
			}
			MethodInfo method = typeof(CampaignManager).GetMethod("ProcessMobileObjectPostCombat", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
			if ((object)method == null)
			{
				Debug.LogError("[AUTORESOLVE] CampaignManager.ProcessMobileObjectPostCombat not found: the losses were not applied");
				return;
			}
			method.Invoke(CampaignManager.instance, new object[1] { mmo });
		}
	}

	public const bool AbortOn = true;

	public const float AbortShareBeaten = 0.25f;

	public const float AbortShareAny = 0.5f;

	private static bool IsBomber(MobileMapObject m)
	{
		if (m == null || m.unitPrefabs == null || m.unitPrefabs.Count == 0)
		{
			return false;
		}
		if (!EngagementManager.instance.unitDataDictionary.TryGetValue(m.unitPrefabs[0], out var value))
		{
			return false;
		}
		UnitSubType unitSubtype = value.unitSubtype;
		if (unitSubtype != UnitSubType.Dive_Bomber && unitSubtype != UnitSubType.Torpedo_Bomber && unitSubtype != UnitSubType.Medium_Bomber)
		{
			return unitSubtype == UnitSubType.Heavy_Bomber;
		}
		return true;
	}

	private static string Beaten(Side s, bool lostFight, List<GameObjectAnimator> home)
	{
		string text = "";
		if (!AbortOn || s == null)
		{
			return text;
		}
		try
		{
			for (int i = 0; i < s.groups.Count; i++)
			{
				Group group = s.groups[i];
				MobileMapObject mmo = group.mmo;
				if (mmo == null || mmo.gameObjectAnimator == null || mmo.currentCampaignAction == 1 || !IsBomber(mmo) || group.craft.Count == 0)
				{
					continue;
				}
				int num = 0;
				for (int j = 0; j < group.craft.Count; j++)
				{
					if (!group.craft[j].alive)
					{
						num++;
					}
				}
				int num2 = group.craft.Count - num;
				float num3 = (float)num / (float)group.craft.Count;
				if (num2 > 0 && num > 0 && ((lostFight && num3 >= 0.25f) || num3 >= 0.5f))
				{
					home.Add(mmo.gameObjectAnimator);
					string text2 = num2 + " " + group.craft[0].name;
					if (!group.known)
					{
						text2 = num2 + " unknown aircraft";
					}
					text = text + ((text.Length > 0) ? ", " : "") + text2;
					Debug.Log("[AUTORESOLVE] strike abort: " + (s.player ? "our" : "enemy") + " " + group.craft[0].name + " group lost " + num + " of " + group.craft.Count + (lostFight ? " and lost the fight" : "") + ", the " + num2 + " left head home");
				}
			}
		}
		catch (Exception ex)
		{
			Debug.LogError("[AUTORESOLVE] strike abort check failed: " + ex.Message);
		}
		return text;
	}

	private static void SendHome(List<GameObjectAnimator> home)
	{
		for (int i = 0; i < home.Count; i++)
		{
			try
			{
				GameObjectAnimator gameObjectAnimator = home[i];
				if (!(gameObjectAnimator == null) && !(gameObjectAnimator.mobileMapObject == null) && (CampaignManager.instance.playerMobile.Contains(gameObjectAnimator) || CampaignManager.instance.otherMobile.Contains(gameObjectAnimator)))
				{
					gameObjectAnimator.mobileMapObject.escortingThisGOA = null;
					CampaignManager.instance.AirReturnToBase(gameObjectAnimator);
				}
			}
			catch (Exception ex)
			{
				Debug.LogError("[AUTORESOLVE] strike abort: sending a group home failed: " + ex.Message);
			}
		}
	}
}
