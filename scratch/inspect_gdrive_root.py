import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

print("Top keys in inv:", list(inv.keys()))

# Check folder SuvarnaProject_data
spd = inv.get("SuvarnaProject_data", {})
print("\nItems in top Google Drive folder SuvarnaProject_data:")
for k, v in spd.items():
    print(f"  {v.get('name')} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')} | id: {k}")

# Check River_Mouth
rm = inv.get("River_Mouth", {})
print(f"\nItems in River_Mouth folder ({len(rm)} items):")
for k, v in list(rm.items())[:20]:
    print(f"  {v.get('name')} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')} | id: {k}")

# Check Shoreline
sh = inv.get("Shoreline", {})
print(f"\nItems in Shoreline folder ({len(sh)} items):")
for k, v in list(sh.items())[:20]:
    print(f"  {v.get('name')} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')} | id: {k}")

# Check binary_cleaned
bc = inv.get("binary_cleaned", {})
print(f"\nItems in binary_cleaned folder ({len(bc)} items):")
for k, v in list(bc.items())[:20]:
    print(f"  {v.get('name')} | is_folder: {v.get('is_folder')} | mime: {v.get('mime')} | id: {k}")

