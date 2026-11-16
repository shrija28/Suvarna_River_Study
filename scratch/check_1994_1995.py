import sys
import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, "qt_version")

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from backend.deviation_service import deviation_service

try:
    d1994 = deviation_service.get_year_mouth_data(1994)
    d1995 = deviation_service.get_year_mouth_data(1995)

    print("1994 utm:", d1994["mouth_utm_x"], d1994["mouth_utm_y"], "lat/lon:", d1994["mouth_lat"], d1994["mouth_lon"])
    print("1995 utm:", d1995["mouth_utm_x"], d1995["mouth_utm_y"], "lat/lon:", d1995["mouth_lat"], d1995["mouth_lon"])

    dev = deviation_service.calculate_deviation(1989, 2026)
    for row in dev["timeseries"]:
        if row["year"] in [1993, 1994, 1995, 1996]:
            print(f"Year {row['year']}: disp={row['displacement_m']:.2f}m, dx={row['dx_m']:.2f}m, dy={row['dy_m']:.2f}m, FoWidth={row['opening_width_m']}")
except Exception as e:
    import traceback
    traceback.print_exc()
