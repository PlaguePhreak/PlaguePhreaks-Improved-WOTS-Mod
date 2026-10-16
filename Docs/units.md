# Units rule (read before any battle code change)

Decided 12 Oct 2026, after the F10 test: F10 showed about 2,000 for ships the game's ruler measured at 19,169 m.

## How the game measures
- **Battle (tactical) code:** 1 game unit = **10 m**. This covers `Vector3.Distance`, `Utilities.GetXZDistance`, `transform.position`, plane heights and ship/plane speeds. Proof: `Utilities.GetDistanceInKilometers` divides by 0.1, and `ConvertKnotToMetrePerSecond` multiplies by 0.1.
- **Campaign map code:** real metres (`GetDistanceInMetresBetweenMapObjects`, the `mapWidthMetres` values).
- **Config and data files:** mixed. Some are in metres and the game multiplies them by 0.1 (`formationSeaSpacings`, sub ambush offsets). Others are already in game units (aircraft `attackHeight`, `attackRange`, `diveDropHeight`). Check how the game reads a value before changing it.

## Our rule from now on
1. **We always talk in real metres:** in docs, messages, the change log, tuning notes and testing steps.
2. **In battle code, every distance and height is written as metres × 0.1**, so the real value can be read straight off the line. For example, 1,200 m is written as:
```csharp
if (targetDistance < 1200f * 0.1f)
```
3. **Campaign code** stays in plain metres, because that code already uses metres.
4. **Data files** that are in game units: the doc always gives the metres next to the value, for example `"attackHeight":[205,215]` (2,050-2,150 m).
5. **F10 developer view:** after the `ObjectPoolManager.OnGUI` fix (` * 10f`), it shows real metres, the same as the game's ruler.

## Older changes written with the wrong units (fix list)
These used metres as if they were game units, so they work at 10 times the intended distance. Written in the new style:

| Method (class UnitAISea) | Old | New | Meaning |
|---|---|---|---|
| `KeepStationInBattle` | `1200f` | `1200f * 0.1f` | Break formation within 1,200 m |
| `CoordinateTorpedoes` | `3000f` | `3000f * 0.1f` | Torpedo group: ships within 3,000 m |
| `CheckNavigation` (sub ambush) | `2500f` | `2500f * 0.1f` | Spring ambush within 2,500 m |
| `CheckNavigation` (sub return) | `600f` | `600f * 0.1f` | Return when no ship within 600 m |
| `FireTorpedoes` | `150f` | `150f * 0.1f` | Minimum torpedo target distance 150 m |

Plus `ObjectPoolManager.OnGUI`: ` * 10f` on the F10 distance line.

`air_strike_ai.md` already follows this rule.
