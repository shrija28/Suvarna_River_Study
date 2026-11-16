import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication([])

p = "C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded/media_1794502470161_b23dbcd8.jpg"
img = QImage(p)

preview = img.scaledToWidth(800)
preview.save("scratch/view_b23dbcd8.png")
print("Saved scratch/view_b23dbcd8.png!")

