# Air damage rework (v0.17.3)

**What was wrong (found in the code)**
- **Every plane dies on its 3rd hit:** in vanilla, a plane smokes on its 1st and 2nd hit and goes down on the 3rd, whatever its size. A Zero, a Hellcat and a B-17 all take 3 hits (`DamageableAir.ApplySmallCalibreDamageToAir`). Only the armour chance in the data files makes some planes last longer.
- **Why Zeros are so deadly:** gun "damage" in vanilla is the number of hits each bullet counts as. The Zero's four gun streams are set to 2, 1, 1 and 2, so a single burst from a Zero counts as 6 hits. The Wildcat's six .50s are modelled as 2 streams of 1, so its burst counts as 2 hits. Per pass, a Zero did about 3 times the damage of a Wildcat.
- **It is not a player bonus:** the difficulty settings give both sides the same aircraft armour (1.0 on every preset in `config.txt`).
- **Heavy AA:** a 5-inch burst within 10 m of any plane is an instant kill, including a B-17.

**What changes**
1. **Toughness instead of 3 hits.** Every aircraft type has its own toughness, based on its real size, structure, armour plate and self-sealing tanks. Each hit takes away toughness:
   - At 1/3 damage, the plane trails smoke.
   - At 2/3 damage, it trails a second smoke trail.
   - At full damage, it goes down.
2. **Real gun calibres.** Each hit does damage by calibre. Rate of fire is included, so a slow-firing cannon counts for a little less per hit.
   - 7.7 mm and .30 machine gun: 1
   - .50 machine gun: 2.5
   - 20 mm cannon: 8
