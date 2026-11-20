import urllib.request
import os

fid = '1VPVPU27eLRXt1lc2UXdFK5zGUFJ21OQk'
test_path = 'scratch/test_LULC_1989.png'

# Direct download url candidates
urls = [
    f'https://drive.usercontent.google.com/download?id={fid}&export=download',
    f'https://drive.google.com/uc?export=download&id={fid}',
]

for u in urls:
    try:
        print(f"Trying {u}...")
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            print(f"Downloaded {len(data)} bytes, Content-Type: {resp.headers.get('Content-Type')}")
            if len(data) > 1000 and data.startswith(b'\x89PNG'):
                with open(test_path, 'wb') as f:
                    f.write(data)
                print(f"Successfully saved valid PNG to {test_path}!")
                break
    except Exception as e:
        print(f"Failed: {e}")
