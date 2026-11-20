import sys, os
sys.path.insert(0, r"d:\Suvarna_River_Study")
sys.path.insert(0, r"d:\Suvarna_River_Study\qt_version")
from PySide6.QtWidgets import QApplication
from qt_version.app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.show()
window.login_page.input_username.setText("admin")
window.login_page.input_password.setText("admin123")
window.login_page.btn_login.click()

dev_page = window.deviation_page
print("dev_page title:", dev_page.windowTitle())
print("dev_page base_year:", dev_page.base_year)
print("dev_page target_year:", dev_page.target_year)
print("dev_page current_deviation is None:", dev_page.current_deviation is None)
if dev_page.current_deviation:
    print("displacement_m:", dev_page.current_deviation.get("displacement_m"))
    print("area_change_km2:", dev_page.current_deviation.get("area_change_km2"))
print("Table rowCount:", dev_page.table.rowCount())
for col in range(dev_page.table.columnCount()):
    print("Col", col, dev_page.table.horizontalHeaderItem(col).text())
