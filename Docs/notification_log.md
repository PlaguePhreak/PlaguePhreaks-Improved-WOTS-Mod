# Notification log: bell button and Messages window (v0.26, untested)

What it does: a bell button on the campaign map, between the Book and Fuel buttons. Next to it a small badge shows how many notifications there are, and "N · U new" in orange when some are unread. Clicking the bell opens a **Messages** window: date, message, a **Show** button per row (jumps the map to where it happened), and tabs with counts (All, Contacts, Battles, Fleet, Air, Supply, Admiralty, Other). Keeps the newest 500 per campaign and saves them with the campaign.

Only real events are logged. The "you can't do that" pop-ups (no ship selected, not enough command points and so on) are left out.

Nothing was compiled against the real game. The code compiles against stand-in classes, so a typo-level problem is unlikely, but expect to report back what dnSpy says.

## Install steps (dnSpy), in this order

### Step 1 - the icon
Copy `Override/interface/images/map/bell.png` (from the repo) into the same folder of your game's Override folder, next to `guidebook.png`.

### Step 2 - save field in CampaignData
1. Open class **CampaignData** > right-click > **Edit Class (C#)...**
2. Find the line `public List<string> modSurvivors = new List<string>();` and add under it:
```csharp
	public List<string> notifyLog;
```
3. **Compile**.

### Step 3 - add the new class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Paste all of `Docs/notification_log_ModNotify.cs.txt`, click **Compile**.

### Step 4 - log every message (method ErrorPanel.SetErrorMessage)
1. Class **ErrorPanel** > method **SetErrorMessage** > right-click > **Edit Method (C#)...**
2. Add this as the very last line of the method (after the `if (audioReferences.ContainsKey(dictRef)) { ... }` block):
```csharp
	ModNotify.Add(dictRef, text, s0, s1, s2);
```
3. **Compile**.

### Step 5 - log the pop-up events (method CampaignEvent.CreateEvent)
1. Class **CampaignEvent** > method **CreateEvent** > **Edit Method (C#)...**
2. Find the line `contentText.text = ParseTags(contentText.text);` and add under it:
```csharp
	ModNotify.AddEvent(filepath, currentEventData.header, contentText.text);
```
3. **Compile**.

### Step 6 - save the log (method CampaignManager.GetCampaignDataString)
1. Class **CampaignManager** > method **GetCampaignDataString** > **Edit Method (C#)...**
2. Right above the last line (`return JsonUtility.ToJson(campaignData);`) add:
```csharp
	ModNotify.Save(campaignData);
```
3. **Compile**.

### Step 7 - the buttons (class ModTFOverlay, three methods)
1. Method **BuildButton** > **Edit Method (C#)...**
   - Change `MakeButton(transform, 1, ...` to `MakeButton(transform, 2, ...` (this moves Fuel down one slot; Book stays on top, the bell takes slot 1).
   - Under the line `ModGuide.Build(transform);` add `ModNotify.Build(transform);`
   - **Compile**.
2. Method **Update** > **Edit Method (C#)...**
   - Right after the block `if (buttonObject == null) { BuildButton(instance); }` add `ModNotify.Tick();`
   - **Compile**.
3. Method **OnDisable** > **Edit Method (C#)...**
   - Under `ModGuide.Remove();` add `ModNotify.Remove();`
   - **Compile**.

### Step 8
**File > Save Module**.

## What to check in the game
- Campaign map: Book, bell, Fuel in a column at the top left; badge beside the bell.
- Do something that makes a message (launch aircraft, deliver a ship): badge count goes up and turns orange.
- Click the bell: Messages window, newest on top, tabs with counts, unread rows brighter. Close with X. Badge goes back to the plain count.
- **Show** flies the map to the port or task force named in the message (greyed out when the message has no place).
- Save, quit, load: the log is still there.
- If the bell is a text "BELL" instead of an icon, bell.png is in the wrong folder.
- Problems show in the Unity log as lines starting `[NOTIFY]`.

## Notes
- `MaxEntries` (500) and `BellSlot` (1) are the two numbers at the top of the class.
- Battle results are not logged yet (they do not go through the campaign message panel); the Battles tab holds location fights and bombardments for now.
- Old saves load fine; they just start with an empty log.
- Tab choice by message: Contacts (spotted), Battles (locations, bombardment), Fleet (fuel, deliveries, cargo, crews, survivors), Air (launch, ready), Supply (low supplies, sea lanes, command points), Admiralty (pop-up events such as convoys), Other (any new message type the mod adds later).
