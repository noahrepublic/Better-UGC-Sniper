@echo off

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
python3 %cd%/scripts/config.py
goto ui


:start
cls
python3 pip install -r requirements.txt
python3 main.py
goto ui