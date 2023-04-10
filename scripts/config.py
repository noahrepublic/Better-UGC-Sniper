import requests as r
import json


config = {
    "ROBLOSECURITY": "",
    "cooldownPerLimited": 0.75
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
