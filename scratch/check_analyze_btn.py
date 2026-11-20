import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study")

from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.resize(1600, 950)
window.show()

window.login_page.input_username.setText("admin")
window.login_page.input_password.setText("admin123")
window.login_page.btn_login.click()

window.go_to_river_mouth()
page = window.river_mouth_page
print("analyze_btn text:", page.analyze_btn.text())
print("analyze_btn isVisible:", page.analyze_btn.isVisible())
print("analyze_btn isEnabled:", page.analyze_btn.isEnabled())
print("analyze_btn geometry:", page.analyze_btn.geometry())
print("analyze_btn pos:", page.analyze_btn.pos())
print("analyze_btn mapToGlobal:", page.analyze_btn.mapToGlobal(page.analyze_btn.pos()))
print("window size:", window.size())

# Check sidebar buttons
for btn in page.findChildren(QPushButton):
    print("Button:", btn.text(), "visible:", btn.isVisible(), "geom:", btn.geometry())
