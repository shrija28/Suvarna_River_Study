import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("scratch/test_fo_1995.png")

w, h = img.width(), img.height()
non_black = 0
colors = []

# sample every 10 pixels
for y in range(0, h, 10):
    for x in range(0, w, 10):
        c = img.pixelColor(x, y)
        if c.red() > 20 or c.green() > 20 or c.blue() > 20:
            non_black += 1
            if len(colors) < 15:
                colors.append((x, y, c.red(), c.green(), c.blue()))

print(f"Non-black pixel samples: {non_black}")
print("Sample colors (x, y, R, G, B):", colors)

