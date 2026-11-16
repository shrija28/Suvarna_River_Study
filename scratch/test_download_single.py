import urllib.request
import os

file_id = "1xUPS_E_EZskXjb5PL2Ofk4QpkFHiaNBf"
url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
# Alternative: url = f"https://drive.google.com/uc?export=download&id={file_id}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
        print(f"Downloaded {len(data)} bytes. Content-Type: {resp.headers.get('Content-Type')}")
        if len(data) > 1000 and data.startswith(b'\x89PNG'):
            print("Successfully downloaded valid PNG file!")
            with open("scratch/test_download_1989.png", "wb") as f:
                f.write(data)
        else:
            print("Received response header/content:", data[:200])
except Exception as e:
    print("Download failed:", type(e), e)
