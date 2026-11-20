import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.show()

# Find login widgets
login_page = window.login_page
login_page.input_username.setText("admin")
login_page.input_password.setText("admin123")
print("Clicking signin button...")
login_page.btn_login.click()

print(f"Logged in? is_authenticated = {window.is_authenticated()}")
print(f"root_stack index = {window.root_stack.currentIndex()}")
print(f"main stack index = {window.stack.currentIndex()}")

# Now on Home page, let's click next_btn
print("Clicking next_btn on Home page...")
try:
    window.home_page.next_btn.click()
    print("Clicked next_btn successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()

print(f"After next_btn click: stack index = {window.stack.currentIndex()}")
current_widget = window.stack.currentWidget()
print(f"Current page widget: {type(current_widget).__name__}")
