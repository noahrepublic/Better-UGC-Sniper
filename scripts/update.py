import requests as r

print("Checking for updates...")
script = r.get("https://raw.githubusercontent.com/noahrepublic/Better-UGC-Sniper/main/main.py").text
with open("main.py", "r") as f:
   if f.read() != script:
        print("Script is outdated! Don't want to auto update due to customer requests")