# Balanced starting forces (v0.17.4)

**What I found in the code**
- Your starting task forces are made by `CampaignAI.CreateStandingMissions`, which only runs when a new campaign starts. It already had our earlier edit that gives you two named task forces.
- The AI's starting forces are the free (`noCost`) Patrol missions at the top of each campaign's `sea_missions.txt`. The same method launches all of them at the start.
- Before this change the two sides were uneven:
  - **Solomons campaign (you are the US):** you got 2 cruiser groups. Japan got 8 submarines, 3 destroyer patrols and 2 cruiser groups, but no carrier.
  - **Japanese campaign (you are Japan):** you got a small carrier group and a cruiser group. The US got 5 submarines, 4 destroyer patrols, 2 cruiser groups and a 16-ship carrier group.

**What changes: both sides now start with the same forces**

| Group | Ships | You (US) | You (Japan) | AI |
|---|---|---|---|---|
| Carrier task force | 1 carrier, 1 battleship, 2 cruisers, 5 destroyers | Enterprise, North Carolina, Portland, Atlanta, Balch, Benham, Ellet, Maury, Grayson | Shokaku, Hiei, Tone, Chikuma, Akigumo, Hatsukaze, Yukikaze, Amatsukaze, Maikaze | Same make-up, ships picked by the game |
| Cruiser task force | 1 heavy cruiser, 1 light cruiser, 3 destroyers | San Francisco, Helena, Buchanan, Aaron Ward, Cushing | Chokai, Tenryu, Yudachi, Murasame, Harusame | Same make-up |
| 3 destroyer patrols | 2-4 destroyers each | Random 2-4 each, random mix from Farragut, Mahan, Sims and Benham classes | Random 2-4 each, random mix from Fubuki, Akatsuki and Asashio classes | 2, 3 and 4 destroyers |
| Submarine patrols | Single submarines near the middle of the map | Random 2-3 Gato boats | Random 2-3 Type B boats | 3 submarines |

- The ships in your task forces are the historical ones from August 1942 (the Eastern Solomons carrier groups, and the Savo / Guadalcanal cruiser forces).
- Each of your groups starts at its own station, so no two groups share a spot on the map:
  - **US:** the carriers start east of the Solomons (SPac7) and the cruisers south of Guadalcanal (Sol4). The destroyer patrols start in the Coral Sea (Coral3, Coral2, and Coral4 near New Hebrides). The submarines start in the middle of the map (Sol3, Sol6, Slot8).
  - **Japan:** the carriers start north of the Solomons (SPac1) and the cruisers south of Rabaul (Bism3). The destroyer patrols start off Bougainville and New Ireland (Sol1, SPac4, SPac6). The submarines start in the middle of the map (SPac8, Sol5, Sol2).
  - Every spot is well clear of your other groups, and even further from the enemy's, so nothing starts in a battle.
- **AI carrier and cruiser task forces don't respawn for free** if they are sunk. The AI's destroyer and submarine patrols still respawn, as in vanilla.
- The AI's destroyer and submarine patrol sizes come from the mission file, which only allows fixed numbers. That's why the AI has 2, 3 and 4 destroyers and 3 submarines, while your sizes are random.
- Each of your starting groups writes a `[STARTFLEET]` line to `output_log.txt`.

**This only takes effect in a new campaign.**

Back up the DLL and both `sea_missions.txt` files first.

## Step 1 - files
1. Extract `starting_forces.zip` over your game folder, so its `Override` folder merges with yours. It replaces:
   - `Override/campaign/campaign001/sea_missions.txt`
   - `Override/campaign/campaign002/sea_missions.txt`
2. Only the starting patrols at the top of each file changed. All the other AI missions (intercepts, invasions, convoys and so on) are the same as before.

