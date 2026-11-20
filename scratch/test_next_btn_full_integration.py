import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.resize(1600, 950)
window.show()

# 1. Login
window.login_page.input_username.setText("admin")
window.login_page.input_password.setText("admin123")
window.login_page.btn_login.click()
assert window.is_authenticated()
assert window.stack.currentIndex() == 0
print("Step 1: Logged in and verified on Home Page (index 0) -> PASSED")

# 2. Select 1989 to 2000 on Home page and click Next Step: Analysis
window.home_page.base_year.setCurrentText("1989")
window.home_page.prediction_year.setCurrentText("2000")
print("Selected on Home: Base=1989, Prediction=2000")

window.home_page.next_btn.click()
assert window.stack.currentIndex() == 1, f"Expected stack index 1, got {window.stack.currentIndex()}"
assert type(window.stack.currentWidget()).__name__ == "ResultPage"
print("Step 2: Clicked 'Next Step: Analysis  →' navigated to ResultPage (index 1) -> PASSED")

# Verify ResultPage year range
result_page = window.result_page
assert result_page.base_year == 1989 and result_page.target_year == 2000
result_years = [result_page.year_combo.itemText(i) for i in range(result_page.year_combo.count())]
print("ResultPage available year items:", result_years)
assert "1989" in result_years and "2000" in result_years and "2001" not in result_years

# Capture screenshot of ResultPage
pix = window.grab()
art_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be"
pix.save(os.path.join(art_dir, "next_btn_navigated_to_lulc_analysis.png"))
print("Saved next_btn_navigated_to_lulc_analysis.png")

# 3. Test Navigation from ResultPage to River Mouth Gallery
result_page.go_to_river_mouth()
assert window.stack.currentIndex() == 4, f"Expected stack index 4, got {window.stack.currentIndex()}"
gallery_page = window.river_mouth_page
print("Gallery active display years:", gallery_page.display_years)
assert gallery_page.display_years == list(range(1989, 2001))
print("Step 3: Navigated from ResultPage to Gallery (index 4) with synchronized years -> PASSED")

pix2 = window.grab()
pix2.save(os.path.join(art_dir, "gallery_from_lulc_nav.png"))

# 4. Return to Home page, change selection to 2015-2024, click Next Step: Analysis
gallery_page.go_to_home()
assert window.stack.currentIndex() == 0
print("Step 4: Returned to Home Page -> PASSED")

window.home_page.base_year.setCurrentText("2015")
window.home_page.prediction_year.setCurrentText("2024")
print("Updated on Home: Base=2015, Prediction=2024")

window.home_page.next_btn.click()
assert window.stack.currentIndex() == 1
assert result_page.base_year == 2015 and result_page.target_year == 2024
result_years_2 = [result_page.year_combo.itemText(i) for i in range(result_page.year_combo.count())]
print("ResultPage updated available year items:", result_years_2)
assert "2015" in result_years_2 and "2024" in result_years_2 and "2014" not in result_years_2 and "2025" not in result_years_2
print("Step 5: Next button with updated 2015-2024 selection refreshed and navigated -> PASSED")

pix3 = window.grab()
pix3.save(os.path.join(art_dir, "next_btn_navigated_2015_2024.png"))

print("ALL NEXT BUTTON & NAVIGATION INTEGRATION TESTS PASSED SUCCESSFULLY!")
