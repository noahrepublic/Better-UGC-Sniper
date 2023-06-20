import json
import uuid
import os
import time
import datetime
import asyncio
import httpx

from discord_webhook import AsyncDiscordWebhook, DiscordEmbed


os.system('cls' if os.name == 'nt' else 'clear')

print("Better UGC Sniper by noahrepublic#4323, support server: https://discord.com/invite/Kk8n2QpFCb")
print("https://github.com/noahrepublic/Better-UGC-Sniper")


global start

rateTokens = 60
rateLastRefil = asyncio.get_event_loop().time()

def clear():
    return 'cls' if os.name == 'nt' else 'clear'

class Sniper:
    def __init__(self):
        print("Starting sniper")

        self.buyThreadPurchases = 0 # Used to track how many purchases have been made in the buy thread

        self.discordWebhook = None
        self.items = [] # Items scanning

        self.cooldown = 1 # Cooldown between checks

        self.proxiesEnabled = False
        
        self.maxPrice = 0 # Temporary, might add per item

        # Information prints

        self.checks = 0
        self.purchases = 0

    def printAll(self):
        # add theme print in the future
        print(f"------- Noah's UGC Sniper -------")
        print(f"Checks: {self.checks}")
        print(f"Purchases: {self.purchases}")


    class Account:
        def __init__(self, accounts):
            self.accounts = accounts
            self.accountIndex = 0
            self.accountLength = len(accounts)

        def getPrimaryAccount(self): # Reset, only used this outside of the buy function
            self.accountIndex = 0
            return self.getCurrentAccount()

        def getCurrentAccount(self):
            return self.accounts[self.accountIndex]
        
        def nextAccount(self):
            self.accountIndex += 1

            if self.accountIndex > self.accountLength:
                self.accountIndex = 0

            return self.accounts[self.accountIndex]

    class ProxyHandler:
        class TokenBucket:
            def __init__(self, capacity, rate):
                self.capacity = capacity
                self.rate = rate
                self.tokens = capacity
                self.last = time.monotonic()

            async def consume(self) -> bool:
                await self._fillBucket()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                return False
                
            async def _fillBucket(self) -> None:
                now = time.monotonic()
                dt = now - self.last
                new = dt * self.rate
                self.tokens = min(self.tokens + new, self.capacity)

        def __init__(self, proxies, requestsPerMinute):
            self.proxies = proxies
            self.buckets = {proxy: self.TokenBucket(requestsPerMinute, requestsPerMinute / 60) for proxy in proxies}
            self.proxyIndex = 0
            self.proxyLength = len(proxies) # save from having to call len() every time

        def nextProxy(self) -> str:
            self.currentProxyIndex = (self.currentProxyIndex + 1) % self.proxyLength
            return self.proxies[self.currentProxyIndex]
        
        def currentProxy(self) -> str:
            return self.proxies[self.proxyIndex]
        
        async def rotate(self) -> str:
            while True:
                proxy = self.currentProxy()
                if self.buckets[proxy].consume():
                    return proxy
                
                self.proxyIndex = self.nextProxy() # rotate to next proxy

    
    async def getXToken(self, cookie: str) -> dict:
        async with httpx.AsyncClient(cookies={".ROBLOSECURITY": cookie}, verify=False) as client:
            response = await client.post("https://auth.roblox.com/v2/logout")
            xToken = response.headers.get("x-csrf-token")
            if not xToken:
                raise Exception("Failed to get x-csrf-token, invalid cookie?")
            return {"x-csrf-token": xToken, "created": datetime.datetime.now()}
        
    async def autoXToken(self) -> None:
        while True:
            await asyncio.sleep(10)
            
            for account in self.accountHandler.accounts:

                if not account.get("x-csrf-token") or datetime.datetime.now() > account["created"] + datetime.timedelta(minutes=10):
                    print("Updating x-csrf-tokens")
                    try:
                        response = await self.getXToken(account[".ROBLOSECURITY"])
                        account["x-csrf-token"] = response["x-csrf-token"]
                        account["created"] = response["created"]
                        continue
                    except Exception as e:
                        print(f"Failed to update x-csrf-token for {account['nickName']}: {e}")
                        continue

    async def getProxies(self) -> None:
        try:
            with open("proxies.txt") as f:
                proxies = f.read().replace(" ", "").split("\n")
            for proxy in proxies:
                if proxy == "":
                    proxies.remove(proxy)

            self.proxiesLength = len(proxies)
            
            if self.proxiesLength > 0:
                self.proxiesEnabled = True

                print("Proxies enabled.")
               
                self.proxyHandler = self.ProxyHandler(proxies=proxies, requestsPerMinute=60)
                self.proxiesEnabled = True
            else:
                print("Proxies disabled.")
        except Exception as e:
            print(f"Failed to read proxies.txt: {e}")
            print("proxies.txt not found, Proxies disabled.")

    async def readConfig(self) -> None:
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                configAccounts = config["Accounts"]
                accounts = []

                print("Reading config")
                for account in configAccounts:
                    cookie = account["ROBLOSECURITY"]
                    userId = account["userId"]
                    nickName = account["nickName"]

                    xToken = await self.getXToken(cookie)

                    accounts.append({".ROBLOSECURITY": cookie, "x-csrf-token": xToken["x-csrf-token"], "created": xToken["created"], "userId": userId, "nickName": nickName})

                self.accountHandler = self.Account(accounts=accounts)

                if config["discordWebhook"] != "" and config["discordWebhook"] != None:
                    self.discordWebhook = config["discordWebhook"]
                
                
                for item in config["Items"]:
                    if not item["id"]:
                        continue
                    self.items.append(str(item["id"]))

                self.cooldown = config["cooldownPerCheck"]


        except Exception as e:
            print(f"Could not read config.json {e}")
            exit(0)

    async def buy(self, info: dict, limitedId: int, accountData: dict): # start here tomorrow
        collectibleItemId = info["collectibleItemId"]
        data = {
            "collectibleProductId": info["productId"],
            "collectibleItemId": collectibleItemId,
            "expectedCurrency": 1,
            "expectedPrice": 0,
            "expectedPurchaserId": accountData["userId"],
            "expectedPurchaserType": "User",
            "expectedSellerId": info["creatorTargetId"],
            "expectedSellerType": "User"
        }

        totalErrors = 0

        print(f"Attempting to buy {info['name']}")
        async with httpx.AsyncClient(headers={"x-csrf-token": accountData["x-csrf-token"]}, cookies={".ROBLOSECURITY": accountData[".ROBLOSECURITY"]}) as client:
            while True:
                if totalErrors >= 5:
                    print("Failed to buy, too many errors.")
                    break
                
                data["idempotencyKey"] = str(uuid.uuid4())

                try: 
                    response = await client.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleItemId}/purchase-item", json=data)
                except httpx.ConnectError:
                    print("Failed to connect to Roblox API, retrying...")
                    totalErrors += 1
                    continue
                except httpx.TimeoutException:
                    print(f"Connection timed out")

                if response.status_code == 429:
                    print("Rate limited, retrying in 0.5 seconds")
                    await asyncio.sleep(0.5)
                    continue
                elif response.status_code == 500:
                    print("Invalid parameters? (Roblox)")
                    totalErrors += 1
                    continue

                try:
                    responseJSON = response.json()
                except:
                    print("Failed to decode JSON")
                    totalErrors += 1
                    continue

                if responseJSON.get("errorMessage") and responseJSON.get("errorMessage") == "QuantityExhausted":
                    if totalErrors < 3:
                        print("Quantity exhausted, double checking incase of false positive...")
                        totalErrors += 1
                        continue
                    else:
                        print("Out of stock! Better luck next time.")
                        return
                    
                if responseJSON.get("errorMessage") and responseJSON.get("errorMessage") == "Flooded: purchase requests exceeds limit":
                    print("Roblox: Item purchase request exceeds limit")

                if responseJSON["purchased"]:
                    print(f"Successfully bought {info['name']}!")
                    self.buyThreadPurchases += 1
                    self.purchases += 1

                    tasks = []
                    embed = DiscordEmbed(title="Noah's UGC Sniper")
                    embed.set_footer(text="discord.gg/hw2ttCnmdz")
                    embed.set_timestamp()
                    embed.set_url(f"https://www.roblox.com/catalog/{limitedId}/noahw")
                    if self.discordWebhook:
                        webhook = AsyncDiscordWebhook(url=self.discordWebhook, content=f"Successfully bought {info['name']}!")
                        
                        webhook.add_embed(embed)
                        tasks.append(webhook.execute())

                    await asyncio.gather(*tasks)
                   
                else:
                    print(f"Failed to buy {info['name']}, {responseJSON['errorMessage']}")
                    totalErrors += 1
                    continue
    async def waitRatelimit(self):
        global rateLastRefil
        global rateTokens
        while True:
            if asyncio.get_event_loop().time() - rateLastRefil >= 60:
                rateTokens = 60
                rateLastRefil = asyncio.get_event_loop().time()
            
            if rateTokens <= 0:
                await asyncio.sleep(0.01)
            else:
                rateTokens -= 1
                return True

    async def search(self):
        while True:
            if self.proxiesEnabled and self.proxiesLength > 0:
                proxy = f"http://{await self.proxyHandler.rotate()}"
            else:
                proxy = None
            
            if not self.proxiesEnabled:
                await self.waitRatelimit()

            start = asyncio.get_event_loop().time()

            currentAccount = self.accountHandler.getCurrentAccount()

            
            async with httpx.AsyncClient(proxies=proxy, headers={"x-csrf-token": currentAccount["x-csrf-token"], "Accept": "application/json"}, cookies={".ROBLOSECURITY": currentAccount[".ROBLOSECURITY"]}) as session:
                
                try:
                    response = await session.post("https://catalog.roblox.com/v1/catalog/items/details", json={"items": [{"itemType": "Asset", "id": int(id)} for id in self.items]})
                    limitedsInfo = response.json()["data"]
                except httpx.ConnectTimeout:
                    if self.proxiesEnabled:
                        print("Proxy timed out")
                    else:
                        print("Connection timed out")
                    continue
                except KeyError:
                    if self.proxiesEnabled:
                        print("Proxy failed to connect")
                    else:
                        print(response.text)

                        ##logging.debug(f"Failed to get limiteds info: {response.text}")
                        if response.status_code == 403:
                            response = await self.getXToken(currentAccount[".ROBLOSECURITY"])
                            currentAccount["x-csrf-token"] = response["x-csrf-token"]
                            currentAccount["created"] = response["created"]
                        continue
                except Exception as e:
                    ##logging.debug(f"Failed to get limiteds info: {e}")
                    if response.status_code == 403:
                            response = await self.getXToken(currentAccount[".ROBLOSECURITY"])
                            currentAccount["x-csrf-token"] = response["x-csrf-token"]
                            currentAccount["created"] = response["created"]
                    continue


                

                if response.status_code == 429:
                    if self.proxiesEnabled:
                        continue

                    print("Rate limited, waiting to end")
                    continue # it will start rate limit check

               
                validForProductIds = []

                for limited in limitedsInfo:
                    if limited.get("price") is None:
                        continue

                    if limited.get("unitsAvailableForConsumption", 0):
                        print("Out of stock")
                        continue

                    if limited.get("price") > 0:
                        print("Item is not free")
                        continue

                    if limited.get("priceStatus") != "Off Sale" and limited.get("unitsAvailableForConsumption", 0) > 0 and limited.get("collectibleItemId"):
                        validForProductIds.append(limited)

                validForProductIdsLength = len(validForProductIds)
                if validForProductIdsLength > 0:
                    if not self.proxiesEnabled:
                            await self.waitRatelimit()
                    productIds = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details", json={"itemIds": [id["collectibleItemId"] for id in validForProductIds]})
                    productIds = productIds.json()
                    
                    tasks = []

                    for i in range(validForProductIdsLength):
                        info = validForProductIds[i]

                        info["productId"] = productIds[i]["collectibleProductId"]

                        for account in self.accountHandler.accounts:
                            tasks.append(self.buy(info, info["id"], account)) 

                        
                        await sio.emit("new-limited", {"id": info["id"], "name": info["name"], "productId": info["productId"], "collectibleItemId": info["collectibleItemId"], "creatorTargetId": info["creatorTargetId"]})

                    await asyncio.gather(*tasks)
            
            self.checks += len(self.items)

            end = asyncio.get_event_loop().time()

            print("Checked", round(end - start, 2), "seconds")
            await asyncio.sleep(self.cooldown)


    async def autoPrint(self):
        while True:
            os.system(clear())
            self.printAll()
    
            await asyncio.sleep(0.15)           

    async def main(self):
        print("Started sniper")
        coroutines = []
 
        coroutines.append(self.autoXToken())
        coroutines.append(self.search())
        coroutines.append(self.autoPrint())

        await asyncio.gather(*coroutines)


async def start():
    tasks = []

    tasks.append(asyncio.create_task(sniper.readConfig()))
    tasks.append(asyncio.create_task(sniper.getProxies()))

    await asyncio.gather(*tasks)

    await sniper.main()

if __name__ == "__main__":
    sniper = Sniper()

    asyncio.run(start())
