import sys
from PySide6.QtGui import QImage
from PySide6.QtCore import QRect

img = QImage(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\gallery_page_current.png")
print("Gallery image size:", img.width(), img.height())

w = img.width()
h = img.height()

crop_bottom = img.copy(0, h - 150, w, 150)
crop_bottom.save(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\gallery_bottom_crop.png")

crop_top = img.copy(0, 0, w, 150)
crop_top.save(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\gallery_top_crop.png")
print("Saved crops successfully.")
