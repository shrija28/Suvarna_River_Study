import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication([])

up_dir = "C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded"
for f in os.listdir(up_dir):
    fp = os.path.join(up_dir, f)
    img = QImage(fp)
    if img.width() == 1024 and img.height() in [576, 542]:
        # Check title text area (x=150..400, y=140..170)
        # Just check color variation
        print(f"{f}: {img.width()}x{img.height()}")

