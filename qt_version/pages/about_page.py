from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
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


class AboutPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

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
        title = QLabel("About the Project")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WARM_IVORY};")
        sub = QLabel("Major Project Documentation & System Overview")
        sub.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        top_bar.addLayout(title_box)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Hero Banner
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        hl = QVBoxLayout(hero)
        hl.setSpacing(6)

        ht = QLabel("Hybrid AI Approach for Analyzing River Path Deviation and Its Contributing Factors")
        ht.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {MINT};")
        hl.addWidget(ht)

        hd = QLabel(
            "Focused on the dynamic estuarine environment of the <b>Suvarna (Swarna) River near Kodi Bengre, "
            "Udupi District, Karnataka, India</b>. The research combines multi-decadal satellite remote sensing (1989–2026), "
            "automated spectral water extraction, and a Hybrid Deep Learning framework to quantify historical river course "
            "migration, bankline erosion, and project future estuarine morphodynamics."
        )
        hd.setStyleSheet(f"font-size: 12px; color: {WARM_IVORY}; line-height: 1.5;")
        hd.setWordWrap(True)
        hl.addWidget(hd)
        main_layout.addWidget(hero)

        # 3 Pillar Cards Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        # Pillar 1
        c1 = self.create_pillar_card(
            "Geospatial Remote Sensing",
            "Utilizes multi-spectral Landsat (5 TM, 7 ETM+, 8-9 OLI) calibrated imagery. "
            "Extracts water channels using Modified Normalized Difference Water Index (MNDWI) "
            "with sub-pixel thresholding and morphology filtering.",
            TEAL
        )
        grid.addWidget(c1, 0, 0)

        # Pillar 2
        c2 = self.create_pillar_card(
            "Hybrid AI Architecture",
            "Combines 2D Convolutional Neural Networks (CNN) for spatial feature extraction with "
            "Bi-directional Long Short-Term Memory (BiLSTM) networks for multi-decadal temporal trend "
            "modeling and centerline deviation forecasting.",
            MINT
        )
        grid.addWidget(c2, 0, 1)

        # Pillar 3
        c3 = self.create_pillar_card(
            "Sustainable Coastlines",
            "Provides actionable insights for coastal resilience, sediment drift analysis, and "
            "mangrove wetland conservation along the vulnerable Kodi Bengre sandspit between the "
            "river estuary and the Arabian Sea.",
            SOFT_LIME
        )
        grid.addWidget(c3, 0, 2)

        main_layout.addLayout(grid)

        # Metadata Footer
        meta = QFrame()
        meta.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        ml = QHBoxLayout(meta)
        ml.addWidget(QLabel("<b>Project Scope:</b> Final Year Engineering Major Project & Copyright Documentation"))
        ml.addStretch()
        ml.addWidget(QLabel("<b>Study Area:</b> Kodi Bengre Estuary (13.4380°N, 74.6980°E)"))
        ml.addStretch()
        ml.addWidget(QLabel("<b>Platform:</b> Python 3.11 | PySide6 | Leaflet Engine"))
        main_layout.addWidget(meta)

    def create_pillar_card(self, title, desc, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        l = QVBoxLayout(card)
        l.setSpacing(8)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {color};")
        d = QLabel(desc)
        d.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE}; line-height: 1.4;")
        d.setWordWrap(True)

        l.addWidget(t)
        l.addWidget(d)
        l.addStretch()
        return card

    def go_back(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(0)
        else:
            self.stack.setCurrentIndex(0)
