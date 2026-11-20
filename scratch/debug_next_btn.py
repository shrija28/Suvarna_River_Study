import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()

# Perform login
window.on_login_success({"id": 1, "username": "admin", "role": "Researcher"})
print(f"After login: root_stack index = {window.root_stack.currentIndex()}, main stack index = {window.stack.currentIndex()}")

# Check what home_page.main_window is
print(f"home_page.main_window is: {window.home_page.main_window}")
print(f"hasattr go_to_river_mouth: {hasattr(window.home_page.main_window, 'go_to_river_mouth')}")
print(f"hasattr run_analysis: {hasattr(window.home_page.main_window, 'run_analysis')}")

# Now let's see what happens when next_btn is clicked:
print("Clicking next_btn...")
try:
    window.home_page.next_btn.click()
    print("Click succeeded!")
except Exception as e:
    import traceback
    traceback.print_exc()

print(f"After click: root_stack index = {window.root_stack.currentIndex()}, main stack index = {window.stack.currentIndex()}")
