# Fog of War toggle (F9) – dnSpy patch guide

**What it does:** Press **F9** on the campaign map to show every enemy task force, whether you have spotted it or not. Press **F9** again to go back to normal fog of war.

**How it works:** Enemy icons on the map are just sprites whose transparency depends on how recently you spotted them. This patch forces those icons to full opacity while the toggle is on. It is visual only: the AI is not affected, no "contact spotted" alerts fire, and the game doesn't think you've spotted anything.

> Untested. I can't run the game. If dnSpy shows a compile error, send me a screenshot of the error list and the code window.

**Before you start:** close the game and make sure your `Assembly-CSharp.dll.bak` exists. Copy your current patched DLL somewhere safe too.

As before, **Save Module and reopen dnSpy after Edit 1**, since dnSpy needs to see the new field before the other edits will compile. Add code only; don't delete the existing lines.

---

## Edit 1 – add one field to CampaignData

1. Right-click **CampaignData** → **Edit Class (C#)...**
2. Click at the end of the line `public List<int> orderDaysRemaining = new List<int>();` (the one you added earlier), press Enter, and paste:

```csharp
public bool revealAllContacts;
```

3. **Compile**.
4. **File → Save Module...** → OK. Close dnSpy, reopen it, and open `Assembly-CSharp.dll` from the Managed folder again.

(Because this lives in the campaign data, the on/off state is saved with each campaign. A new campaign starts with fog of war on.)

---

## Edit 2 – make icons opaque when the toggle is on

1. In **CampaignInterface**, right-click **SetContactColor** → **Edit Method (C#)...**
2. Find this part:

```csharp
if (forceZero)
{
    a = 0;
}
```

3. Click at the end of that closing `}`, press Enter, and paste:

```csharp
else if (CampaignManager.instance.campaignData.revealAllContacts)
{
    a = 255;
}
```

4. **Compile.**

---

## Edit 3 – the F9 key

1. In **CampaignInterface**, right-click **Update** → **Edit Method (C#)...**
2. Find the line `this.CheckCampaignInput();`. Click at the end of it, press Enter, and paste:

```csharp
if (Input.GetKeyDown(KeyCode.F9))
{
    CampaignData fogData = CampaignManager.instance.campaignData;
    fogData.revealAllContacts = !fogData.revealAllContacts;
    List<GameObjectAnimator> fogOthers = CampaignManager.instance.otherMobile;
    for (int f = 0; f < fogOthers.Count; f++)
    {
        if (fogOthers[f] != null && fogOthers[f].mobileMapObject != null && fogOthers[f].mobileMapObject.unitPrefabs.Count > 0)
        {
            this.SetContactColor(fogOthers[f].mobileMapObject, false);
        }
    }
}
```

3. **Compile.**

---

## Edit 4 – keep newly appearing enemy groups visible

New enemy groups spawn hidden. This refreshes the icons every 5 in-game minutes while the toggle is on.

1. In **CampaignManager**, right-click **Check5Min** → **Edit Method (C#)...**
2. Click right after the opening `{` of the method, press Enter, and paste:

```csharp
if (this.campaignData.revealAllContacts)
{
    for (int v = 0; v < this.otherMobile.Count; v++)
    {
        if (this.otherMobile[v] != null && this.otherMobile[v].mobileMapObject != null && this.otherMobile[v].mobileMapObject.unitPrefabs.Count > 0)
        {
            CampaignInterface.instance.SetContactColor(this.otherMobile[v].mobileMapObject, false);
        }
    }
}
```

3. **Compile.**
4. **File → Save Module...** → OK.

---

## How to test

1. Start or load a campaign. At first you should see only the enemies you've spotted.
2. Press **F9**. Every enemy task force on the map should appear. Press **F9** again and the unspotted ones should vanish.
3. Let time run a while with the toggle on, and check that newly launched enemy groups show up within a few in-game minutes.

## Things to expect

- Revealed groups that you haven't actually spotted may show less detail when you click them, because the game has no intel on them (this matters if "vague campaign intel" is on in your settings).
- Enemy bases and locations are unaffected. This only reveals mobile task forces.
- If F9 is already used by another program on your PC (such as a screen recorder), tell me and I'll pick a different key.

## To undo

Restore your `.bak` DLL.
