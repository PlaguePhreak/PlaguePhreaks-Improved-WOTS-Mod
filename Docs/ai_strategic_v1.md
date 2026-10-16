# Strategic AI v1 - three small edits (all in class CampaignAI)

**What changes**
1. **More persistent pursuit:** when you have a spotted fleet worth hunting, the AI tries to intercept it on 50% of its decisions instead of 25%.
2. **Supply-line interdiction:** the AI now hunts any single spotted merchant or oiler. Before, it ignored supply ships unless there were more than two merchants together. Your fuel system needs oilers and supply ships, so these now matter.
3. **Smarter bombardment:** the AI usually (60% of the time) bombards your highest-level port or airfield instead of a random one. The other 40% stays random, so it isn't predictable.

Spending is still capped by the AI budget, so this makes the AI choose better targets rather than get unlimited forces.

Back up the DLL first. These are small edits and need no new fields or message files.

## Edit 1 - intercept chance (MakeStrategicDecision)
1. In dnSpy open class **CampaignAI**, right-click **MakeStrategicDecision** > **Edit Method (C#)...**
2. Find this block (near the top, after the `attackOtherLocations` checks):
```csharp
if (UnityEngine.Random.value < 0.25f)
{
    this.CheckInterceptSpottedPlayerSea(this.GetForceAvailable());
```
3. Change `0.25f` to `0.5f`. Compile.

## Edit 2 - hunt single supply ships (CheckInterceptSpottedPlayerSea)
1. Right-click **CheckInterceptSpottedPlayerSea** > **Edit Method (C#)...**
2. Find the `else if` that mentions `UnitSubType.Oiler` and `UnitSubType.Merchant`. It ends with `.Count > 2)`:
```csharp
... UnitSubType.Merchant).Count > 2)
```
3. Change `> 2` to `> 0`. (Only that one number, on the Merchant part.) Compile.

## Edit 3 - pick the best bombardment target (CheckBombardLocation)
1. Right-click **CheckBombardLocation** > **Edit Method (C#)...** and replace the whole method with:
```csharp
private void CheckBombardLocation(int forceAvailable)
{
    List<MapLocation> bombardTargets = this.GetBombardTargets(string.Empty);
    if (bombardTargets.Count != 0)
    {
        MapLocation chosenTarget = bombardTargets[UnityEngine.Random.Range(0, bombardTargets.Count)];
        if (UnityEngine.Random.value < 0.6f)
        {
            for (int t = 0; t < bombardTargets.Count; t++)
            {
                if (bombardTargets[t].portLevel + bombardTargets[t].airfieldLevel > chosenTarget.portLevel + chosenTarget.airfieldLevel)
                {
                    chosenTarget = bombardTargets[t];
                }
            }
        }
        this.CreateAIMobileSea(this.GetMissionByType(MissionType.Bombard), chosenTarget.locationID, false);
    }
}
```
2. Compile, then **File > Save Module**.

## Tuning later
- Intercept chance: the `0.5f` in Edit 1 (higher = more hunting).
- Smart bombardment share: the `0.6f` in Edit 3.

## How to test
Play a campaign for a few weeks of game time. Spot an enemy ship and let it spot your force: you should see enemy task forces heading for your fleets more often. Park an oiler or supply ship near the enemy and see whether a hunter group heads for it. If enemy aggression feels too high, set the 0.5f back toward 0.35f.
