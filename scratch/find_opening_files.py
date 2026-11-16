import os

for root, dirs, files in os.walk("."):
    fo = [f for f in files if "First_Opening" in f or "first_opening" in f.lower() or "opening" in f.lower()]
    if fo:
        print(f"Folder {root}: {fo}")

