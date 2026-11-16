import re
import json

with open("scratch/callback_3_ds:3.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Pattern for item entries:
# [null, "<ID>"], null, null, null, "<mimeType>", ... [[16, null, [null, [[["<Name>", null, 1]]]]
# Let's extract blocks
items = []
pattern = re.compile(
    r'\[null,\"(1[a-zA-Z0-9_-]{25,50})\"\]'
    r'.*?\"(application/vnd\.google-apps\.folder|image/tiff|image/png|application/vnd\.openxmlformats-officedocument\.[^\"]+|\w+/[^\"]+)\"'
    r'.*?\[\[\[\"([^\"]+)\"',
    re.DOTALL
)

for m in pattern.finditer(text):
    item_id = m.group(1)
    mime = m.group(2)
    name = m.group(3)
    items.append({
        "id": item_id,
        "name": name,
        "mime": mime,
        "is_folder": "folder" in mime
    })

print(f"Extracted {len(items)} items from callback_3:")
# Deduplicate by ID
unique_items = {}
for it in items:
    unique_items[it["id"]] = it

for uid, it in sorted(unique_items.items(), key=lambda x: (not x[1]["is_folder"], x[1]["name"])):
    print(f"[{'FOLDER' if it['is_folder'] else 'FILE'}] {it['name']:<35} (ID: {it['id']}, Mime: {it['mime']})")

