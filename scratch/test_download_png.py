import subprocess
import os

fid = "15b1ZCGgLMG1yPWIt_yc1Jk8JEIe_AWjw" # First_Opening_1995.png
out_file = "scratch/First_Opening_1995.png"

# Try downloading with curl from Google Drive export/download endpoint
urls = [
    f"https://drive.usercontent.google.com/download?id={fid}&export=download&authuser=0",
    f"https://drive.google.com/uc?export=download&id={fid}",
    f"https://drive.google.com/uc?id={fid}&export=download"
]

for url in urls:
    print(f"Trying {url}...")
    subprocess.run(["curl.exe", "-sL", url, "-o", out_file], capture_output=True)
    if os.path.exists(out_file):
        sz = os.path.getsize(out_file)
        print(f"  Downloaded size: {sz} bytes")
        with open(out_file, "rb") as f:
            header = f.read(16)
        print(f"  Header: {header}")
        if sz > 1000 and header.startswith(b"\x89PNG"):
            print("  SUCCESS! Valid PNG file downloaded!")
            break

