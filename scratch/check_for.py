import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

for_f = inv.get("First_Opening_Results", {})
print("First_Opening_Results items:")
for k, v in for_f.items():
    print(f"  {v.get('name')} | id: {k} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')}")

