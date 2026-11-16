import sys
import rasterio
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor

app = QApplication.instance() or QApplication([])

with rasterio.open("scratch/Binary_1989.tif") as src:
    data = src.read(1)

h, w = data.shape
img = QImage(w, h, QImage.Format_ARGB32)
img.fill(QColor(3, 27, 24))

for y in range(h):
    for x in range(w):
        if data[y, x] == 1:
            img.setPixelColor(x, y, QColor(0, 191, 165))  # Cyan/Teal
        else:
            img.setPixelColor(x, y, QColor(3, 27, 24))

img.save("scratch/test_render_1989.png")
print("Saved scratch/test_render_1989.png")

