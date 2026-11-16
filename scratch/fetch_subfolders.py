import subprocess
import os
import re
import json

folders = [
    ("SuvarnaProject_data", "10A8PqFuWji3YVSBl1H0YtBoHvrvgDwFv"),
    ("River_Mouth", "1A014V3qHeoxGIGdVgsaYGdEto0tKVc4z"),
    ("Shoreline", "1uO-BZ8JLn0RmzoGkJE_1Bc_sYk271S07"),
    ("Centerline", "1T1jtyh_19cakMp18y-imR1DjClMGS_fg"),
    ("Data", "1MxTMraEvNqgXMkf4vN2qhAclrLo3a1fn"),
    ("First_Opening_Results", "1JT6N7ZEijdG6nqnqztOIN4xMmJcS3iB8"),
    ("Results", "12ejjE7OW4J2XSJb_M6tmLCOztma7tn13"),
    ("LULC", "1G7cdupcm8yk9tFpgED4hGDBZG763dLgx"),
    ("LULC_Result", "1DdsCCTPc39AyIlx3PFg17ne_Lf9D5IBt"),
    ("binary_cleaned", "15Y2km4gxhbdCVPf7PqQDOVi5fUdOZW0H"),
]

os.makedirs("scratch/gdrive_subfolders", exist_ok=True)

inventory = {}

for name, fid in folders:
    url = f"https://drive.google.com/drive/folders/{fid}"
    out_html = f"scratch/gdrive_subfolders/{name}.html"
    print(f"\nFetching {name} ({fid})...")
    subprocess.run(["curl.exe", "-s", url, "-o", out_html], capture_output=True)
    
    if os.path.exists(out_html) and os.path.getsize(out_html) > 1000:
        with open(out_html, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract files and folders
        # Matches in ds:3 callback
        pattern = re.compile(
            r'\[null,\"(1[a-zA-Z0-9_-]{25,50})\"\]'
            r'.*?\"(application/vnd\.google-apps\.folder|image/tiff|image/png|application/vnd\.openxmlformats-officedocument\.[^\"]+|\w+/[^\"]+)\"'
            r'.*?\[\[\[\"([^\"]+)\"',
            re.DOTALL
        )
        items = {}
        for m in pattern.finditer(content):
            item_id = m.group(1)
            mime = m.group(2)
            item_name = m.group(3)
            items[item_id] = {
                "name": item_name,
                "mime": mime,
                "is_folder": "folder" in mime
            }
        inventory[name] = items
        print(f"  -> Found {len(items)} items in {name}")
        for uid, it in sorted(items.items(), key=lambda x: (not x[1]["is_folder"], x[1]["name"]))[:15]:
            print(f"     [{'FOLDER' if it['is_folder'] else 'FILE'}] {it['name']} ({it['mime']})")
    else:
        print(f"  -> Failed or empty for {name}")

with open("scratch/gdrive_inventory.json", "w", encoding="utf-8") as out:
    json.dump(inventory, out, indent=2)

print("\nInventory saved to scratch/gdrive_inventory.json")

