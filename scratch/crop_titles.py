import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

app = QApplication.instance() or QApplication([])

up_dir = "C:/Users/LENOVO/.gemini/antigravity/brain/92f670cd-818e-4f15-aa32-6f8e546a64be/.user_uploaded"
files = [
    "media_1793287380544_ccb36f22.jpg",
    "media_1793681673403_84a9c049.png",
    "media_1793686262509_f7695738.png",
    "media_1793686510896_f436a898.png",
    "media_1793695797897_3b32d79f.jpg",
    "media_1793721847132_86c72c74.jpg",
    "media_1793807669324_206225d0.jpg",
    "media_1794502470161_b23dbcd8.jpg",
    "media_1794502513570_08e596eb.png"
]

for f in files:
    fp = os.path.join(up_dir, f)
    img = QImage(fp)
    crop = img.copy(15, 140, 200, 50)
    crop.save(f"scratch/title_{f[:15]}.png")
print("Saved crops!")

