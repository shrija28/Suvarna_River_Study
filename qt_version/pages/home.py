import os
import re
from PySide6.QtCore import Qt, QUrl, QObject, Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QSizePolicy,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineSettings,
)

from theme import (
    BG_DARK,
    DARK_EMERALD,
    PANEL_GREEN,
    PANEL_SURFACE,
    BORDER_COLOR,
    BORDER_SUBTLE,
    TEAL,
    MINT,
    SOFT_LIME,
    WARM_IVORY,
    MUTED_SAGE,
    AMBER,
    INPUT_BG,
)
from icons import get_icon, get_pixmap


# ============================================================================
# WebEngine Page Console Logging
# ============================================================================
class WebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f"JS [{line}] {message}")


# ============================================================================
# QWebChannel Bridge
# ============================================================================
class Bridge(QObject):
    def __init__(self, home):
        super().__init__()
        self.home = home

    @Slot(float, float, float, float)
    def updateAOI(self, north, south, east, west):
        self.home.set_aoi_coords(north, south, east, west)

    @Slot(str)
    def setMapStatus(self, status):
        self.home.set_map_status(status)

    @Slot(str)
    def setMapModeName(self, mode_name):
        self.home.set_map_mode_name(mode_name)

    @Slot(float, float)
    def updateCursorCoords(self, lat, lon):
        self.home.update_cursor_coords(lat, lon)

    @Slot(str, float, float)
    def updateLocation(self, location_name, lat, lon):
        self.home.set_location(location_name, lat, lon)

    @Slot()
    def clearAOI(self):
        self.home.clear_aoi()