## Step 2 - CampaignAI.CreateStandingMissions
1. Right-click **CreateStandingMissions** (class **CampaignAI**) > **Edit Method (C#)...**
2. Select the whole method, from `public void CreateStandingMissions()` down to its closing `}`, and paste this over it:
```csharp
public void CreateStandingMissions()
{
    try
    {
        CampaignData cd = CampaignManager.instance.campaignData;
        List<string[]> groupClasses = new List<string[]>();
        List<string[]> groupInstances = new List<string[]>();
        List<string> groupStart = new List<string>();
        List<string> groupEnd = new List<string>();
        List<int> groupFormation = new List<int>();
        string[] ddClassPool = null;
        string[] ddInstPool = null;
        string[] ddStart = null;
        string[] ddEnd = null;
        string[] subClassPool = null;
        string[] subInstPool = null;
        string[] subStart = null;
        string[] subEnd = null;
        if (cd.campaignID == "campaign001")
        {
            groupClasses.Add(new string[] { "yorktown", "north_carolina", "portland", "atlanta", "porter", "benham", "benham", "gridley", "gleaves" });
            groupInstances.Add(new string[] { "enterprise", "north carolina", "portland", "atlanta", "balch", "benham", "ellet", "maury", "grayson" });
            groupStart.Add("SPac7");
            groupEnd.Add("SPac7");
            groupFormation.Add(7);
            groupClasses.Add(new string[] { "new_orleans", "brooklyn", "gleaves", "gleaves", "mahan" });
            groupInstances.Add(new string[] { "san francisco", "helena", "buchanan", "aaron ward", "cushing" });
            groupStart.Add("Sol4");
            groupEnd.Add("Sol4");
            groupFormation.Add(0);
            ddClassPool = new string[] { "farragut", "farragut", "farragut", "farragut", "farragut", "mahan", "mahan", "mahan", "sims", "sims", "sims", "benham" };
            ddInstPool = new string[] { "farragut", "dewey", "hull", "monaghan", "dale", "mahan", "lamson", "flusser", "hughes", "anderson", "mustin", "lang" };
            ddStart = new string[] { "Coral3", "Coral2", "Coral4" };
            ddEnd = new string[] { "Coral3", "Coral2", "Coral4" };
            subClassPool = new string[] { "gato", "gato", "gato" };
            subInstPool = new string[] { "gato", "greenling", "grouper" };
            subStart = new string[] { "Sol3", "Sol6", "Slot8" };
            subEnd = new string[] { "Sol3", "Sol6", "Slot8" };
        }
        else if (cd.campaignID == "campaign002")
        {
            groupClasses.Add(new string[] { "shokaku", "kongo", "tone", "tone", "kagero", "kagero", "kagero", "kagero", "kagero" });
            groupInstances.Add(new string[] { "shokaku", "hiei", "tone", "chikuma", "akigumo", "hatsukaze", "yukikaze", "amatsukaze", "maikaze" });
            groupStart.Add("SPac1");
            groupEnd.Add("SPac1");
            groupFormation.Add(7);
            groupClasses.Add(new string[] { "takao", "tenryu", "shiratsuyu", "shiratsuyu", "shiratsuyu" });
            groupInstances.Add(new string[] { "chokai", "tenryu", "yudachi", "murasame", "harusame" });
            groupStart.Add("Bism3");
            groupEnd.Add("Bism3");
            groupFormation.Add(0);
            ddClassPool = new string[] { "fubuki", "fubuki", "fubuki", "fubuki", "fubuki", "fubuki", "akatsuki", "akatsuki", "akatsuki", "asashio", "asashio", "asashio" };
            ddInstPool = new string[] { "fubuki", "shirayuki", "hatsuyuki", "murakumo", "uranami", "shikinami", "akatsuki", "ikazuchi", "inazuma", "asashio", "michishio", "arashio" };
            ddStart = new string[] { "Sol1", "SPac4", "SPac6" };
            ddEnd = new string[] { "Sol1", "SPac4", "SPac6" };
            subClassPool = new string[] { "type_b1", "type_b1", "type_b1" };
            subInstPool = new string[] { "i-15", "i-17", "i-19" };
            subStart = new string[] { "SPac8", "Sol5", "Sol2" };
            subEnd = new string[] { "SPac8", "Sol5", "Sol2" };
        }
        if (ddClassPool != null)
        {
            int[] order = new int[ddClassPool.Length];
            for (int o = 0; o < order.Length; o++)
            {
                order[o] = o;
            }
            for (int o = order.Length - 1; o > 0; o--)
            {
                int swapWith = UnityEngine.Random.Range(0, o + 1);
                int keep = order[o];
                order[o] = order[swapWith];
                order[swapWith] = keep;
            }
            int nextDD = 0;
            for (int p = 0; p < ddStart.Length; p++)
            {
                int count = UnityEngine.Random.Range(2, 5);
                if (nextDD + count > order.Length)
                {
                    count = order.Length - nextDD;
                }
                if (count <= 0)
                {
                    break;
                }
                string[] patrolClasses = new string[count];
                string[] patrolInstances = new string[count];
                for (int q = 0; q < count; q++)
                {
                    patrolClasses[q] = ddClassPool[order[nextDD + q]];
                    patrolInstances[q] = ddInstPool[order[nextDD + q]];
                }
                nextDD += count;
                groupClasses.Add(patrolClasses);
                groupInstances.Add(patrolInstances);
                groupStart.Add(ddStart[p]);
                groupEnd.Add(ddEnd[p]);
                groupFormation.Add(0);
            }
            int subCount = UnityEngine.Random.Range(2, 4);
            for (int s = 0; s < subCount && s < subClassPool.Length; s++)
            {
                groupClasses.Add(new string[] { subClassPool[s] });
                groupInstances.Add(new string[] { subInstPool[s] });
                groupStart.Add(subStart[s]);
                groupEnd.Add(subEnd[s]);
                groupFormation.Add(0);
            }
        }
        MobileMapObject newTF = CampaignInterface.instance.newTaskForce;
        for (int g = 0; g < groupClasses.Count; g++)
        {
            if (!CampaignManager.instance.seaNavigationIndexes.ContainsKey(groupStart[g]) || !CampaignManager.instance.seaNavigationIndexes.ContainsKey(groupEnd[g]))
            {
                UnityEngine.Debug.LogError("[STARTFLEET] missing waypoint " + groupStart[g] + " or " + groupEnd[g]);
                continue;
            }
            Vector3 startPos = CampaignManager.instance.seaNavigationPoints[CampaignManager.instance.seaNavigationIndexes[groupStart[g]]].positionRadius;
            Vector3 endPos = CampaignManager.instance.seaNavigationPoints[CampaignManager.instance.seaNavigationIndexes[groupEnd[g]]].positionRadius;
            Vector2 startV = new Vector2(startPos.x, startPos.y);
            Vector2 endV = new Vector2(endPos.x, endPos.y);
            CampaignInterface.instance.ClearNewGroupData(newTF);
            string shipLog = string.Empty;
            for (int k = 0; k < groupClasses[g].Length; k++)
            {
                string shipClass = groupClasses[g][k];
                if (!EngagementManager.instance.unitDataDictionary.ContainsKey(shipClass))
                {
                    UnityEngine.Debug.LogError("[STARTFLEET] unknown class " + shipClass);
                    continue;
                }
                UnitData shipData = EngagementManager.instance.unitDataDictionary[shipClass];
                int shipInstance = shipData.instancesInClass.IndexOf(groupInstances[g][k]);
                if (shipInstance == -1)
                {
                    UnityEngine.Debug.LogError("[STARTFLEET] unknown ship " + groupInstances[g][k] + " in class " + shipClass);
                    continue;
                }
                if (CampaignManager.instance.GetIndexInDoubleList(shipClass, shipInstance, cd.playerOwnedShipClasses, cd.playerOwnedShipInstances) != -1)
                {
                    continue;
                }
                int unavailableIndex = CampaignManager.instance.GetIndexInDoubleList(shipClass, shipInstance, cd.unavailableShipClasses, cd.unavailableShipInstances);
                if (unavailableIndex != -1)
                {
                    bool namesInSync = cd.unavailableShipInstanceNames.Count == cd.unavailableShipClasses.Count;
                    cd.unavailableShipClasses.RemoveAt(unavailableIndex);
                    cd.unavailableShipInstances.RemoveAt(unavailableIndex);
                    if (namesInSync)
                    {
                        cd.unavailableShipInstanceNames.RemoveAt(unavailableIndex);
                    }
                }
                newTF.unitPrefabs.Add(shipClass);
                newTF.unitInstances.Add(shipInstance);
                newTF.cellVariables.Add(string.Empty);
                newTF.ammunitionRemaining.Add(string.Empty);
                newTF.aircraftCooldown.Add(string.Empty);
                newTF.cargo.Add("0|0|0|0");
                newTF.bombardments.Add(0);
                newTF.paint.Add(0);
                newTF.speedModifier.Add(1f);
                if (shipData.aircraftTotal.Count > 0)
                {
                    newTF.currentAircraft.Add(CampaignManager.instance.SetIntListToString(shipData.aircraftTotal));
                }
                else
                {
                    newTF.currentAircraft.Add(string.Empty);
                }
                if (shipData.namesInClass.Count > 0)
                {
                    newTF.unitDisplayNames.Add(shipData.namesInClass[shipInstance]);
                }
                else
                {
                    newTF.unitDisplayNames.Add(shipData.unitName);
                }
                CampaignManager.instance.ModifyShipInLists(true, shipClass, shipInstance, 0, cd.playerOwnedShipClasses, cd.playerOwnedShipInstances, cd.playerOwnedRepairDays);
                shipLog = shipLog + " " + groupInstances[g][k];
            }
            if (newTF.unitPrefabs.Count > 0)
            {
                newTF.currentFaction = 0;
                newTF.type = 0;
                newTF.formation = groupFormation[g];
                newTF.formationSpacing = 0;
                newTF.speed = CampaignManager.instance.GetMobileMapObjectSpeed(newTF);
                GameObjectAnimator newMobile = CampaignInterface.instance.CreateNewMobileObject(CampaignObjectType.Sea, newTF, startV, false, null, string.Empty);
                if (groupStart[g] != groupEnd[g])
                {
                    CampaignInterface.instance.MoveMobileToDestination(newMobile, endV, true, false);
                }
                UnityEngine.Debug.Log("[STARTFLEET] " + groupStart[g] + " -> " + groupEnd[g] + ":" + shipLog);
            }
            CampaignInterface.instance.ClearNewGroupData(newTF);
        }
    }
    catch (System.Exception ex)
    {
        UnityEngine.Debug.LogError("Starting fleet failed: " + ex.ToString());
    }
    for (int i = 0; i < this.seaMissions.Count; i++)
    {
        if (this.seaMissions[i].missionType == MissionType.Patrol && this.seaMissions[i].noCost)
        {
            this.CreateAIMobileSea(this.seaMissions[i].missionIndex, string.Empty, true);
        }
    }
}
```
3. **Compile**, then **File > Save Module**.

## Testing
1. Start a **new** campaign on each side.
2. **Your forces:** you should see 7 or 8 separate icons: a 9-ship carrier group, a 5-ship cruiser group, 3 destroyer groups of 2-4 ships, and 2 or 3 single submarines, each at its own spot and none on top of another.
3. **AI forces:** press F9 to turn off fog of war, and check the AI has the same: a carrier group, a cruiser group, destroyer groups of 2, 3 and 4 ships, and 3 submarines.
4. In `output_log.txt`, check that:
   - there is one `[STARTFLEET]` line for each of your groups, listing its ships.
   - there are no `[STARTFLEET]` error lines and no "Starting fleet failed" line. If there are, send me the log.

## Tuning
- **Your ships:** change the names in the lists at the top of the method. Each name in the class list pairs with the name in the same position in the ship list.
- **Your destroyer patrol sizes:** `UnityEngine.Random.Range(2, 5)` gives 2 to 4. The second number is one higher than the largest size.
- **Your submarine count:** `UnityEngine.Random.Range(2, 4)` gives 2 or 3.
- **Your stations:** the waypoint names in `groupStart` / `groupEnd`, `ddStart` / `ddEnd` and `subStart` / `subEnd`.
  - When the start and end are the same, the group simply starts there.
  - When they differ, it spawns at the start and sails to the end.
- **AI groups:** edit the first 8 lines of `sea_missions.txt`. The `units` list sets the ships, and `lastWaypoint` sets where they patrol.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.
