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

    # Authenticate into main application
    window.on_login_success({"username": "admin", "role": "Administrator"})
    app.processEvents()

    # Set Home page to 1989 -> 2000
    window.home_page.set_selected_years([1989, 2000])

    # 1. Capture Home Page
    window.navigate_to_page(0)
    app.processEvents()
    home_pix = window.home_page.grab()
    home_pix.save(os.path.join(artifact_dir, "centralized_home_page.png"))
    print("Saved centralized_home_page.png", home_pix.size().toTuple())

    # 2. Capture Gallery Page
    window.go_to_river_mouth()
    app.processEvents()
    gallery_pix = window.river_mouth_page.grab()
    gallery_pix.save(os.path.join(artifact_dir, "centralized_gallery_page_1989_2000.png"))
    print("Saved centralized_gallery_page_1989_2000.png", gallery_pix.size().toTuple())

    # 3. Capture Deviation Page
    window.go_to_analysis()
    app.processEvents()
    dev_pix = window.deviation_page.grab()
    dev_pix.save(os.path.join(artifact_dir, "centralized_deviation_page_1989_2000.png"))
    print("Saved centralized_deviation_page_1989_2000.png", dev_pix.size().toTuple())

    # 4. Capture Deviation Header Bar
    header_pix = window.deviation_page.year_badge_frame.grab()
    header_pix.save(os.path.join(artifact_dir, "centralized_deviation_header_badge.png"))
    print("Saved centralized_deviation_header_badge.png", header_pix.size().toTuple())

if __name__ == "__main__":
    capture()
