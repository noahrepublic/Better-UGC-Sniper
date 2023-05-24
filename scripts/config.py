import requests as r
import json
import os

if not os.path.exists("./config.json"):
    print("Welcome to first time setup")
    config = {
        "Accounts": [],
        "Items": [],
        "cooldownPerCheck": 1,
        "discordWebhook": "",
    }

    roblosecurity = str(input("Enter Primary ROBLOSECURITY: "))
    try:
        userId = r.get("https://users.roblox.com/v1/users/authenticated",
                    cookies={".ROBLOSECURITY": roblosecurity}).json()["id"]
    except:
        print("ROBLOSECURITY is invalid. Restart the script and try again.")
        exit(0)


    friendlyName = str(input("Enter friendly name: "))

    config["Accounts"].append({
        "ROBLOSECURITY": roblosecurity,
        "userId": userId,
        "nickName": friendlyName
    })

    cooldownPerLimited = input("Enter cooldown per limited (Recommended: 0.75): ")
    config["cooldownPerLimited"] = float(cooldownPerLimited)

    discordWebhook = str(input("Enter Discord webhook (Leave blank for none): "))
    config["discordWebhook"] = discordWebhook


    jsonObject = json.dumps(config, indent=4)

    with open("./config.json", "w") as f:
        f.write(jsonObject)
        f.close()
    
    print("Config file created. Restart the script.")
    exit(0)

with open("./config.json", "r") as f:
    print("Loading config...")
    config = json.load(f)
    f.close()

jsonObject = None
print("What would you like to edit? \n"
        "1. Edit limited IDs \n"
        "2. Edit accounts \n"
        "3. Add account \n"
        "4. Remove account \n"
        "5. Cooldown \n"
        "6. Discord webhook \n"
        "7. Exit")

choice = int(input(""))
if choice == 1:
    print("What would you like to do? \n")

    print("1. Add limited ID")
    print("2. Remove limited ID")
    print("3. Clear limited IDs")
    print("4. Exit")

    choice = int(input(""))
    if choice == 1:
        limitedId = int(input("Enter limited ID: "))
        config["Items"].append({"id": limitedId})
        jsonObject = json.dumps(config, indent=4)
    elif choice == 2:
        print("What limited ID would you like to remove? \n")
        for i, item in enumerate(config["Items"]):
            print(f"{i + 1}. {item['id']}")
        choice = int(input(""))
        if choice > len(config["Items"]) + 1:
            print("Invalid choice.")
            exit(0)
        config["Items"].pop(choice - 1)
        jsonObject = json.dumps(config, indent=4)
    elif choice == 3:
        config["Items"] = []
        jsonObject = json.dumps(config, indent=4)
    else:
        exit(0)

elif choice == 2:
    print("What account would you like to edit? \n")
    for i, account in enumerate(config["Accounts"]):
        if i == 0:
            print(f"{i + 1}. {account['userId']} {account['nickName']} (Primary)")
        else:
            print(f"{i + 1}. {account['userId']} {account['nickName']}")
    choice = int(input(""))
    
    if choice > len(config["Accounts"]) + 1:
        print("Invalid choice.")
        exit(0)

    print("What would you like to edit? \n")
    print("1. ROBLOSECURITY")
    print("2. Friendly name")
    editChoice = int(input(""))

    if editChoice == 1:
        roblosecurity = str(input("Enter ROBLOSECURITY: "))
        try:
            userId = r.get("https://users.roblox.com/v1/users/authenticated",
                        cookies={".ROBLOSECURITY": roblosecurity}).json()["id"]
        except:
            print("ROBLOSECURITY is invalid.")
            exit(0)

        config["Accounts"][choice - 1]["ROBLOSECURITY"] = roblosecurity
    elif editChoice == 3:
        friendlyName = str(input("Enter friendly name: "))
        config["Accounts"][choice - 1]["nickName"] = friendlyName

    print("ROBLOSECURITY updated.")
    jsonObject = json.dumps(config, indent=4)
elif choice == 3:
    newRoblosecurity = str(input("Enter ROBLOSECURITY: "))

    try:
        userId = r.get("https://users.roblox.com/v1/users/authenticated",
                    cookies={".ROBLOSECURITY": newRoblosecurity}).json()["id"]
    except:
        print("ROBLOSECURITY is invalid.")
        exit(0)

   
    for i, account in enumerate(config["Accounts"]):
        if account["userId"] == userId:
            print("Account already exists.")
            exit(0)


    friendlyName = str(input("Enter friendly name: "))
    config["Accounts"].append({
        "ROBLOSECURITY": newRoblosecurity,
        "userId": userId,
        "nickName": friendlyName
    })

    jsonObject = json.dumps(config, indent=4)
elif choice == 4:
    print("What account would you like to remove? \n")
    for i, account in enumerate(config["Accounts"]):
        if i == 0:
            print(f"{i + 1}. {account['userId']} {account['nickName']} (Primary)")
        else:
            print(f"{i + 1}. {account['userId']} {account['nickName']}")
        
    choice = int(input(""))
    if choice > len(config["Accounts"]):
        print("Invalid choice.")
        exit(0)

    config["Accounts"].pop(choice - 1)
    jsonObject = json.dumps(config, indent=4)


elif choice == 5:
    cooldownPerCheck = input("Enter cooldown per check: ")
    config["cooldownPerCheck"] = float(cooldownPerCheck)
    jsonObject = json.dumps(config, indent=4)  
elif choice == 6:
    discordWebhook = str(input("Enter Discord webhook (Leave blank for none): "))
    config["discordWebhook"] = discordWebhook
    jsonObject = json.dumps(config, indent=4)
else:
    exit(0)


if jsonObject:
    with open("./config.json", "w") as f:
        f.write(jsonObject)
        f.close()

    print("Config file updated.")
    exit(0)