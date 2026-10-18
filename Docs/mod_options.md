# Mod Options and the new pause menu (v0.27)

**Status: written, not compiled, not tested.** Back up the DLL first. Do the steps in order. If a compile error appears, send me the exact text.

**What you get**
- Pause menu: Resume, Save Game, **Load Game**, **Settings**, **Mod Options**, Back to Main Menu, Quit Game.
- A **Mod Options** button on the main menu too (this is where you change the locked settings before starting a campaign).
- A Mod Options window with 18 on/off switches. They are saved in `modoptions.txt` (next to `options.txt`). Everything defaults to ON.
- The first 6 are **locked in a campaign** (crew system, veteran crews, rescue missions, supply upkeep, supply convoy, survivors event). The campaign remembers the values it started with (saved inside the campaign save), and the window says they are locked because changing them can break a save.
- The last 7 switches stop that kind of notification going into the notification log. The pop-up still appears.

**Left out on purpose**
- "Extra starting task forces" is not a switch. The game's original starting-force method is already replaced by our version and I have no copy of the original to fall back on. Tell me if you want a version that only turns off some of the groups.
- Battle features, hit log and message log tabs, faster ship buying and the hold-to-add aircraft buttons stay always on, as you decided.

**Things to know**
- Crew system OFF also switches off rescue of survivors in battle (it needs the crew records).
- Group numbers on the roster and the minimap switches fully apply from the next battle.
- Load Game goes back to the main menu first, then opens the load list (it asks "are you sure" using the existing confirmation panel). Unsaved progress is lost, same as Back to Main Menu.

