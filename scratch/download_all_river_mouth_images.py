import urllib.request
import re
import os
import shutil
import time

# 1. Target directory
target_dir = r"D:\Suvarna_River_Study\SuvarnaProject_data\river mouth images\First_Opening"
backup_dir = r"D:\Suvarna_River_Study\SuvarnaProject_data\river mouth images\First_Opening_backup"

os.makedirs(target_dir, exist_ok=True)
os.makedirs(backup_dir, exist_ok=True)

# Backup existing files
for f in os.listdir(target_dir):
    src = os.path.join(target_dir, f)
    dst = os.path.join(backup_dir, f)
    if os.path.isfile(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)

print("Backup created in:", backup_dir)

# 2. Parse file list from scratch/river_mouth_folder.html
with open("scratch/river_mouth_folder.html", "r", encoding="utf-8") as f:
    html = f.read()

cleaned = html.replace(r'\x22', '"').replace(r'\x5b', '[').replace(r'\x5d', ']').replace(r'\/', '/')
folder_id = '1xT0nqj6e3VUpIoY4O2IVQ9WE6RE-2NTb'

matches = re.findall(rf'\["([a-zA-Z0-9_-]{{25,}})",\["{folder_id}"\],"([^"]+)","([^"]+)"', cleaned)
print(f"Total files to download: {len(matches)}")

success_count = 0
failed = []

for idx, (file_id, filename, mime) in enumerate(matches, 1):
    save_path = os.path.join(target_dir, filename)
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    downloaded = False
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 1000 and data.startswith(b'\x89PNG'):
                    with open(save_path, "wb") as out_f:
                        out_f.write(data)
                    print(f"[{idx}/{len(matches)}] Downloaded {filename} ({len(data):,} bytes)")
                    success_count += 1
                    downloaded = True
                    break
                else:
                    print(f"[{idx}/{len(matches)}] Attempt {attempt+1} invalid content for {filename}: {len(data)} bytes")
                    time.sleep(1)
        except Exception as e:
            print(f"[{idx}/{len(matches)}] Attempt {attempt+1} error downloading {filename}: {e}")
            time.sleep(2)
            
    if not downloaded:
        failed.append((filename, file_id))

print(f"\nFinished: {success_count}/{len(matches)} files downloaded successfully.")
if failed:
    print("Failed files:", failed)
