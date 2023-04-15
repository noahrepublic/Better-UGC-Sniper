#!/bin/bash

python ./scripts/startcheck.py

while true; do
    clear
    echo "UGC-Sniper Config Editor by noahrepublic#4323"
    echo "THE NEW DISCORD: https://discord.gg/hw2ttCnmdz"
    echo "option select"
    echo
    echo "[1] - Configure Sniper"
    echo "[2] - Start Sniper"
    echo "[3] - Test Proxies (REQUIRES PROXIES IN PROXIES.TXT)"

    read -p "Enter your choice: " o

    case "$o" in
        1)
            clear
            python ./scripts/config.py
            read -p "Press enter to continue"
            ;;
        2)
            clear
            python ./scripts/update.py
            python ./main.py
            read -p "Press enter to continue"
            ;;
        3)
            clear
            python ./scripts/proxytest.py
            read -p "Press enter to continue"
            ;;
        *)
            read -p "Invalid option. Press enter to continue"
            ;;
    esac
done
