import urllib.request
import re
import json

url = 'https://drive.google.com/drive/folders/1KJj-D13IrlsdF7AsUi6X32kPlKeBJ7hh?usp=sharing'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched {len(html)} chars from Google Drive")
        with open("scratch/gdrive_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Look for file/folder names
        # Google Drive embeds folder data in _DRIVE_BOOTSTRAP_DATA or similar JS structures
        items = re.findall(r'\[\"([a-zA-Z0-9_-]{20,})\",\[\"([^\"]+)\"', html)
        print("Found items:", len(items))
        for item_id, name in items[:20]:
            print(f"ID: {item_id} | Name: {name}")
except Exception as e:
    print("Error fetching Google Drive page:", type(e), e)
