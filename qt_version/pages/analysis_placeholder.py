"""
Analysis Page Placeholder - Suvarna River Study GIS Dashboard
Serves as the destination when the user clicks 'Analyze' from the River Mouth Images page.
Matches the application's Dark Emerald theme, header, typography, and styling.
Awaiting user's upcoming analysis requirements.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
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
    AMBER,
)
from icons import get_icon, get_pixmap


class AnalysisPlaceholderPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.build_ui()

    def build_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Left Vertical Navigation Sidebar
        sidebar = self.build_sidebar()
        root_layout.addWidget(sidebar)

        # Main Placeholder Content Area
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(24, 18, 24, 18)
        main_layout.setSpacing(16)

        # Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        back_btn = QPushButton("← Back to River Mouth Images")
        back_btn.setIcon(get_icon("arrow_left", color=MINT, size=16))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedHeight(34)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                border: 1px solid {BORDER_COLOR};
                font-size: 12px;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        back_btn.clicked.connect(self.go_to_river_mouth)
        header_row.addWidget(back_btn)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("River Path Deviation & Morphodynamics Analysis")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {WARM_IVORY};")
        sub = QLabel("Predictive modeling workspace • Spatial-temporal estuarine dynamics")
        sub.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        title_box.addWidget(title)
        title_box.addWidget(sub)

        header_row.addLayout(title_box)
        header_row.addStretch()

        main_layout.addLayout(header_row)

        # Central Placeholder Hero Card
        hero_card = QFrame()
        hero_card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
        """)
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(36, 40, 36, 40)
        hero_layout.setSpacing(18)
        hero_layout.setAlignment(Qt.AlignCenter)

        # Hero Icon
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap("analysis", color=MINT, size=64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(icon_lbl)

        # Hero Title & Status Badge
        badge = QLabel("ANALYSIS MODULE PLACEHOLDER")
        badge.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 800;
            color: {MINT};
            background-color: {DARK_EMERALD};
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid {BORDER_SUBTLE};
            letter-spacing: 1px;
        """)
        hero_layout.addWidget(badge, 0, Qt.AlignCenter)

        h_title = QLabel("Estuarine Analysis Pipeline")
        h_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {WARM_IVORY};")
        hero_layout.addWidget(h_title, 0, Qt.AlignCenter)

        desc = QLabel(
            "This analysis page is set up as a placeholder for your upcoming model requirements.\n"
            "Once you provide the exact analysis specifications (e.g., U-Net spatial segmentation,\n"
            "Bi-LSTM river channel deviation prediction, or sediment transport calculations),\n"
            "the corresponding charts, controls, and prediction maps will be integrated here."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"font-size: 13px; color: {MUTED_SAGE}; line-height: 1.5;")
        hero_layout.addWidget(desc, 0, Qt.AlignCenter)

        # Navigation shortcuts inside card
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        btn_gallery = QPushButton("← Return to River Mouth Gallery")
        btn_gallery.setCursor(Qt.PointingHandCursor)
        btn_gallery.setFixedHeight(38)
        btn_gallery.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                font-size: 12px;
                font-weight: 700;
                padding: 6px 18px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #5ED49D;
            }}
        """)
        btn_gallery.clicked.connect(self.go_to_river_mouth)
        btn_box.addWidget(btn_gallery)

        btn_lulc = QPushButton("View LULC Classification")
        btn_lulc.setCursor(Qt.PointingHandCursor)
        btn_lulc.setFixedHeight(38)
        btn_lulc.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                font-size: 12px;
                font-weight: 600;
                padding: 6px 18px;
                border-radius: 6px;
                border: 1px solid {BORDER_COLOR};
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        btn_lulc.clicked.connect(self.go_to_lulc)
        btn_box.addWidget(btn_lulc)

        btn_weather = QPushButton("View Weather Data")
        btn_weather.setCursor(Qt.PointingHandCursor)
        btn_weather.setFixedHeight(38)
        btn_weather.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                font-size: 12px;
                font-weight: 600;
                padding: 6px 18px;
                border-radius: 6px;
                border: 1px solid {BORDER_COLOR};
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        btn_weather.clicked.connect(self.go_to_weather)
        btn_box.addWidget(btn_weather)

        hero_layout.addLayout(btn_box)
        main_layout.addWidget(hero_card, 1)

        root_layout.addWidget(main_content, 1)

    # ========================================================================
    # Left Navigation Sidebar
    # ========================================================================
    def build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)

        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 800;
            color: {MUTED_SAGE};
            letter-spacing: 1px;
            padding-left: 4px;
            margin-bottom: 4px;
        """)
        layout.addWidget(nav_label)

        # Home Button
        btn_home = QPushButton("  Home")
        btn_home.setIcon(get_icon("home", color=MINT, size=18))
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.setFixedHeight(44)
        btn_home.setStyleSheet(self.get_sidebar_btn_style())
        btn_home.clicked.connect(self.go_to_home)
        layout.addWidget(btn_home)

        # River Mouth Gallery Button
        btn_gallery = QPushButton("  River Mouth")
        btn_gallery.setIcon(get_icon("map_source", color=TEAL, size=18))
        btn_gallery.setCursor(Qt.PointingHandCursor)
        btn_gallery.setFixedHeight(44)
        btn_gallery.setStyleSheet(self.get_sidebar_btn_style())
        btn_gallery.clicked.connect(self.go_to_river_mouth)
        layout.addWidget(btn_gallery)

        # LULC Button
        btn_lulc = QPushButton("  LULC")
        btn_lulc.setIcon(get_icon("lulc", color=TEAL, size=18))
        btn_lulc.setCursor(Qt.PointingHandCursor)
        btn_lulc.setFixedHeight(44)
        btn_lulc.setStyleSheet(self.get_sidebar_btn_style())
        btn_lulc.clicked.connect(self.go_to_lulc)
        layout.addWidget(btn_lulc)

        # Weather Button
        btn_weather = QPushButton("  Weather")
        btn_weather.setIcon(get_icon("weather", color=AMBER, size=18))
        btn_weather.setCursor(Qt.PointingHandCursor)
        btn_weather.setFixedHeight(44)
        btn_weather.setStyleSheet(self.get_sidebar_btn_style())
        btn_weather.clicked.connect(self.go_to_weather)
        layout.addWidget(btn_weather)

        layout.addStretch()
        return sidebar

    def get_sidebar_btn_style(self):
        return f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                text-align: left;
                padding-left: 14px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border: 1px solid {MINT};
                color: {MINT};
            }}
        """

    def go_to_home(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(0)
        else:
            self.stack.setCurrentIndex(0)

    def go_to_river_mouth(self):
        if self.main_window and hasattr(self.main_window, "go_to_river_mouth"):
            self.main_window.go_to_river_mouth()
        elif self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(4)
        else:
            self.stack.setCurrentIndex(4)

    def go_to_lulc(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(1)
        else:
            self.stack.setCurrentIndex(1)

    def go_to_weather(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(2)
        else:
            self.stack.setCurrentIndex(2)

