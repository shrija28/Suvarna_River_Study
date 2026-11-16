import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor

app = QApplication.instance() or QApplication(sys.argv)

for fname in ["media_1794502470161_b23dbcd8.jpg", "media_1794502513570_08e596eb.png", "media_1793686510896_f436a898.png"]:
    p = f"C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded/{fname}"
    img = QImage(p)
    print(f"\n--- {fname} ({img.width()}x{img.height()}) ---")
    # Sample a few pixels from the center of image card 1 (e.g. x=250, y=350)
    for (sx, sy) in [(250, 350), (450, 350), (650, 350), (850, 350)]:
        c = img.pixelColor(sx, sy)
        print(f"  Pixel at ({sx}, {sy}): R={c.red()}, G={c.green()}, B={c.blue()}")

