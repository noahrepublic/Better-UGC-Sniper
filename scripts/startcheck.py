import os

if not os.path.exists("./config.json"):
    print("Ensuring pip is installed")
    os.system("python -m ensurepip --upgrade")

    print("Installing required packages")
    os.system("python -m pip install -r ./requirements.txt")
    exit(0)