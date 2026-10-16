# Torpedo break-back crash fix (v0.17.10)

**What was wrong (found in the code and the log):** when a torpedo hits, `DamageableSea.ApplyDamage` first rolls for a "broken back". It takes the first compartment hit, for example `"2,0,5"`, splits it at the commas and reads the third number. If the torpedo struck high up, that first hit can be a deck or superstructure compartment, whose ID is a single number like `"3"`. There is no third number to read, so the game throws an `IndexOutOfRangeException` and stops. The torpedo then does no damage at all, even though the "struck by torpedo" message has already played. The log showed exactly this for Lang's torpedo on Dale:
```
IndexOutOfRangeException: Array index is out of range.
  at DamageableSea.ApplyDamage (...)
[HITLOG] Dale hit by torpedo from Lang: 0 cells, damage 0 of 363 ...
```
This is a bug in the vanilla game. Our v0.8 torpedo tuning makes the break-back roll come up more often against destroyers, so it shows up more in the mod.

**What changes:** if the first compartment hit has no third number, the torpedo skips the break-back roll and goes on to do its normal damage.

**Install (dnSpy)**
1. In class **DamageableSea**, right-click method **ApplyDamage** > **Edit Method (C#)...**
2. Press Ctrl+F and find `"1,0,"`. You'll see three lines close together, something like this (dnSpy's names may differ, e.g. `array2` may be `array3`):
```csharp
string text = "1,0," + array2[2];
...
text = "0,0," + array2[2];
...
text = "2,0," + array2[2];
```
3. In each of the three lines, replace `array2[2]` (with your own name) with:
```csharp
(array2.Length > 2 ? array2[2] : "none")
```
   The first line then reads, for example:
```csharp
string text = "1,0," + (array2.Length > 2 ? array2[2] : "none");
```
   `"1,0,none"` is not a real compartment, so the next line (`if (this.cellVariables.ContainsKey(text))`) skips the break-back.
4. Click **Compile**, then **File > Save Module**. If the three lines look different from this, send me a screenshot of that part.

**Testing:** fire torpedoes at close range at a destroyer, a few times. The log should no longer show `IndexOutOfRangeException ... DamageableSea.ApplyDamage`, and every torpedo that strikes should show damage in the hit log, unless it's a dud.
