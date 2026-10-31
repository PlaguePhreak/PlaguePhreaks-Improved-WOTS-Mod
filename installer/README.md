# WOTS Mod Installer

Player-facing installer for the mod (Windows, .NET Framework 4.8, one exe with Mono.Cecil embedded).

- Finds War on the Sea through the Steam registry keys and `libraryfolders.vdf` (Browse button as fallback).
- Backs up `Assembly-CSharp.dll` and every override file it replaces into `War on the Sea\WOTS Mod Backup\`;
  "Restore original files" puts everything back and deletes files the mod added.
- Works next to other DLL mods: it does a three-way merge (original 1.09a DLL / mod DLL / the player's DLL).
  Every class, field and method the mod added or changed versus the original is copied into the player's DLL;
  the rest of the player's DLL (other mods' changes) is kept. Methods changed by both are listed and the player chooses.
  If the player's DLL is the untouched original, the mod DLL is copied as it is.
- The original DLL is not shipped: `app/stock.fp` is a fingerprint of it (hash per method body; floats hashed as bits so
  .NET Framework/Mono and .NET Core agree). Regenerate only if the game updates: `MergeCli fp <original dll> stock.fp "War on the Sea x.y"`.

Release layout: `WOTS Mod Installer.exe`, `Mod Files\Assembly-CSharp.dll`, `Mod Files\mod_info.txt`, optional `Mod Files\override\...`.

Build: `dotnet build app/WotsInstaller.csproj -c Release` (works on Linux; needs Mono.Cecil 0.11.6 from NuGet).

Tests run 31 Oct 2026: original+hotfix 3 and original+0.32.19 merges are member-for-member identical to the real builds
(ilverify error lists identical); a synthetic second mod survives the merge and the shared method is reported;
5 install/update/restore scenarios pass (`tests/InstallerTests.cs`); the exe runs under Mono WinForms and gives the same merge.

## Online updates (added 31 Oct 2026)
`app/Updater.cs` reads https://api.github.com/repos/PlaguePhreak/PlaguePhreaks-Improved-WOTS-Mod/releases.
Newest non-draft release with an `Assembly-CSharp.dll` asset wins. Override files = newest `override.zip` at or before it,
plus every later `override_update.zip`, oldest first. Downloads are cached in `%LOCALAPPDATA%\WOTS Mod Installer`.
`update_source.txt` next to the exe (`repo=` / `api=`) points it elsewhere for tests.
Version guard: `ModVersion.Current` of the game DLL vs the new DLL; an older build over a newer one needs an explicit Yes (default No).
