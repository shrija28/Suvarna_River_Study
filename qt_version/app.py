import os
import sys

# Ensure Chromium sandbox does not crash headless or embedded on Windows
if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

# Ensure GUI attaches to interactive user desktop on Windows
if sys.platform == "win32":
    try:
        import ctypes
        user32 = ctypes.windll.user32
        GENERIC_ALL = 0x10000000
        hwinsta = user32.OpenWindowStationW("WinSta0", False, GENERIC_ALL)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
        hdesk = user32.OpenDesktopW("Default", 0, False, GENERIC_ALL)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QBrush, QPainterPath, QColor, QPen, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QSizePolicy,
)

from theme import (
    APP_STYLESHEET,
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
)
from icons import get_icon, get_pixmap
from pages.login_page import LoginPage
from backend.auth_service import auth_service
from pages.home import HomePage
from pages.river_mouth_page import RiverMouthImagesPage
from pages.deviation_page import RiverMouthDeviationPage
from pages.result import ResultPage
from pages.weather_page import WeatherPage
from pages.settings_page import SettingsPage
from pages.about_page import AboutPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Estuarine Mouth Dynamics - Path Deviation Prediction System")
        self.resize(1600, 950)
        self.setStyleSheet(APP_STYLESHEET)
        self.nav_buttons = []

        # Application Icon
        logo_icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
        if os.path.exists(logo_icon_path):
            self.setWindowIcon(QIcon(logo_icon_path))

        # --------------------------------------------------------------------
        # Authentication Session State & Root Stacked Switcher
        # --------------------------------------------------------------------
        self.auth_service = auth_service
        self.current_user = None

        self.root_stack = QStackedWidget()
        self.root_stack.setStyleSheet(f"background-color: {BG_DARK}; border: none;")

        # Screen 1: Modern Login & Authentication Page (Shown First)
        self.login_page = LoginPage(self, on_login_success=self.on_login_success)

        # Screen 2: Protected Main Application Dashboard
        self.main_app_widget = QWidget()
        main_app_layout = QVBoxLayout(self.main_app_widget)
        main_app_layout.setContentsMargins(0, 0, 0, 0)
        main_app_layout.setSpacing(0)

        # --------------------------------------------------------------------
        # Section 3.A: Top Branding Banner
        # --------------------------------------------------------------------
        self.banner = self.build_top_banner()
        main_app_layout.addWidget(self.banner)

        # --------------------------------------------------------------------
        # Section 3.F: Bottom Status Bar (Build early so pages can update it safely)
        # --------------------------------------------------------------------
        self.status_bar = self.build_status_bar()

        # --------------------------------------------------------------------
        # Center Body (QStackedWidget Pages with Full-Width Map - Sidebar Removed)
        # --------------------------------------------------------------------
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Central Stacked Pages
        self.stack = QStackedWidget()
        self.home_page = HomePage(self.stack, self)
        self.result_page = ResultPage(self.stack, self)
        self.weather_page = WeatherPage(self.stack, self)
        self.about_page = AboutPage(self.stack, self)
        self.river_mouth_page = RiverMouthImagesPage(self.stack, self)
        self.deviation_page = RiverMouthDeviationPage(self.stack, self)
        self.settings_page = SettingsPage(self.stack, self)

        self.stack.addWidget(self.home_page)                  # 0: Home
        self.stack.addWidget(self.result_page)                # 1: LULC
        self.stack.addWidget(self.weather_page)               # 2: Weather
        self.stack.addWidget(self.about_page)                 # 3: About
        self.stack.addWidget(self.river_mouth_page)           # 4: River Mouth Images
        self.stack.addWidget(self.deviation_page)             # 5: Deviation Analysis
        self.stack.addWidget(self.settings_page)              # 6: Settings

        body_layout.addWidget(self.stack, 1)
        main_app_layout.addWidget(body_widget, 1)
        main_app_layout.addWidget(self.status_bar)

        # Add both screens to root_stack: Index 0 is Login, Index 1 is Dashboard
        self.root_stack.addWidget(self.login_page)            # 0: Login Screen
        self.root_stack.addWidget(self.main_app_widget)       # 1: Dashboard

        self.setCentralWidget(self.root_stack)

        # Application startup: Display Login Page FIRST (Protected Startup Flow)
        self.root_stack.setCurrentIndex(0)

    # ========================================================================
    # Top Branding Banner
    # ========================================================================
    def build_top_banner(self) -> QFrame:
        banner = QFrame()
        banner.setFixedHeight(94)
        banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #04211D, stop:0.5 #082F28, stop:1 #062621);
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(16, 8, 16, 8)
        banner_layout.setSpacing(14)

        # 1. Spatio-Temporal Estuary Analysis Logo
        logo_label = QLabel()
        logo_label.setFixedSize(58, 58)
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
        if os.path.exists(logo_path):
            src_pix = QPixmap(logo_path)
            if not src_pix.isNull():
                rounded_logo = QPixmap(58, 58)
                rounded_logo.fill(Qt.transparent)
                p = QPainter(rounded_logo)
                p.setRenderHint(QPainter.Antialiasing)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                
                path = QPainterPath()
                path.addRoundedRect(1, 1, 56, 56, 12, 12)
                p.setClipPath(path)
                p.fillRect(1, 1, 56, 56, QColor("#FFFFFF"))
                
                scaled = src_pix.scaled(54, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                ox = (58 - scaled.width()) // 2
                oy = (58 - scaled.height()) // 2
                p.drawPixmap(ox, oy, scaled)
                
                p.setClipping(False)
                p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
                p.drawRoundedRect(1, 1, 56, 56, 12, 12)
                p.end()
                logo_label.setPixmap(rounded_logo)
        banner_layout.addWidget(logo_label)

        # 2. Title & Subtitle Branding
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title_box.setAlignment(Qt.AlignVCenter)

        brand_title = QLabel("Estuarine Mouth Dynamics")
        brand_title.setStyleSheet(f"""
            font-size: 21px;
            font-weight: 800;
            color: {WARM_IVORY};
            letter-spacing: 0.5px;
        """)

        brand_sub = QLabel("Path Deviation Prediction System")
        brand_sub.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {MINT};
        """)

        brand_labels = QLabel("Geospatial Analysis  |  Machine Learning  |  Sustainable Coastlines")
        brand_labels.setStyleSheet(f"""
            font-size: 11px;
            color: {MUTED_SAGE};
        """)

        title_box.addWidget(brand_title)
        title_box.addWidget(brand_sub)
        title_box.addWidget(brand_labels)
        banner_layout.addLayout(title_box)

        banner_layout.addStretch()

        # Location Badge
        loc_badge = QFrame()
        loc_badge.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
                padding: 4px 14px;
            }}
        """)
        lb_layout = QHBoxLayout(loc_badge)
        lb_layout.setContentsMargins(6, 2, 8, 2)
        lb_layout.setSpacing(6)

        pin_icon = QLabel()
        pin_icon.setPixmap(get_pixmap("location", color=TEAL, size=16))
        lb_layout.addWidget(pin_icon)

        self.loc_badge_text = QLabel("Kodi Bengre, Udupi, Karnataka, India")
        self.loc_badge_text.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {WARM_IVORY};")
        lb_layout.addWidget(self.loc_badge_text)

        banner_layout.addWidget(loc_badge)

        # 4. User Profile Badge & Logout Control
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
                padding: 4px 10px;
            }}
        """)
        uf_layout = QHBoxLayout(user_frame)
        uf_layout.setContentsMargins(6, 2, 8, 2)
        uf_layout.setSpacing(6)

        user_icon = QLabel()
        user_icon.setPixmap(get_pixmap("user", color=MINT, size=16))
        uf_layout.addWidget(user_icon)

        self.user_badge_text = QLabel("Researcher")
        self.user_badge_text.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {WARM_IVORY};")
        uf_layout.addWidget(self.user_badge_text)
        banner_layout.addWidget(user_frame)

        # Logout Button
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setIcon(get_icon("logout", color=WARM_IVORY, size=14))
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setToolTip("Sign out of current research session")
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                font-size: 11px;
                font-weight: 600;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 6px;
                padding: 5px 12px;
            }}
            QPushButton:hover {{
                background-color: #381515;
                color: #FF8A80;
                border-color: #B71C1C;
            }}
        """)
        self.btn_logout.clicked.connect(self.logout)
        banner_layout.addWidget(self.btn_logout)

        # 5. Scenic River Estuary Panoramic Graphic
        banner_img_lbl = QLabel()
        banner_img_lbl.setFixedSize(190, 68)
        banner_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "suvarna_banner.png"))
        if os.path.exists(banner_path):
            banner_pix = QPixmap(banner_path)
            if not banner_pix.isNull():
                styled_banner = QPixmap(190, 68)
                styled_banner.fill(Qt.transparent)
                bp = QPainter(styled_banner)
                bp.setRenderHint(QPainter.Antialiasing)
                bpath = QPainterPath()
                bpath.addRoundedRect(0, 0, 190, 68, 8, 8)
                bp.setClipPath(bpath)
                bp.drawPixmap(0, 0, 190, 68, banner_pix.scaled(190, 68, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                # Subtle border highlight
                bp.setPen(BORDER_COLOR)
                bp.drawRoundedRect(0, 0, 189, 67, 8, 8)
                bp.end()
                banner_img_lbl.setPixmap(styled_banner)
        banner_layout.addWidget(banner_img_lbl)

        return banner

    # ========================================================================
    # Bottom Status Bar (Section 3.F)
    # ========================================================================
    def build_status_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(32)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: #041E1A;
                border-top: 1px solid {BORDER_SUBTLE};
                padding: 0 14px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(16)

        # Map status dot & text
        status_box = QHBoxLayout()
        status_box.setSpacing(6)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {MINT}; font-size: 12px;")
        self.status_map_text = QLabel("Map Ready")
        self.status_map_text.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {WARM_IVORY};")
        status_box.addWidget(self.status_dot)
        status_box.addWidget(self.status_map_text)
        layout.addLayout(status_box)

        # Separator
        layout.addWidget(self.create_status_sep())

        # Map Mode Pill
        self.status_mode_pill = QLabel("Mode: OpenStreetMap Standard")
        self.status_mode_pill.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {MUTED_SAGE};
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid {BORDER_SUBTLE};
        """)
        layout.addWidget(self.status_mode_pill)

        # Separator
        layout.addWidget(self.create_status_sep())

        # Study Area
        self.status_study_area = QLabel("Study Area: Kodi Bengre, Udupi")
        self.status_study_area.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        layout.addWidget(self.status_study_area)

        layout.addStretch()

        # Analysis Readiness
        self.status_readiness = QLabel("Analysis: Ready for AOI selection")
        self.status_readiness.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {MINT};")
        layout.addWidget(self.status_readiness)

        # Separator
        layout.addWidget(self.create_status_sep())

        # Data-loaded status
        self.status_data = QLabel("Data: Landsat Multi-Spectral (1989-2026)")
        self.status_data.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        layout.addWidget(self.status_data)

        return bar

    def create_status_sep(self):
        sep = QLabel("|")
        sep.setStyleSheet(f"color: {BORDER_COLOR}; font-size: 11px;")
        return sep

    # ========================================================================
    # Authentication & Session Handlers
    # ========================================================================
    def is_authenticated(self) -> bool:
        """Returns True if a verified user session is currently active."""
        return self.current_user is not None and bool(self.current_user.get("id"))

    def on_login_success(self, user_info: dict):
        """Called upon successful credential validation from LoginPage."""
        self.current_user = user_info
        if hasattr(self, "user_badge_text") and self.user_badge_text:
            display_name = user_info.get("username", "User")
            role = user_info.get("role", "Researcher")
            self.user_badge_text.setText(f"{display_name}  ({role})")

        # Switch to Protected Main Application Dashboard
        self.root_stack.setCurrentIndex(1)

        # Open the existing Home page exactly as it currently looks
        self.navigate_to_page(0)
        self.update_status(
            status_text="Authenticated",
            readiness=f"Active Session: {user_info.get('username')}",
            data_text="Landsat Multi-Spectral (1989-2026)"
        )

    def logout(self):
        """Terminates active session and securely returns to Login Page."""
        self.current_user = None
        if hasattr(self, "login_page"):
            self.login_page.reset_for_logout()
        # Switch back to Login Screen
        self.root_stack.setCurrentIndex(0)
        self.update_status(
            status_text="Logged Out",
            readiness="Authentication Required"
        )

    # ========================================================================
    # Navigation & Status Updating Methods
    # ========================================================================
    def navigate_to_page(self, index: int):
        # Strict protection: Cannot access application pages without authentication
        if not self.is_authenticated():
            self.root_stack.setCurrentIndex(0)
            return
        self.stack.setCurrentIndex(index)
        for btn in self.nav_buttons:
            btn.set_active(btn.page_index == index)

    def go_to_home(self):
        self.navigate_to_page(0)

    def go_to_lulc(self):
        self.navigate_to_page(1)
        if hasattr(self, "result_page") and hasattr(self.result_page, "current_year"):
            y = self.result_page.current_year
            self.update_status(
                status_text=f"LULC Classification Page (Year {y})",
                mode_text="4-Class Satellite Classification",
                readiness="Active"
            )
        else:
            self.update_status(
                status_text="LULC Classification Page",
                mode_text="4-Class Satellite Classification",
                readiness="Active"
            )

    def go_to_weather(self):
        self.navigate_to_page(2)

    def go_to_river_mouth(self):
        self.navigate_to_page(4)
        self.update_status(
            status_text="River Mouth Imagery Gallery",
            mode_text="Multi-Decadal Observations",
            readiness="Ready for Analysis"
        )

    def go_to_analysis(self):
        self.navigate_to_page(5)
        if hasattr(self, "deviation_page") and hasattr(self.deviation_page, "run_analysis"):
            self.deviation_page.run_analysis()
        self.update_status(
            status_text="River-Mouth Deviation Analysis",
            mode_text="Estuarine Morphodynamics",
            readiness="Active"
        )

    def go_to_deviation(self):
        self.go_to_analysis()

    def run_analysis(self, base_year, target_year, aoi_coords=None):
        """Connects Home page Analysis button directly to the ResultPage / LULC pipeline."""
        self.result_page.load_analysis(base_year, target_year, aoi_coords)
        self.navigate_to_page(1)  # Index 1: LULC
        self.update_status(
            status_text=f"LULC Analysis: Year {target_year} (Base: {base_year})",
            readiness=f"Results active ({base_year} → {target_year})",
            data_text=f"Landsat & Weather ({target_year})"
        )


    def update_location(self, location_name, lat=None, lon=None):
        if hasattr(self, "loc_badge_text") and self.loc_badge_text:
            self.loc_badge_text.setText(location_name)
        if hasattr(self, "status_study_area") and self.status_study_area:
            self.status_study_area.setText(f"Study Area: {location_name}")

    def update_status(self, status_text=None, mode_text=None, readiness=None, data_text=None):
        if status_text and hasattr(self, "status_map_text") and self.status_map_text:
            self.status_map_text.setText(status_text)
            if hasattr(self, "status_dot") and self.status_dot:
                if "warning" in status_text.lower() or "error" in status_text.lower() or "offline" in status_text.lower():
                    self.status_dot.setStyleSheet(f"color: {AMBER}; font-size: 12px;")
                else:
                    self.status_dot.setStyleSheet(f"color: {MINT}; font-size: 12px;")
        if mode_text and hasattr(self, "status_mode_pill") and self.status_mode_pill:
            self.status_mode_pill.setText(mode_text)
        if readiness and hasattr(self, "status_readiness") and self.status_readiness:
            self.status_readiness.setText(f"Analysis: {readiness}")
        if data_text and hasattr(self, "status_data") and self.status_data:
            self.status_data.setText(f"Data: {data_text}")


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.raise_()
    window.activateWindow()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())