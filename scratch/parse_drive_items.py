import urllib.request
import re
import json

url = 'https://drive.google.com/drive/folders/1Aol2e9FOR20asy8t8-ZtENTBTL9QZ2Kz?usp=sharing'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Save html to scratch/drive_folder.html so we can analyze it locally
with open('scratch/drive_folder.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Wrote scratch/drive_folder.html')