## Step 1 - save-file field (CampaignData)
1. Right-click class **CampaignData** > **Edit Class (C#)...**
2. Directly under the line `public string campaignID;` add:
```csharp
public string modLocked = "";
```
3. Compile, **File > Save Module**. **Close dnSpy, reopen it and reopen the DLL.**

## Step 2 - the new class
1. Right-click **Assembly-CSharp** > **Add Class...**
2. Paste all of `Docs/mod_options_ModOptions.cs.txt`. Compile.

## Step 3 - pause menu (class PauseMenu)
1. Method **OpenPauseMenu** > **Edit Method (C#)...**. Add as the very last line (after `((Component)this).gameObject.SetActive(true);`):
```csharp
ModOptions.BuildPauseButtons(this);
```
Compile.
2. Method **Resume** > **Edit Method (C#)...**. Add as the very first line:
```csharp
ModOptions.Close();
```
Compile.
3. Method **OnConfirmation** > **Edit Method (C#)...**. Replace the whole method with:
```csharp
public void OnConfirmation()
{
	if (confirmAction == 0)
	{
		Time.timeScale = 1f;
		Map.instance.ClearMap();
		Utilities.ReloadMain();
	}
	else if (confirmAction == 1)
	{
		MenuSystem.instance.QuitGame();
	}
	else if (confirmAction == 2)
	{
		ModOptions.LoadFromPause();
	}
}
```
Compile.

## Step 4 - main menu (class MenuSystem)
1. Method **BackToMain** > **Edit Method (C#)...**. Add as the very first line:
```csharp
if (ModOptions.OnBack())
{
	return;
}
```
Compile.
2. Method **Start** > **Edit Method (C#)...**. Add as the very last line:
```csharp
ModOptions.AfterMenuStart();
```
Compile.

## Step 5 - the switches (one small edit per place)
For each method: right-click > **Edit Method (C#)...**, add the lines as the **first lines** of the method, Compile.

**Crew system** (class **ModCrew**). Same two lines in each of these methods: **OnBattleStart**, **ApplyBattleLosses**, **PortTopUp**, **OnShipSunk**, **RescueTick**:
```csharp
if (!ModOptions.Crew)
{
	return;
}
```
**Rescue missions** (class **ModCrew**, method **CampaignRescueCheck**):
```csharp
if (!ModOptions.Rescue)
{
	return;
}
```
**Survivors event** (class **ModCrew**, method **CreateSurvivorEvent**):
```csharp
if (!ModOptions.Survivors)
{
	return;
}
```
**Veteran crews**
1. Class **MobileMapObject**, method **AwardVeterancy**. Find the line `ModCrew.ApplyBattleLosses(mmo);` and add under it:
```csharp
if (!ModOptions.Veteran)
{
	return;
}
```
2. Class **Utilities**, method **SetSeaEfficiency**. Find the line `num = MobileMapObject.GetVeteranBonus(unit.unitInstanceName);` and change it to:
```csharp
if (ModOptions.Veteran)
{
	num = MobileMapObject.GetVeteranBonus(unit.unitInstanceName);
}
```
**Supply upkeep** (class **ModSupply**): first line of **Daily** and of **AIResupply**:
```csharp
if (!ModOptions.Supply)
{
	return;
}
```
and first line of **DaysLeft** (it returns a string):
```csharp
if (!ModOptions.Supply)
{
	return string.Empty;
}
```
**Supply convoy** (class **ModConvoy**): first line of **Daily** and of **Tick**:
```csharp
if (!ModOptions.Convoy)
{
	return;
}
```
**Minimap upgrades** (class **ModMinimap**, method **Tick**), first lines:
```csharp
for (int b = 0; b < buttons.Length; b++)
{
	if (buttons[b] != null && buttons[b].gameObject.activeSelf != ModOptions.Minimap)
	{
		buttons[b].gameObject.SetActive(ModOptions.Minimap);
	}
}
if (!ModOptions.Minimap)
{
	ClearAll();
	return;
}
```
**Group numbers** (class **ModGroups**, method **UpdateBadges**), first lines:
```csharp
if (!ModOptions.Badges)
{
	return;
}
```
**Task force overlay** (class **ModTFOverlay**, method **Rebuild**), first lines:
```csharp
if (!ModOptions.TFOverlay)
{
	Clear();
	return;
}
```
**Notification log** (class **ModNotify**)
1. Method **Add**: find `int cat = Category(key);` and `if (cat == 0) { return; }` and add right after that block:
```csharp
if (!ModOptions.LogCategory(cat))
{
	return;
}
```
2. Method **AddEvent**: find `Push(6, header + ": " + content, null, null, null);` and put above it:
```csharp
if (!ModOptions.LogCategory(6))
{
	return;
}
```
3. Method **Tick**: first lines inside the `try`:
```csharp
if (bellObj != null && bellObj.activeSelf != ModOptions.Notify)
{
	bellObj.SetActive(ModOptions.Notify);
}
if (!ModOptions.Notify && panel != null)
{
	panel.SetActive(false);
}
```
**Darker nights** (class **SensorManager**, method **GetVisibilityModifier**)
1. Change `num3 = 1.8f;` to `num3 = (ModOptions.DarkNights ? 1.8f : 1.2f);`
2. Change `num3 = Mathf.Max(num3, Mathf.Min(1.3f + 0.15f * (float)num4, 1.8f));` to:
```csharp
num3 = Mathf.Max(num3, ModOptions.DarkNights ? Mathf.Min(1.3f + 0.15f * (float)num4, 1.8f) : Mathf.Min(1.15f + 0.1f * (float)num4, 1.6f));
```
(The night visibility table and the 10 km night encounter range switch themselves in `ModOptions.ApplyNights`.)

Finally **File > Save Module**.

## Test
1. Main menu: a **Mod Options** button should appear under (or near) Options. Open it: 3 groups, 18 rows, click a row to flip ON/OFF. Close with X. Restart the game: the values are kept (`modoptions.txt`).
2. Start a campaign, press Esc: seven buttons. **Mod Options**: the first 6 rows are greyed with "(locked)", the others still change.
3. Pause menu **Settings** opens the game's options screen; Save/Back returns to the pause menu, not the main menu.
4. Pause menu **Load Game**: confirmation, then the main menu opens straight on the load list.
5. Turn off a log category (for example Air), unpause, let an air event happen: no new line in the bell window.
6. Turn off Darker nights and start a night battle: ships are seen from further away.
7. Look in `output_log.txt` for lines starting `[MODOPT]` if anything fails and send them to me.

## Things most likely to need a fix (cannot be checked without the game)
- Button spacing on the pause menu and main menu (I copy an existing button and space them evenly).
- The button text may be replaced by the game's own label code on open (then the new buttons would read "SAVE GAME"). Tell me and I will change how the label is set.
- Settings screen from the pause menu (it shares the main menu's screens, so the picture behind it may look odd).
- Load Game on a battle (not campaign) save.
