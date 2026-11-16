import pandas as pd
fp = "SuvarnaProject_data/average_rainfall/Suvarna_Seasonal_Average_Rainfall_1989_2026.xlsx"
df = pd.read_excel(fp)
print("Columns:", df.columns.tolist())
print(df.head())

