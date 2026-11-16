import sys, os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.abspath("qt_version"))

from backend.weather_service import weather_service
from backend.data_service import data_service

print("Testing WeatherService with verified seasonal rainfall data...")
weather_service.invalidate_cache()

# 1. Test load_seasonal_rainfall
rain_df = weather_service.load_seasonal_rainfall()
print(f"Loaded {len(rain_df)} rainfall records. Years: {rain_df['year'].min()} to {rain_df['year'].max()}")
assert len(rain_df) == 38, f"Expected 38 years, got {len(rain_df)}"

# 2. Check 1989, 2024, 2026 values
row_1989 = rain_df[rain_df["year"] == 1989].iloc[0]
print(f"1989 -> Monsoon: {row_1989['monsoon_rainfall_mm']:.2f} mm | Total: {row_1989['annual_rainfall_mm']:.2f} mm")
assert abs(row_1989['annual_rainfall_mm'] - 3038.496) < 0.01

row_2024 = rain_df[rain_df["year"] == 2024].iloc[0]
print(f"2024 (Peak) -> Monsoon: {row_2024['monsoon_rainfall_mm']:.2f} mm | Total: {row_2024['annual_rainfall_mm']:.2f} mm")
assert abs(row_2024['annual_rainfall_mm'] - 5043.23) < 0.01

row_2026 = rain_df[rain_df["year"] == 2026].iloc[0]
print(f"2026 (Partial) -> Monsoon: {row_2026['monsoon_rainfall_mm']:.2f} mm | Total: {row_2026['annual_rainfall_mm']:.2f} mm | Days: {row_2026['total_days']}")
assert abs(row_2026['annual_rainfall_mm'] - 2844.28) < 0.01
assert row_2026['total_days'] == 212

# 3. Test get_annual_records
records = weather_service.get_annual_records()
print(f"Generated {len(records)} annual records.")
assert len(records) == 38

# 4. Test data_service.get_weather_for_year
w_1989 = data_service.get_weather_for_year(1989)
print("data_service 1989 weather:", w_1989)
assert w_1989["available"] is True
assert abs(w_1989["annual_rainfall_mm"] - 3038.5) < 0.5

# 5. Test export_csv
out_csv = "scratch/test_exported_weather.csv"
n_exported = weather_service.export_csv(out_csv)
print(f"Exported {n_exported} rows to {out_csv}")
assert n_exported == 38

# 6. Test WeatherPage UI creation
from PySide6.QtWidgets import QApplication
from pages.weather_page import WeatherPage

app = QApplication(sys.argv)
wp = WeatherPage(None)
wp.resize(1200, 800)
wp.show()
print(f"WeatherPage created. Table rows: {wp.table.rowCount()}")
assert wp.table.rowCount() == 38

pix = wp.grab()
pix.save("scratch/weather_page_verified.png")
print("Saved screenshot to scratch/weather_page_verified.png")

print("\nALL RAINFALL DATA INTEGRATION TESTS PASSED SUCCESSFULLY!")

