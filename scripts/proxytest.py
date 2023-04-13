import queue
import requests as r
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor
import time
import os

proxies = queue.Queue()

if not os.path.exists("./proxies.txt"):
    print("proxies.txt does not exist.")
    exit(0)

with open("./proxies.txt", "r") as f:
    for proxy in f.read().replace(" ", "").split("\n"):
        if proxy == "":
            continue
        proxies.put(proxy)
    f.close()

    if proxies.empty():
        print("No proxies found in proxies.txt")
        exit(0)

f = open("./proxies.txt", "w")

startSize = proxies.qsize()
print("Starting proxy validation with", startSize, "proxies.")
runs = 0

session = r.Session()

def validateProxy():
    global proxies
    global runs
    while not proxies.empty():
        proxy = proxies.get()
        try:
            response = session.get("https://ipinfo.io/json", proxies={"https": proxy, "http": proxy}, timeout=5)
        except:
            runs += 1
            print(f"{runs}/{startSize}")
            continue
        

        if response.status_code == 200:
            f.write(f"\n{proxy}")
            runs += 1
            print(f"{runs}/{startSize}")
        

    
for _ in range(10):
    Thread(target=validateProxy).start()
