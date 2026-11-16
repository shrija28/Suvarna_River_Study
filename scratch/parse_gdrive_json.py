import re
import json

with open("gdrive_folder.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Look for bootstrapped data
# Usually: window['_DRIVE_bootstrappedData'] = ... or similar
patterns = [
    r"_DRIVE_bootstrappedData\s*=\s*(\{.*?\});",
    r"window\[\'_DRIVE_bootstrappedData\'\]\s*=\s*(\{.*?\});",
    r"AF_initDataCallback\((.*?)\);",
    r"var _DRIVE_bootstrappedData = (.*?);",
]

found = False
for p in patterns:
    for m in re.finditer(p, text, re.DOTALL):
        print(f"Matched pattern: {p[:30]} with len {len(m.group(1))}")
        found = True

# Also extract all file-like entries: ID, name, mimeType
# Drive items in JSON typically look like: ["<ID>", ["<filename>", ...], ...]
entries = []
# Match Google Drive item IDs (28-44 alphanumeric, underscore, hyphen)
id_name_matches = re.findall(r'\[\"([a-zA-Z0-9_-]{25,50})\",\[\"([^\"]+)\"', text)
print("Found [ID, Name] candidate pairs:", len(id_name_matches))
for item_id, item_name in set(id_name_matches):
    print(f"  {item_id} -> {item_name}")

# Also search for any string patterns with filenames
all_files = set(re.findall(r'\"([^\"]+\.(?:csv|xlsx|xls|pdf|tif|tiff|png|jpg|jpeg|keras|h5|txt|py|json|geojson|shp|dbf|shx|prj))\"', text, re.IGNORECASE))
print(f"\nAll filenames with extensions found ({len(all_files)}):")
for f in sorted(list(all_files)):
    print(f"  - {f}")

