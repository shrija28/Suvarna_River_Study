import sys
import os

# Add qt_version to path
sys.path.insert(0, os.path.abspath(r"d:\Suvarna_River_Study\qt_version"))

from PySide6.QtWidgets import QApplication
from app import MainWindow
from backend.data_service import data_service

def test():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # 1. Check Home page selectors
    home = window.home_page
    print("Default Base Year:", home.get_base_year())
    print("Default Prediction Year:", home.get_prediction_year())
    print("Default Selected Years:", home.get_selected_years())
    assert home.get_base_year() == 1989, f"Expected 1989, got {home.get_base_year()}"
    assert home.get_prediction_year() == 2000, f"Expected 2000, got {home.get_prediction_year()}"
    assert home.get_selected_years() == list(range(1989, 2001)), f"Expected 1989..2000, got {home.get_selected_years()}"

    # Verify data_service synchronization
    assert data_service.get_base_year() == 1989
    assert data_service.get_prediction_year() == 2000
    assert data_service.get_selected_years() == list(range(1989, 2001))

    # 2. Check River Mouth Gallery
    window.go_to_river_mouth()
    gallery = window.river_mouth_page
    print("Gallery Display Years:", gallery.display_years)
    print("Gallery Cards Count:", len(gallery.cards))
    assert len(gallery.cards) == 12, f"Expected 12 cards, got {len(gallery.cards)}"
    assert [c.year for c in gallery.cards] == list(range(1989, 2001))

    # 3. Check Deviation Page
    window.go_to_analysis()
    dev_page = window.deviation_page
    print("Deviation Base Year:", dev_page.base_year)
    print("Deviation Target Year:", dev_page.target_year)
    print("Deviation Base Label:", dev_page.lbl_base_val.text())
    print("Deviation Target Label:", dev_page.lbl_target_val.text())
    print("Deviation Table Rows:", dev_page.table.rowCount())
    assert not hasattr(dev_page, "combo_base"), "Deviation page must not have combo_base selector!"
    assert not hasattr(dev_page, "combo_target"), "Deviation page must not have combo_target selector!"
    assert dev_page.base_year == 1989
    assert dev_page.target_year == 2000
    assert dev_page.lbl_base_val.text() == "1989"
    assert dev_page.lbl_target_val.text() == "2000"
    assert dev_page.table.rowCount() == 12, f"Expected 12 rows, got {dev_page.table.rowCount()}"

    # 4. Change Home page selection to 2015 -> 2026
    home.set_selected_years([2015, 2026])
    print("\nUpdated Home Base Year:", home.get_base_year())
    print("Updated Home Prediction Year:", home.get_prediction_year())
    print("Updated Home Selected Years:", home.get_selected_years())
    assert home.get_base_year() == 2015
    assert home.get_prediction_year() == 2026

    # Verify Gallery updates
    window.go_to_river_mouth()
    print("Gallery Display Years (2015-2026):", gallery.display_years)
    print("Gallery Cards Count (2015-2026):", len(gallery.cards))
    assert len(gallery.cards) == 12, f"Expected 12 cards, got {len(gallery.cards)}"
    assert [c.year for c in gallery.cards] == list(range(2015, 2027))

    # Verify Deviation Page updates
    window.go_to_analysis()
    print("Deviation Base Year (2015-2026):", dev_page.base_year)
    print("Deviation Target Year (2015-2026):", dev_page.target_year)
    print("Deviation Base Label:", dev_page.lbl_base_val.text())
    print("Deviation Target Label:", dev_page.lbl_target_val.text())
    print("Deviation Table Rows (2015-2026):", dev_page.table.rowCount())
    assert dev_page.base_year == 2015
    assert dev_page.target_year == 2026
    assert dev_page.lbl_base_val.text() == "2015"
    assert dev_page.lbl_target_val.text() == "2026"
    assert dev_page.table.rowCount() == 12

    # 5. Validation test: Base Year > Prediction Year enforcement
    home.base_year.setCurrentText("2020")
    home.prediction_year.setCurrentText("2010")
    home.on_year_selection_changed()
    print("\nEnforced years when Base > Prediction:", home.get_selected_years())
    assert home.get_selected_years()[0] <= home.get_selected_years()[-1]

    # Reset to 1989 -> 2000
    home.set_selected_years([1989, 2000])

    print("\nALL CENTRALIZED YEAR SELECTION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test()
