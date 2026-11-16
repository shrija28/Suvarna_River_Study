import re
import json

with open("scratch/gdrive_page.html", "r", encoding="utf-8") as f:
    html = f.read()

print("HTML size:", len(html))

# Look for _DRIVE_BOOTSTRAP_DATA or similar
for match in re.finditer(r'window\[\'_DRIVE_BOOTSTRAP_DATA\'\]\s*=\s*', html):
    start = match.end()
    print("Found _DRIVE_BOOTSTRAP_DATA at", start)

# Find all occurrences of strings matching river or mouth or tif or zip or png
found_strings = set()
for m in re.finditer(r'\"([^\"]*(?:river|mouth|image|Binary|NDWI|RGB|\.tif|\.zip)[^\"]*)\"', html, re.IGNORECASE):
    s = m.group(1)
    if len(s) < 150:
        found_strings.add(s)

print("\n--- Matching strings found in HTML ---")
for s in sorted(found_strings):
    print(s)
