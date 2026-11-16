import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

rm_files = {}
for fid, info in inv.get("River_Mouth", {}).items():
    if not info.get("is_folder") and info.get("name", "").startswith("First_Opening_"):
        rm_files[info.get("name")] = fid

print(f"Total First_Opening pngs found: {len(rm_files)}")
for name, fid in sorted(rm_files.items()):
    print(f"  {name}: {fid}")

bin_files = {}
for fid, info in inv.get("binary_cleaned", {}).items():
    if not info.get("is_folder") and info.get("name", "").startswith("Binary_"):
        bin_files[info.get("name")] = fid

print(f"\nTotal Binary tifs found: {len(bin_files)}")
for name, fid in sorted(bin_files.items()):
    print(f"  {name}: {fid}")

