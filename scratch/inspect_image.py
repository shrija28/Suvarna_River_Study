import sys
from PIL import Image

img_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\.user_uploaded\media_1794810007503_bf6df233.jpg"
img = Image.open(img_path)
print("Image size:", img.size)

# Check if pytesseract or any ocr is available
try:
    import pytesseract
    print("pytesseract available")
except ImportError:
    print("pytesseract NOT available")
