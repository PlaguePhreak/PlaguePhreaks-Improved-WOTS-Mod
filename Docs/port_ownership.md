# Ships belong to their building port

**What it does:**
- When you order a ship, the game remembers which port you ordered it at.
- When it is delivered it waits at that port. Trying to recruit it at any other port shows: "<ship> was built at <port> and can only be recruited there."
- A ship you disband at a shipyard (a port that can build ships) becomes stationed there. Disbanding at a port that cannot build ships leaves its station unchanged, so nothing gets stuck.
- Ships you already own, and ships ordered before this update, have no station and can be recruited anywhere as before.
- Caveat: if the port a ship is stationed at is captured, that ship cannot be recruited until you retake it.

Back up the DLL first. Do the steps in order.

## Step A - save-file fields (CampaignData)
1. Right-click class **CampaignData** > **Edit Class (C#)...**
2. Under `public List<int> orderDaysRemaining = new List<int>();` (or anywhere with the other fields) add:
```csharp
public List<string> orderPortNames = new List<string>();
public List<string> homePortClasses = new List<string>();
public List<int> homePortInstances = new List<int>();
public List<string> homePortNames = new List<string>();
```
3. Compile, **File > Save Module**, then **close and reopen dnSpy** and the DLL.

## Step B - helper methods (MobileMapObject)
1. Right-click class **MobileMapObject** > **Edit Class (C#)...**
2. Add next to the veteran methods:
```csharp
public static void SetHomePort(string shipClass, int shipInstance, string portName)
{
    CampaignData cd = CampaignManager.instance.campaignData;
    if (cd.homePortClasses == null)
    {
        cd.homePortClasses = new List<string>();
    }
    if (cd.homePortInstances == null)
    {
        cd.homePortInstances = new List<int>();
    }
    if (cd.homePortNames == null)
    {
        cd.homePortNames = new List<string>();
    }
    int idx = CampaignManager.instance.GetIndexInDoubleList(shipClass, shipInstance, cd.homePortClasses, cd.homePortInstances);
    if (idx == -1)
    {
        cd.homePortClasses.Add(shipClass);
        cd.homePortInstances.Add(shipInstance);
        cd.homePortNames.Add(portName);
    }
    else
    {
        cd.homePortNames[idx] = portName;
    }
}

public static string GetHomePort(string shipClass, int shipInstance)
{
    CampaignData cd = CampaignManager.instance.campaignData;
    if (cd.homePortClasses == null || cd.homePortInstances == null || cd.homePortNames == null)
    {
        return string.Empty;
    }
    int idx = CampaignManager.instance.GetIndexInDoubleList(shipClass, shipInstance, cd.homePortClasses, cd.homePortInstances);
    if (idx == -1 || idx >= cd.homePortNames.Count)
    {
        return string.Empty;
    }
    return cd.homePortNames[idx];
}
```
3. Compile.

## Step C - AddShipToTaskForce (CampaignInterface), two insertions
Right-click **AddShipToTaskForce** > **Edit Method (C#)...**

**C1 - remember the port when ordering.** Find the line containing `orderDaysRemaining.Add(` (in the order block). Add directly after it:
```csharp
CampaignData portBook = CampaignManager.instance.campaignData;
while (portBook.orderPortNames.Count < portBook.orderShipClasses.Count - 1)
{
    portBook.orderPortNames.Add(string.Empty);
}
portBook.orderPortNames.Add((component != null) ? component.locationName : string.Empty);
```
(`component` is the variable just above, set from `this.currentMapObject.GetComponent<MapLocation>()`. If dnSpy shows it under another name, use that name.)

**C2 - block recruiting at the wrong port.** Find the line starting `int num = CampaignManager.instance.IsPlayerShipInstanceAvailable(`. Add directly after it:
```csharp
if (num == -1 && component != null)
{
    string builtAtPort = MobileMapObject.GetHomePort(UnitReference.instance.currentPrefab, UnitReference.instance.namesInClassDropdown.value);
    if (builtAtPort != string.Empty && builtAtPort != component.locationName)
    {
        ErrorPanel.instance.SetErrorMessage("WrongPort", Utilities.GetShipDisplayName(UnitReference.instance.currentPrefab, string.Empty, UnitReference.instance.namesInClassDropdown.value), builtAtPort, string.Empty);
        return;
    }
}
```
Compile.

## Step D - delivery records the port (CampaignManager.CheckDaily)
Right-click **CheckDaily** > **Edit Method (C#)...** and replace the whole method with:
```csharp
private void CheckDaily()
{
    WeatherManager.instance.UpdateWeather();
    CampaignAI.instance.MakeStrategicDecision();
    this.CheckTroopEngagements();
    this.CheckRepairedShips();
    string deliveredNames = string.Empty;
    int deliveredCount = 0;
    for (int i = this.campaignData.orderDaysRemaining.Count - 1; i > -1; i--)
    {
        this.campaignData.orderDaysRemaining[i] = this.campaignData.orderDaysRemaining[i] - 1;
        if (this.campaignData.orderDaysRemaining[i] <= 0)
        {
            string deliveredClass = this.campaignData.orderShipClasses[i];
            int deliveredInstance = this.campaignData.orderShipInstances[i];
            int unavailableIndex = this.GetIndexInDoubleList(deliveredClass, deliveredInstance, this.campaignData.unavailableShipClasses, this.campaignData.unavailableShipInstances);
            if (unavailableIndex != -1)
            {
                bool namesInSync = this.campaignData.unavailableShipInstanceNames.Count == this.campaignData.unavailableShipClasses.Count;
                this.campaignData.unavailableShipClasses.RemoveAt(unavailableIndex);
                this.campaignData.unavailableShipInstances.RemoveAt(unavailableIndex);
                if (namesInSync)
                {
                    this.campaignData.unavailableShipInstanceNames.RemoveAt(unavailableIndex);
                }
            }
            string builtAt = string.Empty;
            if (this.campaignData.orderPortNames != null && i < this.campaignData.orderPortNames.Count)
            {
                builtAt = this.campaignData.orderPortNames[i];
                this.campaignData.orderPortNames.RemoveAt(i);
            }
            if (builtAt != string.Empty)
            {
                MobileMapObject.SetHomePort(deliveredClass, deliveredInstance, builtAt);
            }
            string deliveredName = Utilities.GetShipDisplayName(deliveredClass, string.Empty, deliveredInstance);
            if (deliveredCount > 0)
            {
                deliveredNames = deliveredNames + ", ";
            }
            deliveredNames = deliveredNames + deliveredName;
            deliveredCount++;
            this.campaignData.orderShipClasses.RemoveAt(i);
            this.campaignData.orderShipInstances.RemoveAt(i);
            this.campaignData.orderDaysRemaining.RemoveAt(i);
            if (UnitReference.instance.unitData != null && UnitReference.instance.unitData.unitType == UnitType.Sea)
            {
                UnitReference.instance.SetNamesInClassList(UnitReference.instance.namesInClassDropdown.value);
            }
        }
    }
    if (deliveredCount == 1)
    {
        ErrorPanel.instance.SetErrorMessage("ShipDelivered", deliveredNames, string.Empty, string.Empty);
    }
    else if (deliveredCount > 1)
    {
        ErrorPanel.instance.SetErrorMessage("ShipsDelivered", deliveredNames, string.Empty, string.Empty);
    }
}
```
Compile.

## Step E - disbanding stations the ship (CampaignInterface.DisbandTaskForce)
Right-click **DisbandTaskForce** > **Edit Method (C#)...** Find the line `this.RemoveMapMobileDataAtIndex(this.currentMapObject.mobileMapObject, i);` (inside the loop, last line of the `if` that handles highlighted ships). Add directly **before** it:
```csharp
MapLocation rehomeLoc = CampaignManager.instance.GetClosestLocation(this.currentMapObject, false);
if (rehomeLoc != null && rehomeLoc.createShips)
{
    MobileMapObject.SetHomePort(this.currentMapObject.mobileMapObject.unitPrefabs[i], this.currentMapObject.mobileMapObject.unitInstances[i], rehomeLoc.locationName);
}
```
Compile, then **File > Save Module**.

## Files
- `campaign_message.txt` -> StreamingAssets/default/language/english/dictionary/ (adds `WrongPort`).
- `rules_popup.zip` (updated page 1 text) -> extract over StreamingAssets/default/ (same folders as before).

## Test
1. New campaign, order a ship at a shipyard; after delivery it can be recruited at that shipyard.
2. In the US campaign (two shipyards): order at New Hebrides, wait for delivery, try to recruit at Cooktown: you should get the "built at New Hebrides" message.
