from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QComboBox,
    QCheckBox,
    QLineEdit,
)
from theme import (
    DARK_EMERALD,
    PANEL_SURFACE,
    PANEL_GREEN,
    BORDER_COLOR,
    BORDER_SUBTLE,
    TEAL,
    MINT,
    SOFT_LIME,
    WARM_IVORY,
    MUTED_SAGE,
)
from icons import get_icon


class SettingsPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # Header
        top_bar = QHBoxLayout()
        back = QPushButton("← Back to Map")
        back.setIcon(get_icon("home", color=MINT, size=16))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        back.clicked.connect(self.go_back)
        top_bar.addWidget(back)
        top_bar.addStretch()

        title_box = QVBoxLayout()
        title = QLabel("System Settings & Model Parameters")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WARM_IVORY};")
        sub = QLabel("GIS coordinate reference systems, data caching, and inference parameters")
        sub.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        top_bar.addLayout(title_box)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Settings Card Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        # Card 1: Geospatial Coordinates & CRS
        c1 = self.create_card("Coordinate Reference System (CRS)")
        c1_l = QVBoxLayout(c1)
        c1_l.setContentsMargins(14, 14, 14, 14)
        c1_l.setSpacing(10)

        c1_l.addWidget(QLabel("Project Working CRS:"))
        crs_combo = QComboBox()
        crs_combo.addItems([
            "EPSG:32643 - WGS 84 / UTM Zone 43N (Recommended for Udupi / Karnataka)",
            "EPSG:4326 - WGS 84 (Geographic Lat/Lon)",
            "EPSG:3857 - WGS 84 / Pseudo-Mercator (Web Tile Standard)"
        ])
        c1_l.addWidget(crs_combo)

        c1_l.addWidget(QLabel("Study Area Bounding Preset:"))
        box_combo = QComboBox()
        box_combo.addItems([
            "Kodi Bengre Estuary (13.40°N - 13.48°N, 74.66°E - 74.74°E)",
            "Upper Swarna Basin (Kallianpur - Kemmannu Sector)",
            "Malpe Port & Coastal Zone (13.34°N - 13.40°N)"
        ])
        c1_l.addWidget(box_combo)

        cb1 = QCheckBox("Automatically re-project imported GeoJSON files to project CRS")
        cb1.setChecked(True)
        c1_l.addWidget(cb1)
        c1_l.addStretch()
        grid.addWidget(c1, 0, 0)

        # Card 2: Cache & Performance
        c2 = self.create_card("Map Caching & Storage")
        c2_l = QVBoxLayout(c2)
        c2_l.setContentsMargins(14, 14, 14, 14)
        c2_l.setSpacing(10)

        c2_l.addWidget(QLabel("Tile Cache Storage Path:"))
        path_edit = QLineEdit("d:/Suvarna_River_Study/cache/tiles")
        path_edit.setReadOnly(True)
        c2_l.addWidget(path_edit)

        c2_l.addWidget(QLabel("Offline Tile Cache Retention:"))
        cache_combo = QComboBox()
        cache_combo.addItems(["Cache Most Recent 500 MB", "Cache All Visited Estuary Tiles", "Session-Only (Clear on Exit)"])
        c2_l.addWidget(cache_combo)

        cb2 = QCheckBox("Hardware accelerated OpenGL rendering for Qt WebEngine")
        cb2.setChecked(True)
        c2_l.addWidget(cb2)
        c2_l.addStretch()
        grid.addWidget(c2, 0, 1)

        main_layout.addLayout(grid)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        save_btn = QPushButton("Save Preferences")
        save_btn.setIcon(get_icon("settings", color=DARK_EMERALD, size=16))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                border: none;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {SOFT_LIME};
            }}
        """)
        btn_row.addWidget(save_btn)
        main_layout.addLayout(btn_row)

    def create_card(self, title):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        t = QLabel(title)
        t.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {WARM_IVORY};
            background-color: {DARK_EMERALD};
            padding: 8px 12px;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
            border-bottom: 1px solid {BORDER_SUBTLE};
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(t)
        return card

    def go_back(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(0)
        else:
            self.stack.setCurrentIndex(0)
