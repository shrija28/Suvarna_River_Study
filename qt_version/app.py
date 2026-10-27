import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
)
from PySide6.QtWebEngineCore import QWebEngineProfile
from pages.home import HomePage
from pages.result import ResultPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("River Path Deviation Prediction System")
        self.resize(1600, 900)

        self.stack = QStackedWidget()

        self.home_page = HomePage(self.stack)
        self.result_page = ResultPage(self.stack)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.result_page)

        self.setCentralWidget(self.stack)


app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()

sys.exit(app.exec())