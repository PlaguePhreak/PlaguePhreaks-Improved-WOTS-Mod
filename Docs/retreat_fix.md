# Retreat fix (v0.17.8)

**What was wrong (found in the code):** when an AI ship retreats (`UnitAISea.RetreatUnit`), it heads 20 km directly away from the average position of the player ships it can see (`EngagementAI.GetAveragePositionKnownPlayerSea`). That average had a bug in the vanilla game: it divided the east-west (x) and height (y) values by the number of ships, but **not the north-south (z) value**. With 9 ships in view, the north-south position came out as 9 times too big. That puts the "average" far off to one side, so "away from it" can point straight back through your line. This is why the enemy carrier, Fuso and Myoko all retreated into your formation.

**What changes:** the average is now worked out correctly, so a retreating ship turns away from your ships. This is the only place the game uses this method. A `[RETREAT]` log line shows what each retreat steers away from.

**Install (dnSpy)**
1. In class **EngagementAI**, right-click method **GetAveragePositionKnownPlayerSea** > **Edit Method (C#)...**
2. Select all of it and replace it with:
```csharp
public Vector3 GetAveragePositionKnownPlayerSea(Vector3 myPos)
{
	Vector3 average = Vector3.zero;
	float count = 0f;
	if (this.playerSea != null && this.playerSea.Count > 0)
	{
		for (int i = 0; i < this.playerSea.Count; i++)
		{
			Unit u = this.playerSea[i];
			if (u != null && u.detected && !u.isDestroyed)
			{
				average += u.transform.position;
				count += 1f;
			}
		}
		if (count > 0f)
		{
			// vanilla only divided x and y, so z (the second map axis) was the sum of all ships
			average.x /= count;
			average.y /= count;
			average.z /= count;
		}
		else
		{
			Unit closest = this.GetClosestUnit(myPos, this.playerSea, true);
			if (closest != null)
			{
				average = closest.transform.position;
			}
		}
	}
	UnityEngine.Debug.Log("[RETREAT] retreating away from " + ((count > 0f) ? ("the average of " + count + " known player ships") : "the closest player ship") + ", " + (Vector3.Distance(myPos, average) * 10f).ToString("F0") + " m away");
	return average;
}
```
3. Click **Compile**, then **File > Save Module**.

**Testing:** fight a surface battle until enemy ships retreat. They should turn away from your fleet. The log should show `[RETREAT] retreating away from the average of N known player ships, X m away`.

**Note:** each ship works out its retreat point once, when it starts retreating. If your fleet later sails round in front of it, it keeps going to the same point.
