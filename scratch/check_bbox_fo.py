import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("scratch/test_fo_1995.png")

w, h = img.width(), img.height()
# Find bounding box of content
min_x, max_x = w, 0
min_y, max_y = h, 0

unique_colors = set()

for y in range(0, h, 20):
    for x in range(0, w, 20):
        c = img.pixelColor(x, y)
        if c.red() > 20 or c.green() > 20 or c.blue() > 20:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
            unique_colors.add((c.red()//30*30, c.green()//30*30, c.blue()//30*30))

print(f"Content bbox: X={min_x}..{max_x}, Y={min_y}..{max_y}")
print(f"Unique approximate colors count: {len(unique_colors)}")
print("Color groups:", list(unique_colors)[:15])

