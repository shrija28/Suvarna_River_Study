import os

for root, dirs, files in os.walk("SuvarnaProject_data"):
    tifs = [f for f in files if f.endswith(('.tif', '.png', '.jpg', '.jpeg'))]
    if tifs:
        print(f"Folder {root}: {len(tifs)} images. Sample: {tifs[:10]}")

for root, dirs, files in os.walk("assets"):
    imgs = [f for f in files if f.endswith(('.tif', '.png', '.jpg', '.jpeg'))]
    if imgs:
        print(f"Folder {root}: {len(imgs)} images. Sample: {imgs}")

