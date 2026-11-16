import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication([])

for yr in ["2000", "2020", "2026"]:
    p = f"scratch/First_Opening_{yr}.png"
    img = QImage(p)
    preview = img.scaledToWidth(800)
    preview.save(f"scratch/preview_{yr}.png")
    print(f"Saved preview_{yr}.png ({preview.width()}x{preview.height()})")

