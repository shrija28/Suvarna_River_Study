import sys
from PySide6.QtGui import QImage

img = QImage(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\deviation_page_after_analyze_click.png")
print("Deviation image size:", img.width(), img.height())

w = img.width()
h = img.height()

crop_top = img.copy(0, 0, w, 200)
crop_top.save(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\deviation_top_crop.png")

crop_mid = img.copy(0, 200, w, 400)
crop_mid.save(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\deviation_mid_crop.png")

print("Saved deviation crops.")
