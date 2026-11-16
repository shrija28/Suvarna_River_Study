import os
import rasterio

for folder in ["river mouth images", "river mouth images/image_RGB", "river mouth images/NDWI_images", "river mouth images/Binary"]:
    p = os.path.join("SuvarnaProject_data", folder)
    if os.path.exists(p):
        files = [f for f in os.listdir(p) if f.endswith('.tif')]
        print(f"\n--- Folder {folder}: {len(files)} tifs ---")
        for f in files[:5]:
            fp = os.path.join(p, f)
            sz = os.path.getsize(fp)
            try:
                with rasterio.open(fp) as src:
                    print(f"  {f}: size={sz}, shape=({src.count}, {src.height}, {src.width}), crs={src.crs}, res={src.res}, dtypes={src.dtypes}")
            except Exception as e:
                print(f"  {f}: size={sz}, err={e}")

