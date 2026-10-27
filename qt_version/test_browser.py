import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

app = QApplication(sys.argv)

browser = QWebEngineView()

browser.loadFinished.connect(
    lambda ok: print("Load Finished:", ok)
)

browser.urlChanged.connect(
    lambda url: print("URL:", url.toString())
)

browser.page().titleChanged.connect(
    lambda title: print("Title:", title)
)

browser.resize(1200, 800)
browser.show()

browser.load(QUrl("http://127.0.0.1:8000/webmap/index.html"))

sys.exit(app.exec())