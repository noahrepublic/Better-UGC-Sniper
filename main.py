import requests as r
import json
from threading import Thread
import uuid
import os
import time
import datetime


print("Checking for updates...")
# script = r.get("https://raw.githubusercontent.com/noahrepublic/Better-UGC-Sniper/main/main.py").text
# with open("main.py", "r") as f:
   # if f.read() != script:
       # print("Updating...")
        # with open("main.py", "w") as f:
            # f.write(script)
            # input("Updated please reopen the script")
            # exit(0)


os.system("cls")

print("UGC Sniper by noahrepublic#4323, support server: https://discord.com/invite/Kk8n2QpFCb")
print("https://github.com/noahrepublic/Better-UGC-Sniper")

userId = None
limiteds = []
perCooldown = 0.75

with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").replace("\n", "").split(",")


def getCookie():
    global cookie

    with open("config.json", "r") as f:
            config = json.load(f)
            cookie = config["ROBLOSECURITY"]

            f.close()

    try:
        userId = r.get("https://users.roblox.com/v1/users/authenticated",
                       cookies={".ROBLOSECURITY": cookie}).json()["id"]
    except:
        print("ROBLOSECURITY is invalid, trying to find ROBLOSECURITY in registry...")
        cookie = None

    if cookie == None:

        try:
            import winreg

            path = winreg.HKEY_CURRENT_USER
            robloxcom = winreg.OpenKeyEx(
                path, r"SOFTWARE\\Roblox\\RobloxStudioBrowser\\roblox.com")

            cookie = str(winreg.QueryValueEx(robloxcom, ".ROBLOSECURITY")[0])
        except:
            print(
                "Regex failed, either isn't supported on your system or you are not logged in studio.")
            cookie = None

        if cookie:
            cookie = cookie.split("<")[3]
            cookie = cookie.split(">")[0]
            cookie = cookie.strip()

            try:
                userId = r.get("https://users.roblox.com/v1/users/authenticated",
                               cookies={".ROBLOSECURITY": cookie}).json()["id"]
                print("Automatically found ROBLOSECURITY.")
            except:
                print(
                    "Could not automatically find ROBLOSECURITY. Please enter it manually.")
                exit(0)


def getXToken():
    global xToken

    while True:
        try:
            xToken = session.post(
                "https://auth.roblox.com/").headers['X-CSRF-TOKEN']
        except:
            xToken = None

        if not xToken:
            print("Failed to get x-csrf-token. Site may be down. Retrying in 5...")

            time.sleep(5)
        else:
            session.headers["X-CSRF-TOKEN"] = xToken
            time.sleep(180)


def buyLimited(info, productId):
    itemId = info["collectibleItemId"]


    session.json = {
        "collectibleProductId": productId,
        "collectibleItemId": itemId,
        "expectedCurrency": 1,
        "expectedPrice": 36,
        "expectedPurchaserId": userId,
        "expectedPurchaserType": "User",
        "expectedSellerId": info["creatorTargetId"],
        "expectedSellerType": "User",
    }

    print("Buying " + info["name"])

    available = True

    while available:
        session.json["idempotencyKey"] = str(uuid.uuid4())

        
        response = session.post(
            f"https://apis.roblox.com/marketplace-sales/v1/item/{itemId}/purchase-item")

        if response.reason == "Too Many Requests":
            print("Rate limited", response.status_code)
            time.sleep(0.25)

        try:
            response = response.json()
        except:
            print(response.reason)
            

        if response["purchased"]:
            print("Bought " + info["name"])

        print(response.reason, response.status_code)


def checkLimiteds():
    print("Checking limiteds...")

    for limited in limiteds:
        try:
            limitedInfo = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]}).json()["data"][0]
        except KeyError:
            print("Rate limited")
            time.sleep(60-int(datetime.datetime.now().second)) # https://devforum.roblox.com/t/what-are-the-roblox-ratelimits-or-how-can-i-handle-them/1596921/8
            continue

        if limitedInfo.get("priceStatus", "") != "Off Sale" and limitedInfo.get("collectibleItemId") is not None:
            productId = session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                    json={"itemIds": [limitedInfo["collectibleItemId"]]})
        
            try:
                productId = productId.json()[0]["collectibleProductId"]
                

                buyLimited(limitedInfo, productId)
            except:
                print("Could not get product reason: " + productId.reason + str(productId.status_code))

                if productId.reason == "Unauthorized":
                    print("You were unauthorized, check your ROBLOSECURITY?")
                continue

    

if __name__ == "__main__":
    getCookie()
   
    while not cookie:
        time.sleep(0.1)

    global session

    session = r.Session()
    session.cookies[".ROBLOSECURITY"] = cookie
    session.headers["Content-Type"] = "application/json"


    Thread(target=getXToken).start()

    while not session.headers.get("X-CSRF-TOKEN", ""): # Wait for the xToken to be set
        time.sleep(0.1)

    totalCooldown = len(limiteds) * perCooldown

    

    while True:
        start = time.perf_counter()

        checkLimiteds()

        end = time.perf_counter()

        if end - start < totalCooldown:
            time.sleep(totalCooldown - (end - start))

        os.system("cls")
        print("Taken: " + str(round(time.perf_counter()-start, 4)))
        
    