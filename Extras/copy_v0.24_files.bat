@echo off
rem v0.24: copies the 3D models of the new ships (v0.24.1) and aircraft (v0.24.2) into the game. Double-click to run.
rem Ships and aircraft must be installed together: the new carriers carry the new aircraft.
rem This takes a few minutes and about 2 GB of disk space.

set RAM=E:\mods\WOTS\custom mod\Ram_s Unit Catalog Release\override
set TTE=E:\mods\WOTS\custom mod\Extra files\TTE Override\WarOnTheSea_Data\StreamingAssets\override
set DST=E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets\override

echo Copying RamZ ships (v0.24.1)...
xcopy "%RAM%\unit\sea\agano44" "%DST%\unit\sea\agano44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\agano_kai45" "%DST%\unit\sea\agano_kai45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\akizuki44" "%DST%\unit\sea\akizuki44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\alaska45" "%DST%\unit\sea\alaska45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\aoba44" "%DST%\unit\sea\aoba44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\atlanta42" "%DST%\unit\sea\atlanta42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\atlanta44" "%DST%\unit\sea\atlanta44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\austin47" "%DST%\unit\sea\austin47\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\ayanami42" "%DST%\unit\sea\ayanami42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\balao44" "%DST%\unit\sea\balao44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\balaoguppy" "%DST%\unit\sea\balaoguppy\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\baltimore43" "%DST%\unit\sea\baltimore43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\battle45" "%DST%\unit\sea\battle45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\benson42" "%DST%\unit\sea\benson42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\chidori42" "%DST%\unit\sea\chidori42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\cleveland42" "%DST%\unit\sea\cleveland42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\colossus45" "%DST%\unit\sea\colossus45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\constellation43" "%DST%\unit\sea\constellation43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\county42" "%DST%\unit\sea\county42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\desmoines48" "%DST%\unit\sea\desmoines48\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\enterprise44" "%DST%\unit\sea\enterprise44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\essex44" "%DST%\unit\sea\essex44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\fletcher42" "%DST%\unit\sea\fletcher42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\fletcher43" "%DST%\unit\sea\fletcher43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\fuso44" "%DST%\unit\sea\fuso44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\gato43" "%DST%\unit\sea\gato43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\gearing45" "%DST%\unit\sea\gearing45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\hakuryu45" "%DST%\unit\sea\hakuryu45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\hornet42" "%DST%\unit\sea\hornet42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\independence43" "%DST%\unit\sea\independence43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\iowa44" "%DST%\unit\sea\iowa44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\isuzu44" "%DST%\unit\sea\isuzu44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\kagero43" "%DST%\unit\sea\kagero43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\kitakaze45" "%DST%\unit\sea\kitakaze45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\kongo44" "%DST%\unit\sea\kongo44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\leander44" "%DST%\unit\sea\leander44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\lexington41" "%DST%\unit\sea\lexington41\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\mahan42" "%DST%\unit\sea\mahan42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\maya44" "%DST%\unit\sea\maya44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\midway45" "%DST%\unit\sea\midway45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\midway46" "%DST%\unit\sea\midway46\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\missouri45" "%DST%\unit\sea\missouri45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\mogami44" "%DST%\unit\sea\mogami44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\mutsuki42" "%DST%\unit\sea\mutsuki42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\myoko44" "%DST%\unit\sea\myoko44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\n_class44" "%DST%\unit\sea\n_class44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\nebraska44" "%DST%\unit\sea\nebraska44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\nevada44" "%DST%\unit\sea\nevada44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\neworleans45" "%DST%\unit\sea\neworleans45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\northcarolina43" "%DST%\unit\sea\northcarolina43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\oakland43" "%DST%\unit\sea\oakland43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\oakland45" "%DST%\unit\sea\oakland45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\perth42" "%DST%\unit\sea\perth42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\porter42" "%DST%\unit\sea\porter42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\porter44" "%DST%\unit\sea\porter44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\portland42" "%DST%\unit\sea\portland42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\puertorico45" "%DST%\unit\sea\puertorico45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\ranger42" "%DST%\unit\sea\ranger42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\rudderow44" "%DST%\unit\sea\rudderow44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\saipan" "%DST%\unit\sea\saipan\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\salmon44" "%DST%\unit\sea\salmon44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\sangamon" "%DST%\unit\sea\sangamon\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\saratoga42" "%DST%\unit\sea\saratoga42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\saratoga44" "%DST%\unit\sea\saratoga44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\satsuma45" "%DST%\unit\sea\satsuma45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\sekiryu45" "%DST%\unit\sea\sekiryu45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\shimakaze44" "%DST%\unit\sea\shimakaze44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\shiratsuyu42" "%DST%\unit\sea\shiratsuyu42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\shokaku42" "%DST%\unit\sea\shokaku42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\somers42" "%DST%\unit\sea\somers42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\southdakota43" "%DST%\unit\sea\southdakota43\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\stlouis42" "%DST%\unit\sea\stlouis42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\sumner44" "%DST%\unit\sea\sumner44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\tacoma44" "%DST%\unit\sea\tacoma44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\taiho44" "%DST%\unit\sea\taiho44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\tone44" "%DST%\unit\sea\tone44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\tuv_class44" "%DST%\unit\sea\tuv_class44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\typeb3" "%DST%\unit\sea\typeb3\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\wichita44" "%DST%\unit\sea\wichita44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\worcester47" "%DST%\unit\sea\worcester47\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\yamato45" "%DST%\unit\sea\yamato45\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\yorktown42" "%DST%\unit\sea\yorktown42\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\yugumo44" "%DST%\unit\sea\yugumo44\" /E /I /Y /Q
xcopy "%RAM%\unit\sea\zuikaku44" "%DST%\unit\sea\zuikaku44\" /E /I /Y /Q
echo Copying TTE ships (v0.24.1)...
xcopy "%TTE%\unit\sea\akitsu_maru" "%DST%\unit\sea\akitsu_maru\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\arunta" "%DST%\unit\sea\arunta\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\bogue" "%DST%\unit\sea\bogue\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\chitose" "%DST%\unit\sea\chitose\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\clemson" "%DST%\unit\sea\clemson\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\colorado" "%DST%\unit\sea\colorado\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\hiyo" "%DST%\unit\sea\hiyo\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\hosho" "%DST%\unit\sea\hosho\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\kamikawa_maru" "%DST%\unit\sea\kamikawa_maru\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\kitakami" "%DST%\unit\sea\kitakami\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\new_mexico" "%DST%\unit\sea\new_mexico\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\nisshin" "%DST%\unit\sea\nisshin\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\omaha" "%DST%\unit\sea\omaha\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\pennsylvania" "%DST%\unit\sea\pennsylvania\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\ryuho" "%DST%\unit\sea\ryuho\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\taiyo" "%DST%\unit\sea\taiyo\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\tennessee" "%DST%\unit\sea\tennessee\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\type_a1" "%DST%\unit\sea\type_a1\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\type_c" "%DST%\unit\sea\type_c\" /E /I /Y /Q
xcopy "%TTE%\unit\sea\yubari" "%DST%\unit\sea\yubari\" /E /I /Y /Q
echo Copying aircraft (v0.24.2)...
xcopy "%RAM%\unit\air\a26c45" "%DST%\unit\air\a26c45\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a2d1" "%DST%\unit\air\a2d1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m2mod21" "%DST%\unit\air\a6m2mod21\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m3mod22a" "%DST%\unit\air\a6m3mod22a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m3mod32" "%DST%\unit\air\a6m3mod32\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m5mod52a" "%DST%\unit\air\a6m5mod52a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m5mod52c" "%DST%\unit\air\a6m5mod52c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a6m6c" "%DST%\unit\air\a6m6c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a7m1" "%DST%\unit\air\a7m1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a7m2" "%DST%\unit\air\a7m2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\a8k1" "%DST%\unit\air\a8k1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ad2" "%DST%\unit\air\ad2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\am1" "%DST%\unit\air\am1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\au1" "%DST%\unit\air\au1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b17g" "%DST%\unit\air\b17g\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b25j20" "%DST%\unit\air\b25j20\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b26b" "%DST%\unit\air\b26b\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b29a" "%DST%\unit\air\b29a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b5n2" "%DST%\unit\air\b5n2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b6n2a" "%DST%\unit\air\b6n2a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\b7a2" "%DST%\unit\air\b7a2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\beaufightermkvic" "%DST%\unit\air\beaufightermkvic\" /E /I /Y /Q
xcopy "%RAM%\unit\air\btd1" "%DST%\unit\air\btd1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\corsairmkii" "%DST%\unit\air\corsairmkii\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d3a1" "%DST%\unit\air\d3a1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d3a2" "%DST%\unit\air\d3a2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d4y1c" "%DST%\unit\air\d4y1c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d4y2" "%DST%\unit\air\d4y2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d4y3a" "%DST%\unit\air\d4y3a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\d4y5" "%DST%\unit\air\d4y5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\e13a1" "%DST%\unit\air\e13a1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f2a3" "%DST%\unit\air\f2a3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f2g1_corsair" "%DST%\unit\air\f2g1_corsair\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f2g2_corsair" "%DST%\unit\air\f2g2_corsair\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4f3" "%DST%\unit\air\f4f3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4f4" "%DST%\unit\air\f4f4\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4u1a" "%DST%\unit\air\f4u1a\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4u1d" "%DST%\unit\air\f4u1d\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4u2" "%DST%\unit\air\f4u2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4u4_corsair" "%DST%\unit\air\f4u4_corsair\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f4u4b_corsair" "%DST%\unit\air\f4u4b_corsair\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f6f3" "%DST%\unit\air\f6f3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f6f5" "%DST%\unit\air\f6f5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f6f5n" "%DST%\unit\air\f6f5n\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f7f3" "%DST%\unit\air\f7f3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\f8f1b" "%DST%\unit\air\f8f1b\" /E /I /Y /Q
xcopy "%RAM%\unit\air\firebrandmk4" "%DST%\unit\air\firebrandmk4\" /E /I /Y /Q
xcopy "%RAM%\unit\air\fm2" "%DST%\unit\air\fm2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\g8n1" "%DST%\unit\air\g8n1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\j5n2" "%DST%\unit\air\j5n2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\j6k1" "%DST%\unit\air\j6k1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\j7w1" "%DST%\unit\air\j7w1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki100" "%DST%\unit\air\ki100\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki67otsu" "%DST%\unit\air\ki67otsu\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki83" "%DST%\unit\air\ki83\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki84otsu" "%DST%\unit\air\ki84otsu\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki87" "%DST%\unit\air\ki87\" /E /I /Y /Q
xcopy "%RAM%\unit\air\ki94ii" "%DST%\unit\air\ki94ii\" /E /I /Y /Q
xcopy "%RAM%\unit\air\n1k1" "%DST%\unit\air\n1k1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\n1k1ja" "%DST%\unit\air\n1k1ja\" /E /I /Y /Q
xcopy "%RAM%\unit\air\n1k2ja" "%DST%\unit\air\n1k2ja\" /E /I /Y /Q
xcopy "%RAM%\unit\air\os2u3" "%DST%\unit\air\os2u3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p1y1" "%DST%\unit\air\p1y1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p38g10" "%DST%\unit\air\p38g10\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p38j15" "%DST%\unit\air\p38j15\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p38k" "%DST%\unit\air\p38k\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p38l5" "%DST%\unit\air\p38l5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p39d" "%DST%\unit\air\p39d\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p40f" "%DST%\unit\air\p40f\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p43a1" "%DST%\unit\air\p43a1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p47d28" "%DST%\unit\air\p47d28\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p47m1" "%DST%\unit\air\p47m1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p47n15" "%DST%\unit\air\p47n15\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p51d20" "%DST%\unit\air\p51d20\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p51h5" "%DST%\unit\air\p51h5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p61c" "%DST%\unit\air\p61c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p63c5" "%DST%\unit\air\p63c5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\p82b" "%DST%\unit\air\p82b\" /E /I /Y /Q
xcopy "%RAM%\unit\air\pb4y" "%DST%\unit\air\pb4y\" /E /I /Y /Q
xcopy "%RAM%\unit\air\pbj1j" "%DST%\unit\air\pbj1j\" /E /I /Y /Q
xcopy "%RAM%\unit\air\pv2d" "%DST%\unit\air\pv2d\" /E /I /Y /Q
xcopy "%RAM%\unit\air\r2y2" "%DST%\unit\air\r2y2\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sb2c1c" "%DST%\unit\air\sb2c1c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sb2c4" "%DST%\unit\air\sb2c4\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sb2u3" "%DST%\unit\air\sb2u3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sbd3" "%DST%\unit\air\sbd3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sbd5" "%DST%\unit\air\sbd5\" /E /I /Y /Q
xcopy "%RAM%\unit\air\sbd6" "%DST%\unit\air\sbd6\" /E /I /Y /Q
xcopy "%RAM%\unit\air\soc1" "%DST%\unit\air\soc1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\tbd1" "%DST%\unit\air\tbd1\" /E /I /Y /Q
xcopy "%RAM%\unit\air\tbf1c" "%DST%\unit\air\tbf1c\" /E /I /Y /Q
xcopy "%RAM%\unit\air\tbm3" "%DST%\unit\air\tbm3\" /E /I /Y /Q
xcopy "%RAM%\unit\air\walrusmk1" "%DST%\unit\air\walrusmk1\" /E /I /Y /Q

