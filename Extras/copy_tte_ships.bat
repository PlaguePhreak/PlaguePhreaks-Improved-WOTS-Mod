@echo off
rem Copies the 23 TTE ship folders (3D models) into the game. Double-click to run.
set SRC=E:\mods\WOTS\custom mod\TTE Override\WarOnTheSea_Data\StreamingAssets\override\unit\sea
set DST=E:\SteamLibrary\steamapps\common\War on the Sea\WarOnTheSea_Data\StreamingAssets\override\unit\sea

xcopy "%SRC%\heywood" "%DST%\heywood\" /E /I /Y /Q
xcopy "%SRC%\president_jackson" "%DST%\president_jackson\" /E /I /Y /Q
xcopy "%SRC%\attack_transport" "%DST%\attack_transport\" /E /I /Y /Q
xcopy "%SRC%\hospital_ship" "%DST%\hospital_ship\" /E /I /Y /Q
xcopy "%SRC%\arcturus" "%DST%\arcturus\" /E /I /Y /Q
xcopy "%SRC%\harris" "%DST%\harris\" /E /I /Y /Q
xcopy "%SRC%\mount_hood" "%DST%\mount_hood\" /E /I /Y /Q
xcopy "%SRC%\patapsco" "%DST%\patapsco\" /E /I /Y /Q
xcopy "%SRC%\manley" "%DST%\manley\" /E /I /Y /Q
xcopy "%SRC%\mccawley" "%DST%\mccawley\" /E /I /Y /Q
xcopy "%SRC%\generic_maru" "%DST%\generic_maru\" /E /I /Y /Q
xcopy "%SRC%\type_1b" "%DST%\type_1b\" /E /I /Y /Q
xcopy "%SRC%\type_1c" "%DST%\type_1c\" /E /I /Y /Q
xcopy "%SRC%\type_1k" "%DST%\type_1k\" /E /I /Y /Q
xcopy "%SRC%\type_2tl" "%DST%\type_2tl\" /E /I /Y /Q
xcopy "%SRC%\type_3a" "%DST%\type_3a\" /E /I /Y /Q
xcopy "%SRC%\type_a_merchant" "%DST%\type_a_merchant\" /E /I /Y /Q
xcopy "%SRC%\ural_maru" "%DST%\ural_maru\" /E /I /Y /Q
xcopy "%SRC%\akita_maru" "%DST%\akita_maru\" /E /I /Y /Q
xcopy "%SRC%\kasagisan_maru" "%DST%\kasagisan_maru\" /E /I /Y /Q
xcopy "%SRC%\taihosan_maru" "%DST%\taihosan_maru\" /E /I /Y /Q
xcopy "%SRC%\hakushika_maru" "%DST%\hakushika_maru\" /E /I /Y /Q
xcopy "%SRC%\aratama_maru" "%DST%\aratama_maru\" /E /I /Y /Q

echo Done. Now copy the Override folder (see INSTALL.txt step 2).
pause
