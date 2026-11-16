import os
import pandas as pd

def get_dir_inventory(path):
    inv = []
    if not os.path.exists(path):
        return inv
    for root, dirs, files in os.walk(path):
        for f in files:
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, "SuvarnaProject_data")
            sz_bytes = os.path.getsize(full_p)
            sz_str = f"{sz_bytes / 1024:.1f} KB" if sz_bytes < 1024*1024 else f"{sz_bytes / (1024*1024):.2f} MB"
            ext = os.path.splitext(f)[1].lower()
            inv.append({
                "rel_path": rel_p,
                "filename": f,
                "ext": ext,
                "size_bytes": sz_bytes,
                "size_str": sz_str
            })
    return inv

items = get_dir_inventory("SuvarnaProject_data")
print(f"Total files in local SuvarnaProject_data: {len(items)}")

# Group by category
categories = {
    "Weather & Rainfall": [i for i in items if "rainfall" in i["rel_path"].lower() or "weather" in i["rel_path"].lower()],
    "LULC Classification": [i for i in items if "lulc" in i["rel_path"].lower() or "water_body_area" in i["rel_path"].lower()],
    "Satellite Imagery (RGB)": [i for i in items if "image_rgb" in i["rel_path"].lower()],
    "Satellite Imagery (NDWI)": [i for i in items if "ndwi" in i["rel_path"].lower()],
    "Binary & AI Model": [i for i in items if "binary" in i["rel_path"].lower()],
    "River-Mouth Morphometrics": [i for i in items if "opening" in i["rel_path"].lower() or "width" in i["rel_path"].lower()],
}

for cat, file_list in categories.items():
    print(f"\n=== {cat} ({len(file_list)} files) ===")
    total_sz = sum(f["size_bytes"] for f in file_list)
    sz_str = f"{total_sz / 1024:.1f} KB" if total_sz < 1024*1024 else f"{total_sz / (1024*1024):.2f} MB"
    print(f"Total size: {sz_str}")
    for f in sorted(file_list, key=lambda x: x["filename"])[:10]:
        print(f"  - {f['filename']} ({f['size_str']})")

