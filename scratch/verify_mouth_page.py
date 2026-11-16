import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"

project_root = r"d:\Suvarna_River_Study"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "qt_version"))

from PySide6.QtWidgets import QApplication, QStackedWidget
from qt_version.pages.river_mouth_page import RiverMouthImagesPage

app = QApplication.instance() or QApplication([])

stack = QStackedWidget()
page = RiverMouthImagesPage(stack)
stack.addWidget(page)
stack.resize(1280, 800)
page.show()

# Set view mode to first_opening
page.set_view_mode("first_opening")

print("Display years:", page.display_years)
print("Number of cards:", len(page.cards))

for card in page.cards:
    print(f"Year {card.year}: meta='{card.meta_lbl.text()}'")

# Render screenshot
pixmap = stack.grab()
out_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\scratch\river_mouth_gallery_verified.png"
pixmap.save(out_path)
print("Saved screenshot to:", out_path)
