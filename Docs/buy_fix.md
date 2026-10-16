# v0.21 Faster ship buying [BUY]

Finding: after buying a ship that is already in the pool (state -1), `UnitReference.SetNamesInClassList`
already jumps the dropdown to the first ship still available, so no change is needed there.
The gap is ORDERING a ship that has to be built (state 1): `AddShipToTaskForce` returns right after the order
and the dropdown stays on the same ship.

Fix: in CampaignInterface.AddShipToTaskForce, inside `if (num2 == 1)`, after the
`if (orderAvailable != null && orderAvailable.Count == 3) { ... }` block and just before the `return;` that follows it, add:

```csharp
if (player)
{
    int buyCount = UnitReference.instance.namesInClassDropdown.options.Count;
    for (int buyStep = 1; buyStep < buyCount; buyStep++)
    {
        int buyIndex = (value + buyStep) % buyCount;
        int buyState = CampaignManager.instance.IsPlayerShipInstanceAvailable(currentPrefab, buyIndex);
        bool buyOk = false;
        if (buyState == -1)
        {
            string buyHome = MobileMapObject.GetHomePort(currentPrefab, buyIndex);
            buyOk = buyHome == string.Empty || component == null || buyHome == component.locationName;
        }
        else if (buyState == 1 && CampaignManager.instance.GetIndexInDoubleList(currentPrefab, buyIndex, campaignData.orderShipClasses, campaignData.orderShipInstances) == -1)
        {
            buyOk = component == null || component.portLevel >= num;
        }
        if (buyOk)
        {
            UnitReference.instance.namesInClassDropdown.value = buyIndex;
            Debug.Log("[BUY] next ship in class: " + buyIndex);
            break;
        }
    }
}
```
Status: written, not yet compiled or tested.
