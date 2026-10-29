# dnSpy steps for 0.32.5 (only if you build it by hand; the DLL in this folder already has all of this)

Open the 0.32.1 `Assembly-CSharp.dll` in dnSpy (or 0.32.3: then only step 1 as Edit Class on ModGlobe, and step 3).

1. Right-click the `-` (top) namespace, **Add Class (C#)**. Delete what is there, paste all of `ModGlobe.cs.txt`, **Compile**. (It needs `ModGeo` from 0.32.1 to be there already.)
2. `CampaignManager` > `StartCampaign` > **Edit Method (C#)**. Just above the line `((MonoBehaviour)this).StartCoroutine(SetupCampaign(filepath));` add:
   `ModGlobe.Ensure(this);` and **Compile**.
3. `ModVersion`: change `Current` to "0.32.5" and the menu text to "Version 0.32.5 globe test 4".
4. **File > Save Module**.
5. Copy the `override` folder from this pack into `WarOnTheSea_Data\StreamingAssets\` (it holds `ModAssets\globe\earth.jpg`).
