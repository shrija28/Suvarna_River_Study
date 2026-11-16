import json
import os

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

print("Folders in inventory:", list(inv.keys()))

for folder, items in inv.items():
    print(f"\n=== Folder: {folder} ===")
    for item_id, item_info in items.items():
        name = item_info.get("name", "")
        is_folder = item_info.get("is_folder", False)
        mime = item_info.get("mime", "")
        if not is_folder:
            print(f"  FILE: {name} (mime: {mime}, id: {item_id})")
        else:
            print(f"  DIR: {name} (id: {item_id})")

