# Veteran crews

**What it does:** every player ship that survives a battle earns 1 battle of experience (tracked per ship by name, saved with the campaign).
Ranks: 0-1 battles Green (no bonus), 2-4 Trained (+4%), 5-8 Veteran (+8%), 9+ Elite (+12%).
The bonus raises combat efficiency, which speeds up gun/torpedo reloads and damage-control repairs. Damage still lowers efficiency as normal.
After a battle a popup lists promotions, e.g. "Crews have gained experience: Dale (Trained), Hull (Trained)".
Enemy ships get no bonus. Sunk ships lose their experience with them.
Old saves work (everyone starts Green).

Do the steps in order. Back up the DLL first.

## Step A - save-file fields (CampaignData)
1. Right-click class **CampaignData** > **Edit Class (C#)...**
2. Directly under the line `public List<int> sunkShipInstances;` add:
```csharp
public List<string> vetNames = new List<string>();
public List<int> vetBattles = new List<int>();
```
3. Compile, then **File > Save Module**. **Close dnSpy and reopen it, reopen the DLL** (so the new fields are seen).

## Step B - helper methods (MobileMapObject)
1. Right-click class **MobileMapObject** > **Edit Class (C#)...**
2. Add these methods anywhere inside the class (e.g. just before the last closing brace):
```csharp
public static int GetVeteranBattles(string shipName)
{
    CampaignData cd = CampaignManager.instance.campaignData;
    if (cd.vetNames == null || cd.vetBattles == null)
    {
        return 0;
    }
    int idx = cd.vetNames.IndexOf(shipName);
    if (idx == -1 || idx >= cd.vetBattles.Count)
    {
        return 0;
    }
    return cd.vetBattles[idx];
}

public static float GetVeteranBonus(string shipName)
{
    int b = MobileMapObject.GetVeteranBattles(shipName);
    if (b >= 9)
    {
        return 0.12f;
    }
    if (b >= 5)
    {
        return 0.08f;
    }
    if (b >= 2)
    {
        return 0.04f;
    }
    return 0f;
}

public static string GetVeteranRank(int b)
{
    if (b >= 9)
    {
        return "Elite";
    }
    if (b >= 5)
    {
        return "Veteran";
    }
    if (b >= 2)
    {
        return "Trained";
    }
    return "Green";
}

public static void AwardVeterancy(MobileMapObject mmo)
{
    if (mmo.currentFaction != 0 || mmo.type != 0)
    {
        return;
    }
    CampaignData cd = CampaignManager.instance.campaignData;
    if (cd.vetNames == null)
    {
        cd.vetNames = new List<string>();
    }
    if (cd.vetBattles == null)
    {
        cd.vetBattles = new List<int>();
    }
    string promoted = string.Empty;
    for (int i = 0; i < mmo.unitPrefabs.Count; i++)
    {
        if (i >= mmo.cellVariables.Count || mmo.cellVariables[i] == "DESTROYED")
        {
            continue;
        }
        string shipName = Utilities.GetShipDisplayName(mmo.unitPrefabs[i], string.Empty, mmo.unitInstances[i]);
        int idx = cd.vetNames.IndexOf(shipName);
        int before = 0;
        if (idx == -1)
        {
            cd.vetNames.Add(shipName);
            cd.vetBattles.Add(0);
            idx = cd.vetNames.Count - 1;
        }
        else
        {
            before = cd.vetBattles[idx];
        }
        cd.vetBattles[idx] = before + 1;
        string oldRank = MobileMapObject.GetVeteranRank(before);
        string newRank = MobileMapObject.GetVeteranRank(before + 1);
        if (oldRank != newRank)
        {
            if (promoted != string.Empty)
            {
                promoted = promoted + ", ";
            }
            promoted = promoted + shipName + " (" + newRank + ")";
        }
    }
    if (promoted != string.Empty)
    {
        try
        {
            ErrorPanel.instance.SetErrorMessage("CrewPromoted", promoted, string.Empty, string.Empty);
        }
        catch
        {
        }
    }
}
```
3. Compile (if it complains about something, send me a screenshot).

## Step C - award experience after battle (CampaignManager)
1. Right-click method **ProcessMobileObjectPostCombat** (CampaignManager) > **Edit Method (C#)...**
2. Find `if (mmo.cellVariables.Count > 0)` (it comes right after the `mmo.postEngagementTimer = this.campaignData.postEngageSubCooldown;` block). Insert as the **first line inside its braces**:
```csharp
MobileMapObject.AwardVeterancy(mmo);
```
So it reads:
```csharp
if (mmo.cellVariables.Count > 0)
{
    MobileMapObject.AwardVeterancy(mmo);
    if (mmo.currentFaction != 0)
    ...
```
3. Compile.

## Step D - apply the bonus in combat (Utilities.SetSeaEfficiency)
1. Right-click method **SetSeaEfficiency** (class Utilities) > **Edit Method (C#)...**, replace the whole method with:
```csharp
public static void SetSeaEfficiency(Unit unit)
{
    float vetBonus = 0f;
    if (unit.faction == Faction.Player && unit.unitInstanceName != null)
    {
        try
        {
            if (EngagementData.instance != null && EngagementData.instance.isCampaignEngagement && CampaignManager.instance != null && CampaignManager.instance.campaignData != null)
            {
                vetBonus = MobileMapObject.GetVeteranBonus(unit.unitInstanceName);
            }
        }
        catch
        {
        }
    }
    float num = 1f * Utilities.GetDifficultyModifier(Difficulty.Efficiency, unit.faction) + vetBonus;
    num -= (float)(unit.damageableSea.cellsOffline.Count + unit.damageableSea.cellsBurning.Count + unit.damageableSea.cellsFlooded.Count) * Config.instance.effLossPerOffBurnFlood;
    if (Utilities.IsCommandOffline(unit))
    {
        num -= Config.instance.effLossNoCommand;
    }
    num = Mathf.Clamp(num, Config.instance.minEfficiency, 1f + vetBonus);
    unit.efficiency = num;
    unit.twoMinusEfficiency = 2f - num;
}
```
2. Compile, then **File > Save Module**.

## Message file
Replace `campaign_message.txt` (StreamingAssets/default/language/english/dictionary/) with the attached copy (adds `CrewPromoted`).

## Testing
Fight a battle with a player task force, survive, and return to the map. After 2 battles you should see the promotion popup. In the next battle, open a veteran ship's damage-control screen: its efficiency should read above 100% (e.g. 104%).
