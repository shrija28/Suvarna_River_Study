import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QSizePolicy
)

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineSettings
)


# ==========================================================
# Browser Console
# ==========================================================

class WebPage(QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f"JS [{line}] {message}")


# ==========================================================
# Home Page
# ==========================================================
class Bridge(QObject):

    def __init__(self, home):
        super().__init__()
        self.home = home


    @Slot(float, float, float, float)
    def updateAOI(self, north, south, east, west):

        print("========= AOI =========")
        print("North :", north)
        print("South :", south)
        print("East  :", east)
        print("West  :", west)
        print("=======================")

        self.home.north_lat.setText(f"{north:.6f}")
        self.home.south_lat.setText(f"{south:.6f}")
        self.home.east_lon.setText(f"{east:.6f}")
        self.home.west_lon.setText(f"{west:.6f}")
class HomePage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack
        self.build_ui()


    def build_ui(self):

        # ======================================================
        # Main Layout
        # ======================================================

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)


        # ======================================================
        # Title
        # ======================================================

        title = QLabel("River Path Deviation Prediction System")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""

            QLabel{

                font-size:26px;

                font-weight:bold;

                color:white;

                background:#1976D2;

                padding:12px;

                border-radius:8px;

            }

        """)

        main_layout.addWidget(title)


        # ======================================================
        # Map Heading
        # ======================================================

        map_title = QLabel("Interactive Satellite Map")

        map_title.setAlignment(Qt.AlignCenter)

        map_title.setStyleSheet("""

            QLabel{

                font-size:18px;

                font-weight:bold;

                padding:8px;

            }

        """)

        main_layout.addWidget(map_title)


        # ======================================================
        # Middle Layout
        # ======================================================

        middle = QHBoxLayout()

        middle.setSpacing(15)


        # ======================================================
        # LEFT PANEL
        # ======================================================

        left = QFrame()

        left.setFrameShape(QFrame.StyledPanel)

        left.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        left_layout = QVBoxLayout(left)

        left_layout.setContentsMargins(0,0,0,0)

        left_layout.setSpacing(0)


        # ======================================================
        # Browser
        # ======================================================

        self.browser = QWebEngineView()

        page = WebPage(self.browser)

        self.browser.setPage(page)
        self.channel = QWebChannel(self.browser.page())

        self.bridge = Bridge(self)

        self.channel.registerObject("bridge", self.bridge)

        page.setWebChannel(self.channel)

        settings = self.browser.settings()

        settings.setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls,
            True
        )

        settings.setAttribute(
            QWebEngineSettings.LocalContentCanAccessFileUrls,
            True
        )

        settings.setAttribute(
            QWebEngineSettings.JavascriptEnabled,
            True
        )

        map_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "webmap",
                "index.html"
            )
        )

        print("Map :", map_path)
        print("Exists :", os.path.exists(map_path))

        self.browser.load(QUrl.fromLocalFile(map_path))

        self.browser.loadFinished.connect(
            lambda ok: print("HTML Loaded :", ok)
        )

        left_layout.addWidget(self.browser)


        # ======================================================
        # RIGHT PANEL
        # ======================================================

        right = QFrame()

        right.setFrameShape(QFrame.StyledPanel)

        right.setFixedWidth(330)

        right_layout = QVBoxLayout(right)

        right_layout.setSpacing(12)


        heading = QLabel("Control Panel")

        heading.setAlignment(Qt.AlignCenter)

        heading.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        right_layout.addWidget(heading)


        # -------------------------------
        # Base Year
        # -------------------------------

        right_layout.addWidget(QLabel("Base Year"))

        self.base_year = QComboBox()

        self.base_year.addItems([
            "1989",
            "1990",
            "1991",     
            "1992",
            "1993",
            "1994", 
            "1995",
            "1996",
            "1997",
            "1998",
            "1999",
            "2000",
            "2001",
            "2002",
            "2003",
            "2004",
            "2005",
            "2006",
            "2007",
            "2008",
            "2009",
            "2010",
            "2011",
            "2012",
            "2013",
            "2014",
            "2015",
            "2016",
            "2017",
            "2018",
            "2019",
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026"
        ])

        right_layout.addWidget(self.base_year)


        # -------------------------------
        # Prediction Year
        # -------------------------------
        # -------------------------------
        # Prediction Year
        # -------------------------------

        right_layout.addWidget(QLabel("Prediction Year"))

        self.prediction_year = QComboBox()

        right_layout.addWidget(self.prediction_year)

        # Populate prediction years initially
        self.update_prediction_years()

        # Update whenever Base Year changes
        self.base_year.currentIndexChanged.connect(
            lambda: self.update_prediction_years()
        )
        
        # -------------------------------
# North Latitude
# -------------------------------

        right_layout.addWidget(QLabel("North Latitude"))

        self.north_lat = QLineEdit()
        self.north_lat.setReadOnly(True)

        right_layout.addWidget(self.north_lat)


        # -------------------------------
        # South Latitude
        # -------------------------------

        right_layout.addWidget(QLabel("South Latitude"))

        self.south_lat = QLineEdit()
        self.south_lat.setReadOnly(True)

        right_layout.addWidget(self.south_lat)


        # -------------------------------
        # East Longitude
        # -------------------------------

        right_layout.addWidget(QLabel("East Longitude"))

        self.east_lon = QLineEdit()
        self.east_lon.setReadOnly(True)

        right_layout.addWidget(self.east_lon)


        # -------------------------------
        # West Longitude
        # -------------------------------

        right_layout.addWidget(QLabel("West Longitude"))

        self.west_lon = QLineEdit()
        self.west_lon.setReadOnly(True)

        right_layout.addWidget(self.west_lon)






        # -------------------------------
        # Buttons
        # -------------------------------

        right_layout.addStretch()

# -------------------------------
# Next Button
# -------------------------------

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.go_to_result)

        self.next_btn.setMinimumHeight(40)
        self.next_btn.setStyleSheet("""
        QPushButton {
            background-color: #1976D2;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #1565C0;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }
        """)
        right_layout.addSpacing(15)

        right_layout.addWidget(self.next_btn)

        right_layout.addStretch()
        # ======================================================
        # Add Panels
        # ======================================================

        middle.addWidget(left,5)

        middle.addWidget(right,2)

        main_layout.addLayout(middle)


        # ======================================================
        # Status
        # ======================================================

        self.status = QLabel("Status : Ready")

        self.status.setStyleSheet("""

            QLabel{

                padding:8px;

                background:#EEEEEE;

                border:1px solid #CCCCCC;

            }

        """)

        main_layout.addWidget(self.status)
    def update_prediction_years(self):

        self.prediction_year.clear()

        base_year = int(self.base_year.currentText())

        for year in range(base_year + 1, 2027):
            self.prediction_year.addItem(str(year))

        print("Base Year:", base_year)
        print("Prediction Years:",
            [self.prediction_year.itemText(i)
            for i in range(self.prediction_year.count())])
    def go_to_result(self):
        print("Next button clicked.")
        print("Stack object:", self.stack)
        print("Before:", self.stack.currentIndex())

        self.stack.setCurrentIndex(1)

        print("After:", self.stack.currentIndex())