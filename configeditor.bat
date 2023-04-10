@echo off

:ui
cls
title UGC-Sniper Config Editor by noahrepublic#4323
echo option select
echo.
echo [1] - Configure Sniper (REQUIRED SET UP TO USE)

set /p o=
if %o%==1 goto config

pause

:config
cls
python3 ./scripts/config.py