with open("scratch/gdrive_page.html", "r", encoding="utf-8") as f:
    raw = f.read()

# Replace js hex escapes
cleaned = raw.replace(r'\x22', '"').replace(r'\x5b', '[').replace(r'\x5d', ']').replace(r'\/', '/')

import re

# Find all items that have a parent of 1KJj-D13IrlsdF7AsUi6X32kPlKeBJ7hh
matches = re.findall(r'\["([a-zA-Z0-9_-]{25,})",\["1KJj-D13IrlsdF7AsUi6X32kPlKeBJ7hh"\],"([^"]+)","([^"]+)"', cleaned)
print(f"Items in root folder: {len(matches)}")
for item_id, name, mime in matches:
    print(f"- {name} | Type: {mime} | ID: {item_id}")
