# Keybinds

What the game and the mod use, checked against `keybindsWASD.txt`, `keybindsNUMPAD.txt` and the keys hard-coded in the DLL (13 Oct 2026).

## Function keys
| Key | Battle | Campaign map |
|---|---|---|
| F1 | Help / menu dialog (hard-coded, `MenuSystem.Update`) | same |
| F2 | **Mod: next message log tab** (General / Hit log / Crew, v0.19.2) | - |
| F3 | **Mod: developer view** (testers only, was F10) | free |
| F4 | free | **Mod: create a survivor event** (testers only) |
| F5 | Menu | Campaign summary |
| F6 | Unit ID | Unit ID |
| F7 | Orders | Next task force |
| F8 | Damage control | Next location |
| F9 | Time compression | **Mod: reveal enemies** (testers only) |
| F10 | Hide UI | - |
| F11 | **Mod: minimap layers all on / off** (v0.19.5) | free |
| F12 | free in game (Steam screenshot) | same |

## Other keys
- **Battle:** Space pause, arrow keys camera, = / - zoom, T target mode, Y nearest air target, N navigation mode, H (WASD) or S (numpad) select mode, C chase cam, F follow cam, Esc cancel, Tab map, M map size, X lock map, B binoculars, ` freeze camera, . / , unit ID next / previous, Return classify, V (WASD) or A (numpad) attack, WASD or numpad rudder, depth and stop, R / E (WASD) or numpad + / - speed, 1-0 weapons, ; radar, ' active sonar, L message log.
- **Campaign map:** 1 next filtered task force, 2 next friendly location, 4 centre map, 5-0 map filters, , / . time back / forward, Space pause, / max time, \ ruler, P map marker.

## Mod keys with Ctrl (battle, v0.19.3)
- **Ctrl+A** all ships, **Ctrl+D** destroyers, **Ctrl+C** cruisers, **Ctrl+B** battleships and carriers.
- **Ctrl+Shift+1-5** save the ticked ships as a group, **Ctrl+1-5** select it again.
- The game doesn't use Ctrl in battle. While Ctrl is held, the game's own battle keys are ignored.

## Mod key changes
- **v0.17.9:** developer view moved from F10 to F3. F10 is the game's Hide UI key, so pressing it also hid the interface.
- **v0.18.4:** F4 on the campaign map creates a survivor event (testers only).
- **v0.19:** F2 shows or hides the hit log in battle (from v0.19.2 it steps through the General, Hit log and Crew tabs).
- **v0.19.3:** Ctrl selection and group keys in battle.
- **v0.19.5:** F11 switches all minimap layers on or off in battle.
- **Free for later mod features:** F11 on the campaign map.

## Install - developer view on F3
1. In class **EngagementManager**, right-click method **Update** > **Edit Method (C#)...**
2. Find (Ctrl+F) `KeyCode.F10` and change it to `KeyCode.F3`. There is only one.
3. Click **Compile**.
4. In class **ObjectPoolManager**, right-click method **OnGUI** > **Edit Method (C#)...**, find (Ctrl+F) `F10 to hide` and change it to `F3 to hide`. Click **Compile**, then **File > Save Module**.
5. Replace `modrules5.txt` in both campaigns (`override/language/english/campaign/campaign001/event/` and `campaign002/event/`) with the copies in `rules_popups_v1.8.3.zip`. The Testers! page now says F3.
