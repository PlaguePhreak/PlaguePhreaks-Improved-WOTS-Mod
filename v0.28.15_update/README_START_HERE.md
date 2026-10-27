# v0.28.15 update: fly your plane with the keys, plus a new flight panel

**Install 0.28.14 first** (v0.28.14_update). This update builds on its class ModAirPanel.

One new class and one new line. In dnSpy, after each step: **Compile**. When both are done: **File > Save Module**.

## 1. Add the new class ModAirStick
1. In dnSpy, right-click the `-` (empty namespace) folder of Assembly-CSharp > **Add Class (C#)**.
2. Delete everything in the window and paste all of `1_ModAirStick.cs.txt`. **Compile**.

## 2. ModAirPanel.Limits (starts the new panel)
1. Open the class `ModAirPanel`, find the method `Limits`, right-click > **Edit Method (C#)**.
2. Add this line as the **first line** inside the method (right after the opening `{`):
   `ModAirStick.Ensure();`
3. **Compile**.

Then **File > Save Module**. No stock game method is changed in this update.

## What changes in game (your own aircraft only)

**The flight panel** appears when you select one of your planes. Drag it by its title bar, and press **I** to hide or show it.
- Big numbers: speed, height, climb rate, heading.
- One line with the set speed, fuel %, seconds of gun fire left and damage %.
- What the plane is doing, for example "attacking A6M2 Zero, mode turn fight", "flying its route", "in formation" or "flown by you (stick)".
- Red warnings: STALL, OVERSPEED, FIRE, LOW FUEL, NO AMMO. Flaps and "bombs on" also show here.
- Speed buttons: **Cruise** (65% of top speed), **Climb** (best climb speed), **Combat** (corner speed, the best turn) and **Max**.
- Height buttons: **300 m, 1500 m, 3000 m, 6000 m, Ceiling** (never above the plane's ceiling).
- Without stick mode, the quick buttons move the game's own sliders, so they work like dragging the sliders. That also means they take the plane off a route or out of a formation, the same as a slider does.

**Stick mode:** press **G** (or click the Stick button) to fly the selected plane yourself. Press G again to give it back.
| Key (WASD key set) | What it does |
|---|---|
| **A / D** | Bank and turn while held. A tap gives a gentle turn, and holding for a second gives the hardest turn the plane can pull. Let go and it rolls level. |
| **W / S** | Nose up / nose down while held. Let go and the plane holds that height. |
| **R / E** | Throttle up / down (the same speed keys as before). |
| The game's stop key | Wings level and hold this height. |
| **Left Shift** | Guns fire while held. |
| **J / K / U** | Split-S, Immelmann, barrel roll (the mod's own moves). They only start where they can be flown, otherwise the panel says why. |

- The keys follow your own key bindings, so the numpad set works too.
- The flight model still applies. Climbing costs speed and diving gains it. The nose won't come up further than the engine or the speed can pay for. Below the stall speed the nose drops.
- The AI and the collision avoidance leave the plane alone while you fly it. Its wingmen keep following it.
- Stick mode ends by itself when you give the plane an order (attack, waypoint, follow), select another unit, the plane is shot down, or it leaves the battle. The panel shows why.
- The camera keys (arrows), the chase camera (C) and the weapon keys (1-0) work as before. In stick mode, holding a turn key no longer blocks the weapon keys.

## Knobs (top of ModAirStick)
- `InvertPitch = false`. Set it to `true` if you want W to push the nose down like a joystick.
- `StickKey`, `PanelKey`, `FireKey`, `SplitSKey`, `ImmelmannKey`, `RollKey`: change the keys here (for example `KeyCode.G`).
- `PitchStickRate = 30f`: how fast W / S move the nose (degrees per second).
- `BankStart = 0.4f` and `BankBuild = 1.0f`: how hard a tap of A / D turns, and how long a hold takes to reach the full turn.
- `ThrottleRate = 0.25f`: how fast R / E change the speed.
- `On = false` turns the panel and stick mode off.

## Check
1. Select one of your fighters in a battle. The flight panel shows up on the left.
2. Press G. The Stick button turns green and the log shows `[STICK] ... stick mode on`.
3. Hold A. The plane banks left and turns. Let go and it flies straight.
4. Hold W for two seconds, then let go. The plane climbs, then levels off and holds that height.
5. Press G again. The log shows `[STICK] ... stick mode off, G pressed`.

Known limit: clicking the panel while a ship or plane is right behind it on screen may also select that unit.
