import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication([])
img_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\.user_uploaded\media_1794810007503_bf6df233.jpg"
img = QImage(img_path)

# Let's crop just the numbers column (Mouth Width, Longitude, Latitude, East Shift, North Shift)
# for rows 9, 10, 11
# In 1024x418 image, the header is ~20px, each row is about (418-20)/38 ~ 10.4px
for r in [9, 10, 11, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
    y = int(22 + r * 10.3)
    img.copy(0, max(0, y - 5), img.width(), 22).save(f"scratch/row_{r}.png")
print("Saved row crops")
