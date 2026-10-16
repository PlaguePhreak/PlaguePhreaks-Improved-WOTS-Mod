# Air strike AI: steep dives, auto attack, hammer and anvil (v0.17, part 2)

**What was wrong (found in the code)**
- **Shallow dives:** dive bombers enter a battle at only 880-1,000 m (`EngagementData.CreateUnitGroup`). They push over at 850 m while still 1.2 km short of the target (`EngagementAI.DiveBombApproach`), so the dive can't be steeper than about 35°. That is the glide you see.
- **No auto attack for your bombers:** the game's "auto" mode for aircraft only handles dogfights. Your bombers only attack a ship when you order them to.
- **Torpedo runs:** a torpedo bomber flies straight at the target from wherever it happens to be. It never sets up a beam attack, and two flights never split to both bows.
- **Target choice:** the AI picks a ship type at random by weight. It ignores distance, ignores how many planes are already on that ship, and keeps attacking a ship that is already sinking.

**What changes**
1. **Real dive bombing:** dive bombers enter battle at 2,000-2,200 m and push over about 1,100-1,200 m from the target. That gives about a 70-75° dive (Fix v2; the first test at 800 m gave 80-90°), with release at 450-550 m. This applies to the Dauntless, Helldiver, Val and Judy, for both sides.
2. **Auto attack (your bombers):** any dive, torpedo or level bomber flight of yours that still has its payload and has no orders picks its own target and attacks.
   - A manual attack order always wins, and so do waypoints.
   - When the waypoints run out, the flight goes back to auto.
   - A flight you have selected and are steering yourself is left alone.
3. **Smarter target choice (both sides):**
   - Flights prefer carriers, then battleships, then cruisers.
   - Each flight counts how many planes are already attacking a ship. Up to 2-3 flights stack on a carrier, then the next flight picks another big ship.
   - Torpedo bombers avoid destroyers.
   - Ships that are already burning or flooding are slightly preferred, so they get finished off.
   - Closer ships are preferred.
   - Ships that are already sinking are ignored.
4. **Break off from a doomed ship:** if a flight's target is crippled before the flight starts its run, it switches to a new target. Crippled means at least 50% damaged, at least 30% flooded, or stopped in the water and 30% damaged. Flights that are already committed carry on: a dive bomber already in its dive, a torpedo bomber inside 2.5 km, or a level bomber inside 4 km. This applies to the AI and to your auto-attacking flights, not to your manual orders.
5. **Hammer and anvil (torpedo bombers):**
   - A torpedo flight first flies to a set-up point about 3.5 km out, 60° off the target's bow. Then it turns in for a bow or beam attack, instead of a stern chase.
   - When two or more torpedo flights attack the same ship, they alternate between the port and starboard bows. Whichever way the ship turns, it turns into somebody's torpedoes.
   - A flight that is already well placed (35-100° off the bow on its side) or inside 2.5 km runs straight in.
   - This applies to the AI and to your auto-attacking flights. Your manual torpedo orders fly exactly as before.

Back up the DLL first. Do the steps in this order.

