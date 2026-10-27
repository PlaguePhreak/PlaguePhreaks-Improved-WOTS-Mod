# v0.28.16 update: chase camera on the tail of the aircraft

One new class and one new line. In dnSpy, after each step: **Compile**. When both are done: **File > Save Module**.

## 1. Add the new class ModChaseCam
1. In dnSpy, right-click the `-` (empty namespace) folder of Assembly-CSharp > **Add Class (C#)**.
2. Delete everything in the window and paste all of `1_ModChaseCam.cs.txt`. **Compile**.

## 2. ThirdPersonCamera.LateUpdate
1. Open the class `ThirdPersonCamera`, find the method `LateUpdate`, right-click > **Edit Method (C#)**.
2. At the top of the method are these lines:
   ```
   if (!LoadScreen.loadComplete)
   {
       return;
   }
   ```
3. Add this new line **just below** them:
   `if (ModChaseCam.Apply(this)) { return; }`
4. **Compile**.

Then **File > Save Module**.

## What changes in game (aircraft only, ships keep the old chase camera)
- With the chase camera on (C), the camera sits behind the tail and climbs, dives, turns and banks with the plane. The horizon tilts in a turn.
- The movement is smoothed a little, so it doesn't shake. The plane always stays in the middle of the picture, also at time compression.
- Zoom (mouse wheel, = and -) still sets how far behind the camera is.
- Hold the right mouse button to look around. Let go and the camera swings back behind the tail.
- The arrow keys and freeze camera (`) switch chase mode off, as before.

## Knobs (top of ModChaseCam)
- `RollWithPlane = true`. Set it to `false` to keep the horizon level (the camera still follows climbs, dives and turns).
- `FollowRate = 6f`. Higher makes the camera stiffer, lower makes it lazier.
- `HeightShare = 0.18f`. How high above the tail the camera sits (0 = straight behind).
- `On = false` brings back the game's own chase camera.

## Check
1. Select one of your planes and press C.
2. Press G and fly a climbing turn. The camera stays behind the tail and tilts with the wings.
3. Press C again, or an arrow key. The camera goes back to the normal free view without a jump.
