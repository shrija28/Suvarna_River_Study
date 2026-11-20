"""
River Mouth Images Page - Suvarna River Study GIS Dashboard
Displays multi-decadal river-mouth satellite observations (1989-2026)
in a clean, evenly-spaced responsive grid.
Includes:
- Fixed vertical navigation sidebar on left (Home, LULC, Weather)
- Upper-right Download button to export displayed images
- Bottom Analyze button navigating to the next analysis placeholder
Theme: Dark Emerald & Tropical Coastal GIS
"""

import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIntValidator
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QInputDialog,
)

from theme import (
    BG_DARK,
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
from backend.data_service import data_service
from nav_button import SidebarNavButton

# Use crisp custom-painted navigation button to eliminate all border/clipping line glitches
NavSidebarButton = SidebarNavButton


# ============================================================================
# Single Year Image Card
# ============================================================================
class YearImageCard(QFrame):
    def __init__(self, year: int, pixmap: QPixmap, meta: dict, on_download_single=None):
        super().__init__()
        self.year = year
        self.raw_pixmap = pixmap
        self.meta = meta
        self.on_download_single = on_download_single

        self.setStyleSheet(f"""
            YearImageCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            YearImageCard:hover {{
                border: 1px solid {MINT};
            }}
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(6)

        # Header: Year Label and Download Button
        header_row = QHBoxLayout()
        header_row.setSpacing(6)

        year_lbl = QLabel(str(year))
        year_lbl.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 800;
            color: {MINT};
            letter-spacing: 0.5px;
        """)
        header_row.addWidget(year_lbl)
        header_row.addStretch()

        # Download icon button for single year
        dl_btn = QPushButton()
        dl_btn.setFixedSize(24, 24)
        dl_btn.setCursor(Qt.PointingHandCursor)
        dl_btn.setIcon(get_icon("download", color=MUTED_SAGE, size=14))
        dl_btn.setToolTip(f"Download {year} River Mouth Image")
        dl_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                border-color: {MINT};
            }}
        """)
        if on_download_single:
            dl_btn.clicked.connect(lambda: on_download_single(self.year, self.raw_pixmap))
        header_row.addWidget(dl_btn)

        card_layout.addLayout(header_row)

        # Satellite Image Display
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.img_label.setMinimumSize(220, 160)
        self.img_label.setStyleSheet(f"""
            background-color: {BG_DARK};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 6px;
        """)
        card_layout.addWidget(self.img_label, 1)
        self.setMinimumHeight(235)
        self.setMinimumWidth(220)

        # Footer: Metadata info
        footer_row = QHBoxLayout()
        w_km2 = meta.get("water_km2", 0.0) if meta else 0.0
        width_m = meta.get("width_m") if meta else None
        is_avail = meta.get("available", True) if meta else True
        if not is_avail or pixmap is None or pixmap.isNull():
            meta_text = f"Observation Unavailable ({self.year})"
        elif meta and meta.get("view_mode") == "first_opening" and width_m:
            meta_text = f"Mouth Width: {width_m:.1f} m  |  First Opening (Drive)"
        elif meta and meta.get("view_mode") == "first_opening":
            meta_text = f"Estuary Water: {w_km2:.2f} km²  |  Baseline Geometry"
        else:
            meta_text = f"Estuary Water: {w_km2:.2f} km²  |  30m Landsat Mask"
        self.meta_lbl = QLabel(meta_text)
        self.meta_lbl.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE};")
        footer_row.addWidget(self.meta_lbl)
        footer_row.addStretch()
        card_layout.addLayout(footer_row)

        self.update_image()

    def update_data(self, pixmap: QPixmap, meta: dict, view_mode: str = "mask"):
        self.raw_pixmap = pixmap
        self.meta = meta
        w_km2 = meta.get("water_km2", 0.0) if meta else 0.0
        width_m = meta.get("width_m") if meta else None
        is_avail = meta.get("available", True) if meta else True
        if not is_avail or pixmap is None or pixmap.isNull():
            meta_text = f"Observation Unavailable ({self.year})"
        elif view_mode == "first_opening" and width_m:
            meta_text = f"Mouth Width: {width_m:.1f} m  |  First Opening (Drive)"
        elif view_mode == "first_opening":
            meta_text = f"Estuary Water: {w_km2:.2f} km²  |  Baseline Geometry"
        else:
            meta_text = f"Estuary Water: {w_km2:.2f} km²  |  30m Landsat Mask"
        self.meta_lbl.setText(meta_text)
        self.update_image()

    def update_image(self):
        if self.raw_pixmap and not self.raw_pixmap.isNull():
            target_size = self.img_label.size()
            if target_size.width() < 100 or target_size.height() < 100:
                target_size = QSize(240, 170)
            scaled = self.raw_pixmap.scaled(
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled)
            self.img_label.setText("")
            self.img_label.setStyleSheet(f"""
                background-color: {BG_DARK};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 6px;
            """)
        else:
            self.img_label.setPixmap(QPixmap())
            self.img_label.setText(f"Image not available for this year\n({self.year})")
            self.img_label.setStyleSheet(f"""
                background-color: {BG_DARK};
                color: {MUTED_SAGE};
                font-size: 11px;
                font-weight: 600;
                border: 1px dashed {BORDER_SUBTLE};
                border-radius: 6px;
                padding: 10px;
            """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()


# ============================================================================
# Main River Mouth Images Page
# ============================================================================
class RiverMouthImagesPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.cards = []
        self.current_view_mode = "mask"
        self._fallback_years = [1989, 2000]
        self.build_ui()

    @property
    def display_years(self) -> list[int]:
        """
        Reuses the Home page's selected Base Year and Prediction Year state directly.
        Returns the full inclusive year range (e.g. 1989..2000).
        """
        if self.main_window and hasattr(self.main_window, "home_page") and hasattr(self.main_window.home_page, "get_selected_years"):
            return self.main_window.home_page.get_selected_years()
        if hasattr(self, "_fallback_years") and self._fallback_years:
            return self._fallback_years
        return list(range(1989, 2001))

    @display_years.setter
    def display_years(self, years: list):
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
        self._fallback_years = list(range(valid[0], valid[-1] + 1))
        if self.main_window and hasattr(self.main_window, "home_page") and hasattr(self.main_window.home_page, "set_selected_years"):
            self.main_window.home_page.set_selected_years(self._fallback_years)

    @property
    def DISPLAY_YEARS(self):
        """Backwards compatibility accessor for benchmark years."""
        return self.display_years

    def showEvent(self, event):
        super().showEvent(event)
        # Always synchronize with Home page's selected-year range upon opening
        current_card_years = [c.year for c in self.cards]
        if current_card_years != self.display_years:
            self.populate_gallery()

    def build_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --------------------------------------------------------------------
        # Left Vertical Navigation Sidebar (Home, LULC, Weather)
        # --------------------------------------------------------------------
        sidebar = self.build_sidebar()
        root_layout.addWidget(sidebar)

        # --------------------------------------------------------------------
        # Main Content Area: Header Bar + Benchmark Toolbar + Grid + Bottom
        # --------------------------------------------------------------------
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 14, 20, 14)
        main_layout.setSpacing(12)

        # 1. Gallery Header Row (Title & Download Button in Upper Right)
        gallery_header = QHBoxLayout()
        gallery_header.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title = QLabel("River Mouth Satellite Imagery Gallery")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {WARM_IVORY};
            letter-spacing: 0.3px;
        """)

        title_box.addWidget(title)
        gallery_header.addLayout(title_box)

        gallery_header.addStretch()

        # Mode Toggle Selector: [ 🌊 Estuarine Water Masks ]  [ 📍 First-Opening Detection (Drive) ]
        mode_box = QFrame()
        mode_box.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
        """)
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.setContentsMargins(3, 2, 3, 2)
        mode_layout.setSpacing(4)

        self.btn_mode_mask = QPushButton("🌊 Estuarine Water Masks")
        self.btn_mode_mask.setFixedHeight(28)
        self.btn_mode_mask.setCursor(Qt.PointingHandCursor)
        self.btn_mode_mask.clicked.connect(lambda: self.set_view_mode("mask"))

        self.btn_mode_opening = QPushButton("📍 First-Opening Detection (Drive)")
        self.btn_mode_opening.setFixedHeight(28)
        self.btn_mode_opening.setCursor(Qt.PointingHandCursor)
        self.btn_mode_opening.clicked.connect(lambda: self.set_view_mode("first_opening"))

        mode_layout.addWidget(self.btn_mode_mask)
        mode_layout.addWidget(self.btn_mode_opening)
        gallery_header.addWidget(mode_box)
        self._update_toggle_styles()

        # Download Button in Upper-Right Corner
        self.download_btn = QPushButton("Download Images")
        self.download_btn.setIcon(get_icon("download", color=DARK_EMERALD, size=16))
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setFixedHeight(34)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: #5ED49D;
            }}
            QPushButton:pressed {{
                background-color: {TEAL};
            }}
        """)
        self.download_btn.clicked.connect(self.download_all_images)
        gallery_header.addWidget(self.download_btn)

        # Analyze Button in Header
        self.header_analyze_btn = QPushButton("Analyze Deviation  →")
        self.header_analyze_btn.setIcon(get_icon("analysis", color=DARK_EMERALD, size=16))
        self.header_analyze_btn.setCursor(Qt.PointingHandCursor)
        self.header_analyze_btn.setFixedHeight(34)
        self.header_analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SOFT_LIME};
                color: {DARK_EMERALD};
                font-size: 12px;
                font-weight: 800;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: #D4F090;
            }}
            QPushButton:pressed {{
                background-color: {MINT};
            }}
        """)
        self.header_analyze_btn.clicked.connect(self.go_to_analysis)
        gallery_header.addWidget(self.header_analyze_btn)

        main_layout.addLayout(gallery_header)

        # 2. Scrollable Image Gallery Grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        grid_container = QWidget()
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(14)
        self.grid_layout.setContentsMargins(0, 4, 4, 4)

        # Load real satellite images for each year and populate grid
        self.populate_gallery()

        scroll_area.setWidget(grid_container)
        main_layout.addWidget(scroll_area, 1)

        # 3. Bottom Action Bar with Analyze Button
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(50)
        bottom_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(16, 6, 16, 6)
        bottom_layout.setSpacing(14)
        bottom_layout.addStretch()

        # Analyze Button at Bottom
        self.analyze_btn = QPushButton("Analyze  →")
        self.analyze_btn.setIcon(get_icon("analysis", color=DARK_EMERALD, size=16))
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setFixedHeight(38)
        self.analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                font-size: 13px;
                font-weight: 800;
                border: none;
                border-radius: 6px;
                padding: 8px 26px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: #5ED49D;
            }}
            QPushButton:pressed {{
                background-color: {TEAL};
            }}
        """)
        self.analyze_btn.clicked.connect(self.go_to_analysis)
        bottom_layout.addWidget(self.analyze_btn)

        main_layout.addWidget(bottom_bar)

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

        # Sidebar Title
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

        # 1. Home Button -> navigates to page 0
        btn_home = NavSidebarButton(
            icon_name="home",
            title="Home",
            desc="Map & Study Area",
            on_click=self.go_to_home
        )
        layout.addWidget(btn_home)

        # 2. LULC Button -> navigates to page 1
        btn_lulc = NavSidebarButton(
            icon_name="lulc",
            title="LULC",
            desc="Land Use & Migration",
            on_click=self.go_to_lulc
        )
        layout.addWidget(btn_lulc)

        # 3. Weather Button -> navigates to page 2
        btn_weather = NavSidebarButton(
            icon_name="weather",
            title="Weather",
            desc="Rainfall & Climate Data",
            on_click=self.go_to_weather
        )
        layout.addWidget(btn_weather)

        layout.addStretch()

        # Context Card at bottom of sidebar
        context_card = QFrame()
        context_card.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        c_layout = QVBoxLayout(context_card)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(4)

        tag = QLabel("ESTUARY IMAGERY")
        tag.setStyleSheet(f"font-size: 9px; font-weight: 800; color: {MINT}; letter-spacing: 0.5px;")
        c_desc = QLabel("Multi-decadal multi-spectral rasters tracking spit morphology & tidal inlet migration.")
        c_desc.setWordWrap(True)
        c_desc.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; line-height: 1.3;")

        c_layout.addWidget(tag)
        c_layout.addWidget(c_desc)
        layout.addWidget(context_card)

        return sidebar

    # ========================================================================
    # View Mode Toggle & Gallery Population
    # ========================================================================
    def _update_toggle_styles(self):
        active_style = f"""
            QPushButton {{
                background-color: {TEAL};
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {MUTED_SAGE};
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
            }}
        """
        if self.current_view_mode == "mask":
            self.btn_mode_mask.setStyleSheet(active_style)
            self.btn_mode_opening.setStyleSheet(inactive_style)
        else:
            self.btn_mode_mask.setStyleSheet(inactive_style)
            self.btn_mode_opening.setStyleSheet(active_style)

    def set_view_mode(self, mode: str):
        if self.current_view_mode == mode and self.cards:
            return
        self.current_view_mode = mode
        self._update_toggle_styles()
        for card in self.cards:
            pix, meta = data_service.get_raster_image_for_year(card.year, view_mode=mode)
            card.update_data(pix, meta, view_mode=mode)
        if self.main_window and hasattr(self.main_window, "update_status"):
            desc = "Clean Estuarine Water Masks" if mode == "mask" else "Google Drive First-Opening Mouth Detections"
            self.main_window.update_status(status_text=f"River Mouth Gallery: {desc}")

    def set_selected_years(self, years: list, force_reload: bool = False):
        """
        Reuses and updates the Home page's selected-year state directly.
        Ensures the gallery and Home page always remain synchronized, rather
        than maintaining two independent year selections.
        """
        if years and self.main_window and hasattr(self.main_window, "home_page") and hasattr(self.main_window.home_page, "set_selected_years"):
            self.main_window.home_page.set_selected_years(years)
        elif years:
            self._fallback_years = sorted(list(set(int(y) for y in years if str(y).strip().isdigit())))

        self.populate_gallery()

    def populate_gallery(self):
        # Clear existing widgets cleanly
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.cards.clear()

        years = self.display_years
        num_years = len(years)
        if num_years == 0:
            empty_lbl = QLabel("No observation years selected on the Home page.")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"font-size: 13px; color: {MUTED_SAGE}; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
            return

        # Dynamically adjust column count to match the number of selected years
        if num_years <= 4:
            cols = max(1, num_years)
        elif num_years == 6:
            cols = 3
        else:
            cols = 4

        self.grid_layout.setAlignment(Qt.AlignTop)
        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 1)

        for idx, yr in enumerate(years):
            pix, meta = data_service.get_raster_image_for_year(yr, view_mode=self.current_view_mode)
            card = YearImageCard(
                year=yr,
                pixmap=pix,
                meta=meta,
                on_download_single=self.download_single_image
            )
            self.cards.append(card)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)

    # ========================================================================
    # Navigation Actions
    # ========================================================================
    def go_to_home(self):
        """Navigates to the application's first page (Home)."""
        if self.main_window and hasattr(self.main_window, "go_to_home"):
            self.main_window.go_to_home()
        elif self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(0)
        else:
            self.stack.setCurrentIndex(0)

    def go_to_lulc(self):
        """Navigates to the existing LULC page."""
        if self.main_window and hasattr(self.main_window, "go_to_lulc"):
            self.main_window.go_to_lulc()
        elif self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(1)
        else:
            self.stack.setCurrentIndex(1)

    def go_to_weather(self):
        """Navigates to the Weather Data page."""
        if self.main_window and hasattr(self.main_window, "go_to_weather"):
            self.main_window.go_to_weather()
        elif self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(2)
        else:
            self.stack.setCurrentIndex(2)

    def go_to_analysis(self):
        """Navigates to the River Mouth Deviation Analysis page."""
        years = self.display_years
        b_yr = years[0] if years else 1989
        t_yr = years[-1] if len(years) > 1 else (years[0] if years else 2026)

        print(f"[Gallery] Analyze clicked: Navigating to Deviation Analysis (Base={b_yr}, Target={t_yr})")

        # Synchronize centralized data service
        from backend.data_service import data_service
        data_service.set_year_range(b_yr, t_yr)

        if self.main_window and hasattr(self.main_window, "go_to_analysis"):
            self.main_window.go_to_analysis()
        elif self.main_window and hasattr(self.main_window, "navigate_to_page"):
            if hasattr(self.main_window, "deviation_page") and hasattr(self.main_window.deviation_page, "set_years"):
                self.main_window.deviation_page.set_years(b_yr, t_yr)
            self.main_window.navigate_to_page(5)  # Index 5: Deviation Analysis
        elif self.stack:
            self.stack.setCurrentIndex(5)

    # ========================================================================
    # Download Functionality
    # ========================================================================
    def download_all_images(self):
        """Exports all displayed river mouth images within the selected range to a folder chosen by user."""
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Save River Mouth Images",
            os.path.expanduser("~")
        )
        if not target_dir:
            return

        saved_files = []
        mode_prefix = "First_Opening" if self.current_view_mode == "first_opening" else "Water_Mask"
        for card in self.cards:
            if card.raw_pixmap and not card.raw_pixmap.isNull():
                orig_fn = card.meta.get("filename") if card.meta else ""
                if orig_fn:
                    base_name, _ = os.path.splitext(orig_fn)
                    fn = f"{base_name}.png"
                else:
                    fn = f"Suvarna_{mode_prefix}_{card.year}.png"
                out_path = os.path.join(target_dir, fn)
                card.raw_pixmap.save(out_path, "PNG")
                saved_files.append(fn)

        if saved_files:
            msg = (
                f"Successfully downloaded {len(saved_files)} river-mouth images to:\n\n"
                f"{target_dir}\n\n"
                f"Files: {', '.join(saved_files)}"
            )
            QMessageBox.information(self, "Download Complete", msg)
            if self.main_window and hasattr(self.main_window, "update_status"):
                self.main_window.update_status(
                    status_text=f"Downloaded {len(saved_files)} river-mouth images"
                )
        else:
            QMessageBox.warning(self, "Download Notice", "No valid image rasters were found to export for the selected years.")

    def download_single_image(self, year: int, pixmap: QPixmap):
        """Exports a single year's river mouth image to user-chosen path."""
        if not pixmap or pixmap.isNull():
            QMessageBox.warning(self, "Download Warning", f"Image not available for this year ({year}).")
            return

        matching_card = next((c for c in self.cards if c.year == year), None)
        orig_fn = matching_card.meta.get("filename") if matching_card and matching_card.meta else ""
        if orig_fn:
            base_name, _ = os.path.splitext(orig_fn)
            default_name = f"{base_name}.png"
        else:
            mode_prefix = "First_Opening" if self.current_view_mode == "first_opening" else "Water_Mask"
            default_name = f"Suvarna_{mode_prefix}_{year}.png"

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save River Mouth Image ({year})",
            os.path.join(os.path.expanduser("~"), default_name),
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if out_path:
            pixmap.save(out_path)
            QMessageBox.information(
                self,
                "Image Saved",
                f"Successfully saved {year} river-mouth image to:\n{out_path}"
            )

