import sys
import os
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox --disable-gpu'
sys.path.insert(0, 'qt_version')
from PySide6.QtWidgets import QApplication
from app import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
win = MainWindow()
win.resize(1366, 768)
win.on_login_success({'id': 1, 'username': 'admin', 'role': 'Administrator'})

out_dir = r'C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be'

# Navigate to LULC Page
win.go_to_lulc()
lulc_page = win.result_page

# 1. Year 1989
lulc_page.year_combo.setCurrentText('1989')
win.repaint()
app.processEvents()

p1989 = win.grab()
p1989_path = os.path.join(out_dir, 'lulc_page_1989_verified.png')
p1989.save(p1989_path, 'PNG')
print('Saved LULC 1989 screenshot:', p1989_path)

# 2. Year 2000
lulc_page.year_combo.setCurrentText('2000')
win.repaint()
app.processEvents()

p2000 = win.grab()
p2000_path = os.path.join(out_dir, 'lulc_page_2000_verified.png')
p2000.save(p2000_path, 'PNG')
print('Saved LULC 2000 screenshot:', p2000_path)

# 3. Year 2024
lulc_page.year_combo.setCurrentText('2024')
win.repaint()
app.processEvents()

p2024 = win.grab()
p2024_path = os.path.join(out_dir, 'lulc_page_2024_verified.png')
p2024.save(p2024_path, 'PNG')
print('Saved LULC 2024 screenshot:', p2024_path)

print('All LULC screenshots saved successfully!')
