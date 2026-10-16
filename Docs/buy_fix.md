# v0.21 Faster ship buying [BUY]

Method: CampaignInterface.AddShipToTaskForce. After the line
`UnitReference.instance.SetNamesInClassList(UnitReference.instance.namesInClassDropdown.value);`
(near the end, after the ship is added to the new task force) add:

```csharp
if (player && UnitReference.instance.namesInClassDropdown.options.Count > 1)
{
    MapLocation buyPort = this.currentMapObject.GetComponent<MapLocation>();
    int buyCount = UnitReference.instance.namesInClassDropdown.options.Count;
    int buyStart = UnitReference.instance.namesInClassDropdown.value;
    for (int buyStep = 1; buyStep < buyCount; buyStep++)
    {
        int buyIndex = (buyStart + buyStep) % buyCount;
        if (CampaignManager.instance.IsPlayerShipInstanceAvailable(UnitReference.instance.currentPrefab, buyIndex) != -1)
        {
            continue;
        }
        string buyHome = MobileMapObject.GetHomePort(UnitReference.instance.currentPrefab, buyIndex);
        if (buyHome != string.Empty && buyPort != null && buyHome != buyPort.locationName)
        {
            continue;
        }
        UnitReference.instance.namesInClassDropdown.value = buyIndex;
        Debug.Log("[BUY] next ship in class: " + buyIndex);
        break;
    }
}
```
Status: written, not yet compiled or tested.
