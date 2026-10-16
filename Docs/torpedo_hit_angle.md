# v0.21.2 Torpedo hit angle [TORPHIT]

Method: Ammunition.ExplodeAmmunition. Find these two lines near the top:
```csharp
float value = UnityEngine.Random.value;
bool flag = value < dudRate;
```
Replace them with:
```csharp
float value = UnityEngine.Random.value;
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
    UnityEngine.Debug.Log("[TORPHIT] " + base.name + " angle " + hitAngle.ToString("F0") + " dud chance " + hitChance.ToString("F2"));
}
bool flag = value < hitChance;
```
Notes: only active when the game's "dud torpedoes" option is on (dudRate is 0 otherwise).
Mark 13/14/15 get +25% dud near 90 degrees and 40% fewer duds on angled hits (under 45 degrees).
Status: compiled and tested (Mark 13 bounced off Yorktown at 11 degrees).


## Part 2 - glancing hits bounce off (replaces the glancing dud chance above)
Method: Ammunition.OnTriggerEnter. Find the end of the long `if (component3.unitID == firedByUnitID || ...) { return; }` check
and the line `if (Time.timeScale != 1f)` right after it. Insert directly BEFORE `if (Time.timeScale != 1f)`:
```csharp
if ((ammoType == AmmoType.Torpedo || ammoType == AmmoType.Aerial_Torpedo) && dudRate > 0f)
{
    AmmunitionMoveTorpedo bounceMove = base.GetComponent<AmmunitionMoveTorpedo>();
    if (bounceMove != null)
    {
        Vector3 bounceFwd = base.transform.forward;
        bounceFwd.y = 0f;
        bounceFwd.Normalize();
        Vector3 bounceRight = component3.transform.right;
        bounceRight.y = 0f;
        bounceRight.Normalize();
        float bounceLateral = Vector3.Dot(bounceFwd, bounceRight);
        float bounceAngle = Mathf.Asin(Mathf.Clamp01(Mathf.Abs(bounceLateral))) * 57.29578f;
        if (bounceAngle < 25f && (bounceAngle < 15f || UnityEngine.Random.value < (25f - bounceAngle) / 10f))
        {
            Vector3 bounceNew = bounceFwd - 2f * bounceLateral * bounceRight;
            base.transform.position += bounceRight * ((bounceLateral > 0f) ? -3f : 3f);
            base.transform.rotation = Quaternion.LookRotation(bounceNew);
            bounceMove.gyroDone = true;
            ((Behaviour)bounceMove).enabled = true;
            UnityEngine.Debug.Log("[TORPHIT] " + base.name + " bounced off " + component3.name + " at " + bounceAngle.ToString("F0") + " degrees");
            return;
        }
    }
}
```
Chance to bounce: 100% under 15 degrees, then fading to 0% at 25 degrees (changed from a fade starting at 0 degrees, where a 7 degree hit still exploded about a third of the time). A bounced torpedo keeps running on its mirrored heading and can hit another ship.
Status: compiled and tested (Mark 13 bounced off Yorktown at 11 degrees).