3. **Armour that depends on calibre.** Pilot armour and self-sealing tanks stop most rifle-calibre bullets, some .50 hits, and few cannon shells. On top of that, the game's existing 25% "glancing hit" chance still applies to every plane.
4. **Ship light AA** (20 mm, 25 mm, 40 mm, 1.1 in and .50, which the game doesn't tell apart) does 7 per hit. Ships that have their own AA damage values in their data keep them.
5. **Heavy AA bursts:**
   - Within 10 m: 40 damage. This kills Japanese aircraft, Wildcats and Dauntlesses. It badly damages Hellcats, Avengers and medium bombers, and a B-17 can survive it.
   - From 10 to 20 m: 1 to 16 damage, less the further out the plane is. Armour applies.
   - Planes still break off a dogfight when flak bursts near them.
6. **Damage carried over from an earlier battle** (smoke trails at the start) now counts as 1/3 toughness per smoke trail.
7. **Bombs and torpedoes were checked and left unchanged.** Their damage values already match the real explosive charges (see "Bombs and torpedoes" below).
8. **Debug log lines:**
   - `[AIRDMG]` each time a plane starts smoking or goes down, with its damage and toughness.
   - One `[AIRDMG]` line for each plane when it spawns, showing its gun damage, toughness and armour.

**Aircraft table** (all set in `DamageableAir`, easy to change later)

| Aircraft | Toughness | Armour | Fixed guns (per stream) | Rear gunner |
|---|---|---|---|---|
| Zero (and kamikaze) | 24 | 0 | 20 mm 8 (wings), 7.7 mm 1.5 (nose, fast-firing Type 97) | - |
| Val | 22 | 0 | 1 | 1 |
| Kate | 22 | 0 | - | 1 |
| Judy (and kamikaze) | 18 | 0 | 1 | 1 |
| Pete | 16 | 0 | 1 | 1 |
| Jake | 18 | 0 | - | 1 |
| Betty | 36 | 0 | - | 2 (20 mm tail + 7.7 mm) |
| Wildcat (F4F-4, 6x .50) | 28 | 0.30 | 7.5 (3 guns per wing) | - |
| Hellcat | 45 | 0.45 | 2.5 | - |
| Corsair | 42 | 0.45 | 2.5 | - |
| Dauntless | 30 | 0.30 | 2.5 | 2 (twin .30) |
| Helldiver | 36 | 0.30 | 2.5 | 2 (twin .30) |
| Devastator | 26 | 0.15 | 1 | 1 |
| Avenger | 44 | 0.35 | 1 | 2 (.50 turret + .30) |
| Kingfisher | 18 | 0.10 | 1 | 1 |
| Walrus | 20 | 0 | 1 | 1 |
| B-25C | 66 | 0.35 | 2.5 | 2.5 |
| B-17F | 120 | 0.50 | - | 2.5 |

Any aircraft not in the table (for example one added by another mod) gets toughness 10 + its weight in kg / 300, and keeps its own armour and gun values from its files.

**Average hits to bring a plane down** (old -> new, including the glancing and armour chances)

| Aircraft | Hits from a Zero | Hits from a Wildcat | Hits from ship light AA |
|---|---|---|---|
| Zero | - | 4.0 -> 4.3 | 4.0 -> 4.6 |
| Kate / Val | - | 4.0 -> 3.9 | 4.0 -> 4.2 |
| Wildcat | 3.3 -> 8.8 | - | 5.0 -> 5.8 |
| Hellcat | 4.8 -> 15.1 | - | 7.3 -> 9.8 |
| Dauntless | 3.3 -> 9.5 | - | 5.0 -> 6.2 |
| Avenger | 3.3 -> 14.2 | - | 5.0 -> 9.3 |
| B-17F | 7.6 -> 42.7 | - | 11.4 -> 26.7 |

A Zero has 4 gun streams and a Wildcat has 2, so the Zero lands about twice as many hits per second on target. Head to head, a Zero and a Wildcat now kill each other at about the same rate (about 4.5 Wildcat-equivalent hits each way). The Zero turns better and still burns easily; the Wildcat soaks up 7.7 mm fire.

*Retuned in v0.17.5 after testing: Zero toughness 18 -> 24, .50 hits 3 -> 2.5, 20 mm hits 6.5 -> 8, Zero nose guns 1 -> 1.5, and US bombers less tough (Dauntless 36 -> 30, Helldiver 42 -> 36, Avenger 54 -> 44, Devastator 30 -> 26).*

Back up the DLL first. Do the steps in order.

## Step 1 - DamageableAir (whole class)
1. Right-click class **DamageableAir** > **Edit Class (C#)...**
2. Leave the `using` lines at the top alone. Select everything from `public class DamageableAir` down to the very last `}`, and paste this over it:
```csharp
public class DamageableAir : MonoBehaviour
{
    public void ApplyDamageToAIR(AmmunitionDamage ammunitionDamage, Collision collision)
    {
        if (this.smokeParticlesShotDown.Count != 0)
        {
            return;
        }
        float burst = ammunitionDamage.sphereCollider.radius / ammunitionDamage.maxRadius;
        Vector3 point = collision.contacts[0].point;
        if (burst < 0.5f)
        {
            this.ApplySmallCalibreDamageToAir(DamageableAir.ModFlakClose, point, false, false, false);
        }
        else
        {
            this.ApplySmallCalibreDamageToAir(DamageableAir.ModFlakFar * Mathf.Clamp01(1f - burst) + 1f, point, false, false, true);
        }
        if (this.parentUnit.unitAI.currentAIAction == AIAction.Attack_Unit && this.parentUnit.unitAI.focusedUnit != null && this.parentUnit.unitAI.focusedUnit.unitAir != null)
        {
            this.parentUnit.unitAI.BreakAwayFromUnit();
        }
    }

    public void ApplySmallCalibreDamageToAir(float damage, Vector3 hitPoint, bool keepFlying, bool noFlash, bool checkArmor)
    {
        if (!noFlash)
        {
            GameObject flash = ObjectPoolManager.CreatePooled(Library.instance.particleEffectsDictionary["aircraftHitFlashes"], hitPoint, Quaternion.identity);
            flash.transform.SetParent(base.transform);
        }
        if (this.parentUnit == null || this.parentUnit.unitAir == null || this.parentUnit.unitAir.shootDown || this.smokeParticlesShotDown.Count != 0)
        {
            return;
        }
        float toughness = DamageableAir.ModAirToughness(this.parentUnit);
        float hit = damage;
        if (hit <= 0f)
        {
            hit = toughness / 3f + 0.01f;
        }
        else if (checkArmor && this.ModArmourAbsorb(hit))
        {
            return;
        }
        int smokeBefore = this.smokeParticlesAir.Count;
        this.modDamage += hit;
        float part = this.modDamage / toughness;
        int smokeWanted = 0;
        if (part >= 0.6667f)
        {
            smokeWanted = 2;
        }
        else if (part >= 0.3333f)
        {
            smokeWanted = 1;
        }
        while (this.smokeParticlesAir.Count < smokeWanted && this.smokeParticlesAir.Count < 2)
        {
            this.ModAddSmoke(hitPoint);
        }
        if (part >= 1f && !keepFlying)
        {
            Utilities.PlayAllParticles(this.smokeParticlesAir, false);
            this.parentUnit.unitAir.shootDown = true;
            UnityEngine.Debug.Log("[AIRDMG] " + DamageableAir.ModAirKey(this.parentUnit) + " id " + this.parentUnit.GetInstanceID() + " side " + this.parentUnit.faction + " SHOT DOWN, damage " + this.modDamage.ToString("F1") + " / " + toughness.ToString("F1"));
        }
        else if (this.smokeParticlesAir.Count != smokeBefore)
        {
            UnityEngine.Debug.Log("[AIRDMG] " + DamageableAir.ModAirKey(this.parentUnit) + " id " + this.parentUnit.GetInstanceID() + " side " + this.parentUnit.faction + " smoking (" + this.smokeParticlesAir.Count + "), damage " + this.modDamage.ToString("F1") + " / " + toughness.ToString("F1"));
        }
    }

    private bool CheckArmorAbsorb()
    {
        return UnityEngine.Random.value < Config.instance.baseAircraftAbsorb || UnityEngine.Random.value < this.parentUnit.unitData.armorAbsorbProbability * Utilities.GetDifficultyModifier(Difficulty.AirAbsorb, this.parentUnit.faction);
    }

    private bool ModArmourAbsorb(float hit)
    {
        if (UnityEngine.Random.value < Config.instance.baseAircraftAbsorb)
        {
            return true;
        }
        float armour = DamageableAir.ModAirArmour(this.parentUnit);
        armour *= Utilities.GetDifficultyModifier(Difficulty.AirAbsorb, this.parentUnit.faction);
        armour *= Mathf.Clamp01(2f / hit);
        return UnityEngine.Random.value < armour;
    }

    private void ModAddSmoke(Vector3 hitPoint)
    {
        GameObject smoke = ObjectPoolManager.CreatePooled(Library.instance.particleEffectsDictionary["air_smokeTrail"], hitPoint, Quaternion.identity);
        smoke.transform.SetParent(base.transform);
        ParticleSystem smokePS = smoke.GetComponent<ParticleSystem>();
        this.smokeParticlesAir.Add(smokePS);
        ParticleSystem.MainModule smokeMain = smokePS.main;
        smokeMain.startSize = new ParticleSystem.MinMaxCurve(1f, UnityEngine.Random.Range(1f, 3f));
        smokeMain.startColor = Library.instance.smokeTrailColours.Evaluate(UnityEngine.Random.value);
    }

    public void StopFireAudio()
    {
        for (int i = 0; i < this.smokeParticlesShotDown.Count; i++)
        {
            AudioSource component = this.smokeParticlesShotDown[i].GetComponent<AudioSource>();
            if (component != null)
            {
                component.Stop();
            }
        }
    }

    public static string ModAirKey(Unit unit)
    {
        if (unit == null)
        {
            return string.Empty;
        }
        return unit.gameObject.name.Replace("(Clone)", string.Empty).Trim().ToLowerInvariant();
    }

    public static float ModAirToughness(Unit unit)
    {
        switch (DamageableAir.ModAirKey(unit))
        {
        case "zero":
        case "zero_kamikaze":
            return 24f;
        case "val":
            return 22f;
        case "kate":
            return 22f;
        case "judy":
        case "judy_kamikaze":
            return 18f;
        case "pete":
            return 16f;
        case "jake":
            return 18f;
        case "betty":
            return 36f;
        case "wildcat":
            return 28f;
        case "hellcat":
            return 45f;
        case "corsair":
            return 42f;
        case "dauntless":
            return 30f;
        case "helldiver":
            return 36f;
        case "devastator":
            return 26f;
        case "avenger":
            return 44f;
        case "kingfisher":
            return 18f;
        case "walrus":
            return 20f;
        case "b25c":
            return 66f;
        case "b17f":
            return 120f;
        }
        if (unit != null && unit.unitData != null)
        {
            return 10f + (float)unit.unitData.displacement_weight / 300f;
        }
        return 18f;
    }

    public static float ModAirArmour(Unit unit)
    {
        switch (DamageableAir.ModAirKey(unit))
        {
        case "zero":
        case "zero_kamikaze":
        case "val":
        case "kate":
        case "judy":
        case "judy_kamikaze":
        case "pete":
        case "jake":
        case "betty":
        case "walrus":
            return 0f;
        case "wildcat":
            return 0.3f;
        case "hellcat":
            return 0.45f;
        case "corsair":
            return 0.45f;
        case "dauntless":
            return 0.3f;
        case "helldiver":
            return 0.3f;
        case "devastator":
            return 0.15f;
        case "avenger":
            return 0.35f;
        case "kingfisher":
            return 0.1f;
        case "b25c":
            return 0.35f;
        case "b17f":
            return 0.5f;
        }
        if (unit != null && unit.unitData != null)
        {
            return unit.unitData.armorAbsorbProbability;
        }
        return 0f;
    }

    public static float ModFixedGunDamage(Unit unit, int stream)
    {
        switch (DamageableAir.ModAirKey(unit))
        {
        case "zero":
        case "zero_kamikaze":
            if (stream == 0 || stream == 3)
            {
                return DamageableAir.ModGun20mm;
            }
            return DamageableAir.ModGun77mm * 1.5f;
        case "wildcat":
            return DamageableAir.ModGun50cal * 3f;
        case "hellcat":
        case "corsair":
        case "dauntless":
        case "helldiver":
        case "b25c":
            return DamageableAir.ModGun50cal;
        case "avenger":
        case "devastator":
        case "val":
        case "judy":
        case "judy_kamikaze":
        case "pete":
        case "kingfisher":
        case "walrus":
            return DamageableAir.ModGun77mm;
        }
        return -1f;
    }

    public static float ModGunnerDamage(Unit unit)
    {
        switch (DamageableAir.ModAirKey(unit))
        {
        case "kate":
        case "val":
        case "judy":
        case "judy_kamikaze":
        case "jake":
        case "pete":
        case "devastator":
        case "kingfisher":
        case "walrus":
            return DamageableAir.ModGun77mm;
        case "betty":
        case "dauntless":
        case "helldiver":
        case "avenger":
            return 2f;
        case "b25c":
        case "b17f":
            return DamageableAir.ModGun50cal;
        }
        return -1f;
    }

    public Unit parentUnit;

    public List<ParticleSystem> smokeParticlesAir = new List<ParticleSystem>();

    public List<GameObject> smokeParticlesShotDown = new List<GameObject>();

    public float modDamage;

    public const float ModGun77mm = 1f;

    public const float ModGun50cal = 2.5f;

    public const float ModGun20mm = 8f;

    public const float ModShipLightAA = 7f;

    public const float ModFlakClose = 40f;

    public const float ModFlakFar = 30f;
}
```
3. **Compile**, then **File > Save Module**.
4. **Close dnSpy and reopen it**, then reopen the DLL. The next steps use the new parts of this class.

## Step 2 - AAAParticleCollisions.OnParticleCollision
This makes each bullet do its full damage once, instead of counting as several hits.
1. Right-click **OnParticleCollision** (class **AAAParticleCollisions**) > **Edit Method (C#)...**
2. Select the whole method and paste this over it:
```csharp
private void OnParticleCollision(GameObject other)
{
    this.aaaParticle.GetCollisionEvents(other, this.collisionEvents);
    if (this.collisionEvents.Count == 0)
    {
        return;
    }
    if (other.layer == 4)
    {
        ObjectPoolManager.CreatePooled(Library.instance.particleEffectsDictionary["splashMicro"], this.collisionEvents[0].intersection, Quaternion.identity);
        return;
    }
    Unit component = other.GetComponent<Unit>();
    if (component == null)
    {
        return;
    }
    if (component.unitAir != null && this.damage > 0f)
    {
        component.unitAir.damageableAir.ApplySmallCalibreDamageToAir(this.damage, this.collisionEvents[0].intersection, false, false, true);
    }
    if (component.unitSea != null)
    {
        component.unitSea.damageableSea.ApplySmallCalibreDamage(this.damage, this.collisionEvents[0].intersection, other.name);
    }
}
```
3. **Compile.**

(Strafing ships is not affected. The ship damage code doesn't use the gun damage value.)

## Step 3 - WeaponParticle.Start (fighter and bomber fixed guns)
1. Right-click **Start** (class **WeaponParticle**) > **Edit Method (C#)...**
2. Select the whole method and paste this over it:
```csharp
private void Start()
{
    this.parentUnit = base.GetComponentInParent<Unit>();
    base.enabled = false;
    if (this.parentUnit == null || this.particles == null)
    {
        return;
    }
    string modLog = string.Empty;
    for (int i = 0; i < this.particles.Length; i++)
    {
        if (this.particles[i] == null)
        {
            continue;
        }
        AAAParticleCollisions gunHits = this.particles[i].GetComponent<AAAParticleCollisions>();
        if (gunHits == null)
        {
            continue;
        }
        float gunDamage = DamageableAir.ModFixedGunDamage(this.parentUnit, i);
        if (gunDamage > 0f)
        {
            gunHits.damage = gunDamage;
        }
        modLog = modLog + " " + gunHits.damage.ToString("F1");
    }
    UnityEngine.Debug.Log("[AIRDMG] " + DamageableAir.ModAirKey(this.parentUnit) + " fixed guns:" + modLog + " | toughness " + DamageableAir.ModAirToughness(this.parentUnit).ToString("F0") + " armour " + DamageableAir.ModAirArmour(this.parentUnit).ToString("F2"));
}
```
3. **Compile.**

## Step 4 - WeaponAAA.InitialiseAAA (rear gunners and ship AA)
1. Right-click **InitialiseAAA** (class **WeaponAAA**) > **Edit Method (C#)...**
2. Don't delete anything. Click just before the **last** `}` of the method (the one that closes the method), press Enter, and paste:
```csharp
if (this.parentUnit != null && this.aaaParticles != null)
{
    float modAAA = -1f;
    if (this.parentUnit.unitAir != null)
    {
        modAAA = DamageableAir.ModGunnerDamage(this.parentUnit);
    }
    else if (this.parentUnit.unitSea != null && (this.sizes == null || this.sizes.Length == 0))
    {
        modAAA = DamageableAir.ModShipLightAA;
    }
    if (modAAA > 0f)
    {
        for (int m = 0; m < this.aaaParticles.Length; m++)
        {
            if (this.aaaParticles[m] != null)
            {
                AAAParticleCollisions aaaHits = this.aaaParticles[m].GetComponent<AAAParticleCollisions>();
                if (aaaHits != null)
                {
                    aaaHits.damage = modAAA;
                }
            }
        }
    }
}
```
3. **Compile**, then **File > Save Module**.

No text files to copy. Everything is in the DLL.

## Testing
1. Start a battle with US fighters against Zeros (a custom battle is quickest). Fly a few dogfights.
2. **Zeros vs Wildcats:** a Zero should smoke after one good Wildcat burst and go down after one or two more. A Wildcat should take a long beating from a Zero, unless the Zero lands its 20 mm.
3. **Ship AA:** a Japanese strike against a US fleet should lose planes about as often as before. US strikes should hold up a little better against Japanese AA.
4. **B-17s** should shrug off most fighter attacks and some close 5-inch bursts.
5. In `output_log.txt`, check that:
   - each plane writes one `[AIRDMG] <type> fixed guns: ... | toughness .. armour ..` line when it spawns. For example, `zero fixed guns: 6.5 1.0 1.0 6.5`, and `wildcat fixed guns: 9.0 9.0`.
   - an `[AIRDMG] ... smoking` or `... SHOT DOWN` line appears with the damage and toughness.
6. If a plane's spawn line shows the wrong numbers, or its name isn't in the table, send me that line.

## Tuning (all in class DamageableAir)
- **Toughness:** the numbers in `ModAirToughness`. Higher means harder to shoot down.
- **Armour:** the numbers in `ModAirArmour` (0 = none, 0.5 = stops half of the rifle-calibre hits).
- **Gun power:**
  - `ModGun77mm` (1), `ModGun50cal` (2.5) and `ModGun20mm` (8) at the bottom of the class.
  - The per-plane choice is in `ModFixedGunDamage` and `ModGunnerDamage`.
- **Ship AA:** `ModShipLightAA` (7). Higher means deadlier ship AA.
- **Heavy AA:** `ModFlakClose` (40, within 10 m) and `ModFlakFar` (30, scaled down to 0 at 20 m).
- **Glancing hits:** `config.txt` `baseAircraftAbsorb` (0.25).

## Bombs and torpedoes (checked, no change)
The game's bomb and torpedo damage values follow their real explosive charges:
- US 2,000 lb bomb: 481 kg
- 1,000 lb bomb: 137 kg
- 1,600 lb AP bomb: 95 kg
- Japanese No.25 Model 2 (250 kg) bomb: 103 kg
- Type 99 No.25 bomb: 60 kg
- No.80 land bomb: 382 kg
- Type 91 aerial torpedo: about 205-235 kg charge in 1941-42; the game uses 257
- Mark 13 aerial torpedo: 270 kg Torpex (late-war version); the game uses 274
- The Mark 13's 30% dud rate matches its poor 1942-43 record. The Type 91's 4% matches its reliability.

These are left as they are.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.
