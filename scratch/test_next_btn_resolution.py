import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
win = MainWindow()
win.resize(1600, 950)
win.show()

# 1. Login
win.login_page.input_username.setText("admin")
win.login_page.input_password.setText("admin123")
win.login_page.handle_login()

assert win.stack.currentIndex() == 0, f"Expected Home Page (0), got {win.stack.currentIndex()}"
print("[PASS] Step 1: Logged in and verified on Home Page")

# 2. Configure Home page years to 1989 -> 2000
home = win.home_page
home.base_year.setCurrentText("1989")
home.prediction_year.setCurrentText("2000")
print("[INFO] Selected Home years: Base=1989, Prediction=2000")

# 3. Click Next Step: Analysis button
print("[INFO] Clicking 'Next Step: Analysis  →'...")
home.next_btn.click()

# Verify it navigates to River Mouth Satellite Imagery Gallery (page 4)
curr_idx = win.stack.currentIndex()
curr_widget = win.stack.currentWidget()
print(f"[INFO] Current stack index after next_btn click: {curr_idx} ({type(curr_widget).__name__})")
assert curr_idx == 4, f"Expected Gallery Page (4), got {curr_idx}"
gallery = win.river_mouth_page
print(f"[INFO] Gallery display years: {gallery.display_years}")
assert gallery.display_years == list(range(1989, 2001)), f"Unexpected gallery years: {gallery.display_years}"
print("[PASS] Step 2: Next Step: Analysis navigated to River Mouth Satellite Imagery Gallery with 1989–2000!")

# Capture screenshot of gallery from next_btn
art_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be"
win.grab().save(os.path.join(art_dir, "next_btn_navigated_gallery_1989_2000.png"))
print("[INFO] Saved next_btn_navigated_gallery_1989_2000.png")

# 4. From Gallery, click Analyze Deviation -> Page 5
print("[INFO] Clicking 'Analyze Deviation  →' from Gallery...")
gallery.header_analyze_btn.click()
assert win.stack.currentIndex() == 5, f"Expected Deviation Page (5), got {win.stack.currentIndex()}"
dev_page = win.deviation_page
assert dev_page.base_year == 1989 and dev_page.target_year == 2000
assert dev_page.table.rowCount() == 12, f"Expected 12 rows in deviation table, got {dev_page.table.rowCount()}"
print("[PASS] Step 3: Navigated from Gallery to Deviation Analysis (1989–2000, 12 rows)!")

# 5. Return to Home, test direct LULC button
dev_page.go_to_home()
assert win.stack.currentIndex() == 0
print("[INFO] Returned to Home page. Testing direct LULC Analysis button...")
home.btn_quick_lulc.click()
assert win.stack.currentIndex() == 1, f"Expected LULC Page (1), got {win.stack.currentIndex()}"
result_page = win.result_page
assert result_page.base_year == 1989 and result_page.target_year == 2000
print("[PASS] Step 4: Direct LULC button navigated to ResultPage with 1989–2000!")

# 6. Return to Home, test direct Deviation Report button
result_page.go_to_home()
assert win.stack.currentIndex() == 0
print("[INFO] Returned to Home page. Testing direct Deviation Report button...")
home.btn_quick_dev.click()
assert win.stack.currentIndex() == 5, f"Expected Deviation Page (5), got {win.stack.currentIndex()}"
print("[PASS] Step 5: Direct Deviation Report button navigated to Deviation Page with 1989–2000!")

# 7. Return to Home, change to 2015-2024, click Next Step: Analysis
dev_page.go_to_home()
assert win.stack.currentIndex() == 0
home.base_year.setCurrentText("2015")
home.prediction_year.setCurrentText("2024")
print("[INFO] Changed Home selection to 2015–2024. Clicking 'Next Step: Analysis  →'...")
home.next_btn.click()
assert win.stack.currentIndex() == 4
assert gallery.display_years == list(range(2015, 2025))
print(f"[PASS] Step 6: Next button with updated 2015–2024 navigated to Gallery with {len(gallery.display_years)} years!")

# Save final screenshot of Home page with new buttons
gallery.go_to_home()
win.grab().save(os.path.join(art_dir, "home_page_with_all_next_buttons_verified.png"))
print("[INFO] Saved home_page_with_all_next_buttons_verified.png")

print("ALL NEXT BUTTON RESOLUTION TESTS PASSED SUCCESSFULLY!")
