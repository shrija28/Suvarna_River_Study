import subprocess
import os

files_to_download = [
    ("2000", "1URRXdKMh43RRu_WAF_11r5hPAZESITKO"),
    ("2015", "1LAz3RFzoU_oVBuvbHdbVvXBC16QheD9J"),
    ("2020", "1hXfJo0TR3Y8_xJn5fIdfCcbenBoyDbVx"),
    ("2024", "1D6pnmAdODXhD_MYyKnsVLEvI3T_EzTNv"),
    ("2026", "1ByK6vmygrZfpCztgzN_5UV5QTUvPhZut"),
]

for yr, fid in files_to_download:
    out_path = f"scratch/First_Opening_{yr}.png"
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download"
    print(f"Downloading {yr}...")
    subprocess.run(["curl.exe", "-sL", url, "-o", out_path])
    if os.path.exists(out_path):
        print(f"  {yr}: {os.path.getsize(out_path)} bytes")

