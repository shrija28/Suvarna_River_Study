import os
import rasterio
import numpy as np

for yr in [1989, 1990, 1995, 2000, 2015, 2020, 2024, 2026]:
    for typ in ["RGB", "NDWI", "Binary"]:
        if typ == "RGB":
            p = f"SuvarnaProject_data/river mouth images/image_RGB/RGB_{yr}.tif"
        elif typ == "NDWI":
            p = f"SuvarnaProject_data/river mouth images/NDWI_images/NDWI_{yr}.tif"
        else:
            p = f"SuvarnaProject_data/river mouth images/Binary/Binary_{yr}.tif"
        
        if os.path.exists(p):
            with rasterio.open(p) as src:
                print(f"{typ}_{yr}: shape={src.shape}, bounds={src.bounds}")
        else:
            print(f"{typ}_{yr}: NOT FOUND")