# ============================================================================
# Home Page Widget
# ============================================================================
class HomePage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.active_mode = "map"
        self.current_location_name = "Kodi Bengre, Udupi, Karnataka, India"
        self.current_lat = 13.4380
        self.current_lon = 74.6980
        self.build_ui()

    def build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(14)

        # ====================================================================
        # LEFT/CENTER: Interactive Map Panel & Bottom Information Cards
        # ====================================================================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # --------------------------------------------------------------------
        # Map Panel Header (Title, Subtitle, and Compact Map Style Controls)
        # --------------------------------------------------------------------
        map_header = QFrame()
        map_header.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 4px 10px;
            }}
        """)
        header_layout = QHBoxLayout(map_header)
        header_layout.setContentsMargins(8, 6, 8, 6)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        self.title_lbl = QLabel("Interactive Estuarine Mouth Dynamics Map")
        self.title_lbl.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {WARM_IVORY};
            letter-spacing: 0.3px;
        """)

        self.subtitle_lbl = QLabel(
            "Explore the study area, select region of interest, and analyze dynamic river mouth characteristics"
        )
        self.subtitle_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {MUTED_SAGE};
        """)

        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.subtitle_lbl)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Compact Map-Style Controls: Map, Satellite, Hybrid, Terrain
        mode_btn_box = QHBoxLayout()
        mode_btn_box.setSpacing(4)

        self.mode_buttons = {}
        modes = [
            ("map", "Map"),
            ("satellite", "Satellite"),
            ("hybrid", "Hybrid"),
            ("terrain", "Terrain"),
        ]

        for mode_key, mode_label in modes:
            btn = QPushButton(mode_label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda checked=False, m=mode_key: self.set_map_mode(m))
            self.mode_buttons[mode_key] = btn
            mode_btn_box.addWidget(btn)

        self.update_mode_button_styles("map")
        header_layout.addLayout(mode_btn_box)

        left_layout.addWidget(map_header)

        # --------------------------------------------------------------------
        # Embedded Web Map View (QWebEngineView)
        # --------------------------------------------------------------------
        map_frame = QFrame()
        map_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        map_frame_layout = QVBoxLayout(map_frame)
        map_frame_layout.setContentsMargins(2, 2, 2, 2)

        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        page = WebPage(self.browser)
        self.browser.setPage(page)

        self.channel = QWebChannel(self.browser.page())
        self.bridge = Bridge(self)
        self.channel.registerObject("bridge", self.bridge)
        page.setWebChannel(self.channel)

        for s in (self.browser.settings(), page.settings()):
            s.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            s.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

        map_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "webmap", "index.html")
        )
        self.browser.load(QUrl.fromLocalFile(map_path))
        self.browser.loadFinished.connect(self.on_map_load_finished)

        map_frame_layout.addWidget(self.browser)
        left_layout.addWidget(map_frame, 1)
        # --------------------------------------------------------------------
        # Bottom Information Cards Removed (Map expanded to fill full height)
        # --------------------------------------------------------------------
        self.card_loc_val = None
        self.card_loc_sub = None
        self.card_coords_val = None
        self.card_coords_sub = None
        self.card_source_val = None
        self.card_source_sub = None
        self.card_type_val = None
        self.card_type_sub = None
        
        
        main_layout.addWidget(left_container, 7)

        # ====================================================================
        # RIGHT PANEL: Analysis Parameters (Section 3.D)
        # ====================================================================
        right_panel = QFrame()
        right_panel.setFixedWidth(340)
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        # Panel Header
        panel_header_layout = QHBoxLayout()
        panel_title_box = QVBoxLayout()
        panel_title_box.setSpacing(2)

        panel_title = QLabel("Analysis Parameters")
        panel_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {WARM_IVORY};
        """)

        panel_sub = QLabel("Model configuration & spatial extent")
        panel_sub.setStyleSheet(f"""
            font-size: 11px;
            color: {MUTED_SAGE};
        """)
        panel_title_box.addWidget(panel_title)
        panel_title_box.addWidget(panel_sub)
        panel_header_layout.addLayout(panel_title_box)

        # Spatial ML Badge
        badge = QLabel("SPATIAL ML")
        badge.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {MINT};
            font-size: 10px;
            font-weight: 700;
            padding: 3px 7px;
            border-radius: 4px;
            border: 1px solid {BORDER_COLOR};
        """)
        panel_header_layout.addWidget(badge)
        right_layout.addLayout(panel_header_layout)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {BORDER_SUBTLE}; border: none; height: 1px;")
        right_layout.addWidget(divider)

        # Section: Year Selection
        temporal_lbl = QLabel("TEMPORAL CONFIGURATION")
        temporal_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {TEAL}; letter-spacing: 0.5px;")
        right_layout.addWidget(temporal_lbl)

        # Base Year
        by_label = QLabel("Base Year (Historical Reference)")
        by_label.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        right_layout.addWidget(by_label)

        val = QIntValidator(1989, 2026, self)

        self.base_year = QComboBox()
        self.base_year.setEditable(True)
        self.base_year.addItems([str(y) for y in range(1989, 2027)])
        self.base_year.setCurrentText("1989")
        self.base_year.setToolTip("Select baseline year (1989–2026) or enter observation year")
        if self.base_year.lineEdit():
            self.base_year.lineEdit().setPlaceholderText("1989")
            self.base_year.lineEdit().setValidator(val)
        right_layout.addWidget(self.base_year)

        # Prediction Year
        py_label = QLabel("Prediction Target Year")
        py_label.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        right_layout.addWidget(py_label)

        self.prediction_year = QComboBox()
        self.prediction_year.setEditable(True)
        self.prediction_year.setToolTip("Select prediction target year (1989–2026)")
        if self.prediction_year.lineEdit():
            self.prediction_year.lineEdit().setPlaceholderText("2000")
            self.prediction_year.lineEdit().setValidator(val)
        right_layout.addWidget(self.prediction_year)

        self.update_prediction_years()
        self.base_year.currentIndexChanged.connect(self.update_prediction_years)
        if self.base_year.lineEdit():
            self.base_year.lineEdit().editingFinished.connect(self.update_prediction_years)
        self.prediction_year.currentIndexChanged.connect(self.on_year_selection_changed)
        if self.prediction_year.lineEdit():
            self.prediction_year.lineEdit().editingFinished.connect(self.on_year_selection_changed)

        right_layout.addSpacing(6)

        # Section: Study Area Coordinates (AOI)
        aoi_header_box = QHBoxLayout()
        aoi_lbl = QLabel("STUDY AREA COORDINATES (AOI)")
        aoi_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {MINT}; letter-spacing: 0.5px;")
        aoi_header_box.addWidget(aoi_lbl)
        aoi_header_box.addStretch()

        aoi_badge = QLabel("Draw Rectangle")
        aoi_badge.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; font-style: italic;")
        aoi_header_box.addWidget(aoi_badge)
        right_layout.addLayout(aoi_header_box)

        # Two-Column Grid for Coordinates (North, South, East, West)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        # Column 1: North & South
        grid.addWidget(self.create_field_label("North Latitude (°N)"), 0, 0)
        self.north_lat = QLineEdit()
        self.north_lat.setReadOnly(True)
        self.north_lat.setPlaceholderText("13.480000")
        grid.addWidget(self.north_lat, 1, 0)

        grid.addWidget(self.create_field_label("South Latitude (°N)"), 2, 0)
        self.south_lat = QLineEdit()
        self.south_lat.setReadOnly(True)
        self.south_lat.setPlaceholderText("13.400000")
        grid.addWidget(self.south_lat, 3, 0)

        # Column 2: East & West
        grid.addWidget(self.create_field_label("East Longitude (°E)"), 0, 1)
        self.east_lon = QLineEdit()
        self.east_lon.setReadOnly(True)
        self.east_lon.setPlaceholderText("74.740000")
        grid.addWidget(self.east_lon, 1, 1)

        grid.addWidget(self.create_field_label("West Longitude (°E)"), 2, 1)
        self.west_lon = QLineEdit()
        self.west_lon.setReadOnly(True)
        self.west_lon.setPlaceholderText("74.660000")
        grid.addWidget(self.west_lon, 3, 1)

        right_layout.addLayout(grid)

        # AOI Action Buttons (Focus Study Area & Clear AOI)
        aoi_btn_row = QHBoxLayout()
        aoi_btn_row.setSpacing(8)

        self.btn_focus = QPushButton("Focus Location")
        self.btn_focus.setIcon(get_icon("crosshair", color=MINT, size=16))
        self.btn_focus.setCursor(Qt.PointingHandCursor)
        self.btn_focus.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                font-size: 11px;
                padding: 6px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        self.btn_focus.clicked.connect(self.center_study_area)
        aoi_btn_row.addWidget(self.btn_focus)

        self.btn_clear_aoi = QPushButton("Clear AOI")
        self.btn_clear_aoi.setIcon(get_icon("refresh", color=MUTED_SAGE, size=16))
        self.btn_clear_aoi.setCursor(Qt.PointingHandCursor)
        self.btn_clear_aoi.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MUTED_SAGE};
                border: 1px solid {BORDER_COLOR};
                font-size: 11px;
                padding: 6px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                color: {WARM_IVORY};
            }}
        """)
        self.btn_clear_aoi.clicked.connect(self.clear_aoi_clicked)
        aoi_btn_row.addWidget(self.btn_clear_aoi)

        right_layout.addLayout(aoi_btn_row)

        right_layout.addStretch()

        # Status note above button
        self.aoi_status_note = QLabel("Use top-left map toolbar to draw rectangle AOI")
        self.aoi_status_note.setStyleSheet(f"""
            font-size: 11px;
            color: {MUTED_SAGE};
            font-style: italic;
            text-align: center;
        """)
        self.aoi_status_note.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.aoi_status_note)

        # Next Button (Prominent Mint/Teal Button with Arrow)
        self.next_btn = QPushButton("Next Step: Analysis  →")
        self.next_btn.setMinimumHeight(44)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {TEAL}, stop:1 {MINT});
                color: {BG_DARK};
                font-size: 14px;
                font-weight: 700;
                border: none;
                border-radius: 8px;
                padding: 10px;
                letter-spacing: 0.4px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MINT}, stop:1 {SOFT_LIME});
            }}
            QPushButton:pressed {{
                background: {TEAL};
            }}
        """)
        self.next_btn.clicked.connect(self.go_to_result)
        right_layout.addWidget(self.next_btn)

        # Quick Direct Access to LULC Classification & Deviation Report
        quick_nav_row = QHBoxLayout()
        quick_nav_row.setSpacing(8)

        self.btn_quick_lulc = QPushButton("LULC Analysis")
        self.btn_quick_lulc.setIcon(get_icon("lulc", color=MINT, size=14))
        self.btn_quick_lulc.setCursor(Qt.PointingHandCursor)
        self.btn_quick_lulc.setFixedHeight(30)
        self.btn_quick_lulc.setToolTip("Directly open Land Use / Land Cover Analysis for selected years")
        self.btn_quick_lulc.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
                color: {SOFT_LIME};
            }}
        """)
        self.btn_quick_lulc.clicked.connect(self.go_to_lulc_direct)
        quick_nav_row.addWidget(self.btn_quick_lulc)

        self.btn_quick_dev = QPushButton("Deviation Report")
        self.btn_quick_dev.setIcon(get_icon("analysis", color=MINT, size=14))
        self.btn_quick_dev.setCursor(Qt.PointingHandCursor)
        self.btn_quick_dev.setFixedHeight(30)
        self.btn_quick_dev.setToolTip("Directly open River-Mouth Deviation & Displacement Analysis for selected years")
        self.btn_quick_dev.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
                color: {SOFT_LIME};
            }}
        """)
        self.btn_quick_dev.clicked.connect(self.go_to_deviation_direct)
        quick_nav_row.addWidget(self.btn_quick_dev)

        right_layout.addLayout(quick_nav_row)

        main_layout.addWidget(right_panel, 3)

    # ========================================================================
    # Helper: Create Info Card
    # ========================================================================
    def create_info_card(self, icon_name, icon_color, title, primary, secondary):
        card = QFrame()
        card.setFixedHeight(72)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Icon box
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap(icon_name, color=icon_color, size=22))
        icon_lbl.setFixedSize(26, 26)
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        # Text box
        t_box = QVBoxLayout()
        t_box.setContentsMargins(0, 0, 0, 0)
        t_box.setSpacing(1)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"""
            font-size: 9px;
            font-weight: 700;
            color: {icon_color};
            letter-spacing: 0.5px;
        """)

        p_lbl = QLabel(primary)
        p_lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {WARM_IVORY};
        """)

        s_lbl = QLabel(secondary)
        s_lbl.setStyleSheet(f"""
            font-size: 9px;
            color: {MUTED_SAGE};
        """)

        t_box.addWidget(t_lbl)
        t_box.addWidget(p_lbl)
        t_box.addWidget(s_lbl)
        layout.addLayout(t_box)

        return card, p_lbl, s_lbl

    def create_field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE}; font-weight: 500;")
        return lbl

    # ========================================================================
    # Map Mode Controls
    # ========================================================================
    def set_map_mode(self, mode):
        self.active_mode = mode
        self.update_mode_button_styles(mode)
        self.browser.page().runJavaScript(f"if (window.setMapMode) window.setMapMode('{mode}');")

    def update_mode_button_styles(self, active_mode):
        for mode_key, btn in self.mode_buttons.items():
            is_active = (mode_key == active_mode)
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PANEL_GREEN};
                        color: {MINT};
                        border: 1px solid {MINT};
                        border-radius: 4px;
                        font-weight: 700;
                        font-size: 11px;
                        padding: 3px 10px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {DARK_EMERALD};
                        color: {MUTED_SAGE};
                        border: 1px solid {BORDER_SUBTLE};
                        border-radius: 4px;
                        font-weight: 500;
                        font-size: 11px;
                        padding: 3px 10px;
                    }}
                    QPushButton:hover {{
                        color: {WARM_IVORY};
                        border-color: {BORDER_COLOR};
                    }}
                """)

    # ========================================================================
    # Slot Callbacks & Data Updating
    # ========================================================================
    def set_aoi_coords(self, north, south, east, west):
        print(f"AOI updated: N={north:.6f}, S={south:.6f}, E={east:.6f}, W={west:.6f}")
        self.north_lat.setText(f"{north:.6f}")
        self.south_lat.setText(f"{south:.6f}")
        self.east_lon.setText(f"{east:.6f}")
        self.west_lon.setText(f"{west:.6f}")

        if self.card_coords_val:
            self.card_coords_val.setText(f"{south:.4f}°N to {north:.4f}°N")
            self.card_coords_sub.setText(f"{west:.4f}°E to {east:.4f}°E (AOI Extent)")
        self.aoi_status_note.setText("✓ Area of Interest captured successfully")
        self.aoi_status_note.setStyleSheet(f"font-size: 11px; color: {MINT}; font-weight: 600;")

        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(
                status_text="AOI Extent Defined",
                readiness="Ready for ML Analysis"
            )

    def set_map_status(self, status):
        print(f"Map status: {status}")
        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(status_text=status)

    def set_map_mode_name(self, mode_name):
        if self.card_source_val:
            self.card_source_val.setText(mode_name)
        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(mode_text=f"Mode: {mode_name}")

    def update_cursor_coords(self, lat, lon):
        if self.card_coords_val and not self.north_lat.text():
            self.card_coords_val.setText(f"{lat:.4f}° N, {lon:.4f}° E")

    def clear_aoi(self):
        self.north_lat.clear()
        self.south_lat.clear()
        self.east_lon.clear()
        self.west_lon.clear()
        if self.card_coords_val:
            self.card_coords_val.setText("13.4380° N, 74.6980° E")
            self.card_coords_sub.setText("WGS84 / EPSG:4326 (Estuary Mouth)")
        self.aoi_status_note.setText("Use top-left map toolbar to draw rectangle AOI")
        self.aoi_status_note.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE}; font-style: italic;")
        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(
                status_text="Map Ready",
                readiness="Ready for AOI selection"
            )

    def clear_aoi_clicked(self):
        self.browser.page().runJavaScript("if (window.clearOverlayLayer) window.clearOverlayLayer('aoi');")
        self.clear_aoi()

    def on_map_load_finished(self, ok):
        print("HTML Loaded :", ok)
        if ok:
            if self.main_window and hasattr(self.main_window, "update_status"):
                loc_short = self.current_location_name.split(",")[0].strip() if self.current_location_name else "Study Area"
                self.main_window.update_status(
                    status_text=f"Map Ready ({loc_short})",
                    readiness="Ready for AOI selection"
                )
        else:
            if self.main_window and hasattr(self.main_window, "update_status"):
                self.main_window.update_status(
                    status_text="Map Load Warning (Check internet)",
                    readiness="Offline Mode"
                )

    def get_base_year(self) -> int:
        """Returns the currently selected Base Year, clamped to valid dataset bounds (1989-2026)."""
        text = self.base_year.currentText().strip() if hasattr(self, "base_year") else "1989"
        m = re.search(r"\b(19\d\d|20\d\d)\b", text)
        val = int(m.group(1)) if m else 1989
        return max(1989, min(2026, val))

    def get_prediction_year(self) -> int:
        """Returns the currently selected Prediction Target Year, clamped to valid dataset bounds (1989-2026)."""
        text = self.prediction_year.currentText().strip() if hasattr(self, "prediction_year") else "2000"
        m = re.findall(r"\b(19\d\d|20\d\d)\b", text)
        val = int(m[-1]) if m else 2000
        return max(1989, min(2026, val))

    def on_year_selection_changed(self):
        """Called when Base Year or Prediction Year changes; synchronizes global data service and status bar."""
        b = self.get_base_year()
        p = self.get_prediction_year()
        from backend.data_service import data_service
        data_service.set_year_range(b, p)
        years = data_service.get_selected_years()
        if self.main_window and hasattr(self.main_window, "update_status"):
            if hasattr(self.main_window, "stack") and self.main_window.stack.currentIndex() == 0:
                self.main_window.update_status(
                    data_text=f"Range: {b}–{p} ({len(years)} yrs)"
                )

    def update_prediction_years(self):
        """
        Updates the Prediction Year dropdown to ensure Base Year <= Prediction Year.
        Populates single clean observation years from Base Year to 2026.
        """
        base_year = self.get_base_year()
        current_pred = self.get_prediction_year()

        self.prediction_year.blockSignals(True)
        self.prediction_year.clear()

        # Add single sequential years from Base Year to 2026 (inclusive)
        for year in range(base_year, 2027):
            self.prediction_year.addItem(str(year))

        # Preserve previously selected prediction year if valid and >= base_year
        if current_pred >= base_year:
            idx = self.prediction_year.findText(str(current_pred))
            if idx >= 0:
                self.prediction_year.setCurrentIndex(idx)
            else:
                self.prediction_year.setCurrentText(str(current_pred))
        else:
            default_target = 2000 if (base_year <= 2000) else base_year
            idx = self.prediction_year.findText(str(default_target))
            if idx >= 0:
                self.prediction_year.setCurrentIndex(idx)
            else:
                self.prediction_year.setCurrentIndex(0)

        self.prediction_year.blockSignals(False)
        self.on_year_selection_changed()

    def get_selected_years(self) -> list[int]:
        """
        Returns the inclusive chronological year range between the selected Base Year and Prediction Year:
        e.g., Base Year 1989 and Prediction Year 2000 -> [1989, 1990, ..., 2000].
        Validation:
        - Base Year must be earlier than or equal to Prediction Year.
        - The range includes both the Base Year and Prediction Year.
        - Clamps years to valid project observation bounds (1989 to 2026).
        """
        base_y = self.get_base_year()
        pred_y = self.get_prediction_year()

        # Enforce Base Year <= Prediction Year
        if base_y > pred_y:
            pred_y = base_y

        return list(range(base_y, pred_y + 1))

    @property
    def selected_years(self) -> list[int]:
        """The single source of truth for selected years on the Home page."""
        return self.get_selected_years()

    @selected_years.setter
    def selected_years(self, years: list):
        self.set_selected_years(years)

    def set_selected_years(self, years: list):
        """Sets the selected Base Year and Prediction Year directly on the Home page controls."""
        if not years:
            return
        valid = []
        for y in years:
            try:
                yi = int(str(y).strip())
                if 1980 <= yi <= 2035 and yi not in valid:
                    valid.append(yi)
            except (ValueError, TypeError):
                pass
        valid.sort()
        if not valid:
            return

        b_yr = valid[0]
        p_yr = valid[-1]

        self.base_year.blockSignals(True)
        self.prediction_year.blockSignals(True)
        self.base_year.setCurrentText(str(b_yr))
        self.prediction_year.setCurrentText(str(p_yr))
        self.base_year.blockSignals(False)
        self.prediction_year.blockSignals(False)
        self.update_prediction_years()

    def set_location(self, location_name, lat, lon):
        print(f"Location updated: {location_name} (Lat: {lat:.6f}, Lon: {lon:.6f})")
        self.current_location_name = location_name
        self.current_lat = lat
        self.current_lon = lon
        short_loc = location_name.split(",")[0].strip()
        if hasattr(self, "title_lbl") and self.title_lbl:
            self.title_lbl.setText(f"Interactive Map – {short_loc}")
        if hasattr(self, "subtitle_lbl") and self.subtitle_lbl:
            self.subtitle_lbl.setText(f"Active Study Area: {location_name} ({lat:.4f}° N, {lon:.4f}° E)")
        if not self.north_lat.text():
            self.aoi_status_note.setText(f"✓ Location: {location_name}")
            self.aoi_status_note.setStyleSheet(f"font-size: 11px; color: {MINT}; font-weight: 500;")
        if self.main_window and hasattr(self.main_window, "update_location"):
            self.main_window.update_location(location_name, lat, lon)

    def center_study_area(self):
        self.browser.page().runJavaScript(
            "if (typeof window.focusCurrentLocation === 'function') window.focusCurrentLocation(); else if (typeof window.focusStudyArea === 'function') window.focusStudyArea();"
        )

    def go_to_result(self):
        """Primary action: Synchronizes all models and enters River Mouth Satellite Imagery & Deviation pipeline."""
        try:
            self.next_btn.setText("Opening Analysis...  →")
            self.next_btn.setEnabled(False)
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            selected_years = self.get_selected_years()
            base_y = selected_years[0] if selected_years else 1989
            target_y = selected_years[-1] if len(selected_years) > 1 else (selected_years[0] if selected_years else 2026)
            aoi = None
            if self.north_lat.text() and self.south_lat.text():
                try:
                    aoi = {
                        "north": float(self.north_lat.text()),
                        "south": float(self.south_lat.text()),
                        "east": float(self.east_lon.text()),
                        "west": float(self.west_lon.text())
                    }
                except ValueError:
                    pass

            print(f"Executing Analysis Workflow: Base={base_y}, Target={target_y}, Selected={selected_years}, AOI={aoi}")
            
            # Ensure centralized data service is updated
            from backend.data_service import data_service
            data_service.set_year_range(base_y, target_y)

            # Route to primary analysis pipeline via main_window
            if self.main_window:
                if hasattr(self.main_window, "run_analysis"):
                    self.main_window.run_analysis(base_y, target_y, aoi)
                elif hasattr(self.main_window, "go_to_river_mouth"):
                    self.main_window.go_to_river_mouth(selected_years)
                elif hasattr(self.main_window, "navigate_to_page"):
                    self.main_window.navigate_to_page(4)
                elif self.stack:
                    self.stack.setCurrentIndex(4)
            elif self.stack:
                self.stack.setCurrentIndex(4)
        except Exception as e:
            print(f"[HomePage] Error executing analysis navigation: {e}")
            import traceback
            traceback.print_exc()
            if self.main_window and hasattr(self.main_window, "navigate_to_page"):
                self.main_window.navigate_to_page(4)
            elif self.stack:
                self.stack.setCurrentIndex(4)
        finally:
            self.next_btn.setText("Next Step: Analysis  →")
            self.next_btn.setEnabled(True)

    def go_to_lulc_direct(self):
        """Direct access: Navigates straight to LULC classification page for selected years."""
        selected_years = self.get_selected_years()
        base_y = selected_years[0] if selected_years else 1989
        target_y = selected_years[-1] if len(selected_years) > 1 else 2026
        from backend.data_service import data_service
        data_service.set_year_range(base_y, target_y)
        if self.main_window:
            if hasattr(self.main_window, "go_to_lulc"):
                self.main_window.go_to_lulc()
            elif hasattr(self.main_window, "navigate_to_page"):
                if hasattr(self.main_window, "result_page") and hasattr(self.main_window.result_page, "set_year_range"):
                    self.main_window.result_page.set_year_range(base_y, target_y)
                self.main_window.navigate_to_page(1)
        elif self.stack:
            self.stack.setCurrentIndex(1)

    def go_to_deviation_direct(self):
        """Direct access: Navigates straight to River-Mouth Deviation & Displacement Analysis page."""
        selected_years = self.get_selected_years()
        base_y = selected_years[0] if selected_years else 1989
        target_y = selected_years[-1] if len(selected_years) > 1 else 2026
        from backend.data_service import data_service
        data_service.set_year_range(base_y, target_y)
        if self.main_window:
            if hasattr(self.main_window, "go_to_analysis"):
                self.main_window.go_to_analysis()
            elif hasattr(self.main_window, "navigate_to_page"):
                if hasattr(self.main_window, "deviation_page") and hasattr(self.deviation_page, "set_years"):
                    self.main_window.deviation_page.set_years(base_y, target_y)
                self.main_window.navigate_to_page(5)
        elif self.stack:
            self.stack.setCurrentIndex(5)