import pandas as pd
import rasterio.warp

df = pd.read_csv("SuvarnaProject_data/Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv")
valid = df.dropna(subset=['Longitude', 'Latitude'])
xs, ys = rasterio.warp.transform('EPSG:4326', 'EPSG:32643', valid['Longitude'].tolist(), valid['Latitude'].tolist())
for i in range(min(15, len(valid))):
    r = valid.iloc[i]
    print(f"Year {int(r['Year'])}: UTM_X={xs[i]:.1f}, UTM_Y={ys[i]:.1f}, EastShift={r['East Shift (m)']}, NorthShift={r['North Shift (m)']}")
