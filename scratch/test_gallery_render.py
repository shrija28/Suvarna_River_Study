import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, "qt_version")

from PySide6.QtWidgets import QApplication, QStackedWidget
from pages.river_mouth_page import RiverMouthImagesPage

app = QApplication.instance() or QApplication(sys.argv)

stack = QStackedWidget()
page = RiverMouthImagesPage(stack=stack)
stack.addWidget(page)
stack.resize(1300, 850)
stack.show()

# Switch view mode to first_opening
page.set_view_mode("first_opening")
app.processEvents()

# Grab screenshot
pix = page.grab()
os.makedirs("scratch", exist_ok=True)
pix.save("scratch/test_gallery_first_opening.png")
print("Gallery screenshot saved to scratch/test_gallery_first_opening.png")
