# v0.28.18 hotfix (needs 0.28.18)

Do these in dnSpy, then Compile and File > Save Module at the end.

1. **2_UnitAIAir_ModTorpedoSetup_height.txt**: the fix for "fighters won't engage torpedo bombers". Change one line (steps are in the file).
2. **3_ModAirDamage.cs.txt**: explosions are rarer now, at most 38% (it was 65%). Right-click ModAirDamage, choose Edit Class, select everything, paste the whole file over it, then Compile.
3. **4_ModTorpStrike.cs.txt**: torpedo bombers now split first, and each half gathers off its own bow of the ship, about 3.5 km ahead and 3 km out. They wait until both sides are in place, then all swing in together for a hammer and anvil. A single flight still makes a wave attack. Right-click ModTorpStrike, choose Edit Class, select everything, paste the whole file over it, then Compile.
4. **5_NEW_ModShipHelm.cs.txt + 6_ModAAEvade_Apply.txt**: your ships respond to your controls again. The mod's AA evasion kept taking over your ships while planes were near and fought your sliders. Now it leaves alone the ship you have selected and any ship you are steering by hand. Ships on a route, in a formation or under an order still dodge. Do the steps in file 6.
5. **1_ModDogfight_HuntLimit.cs.txt**: optional. It wasn't the cause, but it does no harm.

In the log, look for `[HELM] ... AA evasion leaves her to you`, `[TORPSTRIKE] ... gather off its port bow` and `... swing in: hammer and anvil`.
