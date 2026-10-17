# Wider formation list (v0.25.2, untested)

Problem: in the formation drop-down the longer names are cut off ("Escorted Double Colu", "Kido Butai (2 Carrier"). The list is built in `LanguageManager.GetUITexts`.

## dnSpy steps
1. Open **LanguageManager** > method **GetUITexts** > right-click > **Edit Method (C#)...**
2. Find this loop (the first one that uses `seaFormations`):
```csharp
for (int n = 0; n < seaFormations.Length; n++)
{
	seaFormations[n].options.Clear();
	seaFormations[n].AddOptions(list);
}
```
3. Add three lines inside it, under `seaFormations[n].AddOptions(list);`:
```csharp
	RectTransform formationList = seaFormations[n].template;
	formationList.pivot = new Vector2(0f, 1f);
	formationList.sizeDelta = new Vector2(formationList.sizeDelta.x + 90f, formationList.sizeDelta.y);
```
4. **Compile**, then **File > Save Module**.

`90f` is the extra width in pixels: use a bigger number if names are still cut, a smaller one if the list is too wide. The pivot line makes the list grow to the right only. If the list looks shifted in the game, delete the pivot line and the list will grow evenly on both sides instead.
The same loop is used for every sea formation drop-down (campaign map and battle screen).
