import subprocess
import os
import rasterio
import numpy as np

downloads = [
    ("1989", "1MJu5obHXSmSi4dpBGpGk98Mssmlef3M9", "Binary_1989.tif"),
    ("1990", "1DRmSI6obGEUe00U_YnvzM5uRVCJVXime", "Binary_1990_Clean.tif"),
    ("2000", "1yjc2EwNYBipyIANjvHxADfVWMspdnilD", "Binary_2000_Clean.tif"),
]

for yr, fid, fname in downloads:
    out_path = f"scratch/{fname}"
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download"
    print(f"Downloading {fname}...")
    subprocess.run(["curl.exe", "-sL", url, "-o", out_path])
    if os.path.exists(out_path):
        sz = os.path.getsize(out_path)
        print(f"  {fname}: {sz} bytes")
        with rasterio.open(out_path) as src:
            data = src.read(1)
            print(f"    shape: {data.shape}, min: {np.nanmin(data)}, max: {np.nanmax(data)}, unique: {np.unique(data)}")

