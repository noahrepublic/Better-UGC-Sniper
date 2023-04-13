#!/bin/sh

python ./scripts/startcheck.py

clear

echo "option select"
echo "-------------"
echo "[1] - Configure Sniper"
echo "[2] - Start Sniper"
echo "[3] - Test Proxies (REQUIRES PROXIES IN PROXIES.TXT)"

read input

case $input in
    1)
        clear
        python3 ./scripts/config.py
        ;;
    2)
        clear
        py ./scripts/update.py
        python3 ./main.py
        ;;
    3)
        clear
        python3 ./scripts/proxytest.py
        ;;
esac
