import re

with open('scratch/drive_folder.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern: aria-label="LULC_YYYY.png Image Shared" ... data-id="FILE_ID"
pattern = r'aria-label="([^"]*LULC_\d{4}\.png)[^"]*".*?data-id="([-\w]{25,})"'
matches = re.findall(pattern, html, re.DOTALL)
print(f"Found {len(matches)} files via aria-label + data-id:")
file_map = {}
for name, fid in matches:
    file_map[name] = fid
    print(f"  {name}: {fid}")

# Also try reverse if any missed: data-id="..." ... aria-label="..."
if len(file_map) < 30:
    pattern2 = r'data-id="([-\w]{25,})"[^>]*>.*?aria-label="([^"]*LULC_\d{4}\.png)'
    matches2 = re.findall(pattern2, html, re.DOTALL)
    for fid, name in matches2:
        if name not in file_map:
            file_map[name] = fid
            print(f"  (reverse) {name}: {fid}")

print(f"Total unique LULC files found: {len(file_map)}")
