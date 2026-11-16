import urllib.request
import re
import json

folder_id = '1xT0nqj6e3VUpIoY4O2IVQ9WE6RE-2NTb'
url = f'https://drive.google.com/drive/folders/{folder_id}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched {len(html)} chars for river mouth images folder")
        with open("scratch/river_mouth_folder.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        cleaned = html.replace(r'\x22', '"').replace(r'\x5b', '[').replace(r'\x5d', ']').replace(r'\/', '/')
        matches = re.findall(rf'\["([a-zA-Z0-9_-]{{25,}})",\["{folder_id}"\],"([^"]+)","([^"]+)"', cleaned)
        print(f"Items in river mouth images: {len(matches)}")
        for item_id, name, mime in matches:
            print(f"- {name} | Type: {mime} | ID: {item_id}")
            
except Exception as e:
    print("Error:", type(e), e)
