import os, sys, traceback
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.abspath("qt_version"))

try:
    from PySide6.QtWidgets import QApplication
    from app import MainWindow
    app = QApplication(sys.argv)
    win = MainWindow()
    print("MainWindow initialized successfully!")
    print("Available pages:", win.stack.count())
except Exception as e:
    traceback.print_exc()
