# Fires act as a detection beacon

**Found in the code:** `SensorManager.GetVisibilityModifier` decides how easy a ship is to see. At night it already boosts ships lit by star shells or searchlights (x1.2, and speed no longer matters). Fires were not counted.

**What changes**
- At night a burning ship counts as lit: x1.25 with 1 fire, +0.1 per extra fire, up to x1.6 (4+ fires). Speed no longer matters.
- By day, smoke from fires gives x1.1.
- Works both ways, so your burning ships also light themselves up for the enemy.

## Step 1 - SensorManager.GetVisibilityModifier
Replace the whole method (keep dnSpy's `using` lines and class line) with:
```csharp
public float GetVisibilityModifier(Unit observer, Unit target, float range)
{
    float landClutter = this.GetLandClutter(observer.transform.position, target.transform.position, range * 1000f * 0.1f, false);
    float behindLand = 1f;
    if (landClutter == 0f)
    {
        return 0f;
    }
    if (landClutter != float.PositiveInfinity)
    {
        behindLand = Config.instance.visualSeaLandBehindModifier;
    }
    float speedFactor = 1f + (-Config.instance.visibilitySpeedModifier + Mathf.Abs(target.percentMaxSpeed) * Config.instance.visibilitySpeedModifier * 2f);
    float lightFactor = 1f;
    bool dark = Utilities.GetIsDark();
    if (dark && (target.illuminationTimer > 0f || target.searchlightTimer > 0f))
    {
        lightFactor = 1.2f;
        speedFactor = 1f;
    }
    int fires = 0;
    if (target.damageableSea != null && target.damageableSea.cellsBurning != null)
    {
        fires = target.damageableSea.cellsBurning.Count;
    }
    if (fires > 0)
    {
        if (dark)
        {
            lightFactor = Mathf.Max(lightFactor, Mathf.Min(1.15f + 0.1f * (float)fires, 1.6f));
            speedFactor = 1f;
        }
        else
        {
            lightFactor = Mathf.Max(lightFactor, 1.1f);
        }
    }
    return speedFactor * behindLand * lightFactor * target.unitData.unitVisualSizeModifier;
}
```
Compile, then File > Save Module.

## Tuning
`1.15f + 0.1f` (per fire at night), `1.6f` (night maximum), `1.1f` (daytime smoke).

Note: I could not compile or run this.
