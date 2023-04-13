@echo off

python ./scripts/startcheck.py

:ui
cls
title UGC-Sniper Config Editor by noahrepublic#4323
echo THE NEW DISCORD: https://discord.gg/hw2ttCnmdz
echo option select
echo.
echo [1] - Configure Sniper
echo [2] - Start Sniper
echo [3] - Test Proxies (REQUIRES PROXIES IN PROXIES.TXT)

set /p o=
if %o%==1 goto config
if %o%==2 goto start
if %o%==3 goto test

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

:test
cls
python ./scripts/proxytest.py
pause
goto ui