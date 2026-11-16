import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

for folder, items in inv.items():
    print(f"\n==========================================")
    print(f"FOLDER: {folder} (Total items: {len(items)})")
    print(f"==========================================")
    for iid, info in items.items():
        name = info.get("name", "")
        if not info.get("is_folder", False):
            print(f"  {name} | id: {iid} | mime: {info.get('mime')}")

