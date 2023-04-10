@echo off

:ui
cls
title UGC-Sniper Config Editor by noahrepublic#4323
echo option select
echo.
echo [1] - Configure Sniper (REQUIRED SET UP TO USE)
echo [2] - Start Sniper (PYTHON REQUIRED)

set /p o=
if %o%==1 goto config
if %o%==2 goto start

pause

:config
cls
python3 ./scripts/config.py

:start
cls
python3 pip install -r requirements.txt
python3 main.py