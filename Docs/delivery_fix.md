# Combined delivery message (CampaignManager.CheckDaily)

1. Replace `campaign_message.txt` in `StreamingAssets/default/language/english/dictionary/` with the attached file (adds `ShipsDelivered`).
2. In dnSpy open **CampaignManager** > right-click **CheckDaily** > **Edit Method (C#)...** and replace the whole method with:

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

3. Compile, then File > Save Module.
