# Faster battle time

**Found in the code:** `CombatInterface.SetTimeCompression` only toggles x1 <-> `Config.timeCompressionFactor` (5). `AllowCompression` blocks speeding up during an air attack.

**What changes:** the button and hotkey cycle x1 -> x2 -> x5 -> top (config, now 10) -> x1. The air-attack block is kept. The physics step is capped at the x5 size, so hits stay accurate at x10 (more CPU work).

## Step 1 - config.txt
`"timeCompressionFactor":10.0` (was 5.0)

## Step 2 - CombatInterface.SetTimeCompression (replace the method)
```csharp
public void SetTimeCompression()
{
    if (ActionReport.instance.gameObject.activeSelf)
    {
        return;
    }
    float current = Time.timeScale;
    float top = Config.instance.timeCompressionFactor;
    float next = 1f;
    float[] steps = new float[] { 2f, 5f, top };
    for (int s = 0; s < steps.Length; s++)
    {
        if (steps[s] > current + 0.01f && steps[s] <= top)
        {
            next = steps[s];
            break;
        }
    }
    if (next > 1f && !this.AllowCompression())
    {
        next = 1f;
    }
    Time.timeScale = next;
    Time.fixedDeltaTime = 0.02f * Mathf.Min(next, 5f);
    this.timeCompressionFactor.text = "x" + Time.timeScale.ToString();
}
```

## Tuning
Top speed = `timeCompressionFactor` in config.txt. `Mathf.Min(next, 5f)`: change 5f to 10f for less CPU (less accurate hits at x10).
