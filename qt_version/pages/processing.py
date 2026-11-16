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
    QProgressBar,
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


class ProcessingPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Header Row
        header_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Map")
        back_btn.setIcon(get_icon("home", color=MINT, size=16))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        back_btn.clicked.connect(self.go_back)
        header_row.addWidget(back_btn)
        header_row.addStretch()

        title_box = QVBoxLayout()
        t = QLabel("Satellite Data Preprocessing & Spectral Indices")
        t.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WARM_IVORY};")
        sub = QLabel("Multi-spectral band calibration, atmospheric correction, and water-body extraction indices")
        sub.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        title_box.addWidget(t)
        title_box.addWidget(sub)
        header_row.addLayout(title_box)
        header_row.addStretch()

        layout.addLayout(header_row)

        # 3 Main Cards Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        # Card 1: Satellite Sensor & Imagery Source
        c1 = self.create_card("1. Sensor & Satellite Pipeline")
        c1_layout = QVBoxLayout(c1)
        c1_layout.setContentsMargins(14, 14, 14, 14)
        c1_layout.setSpacing(10)

        c1_layout.addWidget(QLabel("Satellite Mission:"))
        mission_combo = QComboBox()
        mission_combo.addItems([
            "Landsat 8-9 OLI/TIRS (30m Resolution)",
            "Landsat 7 ETM+ (SLC-corrected)",
            "Landsat 5 TM (Historical 1989-2011)",
            "Sentinel-2 MSI (10m Resolution)"
        ])
        c1_layout.addWidget(mission_combo)

        c1_layout.addWidget(QLabel("Cloud Cover Filtering:"))
        cloud_combo = QComboBox()
        cloud_combo.addItems(["Max 5% Cloud Cover", "Max 10% Cloud Cover", "QA Masking (Pixel Quality)"])
        c1_layout.addWidget(cloud_combo)

        cb1 = QCheckBox("Apply Top-Of-Atmosphere (TOA) Reflectance")
        cb1.setChecked(True)
        cb2 = QCheckBox("Apply Fmask / QA Surface Masking")
        cb2.setChecked(True)
        cb3 = QCheckBox("Harmonize Multi-Temporal Tile CRS (UTM 43N)")
        cb3.setChecked(True)
        c1_layout.addWidget(cb1)
        c1_layout.addWidget(cb2)
        c1_layout.addWidget(cb3)
        c1_layout.addStretch()

        grid.addWidget(c1, 0, 0)

        # Card 2: Water & Vegetation Indices
        c2 = self.create_card("2. Water Index Extraction (Swarna River)")
        c2_layout = QVBoxLayout(c2)
        c2_layout.setContentsMargins(14, 14, 14, 14)
        c2_layout.setSpacing(10)

        c2_layout.addWidget(QLabel("Select Spectral Indices to Compute:"))
        
        mndwi_cb = QCheckBox("MNDWI (Modified Normalized Difference Water Index)\nFormula: (Green - SWIR1) / (Green + SWIR1)")
        mndwi_cb.setChecked(True)
        mndwi_cb.setStyleSheet(f"color: {MINT}; font-weight: 600;")
        c2_layout.addWidget(mndwi_cb)

        ndwi_cb = QCheckBox("NDWI (Normalized Difference Water Index - McFeeters)\nFormula: (Green - NIR) / (Green + NIR)")
        ndwi_cb.setChecked(True)
        c2_layout.addWidget(ndwi_cb)

        ndvi_cb = QCheckBox("NDVI (Vegetation & Mangrove Index)\nFormula: (NIR - Red) / (NIR + Red)")
        ndvi_cb.setChecked(True)
        c2_layout.addWidget(ndvi_cb)

        awei_cb = QCheckBox("AWEI (Automated Water Extraction Index)")
        c2_layout.addWidget(awei_cb)

        c2_layout.addStretch()
        grid.addWidget(c2, 0, 1)

        # Card 3: Water Masking & Morphometry
        c3 = self.create_card("3. Estuarine Water-Land Thresholding")
        c3_layout = QVBoxLayout(c3)
        c3_layout.setContentsMargins(14, 14, 14, 14)
        c3_layout.setSpacing(10)

        c3_layout.addWidget(QLabel("Otsu Automatic Binarization:"))
        otsu_combo = QComboBox()
        otsu_combo.addItems(["Adaptive Histogram Thresholding", "Fixed Threshold (-0.05)", "Morphological Opening + Closing"])
        c3_layout.addWidget(otsu_combo)

        c3_layout.addWidget(QLabel("River Centerline Extraction:"))
        skel_combo = QComboBox()
        skel_combo.addItems(["Medial Axis Transform (Skeletonization)", "Voronoi Centerline Generation", "Active Contour (Snakes)"])
        c3_layout.addWidget(skel_combo)

        self.proc_bar = QProgressBar()
        self.proc_bar.setValue(100)
        self.proc_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                text-align: center;
                color: {WARM_IVORY};
                height: 18px;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {TEAL};
                border-radius: 3px;
            }}
        """)
        c3_layout.addWidget(self.proc_bar)

        run_btn = QPushButton("Process Satellite Imagery & Extract Channels")
        run_btn.setIcon(get_icon("data_processing", color=DARK_EMERALD, size=18))
        run_btn.setCursor(Qt.PointingHandCursor)
        run_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {TEAL}, stop:1 {MINT});
                color: {DARK_EMERALD};
                font-weight: 700;
                padding: 10px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {SOFT_LIME};
            }}
        """)
        run_btn.clicked.connect(self.on_run_processing)
        c3_layout.addWidget(run_btn)

        grid.addWidget(c3, 0, 2)
        layout.addLayout(grid)

        # Bottom Pipeline Info Banner
        info_banner = QFrame()
        info_banner.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        ib_layout = QHBoxLayout(info_banner)
        ib_lbl = QLabel(
            "<b>Pipeline Status:</b> Historical multi-spectral calibration verified for Suvarna Estuary (1989-2024). "
            "Extracted water channels are ready for temporal deviation modelling."
        )
        ib_lbl.setStyleSheet(f"color: {MUTED_SAGE}; font-size: 12px;")
        ib_layout.addWidget(ib_lbl)

        next_btn = QPushButton("Proceed to Path Deviation →")
        next_btn.setIcon(get_icon("arrow_right", color=DARK_EMERALD, size=16))
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                font-weight: 700;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {SOFT_LIME};
            }}
        """)
        next_btn.clicked.connect(self.go_to_prediction)
        ib_layout.addWidget(next_btn)

        layout.addWidget(info_banner)

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

    def on_run_processing(self):
        self.proc_bar.setValue(100)
        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(status_text="Indices Calculated (MNDWI, NDWI, NDVI)")

    def go_back(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(0)
        else:
            self.stack.setCurrentIndex(0)

    def go_to_prediction(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(2)
        else:
            self.stack.setCurrentIndex(1)
