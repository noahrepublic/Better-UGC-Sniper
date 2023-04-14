import requests as r
import json
from threading import Thread
import uuid
import os
import time
import datetime
import queue

os.system("cls")

print("UGC Sniper Premium Edition by noahrepublic#4323, support server: https://discord.gg/hw2ttCnmdz")
print("https://github.com/noahrepublic/Better-UGC-Sniper")


limiteds = []


global start
start = 0

global proxyIndex
proxyIndex = 0
global proxiesEnabled
proxiesEnabled = False

global proxiesLength
proxiesLength = 0

with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").replace("\n", "").split(",")


with open("proxies.txt", "r") as f:
    proxies = f.read().replace(" ", "").split("\n")
    for proxy in proxies:
        if proxy == "":
            proxies.remove(proxy)

    proxiesLength = len(proxies)
    
    if proxiesLength > 0:
        proxiesEnabled = True
        print("Proxies enabled.")
        print(f"Loaded {len(proxies)} proxies.")
    else:
        print("Proxies disabled.")

def getCookie():
    global cookie
    global userId
    global perCooldown

    try:
        with open("config.json", "r") as f:
                config = json.load(f)
                cookie = config["ROBLOSECURITY"]

                perCooldown = config["cooldownPerLimited"]

                f.close()
    except:
        cookie = None
        perCooldown = 0.75


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
            response = session.post(
                "https://auth.roblox.com/")
            
            xToken = response.headers["x-csrf-token"]

        except:
            xToken = None

        
        if xToken:
            session.headers["X-CSRF-TOKEN"] = xToken

        time.sleep(248)


def getProxy():
    global proxyIndex

    if proxyIndex >= proxiesLength - 1:
        proxyIndex = 0
    else:
        proxyIndex += 1

    proxy = proxies[proxyIndex]

    return proxy

def buyLimited(info, productId, limited):
    itemId = info["collectibleItemId"]

    data = {
        "collectibleProductId": productId,
        "collectibleItemId": itemId,
        "expectedCurrency": 1,
        "expectedPrice": 0,
        "expectedPurchaserId": userId,
        "expectedPurchaserType": "User",
        "expectedSellerId": info["creatorTargetId"],
        "expectedSellerType": "User"
    }

    print("Buying " + info["name"])

    available = True

    global proxiesEnabled
    global proxiesLength

    while available:
        data["idempotencyKey"] = str(uuid.uuid4())
        print("Trying to buy " + info["name"])
        if proxiesEnabled:
            proxy = getProxy()
            session.proxies = {"http": proxy, "https": proxy}
        
        response = r.post(
            f"https://apis.roblox.com/marketplace-sales/v1/item/{itemId}/purchase-item", json=data, cookies=session.cookies, headers=session.headers, proxies=session.proxies)

        if response.status_code == 429:
       
            if proxiesEnabled:
                print("Rate limited, Switching proxy")
                continue
            else:
                print("Rate limited")
            time.sleep(0.25)
 
        if response.status_code == 503:
            print("Out of stock! Or website crashed")

            # validate if it's out of stock or not
            try:
                info = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                        json={"items": [{"itemType": "Asset", "id": int(limited)}]})
            except:
                print("Is your limiteds.txt file empty?")
                exit(0)
            
            try:
                left = info.json()["data"][0]["unitsAvailableForConsumption"]
            except:
                print(f"Failed getting stock. Full log: {info.text} - {info.reason}")
                left = 0

            if left == 0:
                available = False
            
                print("Out of stock")

            continue
        if response.status_code == 500:
            print("Invalid parameters (Roblox issue)")
            continue

        try:
            response = response.json()
        except:
            print("Failed to buy ")
            continue
            

        if response["purchased"]:
            print("Bought " + info["name"])



def checkLimiteds():
    print("Checking limiteds...")


    global start
    for limited in limiteds:
        try:
            limitedInfo = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]}, timeout=2).json()["data"][0]
        except r.Timeout:
            if proxiesEnabled:
                print("Proxy timed out (bad proxy), switching proxy")
            continue
        except r.ConnectionError:
            if proxiesEnabled:
                print("Proxy timed out (bad proxy), switching proxy, connection error")
            continue
        
        except KeyError:
            
            if proxiesEnabled:
                print("Rate limited, Switching proxy (Might be a bad proxy)")
                continue
            else:
                print("Rate limited")
            start += (60-int(datetime.datetime.now().second))
            time.sleep(60-int(datetime.datetime.now().second)) # https://devforum.roblox.com/t/what-are-the-roblox-ratelimits-or-how-can-i-handle-them/1596921/8
          
            continue

        if limitedInfo.get("priceStatus", "") != "Off Sale" and limitedInfo.get("collectibleItemId") is not None:
            productId = session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                    json={"itemIds": [limitedInfo["collectibleItemId"]]}, timeout=3)
        
            try:
                productId = productId.json()[0]["collectibleProductId"]
            except:

                if productId.reason == "Unauthorized":
                    print("You were unauthorized, check your ROBLOSECURITY?")
                continue

            buyLimited(limitedInfo, productId, limited)

    

if __name__ == "__main__":
    getCookie()
   
    while not cookie:
        time.sleep(0.1)

    global session

    session = r.Session()
    session.cookies[".ROBLOSECURITY"] = cookie

    session.headers["User-Agent"] = "Roblox/WinInet"


    Thread(target=getXToken).start()

    while not session.headers.get("X-CSRF-TOKEN", ""): # Wait for the xToken to be set
        time.sleep(0.1)

    if proxiesEnabled:
        session.proxies = {"http": proxies[proxyIndex], "https": proxies[proxyIndex]}

    totalCooldown = len(limiteds) * perCooldown


    while True:
        start = time.perf_counter()

        checkLimiteds()

        end = time.perf_counter()

        if end - start < totalCooldown:
            time.sleep(totalCooldown - (end - start))

        os.system("cls")
        print("Time taken: " + str(round(time.perf_counter()-start, 4)))


        if proxiesEnabled:
            print("Proxy: " + proxies[proxyIndex])
            proxy = getProxy()
            session.proxies = {"http": proxy, "https": proxy}
        
    
