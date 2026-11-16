import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("scratch/test_fo_1995.png")
print("Image width:", img.width(), "height:", img.height(), "format:", img.format(), "isNull:", img.isNull())

