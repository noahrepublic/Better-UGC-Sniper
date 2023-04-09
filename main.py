import requests as r
from threading import Thread
import os
import uuid
import time
import datetime
import winreg

path = winreg.HKEY_CURRENT_USER
robloxcom = winreg.OpenKeyEx(path, r"SOFTWARE\\Roblox\\RobloxStudioBrowser\\roblox.com")

with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").split(",")

cookie = str(winreg.QueryValueEx(robloxcom, ".ROBLOSECURITY")[0]) 


if cookie:
    cookie = cookie.split("<")[3]
    cookie = cookie.split(">")[0]
    cookie = cookie.strip()

    try:
        user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}).json()["id"]
        print("Automatically found cookie.")
    except:
        with open("cookie.txt", "r") as f:
            cookie = f.read()
else:
    with open("cookie.txt", "r") as f:
        cookie = f.read()



user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}).json()["id"]
x_token = ""
def get_x_token():
    global x_token

    x_token = r.post("https://auth.roblox.com/v2/logout",
                     cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
    print("Logged in.")

    while 1:
        # Gets the x_token every 4 minutes.
        x_token = r.post("https://auth.roblox.com/v2/logout",
                         cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
        time.sleep(248)


def buy(json, itemid, productid):
    print("Spam buying limited...")

    data = {
        "collectibleItemId": itemid,
        "expectedCurrency": 1,
        "expectedPrice": 0,
        "expectedPurchaserId": user_id,
        "expectedPurchaserType": "User",
        "expectedSellerId": json["creatorTargetId"],
        "expectedSellerType": "User",
        "idempotencyKey": "random uuid4 string that will be your key or smthn",
        "collectibleProductId": productid
    }

    while 1:
        data["idempotencyKey"] = str(uuid.uuid4())
        bought = r.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item", json=data,
            headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie})

        if bought.reason == "Too Many Requests":
            print("Ran into a ratelimit resuming trying again shortly...")
            time.sleep(0.5)
            continue

        try:
            bought = bought.json()
        except:
            print(bought.reason)
            print("Json decoder error whilst trying to buy item.")
            continue

        if not bought["purchased"]:
            print(f"Failed buying the limited, trying again.. Info: {bought} - {data}")
        else:
            print(f"Successfully bought the limited! Info: {bought} - {data}")
            

        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                      json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                      headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()["data"][0]
        except:
            info = {"unitsAvailableForConsumption": 1}

        if info["unitsAvailableForConsumption"] == 0:
            print("Couldn't buy the limited in time. Better luck next time.")
            return


# Get collectible and product id for all the limiteds.
Thread(target=get_x_token).start()

print("Better-UGC-Sniper, upgraded by noahrepublic#4323 \nDiscord server: https://discord.com/invite/Kk8n2QpFCb")
while x_token == "":
    time.sleep(0.01)

# https://apis.roblox.com/marketplace-items/v1/items/details
# https://catalog.roblox.com/v1/catalog/items/details

cooldown = 60/(80/len(limiteds))
while 1:
    start = time.perf_counter()

    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                           headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()["data"][0]
        except KeyError:
            print("Ratelimit! Waiting for next minute to start")
            time.sleep(60-int(datetime.datetime.now().second))
            continue

        if info.get("priceStatus", "") != "Off Sale":
            try:
                productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                    json={"itemIds": [info["collectibleItemId"]]},
                    headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()[0]["collectibleProductId"]

                buy(info, info["collectibleItemId"], productid)
            except:
                print("Caught an error")

    taken = time.perf_counter()-start
    if taken < cooldown:
        time.sleep(cooldown-taken)

    os.system("cls")
    print("Check done.\n"
          f"Time taken: {round(time.perf_counter()-start, 3)}\n"
          f"Ideal time: {round(cooldown, 3)}")
