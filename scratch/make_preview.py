import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("scratch/test_fo_1995.png")

# Scale down to 800x533 and save to scratch/preview_1995.png
preview = img.scaled(800, 533)
preview.save("scratch/preview_1995.png")
print("Saved scratch/preview_1995.png (800x533)")

