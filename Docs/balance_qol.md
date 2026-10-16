# Balance and QOL (v0.17.5)

## 1. Fires can't spread while a damage control party is fighting them

**What was wrong (found in the code)**
- Every few seconds, each burning compartment can set its neighbours alight (`DamageableSea.SpreadFires`).
- A damage control party working on a fire only stopped that fire from burning its own compartment. The fire could still spread to the compartments around it.
- The game only cut the spread chance when the compartment being spread *into* had a party in it (`config.txt` `fireSpreadReducedByParty`). It never checked the compartment the fire was spreading *from*.

**What changes**
- A fire with a damage control party on it no longer spreads.
- Fires with nobody fighting them spread exactly as before, including the "bigger fires spread faster" rule.

Back up the DLL first.

### Step 1 - DamageableSea.SpreadFires
1. Right-click **SpreadFires** (class **DamageableSea**) > **Edit Method (C#)...**
2. Near the top is a loop over the burning compartments. Inside it is the line we changed in the combat damage package:
```csharp
this.ApplyDamageToCell(cellVariable, num, 0f, false, true, true);
```
   That line sits inside a small block that starts with:
```csharp
if (!cellVariable.isDestroyed && !cellVariable.isUnderRepair)
```
3. Click just after the closing `}` of that small block (the `}` straight after the `ApplyDamageToCell` line), press Enter, and paste:
```csharp
if (cellVariable.isUnderRepair)
{
    continue;
}
```
   dnSpy may call the variable something other than `cellVariable`. Use whatever name the `ApplyDamageToCell(` line uses.
4. **Compile**, then **File > Save Module**.

If you can't find the spot, send me a screenshot of the top of SpreadFires.

### Testing
1. In a battle, wait for a ship to catch fire and send a damage control party to it.
2. While the party is working, the fire shouldn't spread to the compartments around it.
3. A fire left alone should still spread as before.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.


## 2. Hold + or - to change the number of aircraft to launch

**What it does**
- In the Create New Air panel, a normal click on **+** or **-** still adds or removes one aircraft.
- **Hold** the button and, after a short pause (0.4 s), the count keeps changing by 20 aircraft a second until you let go.
- Holding **+** stops at the most you can launch: the aircraft available, or the strike limit (`maxInFlight`), whichever is smaller. You won't get the "too many aircraft" message.
- Holding **-** stops at 0.
- The first time a hold starts repeating, it writes an `[AIRHOLD]` line to `output_log.txt`.

**How it works (found in the code)**
- The + and - buttons are made in `CampaignInterface.GenerateAirStrikeIcons` and call `NumberToLaunchUp` / `NumberToLaunchDown`.
- Unity buttons only react to a full click. So this adds a small new class, `ModAirHold`, that watches for the mouse being held over one of those buttons and repeats the click for you.

Back up the DLL first. Do the steps in order.

### Step 1 - new class ModAirHold
1. In the Assembly Explorer, right-click the **Assembly-CSharp** module (or the `{ }` / `-` namespace node under it, where classes like CampaignInterface are listed) > **Add Class (C#)...**
2. Select everything in the window and paste this over it:
```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

public class ModAirHold : MonoBehaviour
{
    private void Update()
    {
        CampaignInterface ci = CampaignInterface.instance;
        if (ci == null || ci.availableAircraft == null || ci.numberToLaunch == null || ci.maxToLaunch == null || EventSystem.current == null)
        {
            this.holdIndex = -1;
            return;
        }
        if (Input.GetMouseButtonDown(0))
        {
            this.holdIndex = this.FindHeldButton(ci);
            this.nextStep = Time.unscaledTime + 0.4f;
            this.logged = false;
        }
        if (this.holdIndex < 0)
        {
            return;
        }
        if (!Input.GetMouseButton(0) || this.holdIndex >= ci.numberToLaunch.Count || this.holdIndex >= ci.maxToLaunch.Count)
        {
            this.holdIndex = -1;
            return;
        }
        if (Time.unscaledTime < this.nextStep)
        {
            return;
        }
        this.nextStep = Time.unscaledTime + 0.05f;
        int current = ci.numberToLaunch[this.holdIndex];
        if (this.holdUp)
        {
            int cap = Mathf.Min(ci.maxToLaunch[this.holdIndex], Config.instance.maxInFlight);
            if (current < cap - 1)
            {
                ci.NumberToLaunchUp(this.holdIndex);
            }
        }
        else if (current > 1)
        {
            ci.NumberToLaunchDown(this.holdIndex);
        }
        if (!this.logged)
        {
            this.logged = true;
            UnityEngine.Debug.Log("[AIRHOLD] holding " + (this.holdUp ? "+" : "-") + " on aircraft type " + this.holdIndex);
        }
    }

    private int FindHeldButton(CampaignInterface ci)
    {
        PointerEventData pointer = new PointerEventData(EventSystem.current);
        pointer.position = Input.mousePosition;
        this.hits.Clear();
        EventSystem.current.RaycastAll(pointer, this.hits);
        for (int h = 0; h < this.hits.Count; h++)
        {
            if (this.hits[h].gameObject == null)
            {
                continue;
            }
            Transform hitTransform = this.hits[h].gameObject.transform;
            for (int i = 0; i < ci.availableAircraft.Length; i++)
            {
                GameObject icon = ci.availableAircraft[i];
                if (icon == null || !icon.activeInHierarchy || icon.transform.childCount < 2)
                {
                    continue;
                }
                Transform holder = icon.transform.GetChild(1);
                if (holder.childCount < 1)
                {
                    continue;
                }
                holder = holder.GetChild(0);
                if (holder.childCount < 2)
                {
                    continue;
                }
                if (hitTransform.IsChildOf(holder.GetChild(1)))
                {
                    this.holdUp = true;
                    return i;
                }
                if (hitTransform.IsChildOf(holder.GetChild(0)))
                {
                    this.holdUp = false;
                    return i;
                }
            }
        }
        return -1;
    }

    private int holdIndex = -1;

    private bool holdUp;

    private float nextStep;

    private bool logged;

    private List<RaycastResult> hits = new List<RaycastResult>();
}
```
3. **Compile**, then **File > Save Module**.
4. **Close dnSpy and reopen it**, then reopen the DLL. The next step uses the new class.

If you can't find **Add Class (C#)...**, send me a screenshot of the right-click menu.

### Step 2 - CampaignInterface.OpenCreateAirStrike
1. Right-click **OpenCreateAirStrike** (class **CampaignInterface**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (base.gameObject.GetComponent<ModAirHold>() == null)
{
    base.gameObject.AddComponent<ModAirHold>();
}
```
3. **Compile**, then **File > Save Module**.

### Testing
1. Open Create New Air at a carrier or airfield.
2. Click + once: the count goes up by 1, as before.
3. Hold +: after a moment it counts up quickly and stops at the maximum.
4. Hold -: it counts down to 0.

### Tuning (in ModAirHold)
- `0.4f`: how long to hold before it starts repeating.
- `0.05f`: time between steps (smaller = faster).

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.


## 3. Fighters spread out instead of ganging up on one plane

**What was wrong (found in the test log)**
- In the US strike test, 16 Zeros on CAP shared only 3-4 bombers between them. One Dauntless was picked as a target 48 times by 9 different Zeros.
- Each extra attacker already made a target less attractive (`0.75` per attacker in `EngagementAI.GetBestDogfightTarget`). But a nearby target with 4 attackers still beat one 4 km further away.

**What changes**
- Once 2 fighters are on a target, it becomes 8.5 times less attractive. A third fighter only joins if every other target is much further away.
- With few targets, the spare fighters now go for the escorts or the bombers that already dropped, instead of queuing behind each other.

### Step 1 - EngagementAI.GetBestDogfightTarget
1. Right-click **GetBestDogfightTarget** (class **EngagementAI**) > **Edit Method (C#)...**
2. Near the end, find the line with `0.75f *`. dnSpy may have renamed the variables, so it will look something like:
```csharp
num *= 1f + 0.75f * (float)num5;
```
3. Change it to this, using the same two names your line uses (here `num` and `num5`):
```csharp
num *= 1f + 0.75f * (float)num5 + ((num5 >= 2) ? 6f : 0f);
```
4. **Compile**, then **File > Save Module**.

## 4. Carrier CAP follows its carrier on the campaign map

**What was wrong (found in the code)**
- When an AI carrier group asks for fighter cover, its carrier launches fighters over **its current position** (`CampaignAI.OnRequestAirCover`).
- The fighters then circle that fixed point. If the carrier moves on, the CAP is left behind, and arrives late or not at all when the carrier is attacked.
- AI fighter cover from an **airfield** already follows the fleet it protects, through the game's escort system (`MobileMapObject.escortingThisGOA`). Carrier cover never set it.

**What changes**
- AI carrier CAP now escorts its own carrier, so it moves with the task force on the map and is overhead when a strike arrives.
- It still lands when its endurance runs out or air operations end for the day, as before.

### Step 1 - CampaignAI.OnRequestAirCover
1. Right-click **OnRequestAirCover** (class **CampaignAI**) > **Edit Method (C#)...**
2. In the carrier part of the method there is exactly one line that calls `this.GroupAIAirStrike(`. It looks like:
```csharp
this.GroupAIAirStrike(list);
```
3. A few lines above it is the line that launches the fighters. It looks like:
```csharp
list.Add(this.CreateAIMobileAir(mobileMapObject.gameObjectAnimator, ...
```
   Note the two names it uses. Here they are `list` (the list of air groups) and `mobileMapObject` (the carrier's task force). dnSpy may show different names.
4. Click just **before** the `this.GroupAIAirStrike(` line, press Enter, and paste this. Replace `list` and `mobileMapObject` with your names if they're different:
```csharp
for (int capIndex = 0; capIndex < list.Count; capIndex++)
{
    if (list[capIndex] != null && list[capIndex].mobileMapObject != null)
    {
        list[capIndex].mobileMapObject.escortingThisGOA = mobileMapObject.gameObjectAnimator;
        UnityEngine.Debug.Log("[CAPFOLLOW] fighter cover now follows " + mobileMapObject.mobileName);
    }
}
```
5. **Compile**, then **File > Save Module**.

If you're not sure which names to use, send me a screenshot of the lines around `GroupAIAirStrike`.

### Testing (sections 3 and 4)
1. Put an AI carrier group on the move and let it launch CAP. On the campaign map, the CAP icon should stay over the moving task force. `output_log.txt` shows a `[CAPFOLLOW]` line.
2. Send a strike at it. The CAP should be overhead when the strike arrives.
3. In the battle, the `[FIGHTER]` lines should show no more than about 2 Zeros picking the same bomber at once, unless there are very few targets left.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.


## 5. Torpedo bombers keep going when they lose sight of their target

**What was wrong (found in the test log and the code)**
- In the overcast test (34% visibility), 4 Avenger flights were heading for Shokaku about 15.5 km out. All 4 went silent at the same moment and flew off without dropping.
- They had lost sight of Shokaku. My torpedo set-up (`UnitAIAir.ModTorpedoSetup`) stops working when the target isn't spotted. The game's own torpedo run (`TorpedoApproach`) then only updates its aim point while the target is spotted. It kept flying to an old aim point that had never been set during the set-up, so the planes flew away.
- The 2 Fuso flights kept sight of their target and attacked normally.

**What changes**
- While a torpedo flight can see its target and is more than 2.5 km away, it remembers where the ship is.
- If it loses sight of the target, it flies to the last place it saw the ship.
- When it gets there and still can't see it, it circles the spot, about 2 km out, so it's ready if the ship turns up again.
- Flights on auto (and the AI's flights) switch to another ship they can see, if there is one. Flights you ordered by hand keep their target and circle until it's spotted again.
- Once a flight is inside 2.5 km and committed to its run, nothing changes. It drops as before.
- Writes `[TORP] ... lost sight of ...` lines to `output_log.txt`.

### Step 1 - UnitAIAir.ModTorpedoSetup
1. Right-click **ModTorpedoSetup** (class **UnitAIAir**) > **Edit Method (C#)...**
2. Click just after the opening `{` of the method, press Enter, and paste:
```csharp
if (this.parentUnit != null && this.focusedUnit != null && !this.focusedUnit.isDestroyed && this.focusedUnit.unitSea != null && (this.followingUnit == null || this.followingUnit.isDestroyed))
{
    float lostShipDist = Utilities.GetXZDistance(base.transform.position, this.focusedUnit.transform.position);
    if (this.focusedUnit.detected)
    {
        if (lostShipDist > 2500f * 0.1f)
        {
            this.attackPosition = this.focusedUnit.transform.position;
        }
    }
    else if (lostShipDist > 2500f * 0.1f)
    {
        float lostDist = Utilities.GetXZDistance(base.transform.position, this.attackPosition);
        bool lostAuto = this.parentUnit.faction != Faction.Player || this.modAutoStrike;
        if (lostAuto && lostDist < 1500f * 0.1f)
        {
            List<Unit> lostShips = (this.parentUnit.faction == Faction.Player) ? EngagementAI.instance.otherSea : EngagementAI.instance.playerSea;
            Unit lostPick = EngagementAI.instance.ModPickStrikeTarget(this.parentUnit, lostShips);
            if (lostPick != null && lostPick != this.focusedUnit && lostPick.detected)
            {
                UnityEngine.Debug.Log("[TORP] " + this.parentUnit.unitData.unitName + " id " + this.parentUnit.GetInstanceID() + " lost sight of " + this.focusedUnit.unitData.unitName + ", switching to " + lostPick.unitData.unitName);
                EngagementAI.instance.ModLaunchFlightAttack(this.parentUnit, lostPick);
                return true;
            }
        }
        Vector3 lostAim = this.attackPosition;
        if (lostDist < 1500f * 0.1f)
        {
            lostAim = this.attackPosition + Quaternion.Euler(0f, Time.time * 6f, 0f) * Vector3.forward * (2000f * 0.1f);
        }
        lostAim.y = base.transform.position.y;
        this.parentUnit.wantedTurnRate = this.GetRequiredTurnRateFlat(lostAim);
        this.parentUnit.wantedHeight = this.SetAircraftWantedHeight(this.attackHeight);
        if (Mathf.Repeat(Time.time, 5f) < 0.1f)
        {
            UnityEngine.Debug.Log("[TORP] " + this.parentUnit.unitData.unitName + " id " + this.parentUnit.GetInstanceID() + " lost sight of " + this.focusedUnit.unitData.unitName + ", heading for last seen position, " + (lostDist * 10f).ToString("F0") + "m away");
        }
        return true;
    }
}
```
3. **Compile**, then **File > Save Module**.

### Testing
1. Send torpedo bombers at a carrier group in bad weather or at long range, so they lose sight of it on the way in.
2. They should keep flying towards it, or circle where it was last seen, instead of flying off.
3. In `output_log.txt`, look for `[TORP] ... lost sight of ..., heading for last seen position` and, for auto flights, `... switching to ...`.

Note: I could not compile or run this. If Compile shows errors, send a screenshot of the error list.
