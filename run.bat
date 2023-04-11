@echo off

python ./scripts/startcheck.py

:ui
cls
title UGC-Sniper Config Editor by noahrepublic#4323
echo option select
echo.
echo [1] - Configure Sniper
echo [2] - Start Sniper

set /p o=
if %o%==1 goto config
if %o%==2 goto start

pause

:config
cls
python ./scripts/config.py
goto ui


:start
cls
python ./scripts/update.py
python ./main.py
pause
goto ui