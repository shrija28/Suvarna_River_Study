import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study\qt_version")
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from backend.deviation_service import deviation_service

print("Available years:", deviation_service.get_available_years())

for b, t in [(1989, 2000), (1989, 2026), (1989, 1989), (2000, 2000), (2015, 2024), (1995, 2005)]:
    try:
        res = deviation_service.calculate_deviation(b, t)
        print(f"calculate_deviation({b}, {t}): {'OK' if res else 'None'}")
    except Exception as e:
        import traceback
        print(f"calculate_deviation({b}, {t}): EXCEPTION {e}")
        traceback.print_exc()
