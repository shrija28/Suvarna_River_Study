import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("scratch/test_fo_1995.png")

# Sample colors at different regions
w, h = img.width(), img.height()
print(f"Dimensions: {w}x{h}")
samples = [
    (w//4, h//4), (w//2, h//4), (3*w//4, h//4),
    (w//4, h//2), (w//2, h//2), (3*w//4, h//2),
    (w//4, 3*h//4), (w//2, 3*h//4), (3*w//4, 3*h//4)
]
for x, y in samples:
    c = img.pixelColor(x, y)
    print(f"Sample at ({x}, {y}): R={c.red()}, G={c.green()}, B={c.blue()}")

