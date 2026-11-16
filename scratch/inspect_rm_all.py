import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

rm = inv.get("River_Mouth", {})
print(f"River_Mouth has {len(rm)} items:")
for k, v in sorted(rm.items(), key=lambda x: x[1].get("name", "")):
    print(f"  {v.get('name')} | id: {k} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')}")

