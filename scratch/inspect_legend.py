from PySide6.QtGui import QImage
import sys

img = QImage(r"D:\Suvarna_River_Study\SuvarnaProject_data\river mouth images\First_Opening\First_Opening_1989.png")
w, h = img.width(), img.height()
print(f"1989 dimensions: {w}x{h}")

crop_tl = img.copy(0, 0, int(w * 0.4), int(h * 0.4))
crop_tl.save("scratch/crop_1989_tl.png")

crop_bl = img.copy(0, int(h * 0.6), int(w * 0.4), int(h * 0.4))
crop_bl.save("scratch/crop_1989_bl.png")

print("Saved QImage crops")
