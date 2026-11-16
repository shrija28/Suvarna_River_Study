import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

print("--- Check River_Mouth files ---")
for k, v in inv.get("River_Mouth", {}).items():
    print(v.get("name"), "-> is_folder:", v.get("is_folder"), "id:", k)

print("\n--- Check binary_cleaned files ---")
for k, v in list(inv.get("binary_cleaned", {}).items())[:15]:
    print(v.get("name"), "-> is_folder:", v.get("is_folder"), "id:", k)

