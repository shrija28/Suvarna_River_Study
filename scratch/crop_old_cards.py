import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
img = QImage("C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded/media_1793686510896_f436a898.png")

# Crop card 1 (1989) and card 6 (2020)
c1 = img.copy(150, 200, 250, 160)
c1.save("scratch/card_1989_old.png")

c6 = img.copy(370, 380, 250, 160)
c6.save("scratch/card_2020_old.png")
print("Saved old card crops!")