echo Copying TTE aircraft (v0.24.2)...
xcopy "%TTE%\unit\air\p400" "%DST%\unit\air\p400\" /E /I /Y /Q
xcopy "%TTE%\unit\air\p38e" "%DST%\unit\air\p38e\" /E /I /Y /Q
xcopy "%TTE%\unit\air\j2f" "%DST%\unit\air\j2f\" /E /I /Y /Q
xcopy "%TTE%\unit\air\pby" "%DST%\unit\air\pby\" /E /I /Y /Q
xcopy "%TTE%\unit\air\pbm" "%DST%\unit\air\pbm\" /E /I /Y /Q
xcopy "%TTE%\unit\air\a20" "%DST%\unit\air\a20\" /E /I /Y /Q
xcopy "%TTE%\unit\air\b24" "%DST%\unit\air\b24\" /E /I /Y /Q
xcopy "%TTE%\unit\air\b25j" "%DST%\unit\air\b25j\" /E /I /Y /Q
xcopy "%TTE%\unit\air\p40" "%DST%\unit\air\p40\" /E /I /Y /Q
xcopy "%TTE%\unit\air\beaufighter" "%DST%\unit\air\beaufighter\" /E /I /Y /Q
xcopy "%TTE%\unit\air\beaufort" "%DST%\unit\air\beaufort\" /E /I /Y /Q
xcopy "%TTE%\unit\air\sunderland" "%DST%\unit\air\sunderland\" /E /I /Y /Q
xcopy "%TTE%\unit\air\a5m4" "%DST%\unit\air\a5m4\" /E /I /Y /Q
xcopy "%TTE%\unit\air\a6m2n" "%DST%\unit\air\a6m2n\" /E /I /Y /Q
xcopy "%TTE%\unit\air\ki43" "%DST%\unit\air\ki43\" /E /I /Y /Q
xcopy "%TTE%\unit\air\ki45" "%DST%\unit\air\ki45\" /E /I /Y /Q
xcopy "%TTE%\unit\air\ki49" "%DST%\unit\air\ki49\" /E /I /Y /Q
xcopy "%TTE%\unit\air\j1n1" "%DST%\unit\air\j1n1\" /E /I /Y /Q
xcopy "%TTE%\unit\air\e14y" "%DST%\unit\air\e14y\" /E /I /Y /Q
xcopy "%TTE%\unit\air\h6k" "%DST%\unit\air\h6k\" /E /I /Y /Q
xcopy "%TTE%\unit\air\emily" "%DST%\unit\air\emily\" /E /I /Y /Q
xcopy "%TTE%\unit\air\g3m" "%DST%\unit\air\g3m\" /E /I /Y /Q
rem TTE bomb and torpedo files: only copied when the game does not already have that file
for %%%%f in ("%%TTE%%\ammunition\*.txt") do if not exist "%%DST%%\ammunition\%%%%~nxf" copy "%%%%f" "%%DST%%\ammunition\" >nul

echo Copying RamZ ammunition (v0.24.2)...
if exist "%RAM%\ammunition" xcopy "%RAM%\ammunition" "%DST%\ammunition\" /E /I /Y /Q
if not exist "%DST%\materials\ammunition_original.txt" copy "%DST%\materials\ammunition.txt" "%DST%\materials\ammunition_original.txt"
copy /Y "%RAM%\materials\ammunition.txt" "%DST%\materials\ammunition.txt"

echo Done. Now copy the Override folder from this repo (see Docs/new_ships_v0.24.md, step 2).
pause
