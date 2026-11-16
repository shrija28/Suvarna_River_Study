import sys
import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, "qt_version")

from PySide6.QtWidgets import QApplication
from backend.data_service import data_service

app = QApplication.instance() or QApplication(sys.argv)

for y in [1989, 1990, 1991, 1995, 2000, 2015, 2020, 2024, 2026]:
    pix, meta = data_service.get_raster_image_for_year(y, view_mode="first_opening")
    if pix and not pix.isNull():
        print(f"Year {y}: Loaded {meta.get('filename')} | Dimensions: {pix.width()}x{pix.height()} | Width_m: {meta.get('width_m')}")
    else:
        print(f"Year {y}: FAILED to load first_opening image")
