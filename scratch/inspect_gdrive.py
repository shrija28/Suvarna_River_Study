import re
import os
import json

with open("gdrive_folder.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("HTML size:", len(text))
title = re.findall(r"<title>(.*?)</title>", text)
print("Title:", title)

# Google Drive embeds folder item data in script tags, often under window['_DRIVE_bootstrappedData'] or similar JS objects
script_data = re.findall(r"<script[^>]*>(.*?)</script>", text, re.DOTALL)
print("Found script tags:", len(script_data))

# Search for any items/names
matches = set(re.findall(r'\"([a-zA-Z0-9_\-\. ]+\.(?:csv|tif|tiff|xlsx|pdf|png|jpg|keras|h5|txt|py))\"', text))
print("Matched filenames in HTML:", len(matches))
for m in sorted(list(matches))[:30]:
    print("  File:", m)

# Search for folder names or strings
folders = set(re.findall(r'\"([a-zA-Z0-9_\- ]{3,40})\"', text))
interesting = [f for f in folders if any(k in f.lower() for k in ["suvarna", "rain", "weather", "river", "mouth", "image", "lulc", "data", "ndwi", "rgb", "binary"])]
print("\nInteresting folder / item keywords in HTML:", interesting)

