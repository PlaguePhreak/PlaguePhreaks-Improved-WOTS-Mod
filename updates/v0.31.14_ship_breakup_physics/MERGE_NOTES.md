# 0.31.14 ship break-up + physics sinking: for merging

- Built on 0.31.13 animated fire (md5 5b0cac40). DLL md5 dc4bd5151007a8b4200c6d0e149d141b.
- Classes changed: `ModSinking` (new buoyancy model: Piece fields, MakeWholePiece, MakeSplitPiece, BuildCells, Fracs, Flow, Step, TickWreck, TickPiece, StartWreck section; Key/Hog no longer called, old fields kept by the patcher) and ModVersion strings only. ModWreckArt is compiled in but identical (LoadPng body kept). No stock method changed, no hooks.
- IL compared with 0.31.13: only ModSinking (11 methods) and ModVersion.Build / BuildPanel strings differ. ilverify error list unchanged.
- Patcher: `KEEP=ModWreckArt.LoadPng NOHOOKS=1 STRINGS=build_tools/strings14.txt dotnet Patcher.dll base.dll patch.dll <Managed> out.dll`, patch.dll = csc of build_tools/WA4.cs + MS4.cs against the base DLL.
- Files: `mod_wreck/` = new `<model>_{fore,mid,aft}.brk` for every non-sub, non-destroyer ship (made by ship2mesh.py + break2.py, see build_tools/run1.sh) and a new `units.txt` (old destroyer lines + every new ship; kamikawa_maru->kamogawa_maru, kuma->nagara, taiyo->zuiho). The 0.29 destroyer kits, burnt.png, puff.png and the 0.31.13 fire_side/fire_top PNGs stay as they are in the player's mod_wreck folder.
- Physics test harness: build_tools/shim.cs (Vector3/Quaternion stand-ins) + test.cs / pose.cs, built by build.sh from the real ModSinking source.
- Later ModSinking changes must start from dnspy_reference/ModSinking.cs.txt.
