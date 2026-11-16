import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication([])
img_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\.user_uploaded\media_1794810007503_bf6df233.jpg"
img = QImage(img_path)
print("Width:", img.width(), "Height:", img.height())

w = img.width()
h = img.height()

# Save 3 chunks
chunk_h = h // 3
img.copy(0, 0, w, chunk_h + 30).save("scratch/chunk1.png")
img.copy(0, chunk_h - 20, w, chunk_h + 40).save("scratch/chunk2.png")
img.copy(0, 2 * chunk_h - 20, w, h - 2 * chunk_h + 20).save("scratch/chunk3.png")
print("Saved 3 chunks")
