with open("scratch/river_mouth_folder.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

cleaned = html.replace(r'\x22', '"').replace(r'\x5b', '[').replace(r'\x5d', ']').replace(r'\/', '/')
folder_id = '1xT0nqj6e3VUpIoY4O2IVQ9WE6RE-2NTb'

matches = re.findall(rf'\["([a-zA-Z0-9_-]{{25,}})",\["{folder_id}"\],"([^"]+)","([^"]+)"', cleaned)
print(f"Total items directly under river mouth images: {len(matches)}")

types = {}
for item_id, name, mime in matches:
    types[mime] = types.get(mime, 0) + 1

print("Item types:", types)
