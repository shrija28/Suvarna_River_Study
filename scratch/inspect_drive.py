import urllib.request
import re
import os

url = 'https://drive.google.com/drive/folders/1Aol2e9FOR20asy8t8-ZtENTBTL9QZ2Kz?usp=sharing'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('Fetched HTML length:', len(html))
        # Look for file titles or ids
        titles = re.findall(r'\["([^"]+\.(?:png|jpg|jpeg|tif|tiff|zip|csv|pdf))"', html)
        print('Found titles:', set(titles))
        # Look for any matches of LULC or files
        general_matches = re.findall(r'["\']([a-zA-Z0-9_\-\.\s]+\.(?:png|jpg|jpeg|tif|tiff|zip|csv|pdf))["\']', html)
        print('General file matches:', set(general_matches))
except Exception as e:
    print('Error:', e)
