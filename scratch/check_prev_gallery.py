import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor

app = QApplication.instance() or QApplication(sys.argv)
p = "C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded/media_1793686510896_f436a898.png"
img = QImage(p)
print(f"Size: {img.width()}x{img.height()}")

# Check non-background colors in the gallery area (y from 150 to 500, x from 200 to 900)
colors = set()
for y in range(160, 500, 10):
    for x in range(160, 950, 10):
        c = img.pixelColor(x, y)
        if c.green() > 150 and c.blue() > 150:
            colors.add((c.red(), c.green(), c.blue()))

print("Found bright cyan/teal pixels:", len(colors))
if colors:
    print("Sample cyan colors:", list(colors)[:5])

