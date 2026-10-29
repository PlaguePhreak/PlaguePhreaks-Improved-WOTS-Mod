# 0.31.1: every ship can blow up and break apart

Built on 0.31 with the changelog box fix (`v0.31_changelog_box`), so it has everything up to 0.31 plus that fix.

## What changed

- **Every ship uses the magazine blast system.** That includes battleships, battlecruisers, carriers, heavy and light cruisers, destroyers, escorts and merchants. Only submarines are left out. Each blast is still sized by the shells left in that magazine (a full battleship magazine is the biggest), and it still starts small, bursts and then smokes.
- **A loaded magazine now destroys any ship.** Before, only a blast that covered a lot of the damage grid sank the ship, so big ships with armoured magazines almost always survived one. Now a magazine that is at least a quarter full is fatal for any ship, whatever its size or armour. The old rule (a blast over 9 squares) still applies too. A nearly empty magazine (under 5%) is still never fatal.
- **It breaks apart.** A fatal blast breaks the ship in two, or blows off the bow or stern, most of the time. That's 75% of the time for a nearly empty magazine, rising to 95% for a full one. Otherwise it plunges fast. A battleship whose fore magazine goes up can lose its whole front end.
- **A torpedo break-back is still for destroyers only.** When a torpedo breaks a ship's back, only destroyers and escorts break in two and set off both magazines, as before.
- Only destroyers and escorts have the hand-made torn break pieces. Bigger ships are cut cleanly where the magazine blew.

## Install

1. Close the game.
2. Go to `E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\Managed\`.
3. Rename `Assembly-CSharp.dll` to `Assembly-CSharp_0.31.dll` as a backup.
4. Copy `Assembly-CSharp.dll` from this folder into `Managed\`.
5. Start the game. The menu should say **Version 0.31.1**.

## In the log

`[SINK] <ship> magazine explosion at square ...: the blast covers 7 squares, magazine 80% full: LETHAL, the ship is lost (at least 25% full)`

## Knobs (top of ModSinking)

| Knob | Default | What it does |
|---|---|---|
| `LethalFull` | 0.25 | A magazine at least this full destroys any ship |
| `LethalCells` | 9 | The old rule: a blast over this many squares is fatal too |
| `EmptyMagazine` | 0.05 | Below this, never fatal |
| `LethalSplitChance` / `FullSplitChance` | 0.75 / 0.95 | Chance a fatal blast breaks the ship (empty / full magazine) |
| `BreakMerchants`, `BreakCruisers`, `BreakOthers` | false | Torpedo break-back for other ship types (off: destroyers only) |

## Checks

- Only the `ModSinking` class changed.
- This replaces the first 0.31.1 DLL I sent (md5 b405c961), which wrongly let torpedoes break the back of every ship.
- `ModVersion.Build` is the changelog box fix, unchanged apart from its text. The version is now 0.31.1, and the changelog gained the line "A magazine blast can tear any ship apart, even a battleship".
- The DLL verifier lists the same warnings as 0.31.
- Not tested in the game. Big ships are cut at runtime with no torn-edge kit, so watch the first battleship or carrier break.

## dnSpy

1. `ModSinking`: Edit Class with `dnspy_reference\ModSinking.cs.txt`.
2. `ModVersion`: change the strings as listed in `dnspy_reference\ModVersion_strings.txt`.
