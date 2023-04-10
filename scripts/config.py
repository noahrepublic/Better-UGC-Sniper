import requests as r
import json
import os

if not os.path.exists("./config.json"):
    print("Welcome to first time setup")
    config = {
        "ROBLOSECURITY": "",
        "cooldownPerLimited": 0.75,
    }

    roblosecurity = str(input("Enter ROBLOSECURITY: "))
    try:
        userId = r.get("https://users.roblox.com/v1/users/authenticated",
                    cookies={".ROBLOSECURITY": roblosecurity}).json()["id"]
    except:
        print("ROBLOSECURITY is invalid. Restart the script and try again.")
        input("Press enter to exit...")
        exit(0)

        
    config["ROBLOSECURITY"] = roblosecurity

    cooldownPerLimited = input("Enter cooldown per limited (Recommended: 0.75): ")
    config["cooldownPerLimited"] = float(cooldownPerLimited)

    jsonObject = json.dumps(config, indent=4)

    with open("./config.json", "w") as f:
        f.write(jsonObject)
        f.close()
    
    print("Config file created. Restart the script.")
    input("Press enter to exit...")
    exit(0)

with open("./config.json", "r") as f:
    print("Loading config...")
    config = json.load(f)
    f.close()

jsonObject = None
print("What would you like to edit? \n"
        "1. ROBLOSECURITY \n"
        "2. Cooldown per limited \n"
        "3. Exit")

choice = int(input(""))

if choice == 1:
    roblosecurity = str(input("Enter ROBLOSECURITY: "))
    try:
        userId = r.get("https://users.roblox.com/v1/users/authenticated",
                    cookies={".ROBLOSECURITY": roblosecurity}).json()["id"]
    except:
        print("ROBLOSECURITY is invalid. Restart the script and try again.")
        input("Press enter to exit...")
        exit(0)

    config["ROBLOSECURITY"] = roblosecurity
    jsonObject = json.dumps(config, indent=4)
elif choice == 2:
    cooldownPerLimited = input("Enter cooldown per limited (Recommended: 0.75): ")
    config["cooldownPerLimited"] = float(cooldownPerLimited)
    jsonObject = json.dumps(config, indent=4)  
elif choice == 3:
    exit(0)


if jsonObject:
    with open("./config.json", "w") as f:
        f.write(jsonObject)
        f.close()

    print("Config file updated. Restart the script.")
    input("Press enter to exit...")
    exit(0)
