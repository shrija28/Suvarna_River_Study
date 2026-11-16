import pandas as pd
import numpy as np

fp = "SuvarnaProject_data/average_rainfall/Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"
df = pd.read_csv(fp)

# Clean numeric conversions
for col in ["Pre-monsoon average (mm/day)", "Monsoon average (mm/day)", "Post-monsoon average (mm/day)",
            "Pre-monsoon days", "Monsoon days", "Post-monsoon days"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

df["pre_monsoon_mm"] = df["Pre-monsoon average (mm/day)"] * df["Pre-monsoon days"]
df["monsoon_mm"] = df["Monsoon average (mm/day)"] * df["Monsoon days"]
df["post_monsoon_mm"] = df["Post-monsoon average (mm/day)"] * df["Post-monsoon days"]
df["annual_rainfall_mm"] = df["pre_monsoon_mm"] + df["monsoon_mm"] + df["post_monsoon_mm"]
df["total_days"] = df["Pre-monsoon days"] + df["Monsoon days"] + df["Post-monsoon days"]

print(df[["Year", "pre_monsoon_mm", "monsoon_mm", "post_monsoon_mm", "annual_rainfall_mm", "total_days"]].head(10))
print("\nTail (recent years):")
print(df[["Year", "pre_monsoon_mm", "monsoon_mm", "post_monsoon_mm", "annual_rainfall_mm", "total_days"]].tail(5))

print("\nMean annual rainfall:", df["annual_rainfall_mm"].mean())
print("Min annual rainfall:", df["annual_rainfall_mm"].min(), "Year:", df.loc[df["annual_rainfall_mm"].idxmin(), "Year"])
print("Max annual rainfall:", df["annual_rainfall_mm"].max(), "Year:", df.loc[df["annual_rainfall_mm"].idxmax(), "Year"])

