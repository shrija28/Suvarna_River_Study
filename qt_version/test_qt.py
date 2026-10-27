import sys

print("1. Program started")

from PySide6.QtWidgets import QApplication, QLabel

print("2. PySide6 imported")

app = QApplication(sys.argv)

print("3. QApplication created")

label = QLabel("Qt is working!")
label.resize(300, 100)
label.show()

print("4. Window shown")

sys.exit(app.exec())