import pandas as pd

df_fo = pd.read_csv('SuvarnaProject_data/First_Opening_1989_2026.csv')
print("--- First_Opening_1989_2026.csv ---")
for idx, r in df_fo.iterrows():
    if int(r['Year']) in [1989, 1990, 1994, 1995, 1996, 2000, 2015, 2020, 2024, 2026]:
        print(f"Year {int(r['Year'])}: Opening_Width_m = {r['Opening_Width_m']}")

df_res = pd.read_csv('SuvarnaProject_data/Suvarna_First_Opening_Results.csv')
print("\n--- Suvarna_First_Opening_Results.csv ---")
for idx, r in df_res.iterrows():
    if int(r['Year']) in [1989, 1990, 1994, 1996, 2000, 2015, 2020, 2024, 2026]:
        print(f"Year {int(r['Year'])}: Width (m) = {r['Width (m)']}")
