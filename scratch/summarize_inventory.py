import json

with open("scratch/gdrive_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

print("=" * 80)
print(f"GOOGLE DRIVE DATASET INVENTORY SUMMARY ({len(inv)} Top Folders Analyzed)")
print("=" * 80)

total_files = 0
total_folders = 0

for folder_name, items in inv.items():
    f_count = sum(1 for it in items.values() if not it["is_folder"])
    d_count = sum(1 for it in items.values() if it["is_folder"])
    total_files += f_count
    total_folders += d_count
    print(f"\n📂 [{folder_name}] - {f_count} files, {d_count} subfolders")
    
    file_list = [it for it in items.values() if not it["is_folder"]]
    folder_list = [it for it in items.values() if it["is_folder"]]
    
    if folder_list:
        print("   Subfolders (sample):", [it["name"] for it in folder_list[:8]])
    if file_list:
        print("   Files (sample):", [it["name"] for it in file_list[:8]])

print("\n" + "=" * 80)
print(f"Grand Total: {total_files} files, {total_folders} subfolders across checked categories")
print("=" * 80)

