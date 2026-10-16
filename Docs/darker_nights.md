# Darker nights (Night fighting, part 1)

**Found in the code:** visual range = `maxSeaVisibility` (30 km) x `visibilityByHour[hour]` x weather. Night was 0.5, so lookouts saw about 15 km. Star shells and searchlights only gave x1.2 (`SensorManager.GetVisibilityModifier`). `Utilities.GetIsDark` uses the same table.

**What changes**
- Night visibility 0.5 -> 0.25 (about 7 km); dawn/dusk slightly darker.
- Lit ships (star shell, searchlight) x1.8 instead of x1.2. Burning ships x1.45 (1 fire), +0.15 per fire, up to x1.8.
- Campaign night encounters start at up to 10 km (was 15).
- Radar is unchanged, so radar ships gain a real night advantage. Japan's `nationNightFightBonus` still applies.

## Step 1 - config.txt
- `"visibilityByHour":[0.25,0.25,0.25,0.25,0.25,0.45,0.65,0.8,0.9,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9,0.8,0.65,0.45,0.25,0.25,0.25,0.25]`
  (was `[0.5,0.5,0.5,0.5,0.5,0.6,0.7,0.8,0.9,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9,0.8,0.7,0.6,0.5,0.5,0.5,0.5]`)
- `"nightEncounterMaxRange":10` (was 15)

## Step 2 - SensorManager.GetVisibilityModifier (fire beacon version)
- `lightFactor = 1.2f;` -> `lightFactor = 1.8f;`
- `Mathf.Min(1.15f + 0.1f * (float)fires, 1.6f)` -> `Mathf.Min(1.3f + 0.15f * (float)fires, 1.8f)`

## Testing
Night battle: ships unseen until a few km apart (unless radar). Star shells, searchlights and fires give ships away from much further.

## Tuning
Raise the 0.25 values (e.g. 0.3) if too dark.