## Step 1 - add one field to UnitAIAir
1. Right-click class **UnitAIAir** > **Edit Class (C#)...**
2. Near the top of the class is the line that declares `aiAttack` (for example `public AIAttack aiAttack;`). Click at the end of that line, press Enter, and paste:
```csharp
public bool modAutoStrike;
```
3. **Compile**, then **File > Save Module**.
4. **Close dnSpy and open it again** (it needs to reload the new field), and reopen the DLL.

## Step 2 - helpers in EngagementAI
1. Right-click class **EngagementAI** > **Edit Class (C#)...**
2. Find the line that starts `public Unit GetBestSeaTarget(`. Click on the empty line just **above** it (between two methods, not inside one) and paste:
```csharp
public bool ModIsShipCrippled(Unit ship)
{
    if (ship == null || ship.isDestroyed)
    {
        return true;
    }
    if (ship.damageableSea == null || ship.unitData == null || ship.unitData.cellDictionary == null || ship.unitData.cellDeckList == null)
    {
        return false;
    }
    float hullCells = (float)ship.unitData.cellDictionary.Count;
    float allCells = hullCells + (float)ship.unitData.cellDeckList.Count;
    if (allCells < 1f)
    {
        return false;
    }
    DamageableSea dmg = ship.damageableSea;
    float damage = ((float)dmg.cellsDamaged.Count + 2f * (float)dmg.cellsDestroyed.Count) / allCells;
    float flooded = (hullCells > 0f) ? ((float)dmg.cellsFlooded.Count / hullCells) : 0f;
    if (damage >= 0.5f || flooded >= 0.3f)
    {
        return true;
    }
    return damage >= 0.3f && ship.currentActualSpeed < 1.5f * 0.1f;
}

public Unit ModPickStrikeTarget(Unit leader, List<Unit> ships)
{
    if (leader == null || ships == null || leader.unitAI == null)
    {
        return null;
    }
    bool torpedo = Utilities.GetIndexOfWeaponType(leader, WeaponType.Aerial_Torpedo) != -1;
    List<Unit> myAir = (leader.faction == Faction.Player) ? this.playerAir : this.otherAir;
    Unit best = null;
    float bestScore = 0f;
    for (int i = 0; i < ships.Count; i++)
    {
        Unit s = ships[i];
        if (s == null || s.isDestroyed || !s.detected || s.unitSea == null || s.unitData == null)
        {
            continue;
        }
        UnitSubType st = s.unitData.unitSubtype;
        if (st == UnitSubType.Submarine && Utilities.isUnitSubmerged(s, -0.2f))
        {
            continue;
        }
        if (this.ModIsShipCrippled(s))
        {
            continue;
        }
        float value = 1f;
        switch (st)
        {
            case UnitSubType.Aircraft_Carrier: value = 10f; break;
            case UnitSubType.Light_Carrier: value = 7f; break;
            case UnitSubType.Battleship: value = 7f; break;
            case UnitSubType.Battlecruiser: value = 6f; break;
            case UnitSubType.Heavy_Cruiser: value = 4f; break;
            case UnitSubType.Light_Cruiser: value = 3.5f; break;
            case UnitSubType.Oiler: value = 3f; break;
            case UnitSubType.Merchant: value = 3f; break;
            case UnitSubType.Destroyer: value = 2f; break;
            case UnitSubType.Destroyer_Escort: value = 1.5f; break;
        }
        if (torpedo && (st == UnitSubType.Destroyer || st == UnitSubType.Destroyer_Escort))
        {
            value *= 0.4f;
        }
        int planes = 0;
        for (int a = 0; a < myAir.Count; a++)
        {
            Unit p = myAir[a];
            if (p == null || p.isDestroyed || p.unitAI == null || p.unitAir == null)
            {
                continue;
            }
            if (p == leader || p.unitAI.followingUnit == leader)
            {
                continue;
            }
            if (p.unitAI.focusedUnit == s && !p.unitAir.hasDroppedPayload)
            {
                planes++;
            }
        }
        value /= 1f + (float)planes / 16f;
        if (s.damageableSea != null && (s.damageableSea.cellsBurning.Count > 0 || s.damageableSea.cellsFlooded.Count > 0))
        {
            value *= 1.15f;
        }
        float dist = Utilities.GetXZDistance(leader.transform.position, s.transform.position);
        value /= 1f + dist / (20000f * 0.1f);
        if (leader.unitAI.focusedUnit == s)
        {
            value *= 1.3f;
        }
        value *= UnityEngine.Random.Range(0.9f, 1.1f);
        if (value > bestScore)
        {
            bestScore = value;
            best = s;
        }
    }
    return best;
}

public void ModLaunchFlightAttack(Unit leader, Unit target)
{
    if (leader == null || target == null || leader.unitAI == null)
    {
        return;
    }
    List<Unit> group = this.GetMeAndMyFollowers(leader, false);
    if (group == null || group.Count == 0)
    {
        return;
    }
    leader.unitAI.focusedUnit = target;
    leader.unitAI.navPoints.Clear();
    this.AttackUnit(group[0]);
    for (int i = 0; i < group.Count; i++)
    {
        Unit u = group[i];
        if (u == null || u.isDestroyed || u.unitAI == null)
        {
            continue;
        }
        u.unitAI.weaponIndexToAttackWith = group[0].unitAI.weaponIndexToAttackWith;
        u.unitAI.focusedUnit = target;
        if (u.unitAir != null && u.unitAir.bombDoors != null && u.unitAir.bombDoors.Count > 0)
        {
            u.unitAir.SetBombDoors(1);
        }
    }
    int w = group[0].unitAI.weaponIndexToAttackWith;
    if (w != Utilities.GetIndexOfWeaponType(group[0], WeaponType.Aerial_Torpedo) && w != Utilities.GetIndexOfWeaponType(group[0], WeaponType.Bomb))
    {
        this.MultipleUnitsAttackTarget(group, target);
    }
    if (leader.unitAIAir != null)
    {
        leader.unitAIAir.modAutoStrike = true;
    }
    UnityEngine.Debug.Log("[AIRAI] " + leader.unitData.unitName + " flight (side " + leader.faction + ") attacks " + target.unitData.unitName);
}
```
3. **Compile.**

## Step 3 - EngagementAI.GetBestSeaTarget
1. Right-click **GetBestSeaTarget** (class **EngagementAI**) > **Edit Method (C#)...**
2. Look at its first line. It takes two things: a `Unit` and a `List<Unit>`. Note the names dnSpy gives them (for example `unit` and `targets`).
3. Click just after the opening `{` of the method, press Enter, and paste (if dnSpy uses other names, replace `unit` and `targets` with them):
```csharp
if (unit != null && unit.unitAir != null)
{
    Unit modPick = this.ModPickStrikeTarget(unit, targets);
    if (modPick != null)
    {
        return modPick;
    }
}
```
4. **Compile.**

## Step 4 - EngagementAI.AttackUnit
This marks a flight as "manual" whenever any attack order goes through the game, so your own orders are never changed. Step 2's `ModLaunchFlightAttack` marks it as auto again afterwards.
1. Right-click **AttackUnit** (class **EngagementAI**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste (use dnSpy's name for the method's `Unit`, if it is not `unit`):
```csharp
if (unit != null && unit.unitAIAir != null)
{
    unit.unitAIAir.modAutoStrike = false;
}
```
3. **Compile**, then **File > Save Module**.

## Step 5 - helpers in UnitAIAir
1. Right-click class **UnitAIAir** > **Edit Class (C#)...**
2. Find the line `public override void CheckNavigation()`. Click on the empty line just **above** it and paste:
```csharp
private void ModCheckAutoStrike()
{
    Unit me = this.parentUnit;
    if (me == null || me.isDestroyed || me.isParked || me.unitAir == null || me.unitData == null || EngagementAI.instance == null)
    {
        return;
    }
    if (EngagementManager.instance != null && EngagementManager.instance.startCombatButton != null && EngagementManager.instance.startCombatButton.activeSelf)
    {
        return;
    }
    if (this.followingUnit != null && !this.followingUnit.isDestroyed)
    {
        return;
    }
    UnitSubType st = me.unitData.unitSubtype;
    if (st != UnitSubType.Dive_Bomber && st != UnitSubType.Torpedo_Bomber && st != UnitSubType.Medium_Bomber && st != UnitSubType.Heavy_Bomber)
    {
        return;
    }
    if (me.unitAir.hasDroppedPayload || this.retreating)
    {
        return;
    }
    bool player = me.faction == Faction.Player;
    Unit target = this.focusedUnit;
    bool onShip = this.currentAIAction == AIAction.Attack_Unit && target != null && !target.isDestroyed && target.unitSea != null;
    if (onShip)
    {
        if (player && !this.modAutoStrike)
        {
            return;
        }
        if (!EngagementAI.instance.ModIsShipCrippled(target))
        {
            return;
        }
        if (this.currentManeuvre == Maneuvre.DiveBomb_Dive || this.aiAttack == AIAttack.Dive_Bomb)
        {
            return;
        }
        float d = Utilities.GetXZDistance(base.transform.position, target.transform.position);
        if (this.aiAttack == AIAttack.Aerial_Torpedo && d < 2500f * 0.1f)
        {
            return;
        }
        if (this.aiAttack == AIAttack.Level_Bomb && d < 4000f * 0.1f)
        {
            return;
        }
    }
    else
    {
        if (this.currentAIAction == AIAction.Attack_Unit && target != null && !target.isDestroyed)
        {
            return;
        }
        if (player)
        {
            if (this.currentAIAction != AIAction.Nothing)
            {
                return;
            }
            if (CombatInterface.instance != null && CombatInterface.instance.currentUnit == me)
            {
                return;
            }
        }
        else if (this.currentAIAction != AIAction.Nothing && this.currentAIAction != AIAction.Follow_Nav_Points)
        {
            return;
        }
    }
    List<Unit> ships = player ? EngagementAI.instance.otherSea : EngagementAI.instance.playerSea;
    Unit pick = EngagementAI.instance.ModPickStrikeTarget(me, ships);
    if (pick == null || pick == target)
    {
        return;
    }
    EngagementAI.instance.ModLaunchFlightAttack(me, pick);
}

private float ModAnvilSide(Unit target, Vector3 toMe)
{
    float sideNow = (Vector3.Dot(target.transform.right, toMe) >= 0f) ? 1f : -1f;
    List<Unit> air = (this.parentUnit.faction == Faction.Player) ? EngagementAI.instance.playerAir : EngagementAI.instance.otherAir;
    int flights = 0;
    int myIndex = 0;
    for (int i = 0; i < air.Count; i++)
    {
        Unit u = air[i];
        if (u == null || u.isDestroyed || u.unitAIAir == null || u.unitAI == null)
        {
            continue;
        }
        if (u.unitAI.followingUnit != null && !u.unitAI.followingUnit.isDestroyed)
        {
            continue;
        }
        if (u.unitAI.focusedUnit != target || u.unitAIAir.aiAttack != AIAttack.Aerial_Torpedo)
        {
            continue;
        }
        if (u == this.parentUnit)
        {
            myIndex = flights;
        }
        flights++;
    }
    if (flights <= 1)
    {
        return sideNow;
    }
    return (myIndex % 2 == 0) ? 1f : -1f;
}

private bool ModTorpedoSetup()
{
    Unit me = this.parentUnit;
    Unit target = this.focusedUnit;
    if (me == null || target == null || target.isDestroyed || target.unitSea == null || !target.detected)
    {
        return false;
    }
    if (me.faction == Faction.Player && !this.modAutoStrike)
    {
        return false;
    }
    if (this.followingUnit != null && !this.followingUnit.isDestroyed)
    {
        return false;
    }
    Vector3 tPos = target.transform.position;
    Vector3 tFwd = target.transform.forward;
    tFwd.y = 0f;
    if (tFwd.sqrMagnitude < 0.001f)
    {
        return false;
    }
    tFwd.Normalize();
    Vector3 toMe = base.transform.position - tPos;
    toMe.y = 0f;
    float dist = toMe.magnitude;
    if (dist < 1200f * 0.1f)
    {
        return false;
    }
    float side = this.ModAnvilSide(target, toMe);
    float sideNow = (Vector3.Dot(target.transform.right, toMe) >= 0f) ? 1f : -1f;
    float angle = Vector3.Angle(tFwd, toMe);
    if (sideNow == side && (dist < 2500f * 0.1f || (angle > 35f && angle < 100f)))
    {
        return false;
    }
    Vector3 setupPoint = tPos + Quaternion.Euler(0f, side * 60f, 0f) * tFwd * (3500f * 0.1f) + tFwd * target.currentActualSpeed * 30f;
    setupPoint.y = base.transform.position.y;
    this.parentUnit.wantedTurnRate = this.GetRequiredTurnRateFlat(setupPoint);
    this.parentUnit.wantedHeight = this.SetAircraftWantedHeight(this.attackHeight);
    return true;
}
```
3. **Compile.**

## Step 6 - UnitAIAir.CheckNavigation
1. Right-click **CheckNavigation** (class **UnitAIAir**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
this.ModCheckAutoStrike();
```
3. **Compile.**

## Step 7 - UnitAIAir.TorpedoApproach
1. Right-click **TorpedoApproach** (class **UnitAIAir**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (this.ModTorpedoSetup())
{
    return;
}
```
3. **Compile.**

## Step 8 - EngagementData.CreateUnitGroup (dive bomber start height)
1. Right-click **CreateUnitGroup** (class **EngagementData**) > **Edit Method (C#)...**
2. Find the line that sets the dive bombers' start height:
```csharp
... .y = Random.Range(88f, 100f);
```
3. Change only the two numbers: `88f` to `200f` and `100f` to `220f`.
4. **Compile**, then **File > Save Module**.

## Step 9 - dive bomber data files (no DLL)
Copy the four attached files into the game's `Override/unit/air/` folders, replacing the old ones:
- `dauntless_data.txt` into `dauntless/`
- `helldiver_data.txt` into `helldiver/`
- `val_data.txt` into `val/`
- `judy_data.txt` into `judy/`

The only change is on the first bomb line of each file. It switches on the aircraft's own attack settings (`"customAttack":true`) and sets:
- `attackHeight` 205-215 (2,050-2,150 m), the height they push over from
- `attackRange` 110-120 (1,100-1,200 m, Fix v2), how far short of the target they push over
- `diveDropHeight` 45-55 (450-550 m), the release height

Everything else is the game's normal value. The kamikaze Judy is unchanged.

## Testing
Watch the game log `WarOnTheSea_Data/output_log.txt`: every automatic attack writes a line starting `[AIRAI]`.
1. **Dive angle:** let an AI dive bomber strike reach your fleet, or send your own. They should arrive high (about 2 km), then roll into a steep 70°+ dive and pull out low.
2. **Auto attack:** launch a strike against an AI fleet and give the bombers no orders. Once enemy ships are spotted, each flight should pick a target on its own. Carriers come first, and the flights spread over the big ships.
3. **Manual still works:** order one flight onto a ship by hand. It should attack exactly as before, with no set-up turn and no switching.
4. **Hammer and anvil:** send 2 or more torpedo flights on auto at a carrier. They should swing out to opposite bows about 3.5 km out, then turn in from both sides.
5. **Break off:** when a ship is clearly sinking, flights that haven't started their run should switch to another ship.

## Tuning
- **ModPickStrikeTarget:**
  - The `value =` numbers: how much each ship type is wanted.
  - `16f`: how many planes on one ship before the next flight looks elsewhere. Bigger means more stacking on carriers.
  - `20000f`: how much distance matters, in metres (20 km halves a ship's score).
- **ModIsShipCrippled:** `0.5f` (damage), `0.3f` (flooding) and `1.5f` (metres per second, about 3 knots) set when a ship counts as doomed.
- **ModTorpedoSetup:**
  - `3500f`: the set-up distance in metres.
  - `60f`: angle off the bow.
  - `35f` / `100f`: the "already well placed" window.
  - `2500f`: commit distance in metres.
- **Data files:** a higher `attackHeight` or a lower `attackRange` gives a steeper dive. The `200f`/`220f` start height in Step 8 should stay within about 15 of `attackHeight`, or the bombers circle to climb first.
- **Units:** every battle distance in the code is written as metres × 0.1 (see `units.md`). The data-file values are in game units (1 unit = 10 m).

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.

---

## Fix: distance units in earlier changes (confirmed in game)
Battle distances in the game's code are in game units of **10 m**, not metres. Confirmed: F10 showed about 2,000 for ships the game's own ruler measured at 19,169 m. Speeds agree: `ConvertKnotToMetrePerSecond` multiplies by 0.1. Some earlier changes compared distances as if they were metres, so those checks work at 10 times the intended distance. To correct them, change only the numbers:

1. **UnitAISea.KeepStationInBattle:** `1200f` to `1200f * 0.1f`. AI ships currently break formation at 12 km instead of 1.2 km, so they drop formation as soon as the gunfight starts.
2. **UnitAISea.CoordinateTorpedoes:** `3000f` to `3000f * 0.1f`. Torpedo groups currently count ships up to 30 km apart instead of 3 km.
3. **UnitAISea.CheckNavigation** (the sub ambush code):
   - `2500f` to `2500f * 0.1f`. Subs currently spring the ambush as soon as any ship is within 25 km, so at once.
   - `600f` to `600f * 0.1f`. The return check currently needs your ships 6 km away.
4. **UnitAISea.FireTorpedoes:** `150f` to `150f * 0.1f`. This is the minimum target distance, meant to be 150 m.

5. **ObjectPoolManager.OnGUI** (the F10 developer view): find the line that measures the distance with `Vector3.Distance(` (it is inside the loop over `playerUnits`). Add ` * 10f` just before the `;` at the end of that line, so F10 shows real metres.

Compile and Save Module after each one.

---

## Fix v2 (after the first test)
The first test found:
- Dives were 80-90° (too steep).
- The torpedo flights didn't arrive together.
- The flight sent round to the far bow cut back across the target's bow, turned in too close and couldn't drop.

What changes:
1. **Dive angle:** the four data files now push over 1,100-1,200 m from the target (`"attackRange":[110,120]`, was 75-85). That should give about 70-75°. Copy the new files over the old ones again.
2. **Going round the bow:** a flight that is on the wrong side first flies to a point 4.5 km ahead of the target (25° off the bow on its own side). Only then does it swing to its set-up point at 3.5 km, 60° off the bow. It stays well clear of the ship while crossing over.
3. **Waiting for each other:** a flight that has reached its set-up position (on its own side, 35-100° off the bow, more than 2 km out) holds there until every other torpedo flight on that ship is in position too. Then they all turn in together. After 90 seconds of waiting it attacks anyway, in case a partner flight was shot down or delayed.
4. **No early turn-in:** a flight only counts as committed (inside 2.5 km) if it is also on its own side and pointing at the target. A flight that is crossing the bow no longer commits by accident.

### Step A - UnitAIAir: new field and new torpedo methods
1. Right-click class **UnitAIAir** > **Edit Class (C#)...**
2. Find the line `public bool modAutoStrike;`. Click at the end of it, press Enter, and paste:
```csharp
public float modTorpWaitStart;
```
3. Find the two old methods `private float ModAnvilSide(` and `private bool ModTorpedoSetup()`. dnSpy moved them near the end of the class. Select from the line `private float ModAnvilSide(` down to the closing `}` of `ModTorpedoSetup` (including any `// Token` comment lines between them), and delete it.
4. Paste this in the same place:
```csharp
private List<Unit> ModTorpFlights(Unit target)
{
    List<Unit> list = new List<Unit>();
    List<Unit> air = (this.parentUnit.faction == Faction.Player) ? EngagementAI.instance.playerAir : EngagementAI.instance.otherAir;
    for (int i = 0; i < air.Count; i++)
    {
        Unit u = air[i];
        if (u == null || u.isDestroyed || u.unitAIAir == null || u.unitAI == null)
        {
            continue;
        }
        if (u.unitAI.followingUnit != null && !u.unitAI.followingUnit.isDestroyed)
        {
            continue;
        }
        if (u.unitAI.focusedUnit != target || u.unitAIAir.aiAttack != AIAttack.Aerial_Torpedo)
        {
            continue;
        }
        if (u.faction == Faction.Player && !u.unitAIAir.modAutoStrike)
        {
            continue;
        }
        list.Add(u);
    }
    return list;
}

private float ModAnvilSide(Unit target, Vector3 toMe)
{
    float sideNow = (Vector3.Dot(target.transform.right, toMe) >= 0f) ? 1f : -1f;
    List<Unit> flights = this.ModTorpFlights(target);
    int myIndex = flights.IndexOf(this.parentUnit);
    if (flights.Count <= 1 || myIndex < 0)
    {
        return sideNow;
    }
    return (myIndex % 2 == 0) ? 1f : -1f;
}

private bool ModAllTorpFlightsReady(Unit target)
{
    List<Unit> flights = this.ModTorpFlights(target);
    if (flights.Count <= 1)
    {
        return true;
    }
    Vector3 tPos = target.transform.position;
    Vector3 tFwd = target.transform.forward;
    tFwd.y = 0f;
    tFwd.Normalize();
    for (int i = 0; i < flights.Count; i++)
    {
        Unit u = flights[i];
        if (u.unitAir == null || u.unitAir.hasDroppedPayload)
        {
            continue;
        }
        float side = (i % 2 == 0) ? 1f : -1f;
        Vector3 to = u.transform.position - tPos;
        to.y = 0f;
        float d = to.magnitude;
        float sideNow = (Vector3.Dot(target.transform.right, to) >= 0f) ? 1f : -1f;
        float angle = Vector3.Angle(tFwd, to);
        bool ready = sideNow == side && ((angle > 35f && angle < 100f && d < 5000f * 0.1f) || d < 2500f * 0.1f);
        if (!ready)
        {
            return false;
        }
    }
    return true;
}

private bool ModTorpedoSetup()
{
    Unit me = this.parentUnit;
    Unit target = this.focusedUnit;
    if (me == null || target == null || target.isDestroyed || target.unitSea == null || !target.detected)
    {
        return false;
    }
    if (me.faction == Faction.Player && !this.modAutoStrike)
    {
        return false;
    }
    if (this.followingUnit != null && !this.followingUnit.isDestroyed)
    {
        return false;
    }
    Vector3 tPos = target.transform.position;
    Vector3 tFwd = target.transform.forward;
    tFwd.y = 0f;
    if (tFwd.sqrMagnitude < 0.001f)
    {
        return false;
    }
    tFwd.Normalize();
    Vector3 toMe = base.transform.position - tPos;
    toMe.y = 0f;
    float dist = toMe.magnitude;
    if (dist < 1200f * 0.1f)
    {
        return false;
    }
    float side = this.ModAnvilSide(target, toMe);
    float sideNow = (Vector3.Dot(target.transform.right, toMe) >= 0f) ? 1f : -1f;
    float angle = Vector3.Angle(tFwd, toMe);
    Vector3 myFwd = base.transform.forward;
    myFwd.y = 0f;
    myFwd.Normalize();
    bool pointedIn = Vector3.Dot(myFwd, -toMe.normalized) > 0.8f;
    if (sideNow == side && dist < 2500f * 0.1f && pointedIn)
    {
        this.modTorpWaitStart = 0f;
        return false;
    }
    bool inPlace = sideNow == side && angle > 35f && angle < 100f && dist > 2000f * 0.1f;
    if (inPlace)
    {
        if (this.ModAllTorpFlightsReady(target))
        {
            return false;
        }
        if (this.modTorpWaitStart <= 0f)
        {
            this.modTorpWaitStart = Time.time;
        }
        if (Time.time - this.modTorpWaitStart > 90f)
        {
            return false;
        }
    }
    Vector3 setupDir;
    float setupRange;
    if (sideNow == side)
    {
        setupDir = Quaternion.Euler(0f, side * 60f, 0f) * tFwd;
        setupRange = 3500f * 0.1f;
    }
    else
    {
        setupDir = Quaternion.Euler(0f, side * 25f, 0f) * tFwd;
        setupRange = 4500f * 0.1f;
    }
    Vector3 setupPoint = tPos + setupDir * setupRange + tFwd * target.currentActualSpeed * 30f;
    setupPoint.y = base.transform.position.y;
    this.parentUnit.wantedTurnRate = this.GetRequiredTurnRateFlat(setupPoint);
    this.parentUnit.wantedHeight = this.SetAircraftWantedHeight(this.attackHeight);
    return true;
}
```
5. **Compile**, then **File > Save Module**. The new field and the new methods are in the same class, so you don't need to reopen dnSpy this time.

### Step B - data files
Copy the four updated files (`dauntless_data.txt`, `helldiver_data.txt`, `val_data.txt`, `judy_data.txt`) over the old ones in `Override/unit/air/`.

### Testing
1. Send 3 or more Kate or Avenger flights on auto at one ship. The far-side flight should swing wide round the bow while the near-side flights circle at their set-up point. Then all of them should turn in together from both bows.
2. Dive bombers should now dive at about 70-75°.

### Tuning
- `90f`: the longest a flight waits for its partners, in seconds.
- `4500f`, `25f`: how far ahead, and how far off the bow, the crossing point is.
- `0.8f`: how directly a flight must point at the target to count as committed (0.8 is about 37°).

---

## Final fix (tested, working)
- The hold signal (`ModReleaseTorpFlights`, with `modTorpWaitStart` = -1 once released) and the 300 s wait went in as given in the chat.
- Step 7 had accidentally emptied `UnitAIAir.TorpedoApproach`, so the torpedo run never happened. It was rebuilt from the original game code with `if (this.ModTorpedoSetup()) { return; }` as its first line.
- Tested: Kates went round, waited, turned in from both bows and hit with several torpedoes. All three cruisers turned to retreat.
- Dive angle at push-over 1,100-1,200 m: still to be checked.
