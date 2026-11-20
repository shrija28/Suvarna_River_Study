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
pix = window.grab()
art_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be"
pix.save(os.path.join(art_dir, "gallery_page_current.png"))
print("Saved gallery_page_current.png")

# Now let's click analyze_btn and see what happens visually
window.river_mouth_page.analyze_btn.click()
pix2 = window.grab()
pix2.save(os.path.join(art_dir, "deviation_page_after_analyze_click.png"))
print("Saved deviation_page_after_analyze_click.png")
