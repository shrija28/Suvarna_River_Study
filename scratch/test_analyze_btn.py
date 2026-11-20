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
print("Logged in successfully.")

# 2. Go to River Mouth Page
window.go_to_river_mouth()
print(f"Current stack index: {window.stack.currentIndex()} ({type(window.stack.currentWidget()).__name__})")

# 3. Click Analyze button on River Mouth Page
print("Clicking analyze_btn...")
try:
    window.river_mouth_page.analyze_btn.click()
    print("Clicked analyze_btn successfully without crash.")
except Exception as e:
    import traceback
    traceback.print_exc()

print(f"Current stack index after click: {window.stack.currentIndex()} ({type(window.stack.currentWidget()).__name__})")
