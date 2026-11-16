import sys
sys.path.insert(0, 'qt_version')
import pandas as pd
import numpy as np
from rasterio.warp import transform as warp_transform

df_table = pd.read_csv("SuvarnaProject_data/Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv")
print("Table columns:", df_table.columns.tolist())
print("Table shape:", df_table.shape)

# Test 1989 and 2026 coords
r89 = df_table[df_table['Year'] == 1989].iloc[0]
r26 = df_table[df_table['Year'] == 2026].iloc[0]

x89, y89 = warp_transform('EPSG:4326', 'EPSG:32643', [r89['Longitude']], [r89['Latitude']])
x26, y26 = warp_transform('EPSG:4326', 'EPSG:32643', [r26['Longitude']], [r26['Latitude']])

dx = x26[0] - x89[0]
dy = y26[0] - y89[0]
dist = np.sqrt(dx**2 + dy**2)
dlat = r26['Latitude'] - r89['Latitude']
dlon = r26['Longitude'] - r89['Longitude']

print(f"1989 UTM: ({x89[0]:.2f}, {y89[0]:.2f})")
print(f"2026 UTM: ({x26[0]:.2f}, {y26[0]:.2f})")
print(f"ΔX (East): {dx:+.2f} m | ΔY (North): {dy:+.2f} m | Euclidean dist: {dist:.2f} m")
print(f"ΔLat: {dlat:+.8f}° | ΔLon: {dlon:+.8f}°")
