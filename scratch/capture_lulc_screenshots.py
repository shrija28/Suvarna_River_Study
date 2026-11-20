import sys
import os

sys.path.insert(0, os.path.abspath(r"d:\Suvarna_River_Study\qt_version"))

from PySide6.QtWidgets import QApplication
from app import MainWindow

artifact_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be"

def capture():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.resize(1366, 768)
    window.show()

    # Authenticate
    window.on_login_success({"username": "admin", "role": "Administrator"})
    app.processEvents()

    # 1. 1989 -> 2000 LULC Page
    window.home_page.set_selected_years([1989, 2000])
    window.go_to_lulc()
    window.result_page.load_year(1989)
    app.processEvents()

    # Capture whole LULC page
    pix_1 = window.result_page.grab()
    pix_1.save(os.path.join(artifact_dir, "lulc_filtered_1989_2000.png"))
    print("Saved lulc_filtered_1989_2000.png")

    # Capture LULC Files Card Table (filtered to 1989-2000)
    pix_table = window.result_page.files_card.grab()
    pix_table.save(os.path.join(artifact_dir, "lulc_table_filtered_1989_2000.png"))
    print("Saved lulc_table_filtered_1989_2000.png")

    # 2. Year 1995 missing data display
    window.result_page.load_year(1995)
    app.processEvents()
    pix_missing = window.result_page.grab()
    pix_missing.save(os.path.join(artifact_dir, "lulc_missing_year_1995.png"))
    print("Saved lulc_missing_year_1995.png")

    # 3. 2015 -> 2026 LULC Page
    window.home_page.set_selected_years([2015, 2026])
    window.go_to_lulc()
    window.result_page.load_year(2024)
    app.processEvents()

    pix_2 = window.result_page.grab()
    pix_2.save(os.path.join(artifact_dir, "lulc_filtered_2015_2026.png"))
    print("Saved lulc_filtered_2015_2026.png")

    # Capture 2015-2026 table
    pix_table_2 = window.result_page.files_card.grab()
    pix_table_2.save(os.path.join(artifact_dir, "lulc_table_filtered_2015_2026.png"))
    print("Saved lulc_table_filtered_2015_2026.png")

if __name__ == "__main__":
    capture()
