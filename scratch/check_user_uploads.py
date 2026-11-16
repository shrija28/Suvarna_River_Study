import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication(sys.argv)
p = "C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded"
for f in os.listdir(p):
    fp = os.path.join(p, f)
    im = QImage(fp)
    print(f"{f}: size={im.width()}x{im.height()}, isNull={im.isNull()}")
