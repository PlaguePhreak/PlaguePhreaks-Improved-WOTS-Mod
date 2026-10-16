# v0.21.2 Torpedo hit angle [TORPHIT]

Method: Ammunition.ExplodeAmmunition. Find these two lines near the top:
```csharp
float value = Random.value;
bool flag = value < dudRate;
```
Replace them with:
```csharp
float value = Random.value;
float hitChance = dudRate;
if (u != null && directHit && dudRate > 0f && (ammoType == AmmoType.Torpedo || ammoType == AmmoType.Aerial_Torpedo))
{
    Vector3 hitTorpFwd = base.transform.forward;
    Vector3 hitShipFwd = u.transform.forward;
    hitTorpFwd.y = 0f;
    hitShipFwd.y = 0f;
    float hitAngle = Vector3.Angle(hitTorpFwd, hitShipFwd);
    if (hitAngle > 90f)
    {
        hitAngle = 180f - hitAngle;
    }
    bool hitContact = base.name.Contains("mark13") || base.name.Contains("mark14") || base.name.Contains("mark15");
    if (hitContact)
    {
        if (hitAngle > 60f)
        {
            hitChance += 0.25f * (hitAngle - 60f) / 30f;
        }
        else if (hitAngle < 45f)
        {
            hitChance *= 0.6f;
        }
    }
    if (hitAngle < 22f)
    {
        hitChance += (1f - hitChance) * 0.6f * (22f - hitAngle) / 22f;
    }
    Debug.Log("[TORPHIT] " + base.name + " angle " + hitAngle.ToString("F0") + " dud chance " + hitChance.ToString("F2"));
}
bool flag = value < hitChance;
```
Notes: only active when the game's "dud torpedoes" option is on (dudRate is 0 otherwise).
Glancing hits (under 22 degrees) add up to a 60% extra chance of a dud at 0 degrees. Mark 13/14/15 get +25% dud near 90 degrees and 40% fewer duds on angled hits (under 45 degrees).
Status: written, not yet compiled or tested.
