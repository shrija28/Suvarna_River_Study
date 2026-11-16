"""
River-Mouth Deviation & Morphodynamic Analysis Page - Suvarna River Study GIS Dashboard
Destination when the user clicks 'Analyze' on the River Mouth Satellite Imagery Gallery.
Features:
1. Navigation sidebar (Home, River Mouth, LULC, Weather)
2. Base-year & Target-year selectors + Run Analysis button
3. Summary cards for Displacement (m), Direction (azimuth & compass), Water Area Change (km²), Annual Rate (m/yr)
4. Satellite comparison view (Base Year vs Target Year channel & mouth throat)
5. Time-series chart of river-mouth displacement (1989-2026) clearly separating Ground Truth vs AI Projection
6. Comprehensive historical measurements data table
7. Multi-format export: CSV, GIS GeoJSON vector, and scientific report
Theme: Dark Emerald & Tropical Coastal GIS
"""

import os
import pandas as pd
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QPainterPath,
    QLinearGradient,
    QPixmap,
    QIntValidator,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
    QMenu,
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
    INPUT_BG,
)
from icons import get_icon, get_pixmap
from backend.deviation_service import deviation_service
from nav_button import SidebarNavButton

# Use crisp custom-painted navigation button to eliminate all border/clipping line glitches
DeviationNavButton = SidebarNavButton


# ============================================================================
# Metric Summary Card Widget
# ============================================================================
class DeviationMetricCard(QFrame):
    def __init__(self, title: str, accent_color: str, subtitle: str):
        super().__init__()
        self.setStyleSheet(f"""
            DeviationMetricCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-top: 3px solid {accent_color};
                border-radius: 8px;
                padding: 10px;
            }}
            DeviationMetricCard:hover {{
                border-color: {MINT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        header_row.setSpacing(6)

        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {MUTED_SAGE}; letter-spacing: 0.3px;")
        header_row.addWidget(t_lbl)
        header_row.addStretch()

        self.badge_lbl = QLabel("--")
        self.badge_lbl.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {WARM_IVORY};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 4px;
            padding: 2px 5px;
            font-size: 9px;
            font-weight: 700;
        """)
        header_row.addWidget(self.badge_lbl)
        layout.addLayout(header_row)

        self.value_lbl = QLabel("--")
        self.value_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {WARM_IVORY}; margin-top: 2px;")
        layout.addWidget(self.value_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE};")
        self.sub_lbl.setWordWrap(True)
        layout.addWidget(self.sub_lbl)

    def set_content(self, value: str, badge: str, subtitle: str = None):
        self.value_lbl.setText(value)
        self.badge_lbl.setText(badge)
        if subtitle:
            self.sub_lbl.setText(subtitle)


# ============================================================================
# Custom Time-Series Displacement Chart Widget
# ============================================================================
class DeviationTimeSeriesChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dev_data = None
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, dev_data):
        self.dev_data = dev_data
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor(DARK_EMERALD))

        if not self.dev_data or "timeseries" not in self.dev_data:
            p.setPen(QColor(MUTED_SAGE))
            p.setFont(QFont("Segoe UI", 12))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "No deviation time-series data available")
            p.end()
            return

        ts = self.dev_data["timeseries"]
        base_y = self.dev_data["base_year"]
        target_y = self.dev_data["target_year"]

        # Margins
        pad_left = 65
        pad_right = 35
        pad_top = 40
        pad_bottom = 45

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)

        # Title
        p.setPen(QColor(WARM_IVORY))
        p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.drawText(16, 24, f"River-Mouth Displacement Relative to Base Year {base_y} (1989–2026)")

        # Legend on top right
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(MINT))
        p.drawText(w - 240, 24, "● Ground Truth Landsat")
        p.setPen(QColor(AMBER))
        p.drawText(w - 100, 24, "◆ AI Projection")

        # Range calculations
        max_dist = max([item["displacement_m"] for item in ts] + [100.0])
        y_max = max(100.0, ((int(max_dist) // 50) + 1) * 50.0)

        # Grid lines (4 intervals)
        p.setFont(QFont("Segoe UI", 9))
        for i in range(5):
            val = (i / 4.0) * y_max
            y_pos = pad_top + plot_h - (val / y_max) * plot_h
            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(pad_left, int(y_pos), pad_left + plot_w, int(y_pos))

            p.setPen(QColor(MUTED_SAGE))
            p.drawText(pad_left - 55, int(y_pos + 4), f"{val:.0f} m")

        # Baseline axis
        p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
        p.drawLine(pad_left, pad_top + plot_h, pad_left + plot_w, pad_top + plot_h)
        p.drawLine(pad_left, pad_top, pad_left, pad_top + plot_h)

        # Map years to X coordinates
        coords = []
        n_pts = len(ts)
        for i, item in enumerate(ts):
            x = pad_left + (i / max(1, n_pts - 1)) * plot_w
            y = pad_top + plot_h - (item["displacement_m"] / y_max) * plot_h
            coords.append((x, y, item))

        # Separate historical vs AI projection segments
        hist_coords = [c for c in coords if not c[2]["is_projection"]]
        proj_coords = [c for c in coords if c[2]["is_projection"]]

        # Fill area under curve (valid measurement years)
        valid_coords = [c for c in coords if c[2].get("has_data", True)]
        if len(valid_coords) > 1:
            area_path = QPainterPath()
            area_path.moveTo(valid_coords[0][0], pad_top + plot_h)
            for x, y, _ in valid_coords:
                area_path.lineTo(x, y)
            area_path.lineTo(valid_coords[-1][0], pad_top + plot_h)
            area_path.closeSubpath()

            grad = QLinearGradient(0, pad_top, 0, pad_top + plot_h)
            grad.setColorAt(0.0, QColor(0, 191, 165, 80))
            grad.setColorAt(1.0, QColor(0, 191, 165, 5))
            p.fillPath(area_path, grad)

        # Draw Historical Line (connecting valid observation years)
        valid_hist_coords = [c for c in coords if not c[2]["is_projection"] and c[2].get("has_data", True)]
        if len(valid_hist_coords) > 1:
            line_path = QPainterPath()
            line_path.moveTo(valid_hist_coords[0][0], valid_hist_coords[0][1])
            for x, y, _ in valid_hist_coords[1:]:
                line_path.lineTo(x, y)
            p.setPen(QPen(QColor(TEAL), 2.5))
            p.drawPath(line_path)

        # Draw Projection Connection Line (Dashed in Amber)
        if proj_coords and valid_hist_coords:
            p_path = QPainterPath()
            p_path.moveTo(valid_hist_coords[-1][0], valid_hist_coords[-1][1])
            for x, y, _ in proj_coords:
                p_path.lineTo(x, y)
            p.setPen(QPen(QColor(AMBER), 2.5, Qt.DashLine))
            p.drawPath(p_path)

        # Draw Data Points & X-Axis Labels
        step_lbl = max(1, n_pts // 8)
        for i, (x, y, item) in enumerate(coords):
            yr = item["year"]
            is_proj = item["is_projection"]
            is_base = item["is_base"]
            is_target = item["is_target"]
            has_data = item.get("has_data", True)

            # X-axis year label
            if i % step_lbl == 0 or is_base or is_target or i == n_pts - 1 or yr == 1995:
                p.setPen(QColor(SOFT_LIME if (is_base or is_target) else (QColor(AMBER) if yr == 1995 else MUTED_SAGE)))
                p.setFont(QFont("Segoe UI", 9, QFont.Bold if (is_base or is_target or yr == 1995) else QFont.Normal))
                p.drawText(int(x - 14), pad_top + plot_h + 18, str(yr))

            # Point Node
            if not has_data or yr == 1995:
                # 1995: Strictly Zero / No Data marker on baseline
                p.setPen(QPen(QColor(AMBER), 1.5, Qt.DotLine))
                p.setBrush(Qt.NoBrush)
                p.drawEllipse(QPointF(x, pad_top + plot_h), 4, 4)
                p.setFont(QFont("Segoe UI", 8))
                p.setPen(QColor(AMBER))
                p.drawText(int(x - 16), pad_top + plot_h - 8, "0m (NaN)")
                continue

            pt_color = QColor(AMBER) if is_proj else QColor(MINT)
            if is_base or is_target:
                p.setPen(QPen(QColor(WARM_IVORY), 2))
                p.setBrush(QBrush(pt_color))
                p.drawEllipse(QPointF(x, y), 6, 6)
                # Value callout
                p.setFont(QFont("Segoe UI", 9, QFont.Bold))
                p.setPen(QColor(WARM_IVORY))
                p.drawText(int(x - 20), int(y - 10), f"{item['displacement_m']:.0f}m")
            else:
                p.setPen(QPen(QColor(BG_DARK), 1.5))
                p.setBrush(QBrush(pt_color))
                if is_proj:
                    # Diamond for projection
                    poly = QPainterPath()
                    poly.moveTo(x, y - 4)
                    poly.lineTo(x + 4, y)
                    poly.lineTo(x, y + 4)
                    poly.lineTo(x - 4, y)
                    poly.closeSubpath()
                    p.fillPath(poly, pt_color)
                else:
                    p.drawEllipse(QPointF(x, y), 3.5, 3.5)

        p.end()


# ============================================================================
# Side-by-Side Satellite Comparison Frame
# ============================================================================
class SatelliteComparisonCard(QFrame):
    def __init__(self):
        super().__init__()
        self.base_pixmap = None
        self.target_pixmap = None

        self.setStyleSheet(f"""
            SatelliteComparisonCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        self.title_lbl = QLabel("River-Mouth Channel Boundary & Throat Comparison")
        self.title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {WARM_IVORY};")
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()

        self.meta_chip = QLabel("30m Landsat • EPSG:32643")
        self.meta_chip.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {MINT};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: 600;
        """)
        header_row.addWidget(self.meta_chip)
        card_layout.addLayout(header_row)

        # Side-by-side Images Container
        images_row = QHBoxLayout()
        images_row.setSpacing(12)

        # Left: Base Year Box
        self.base_box = QFrame()
        self.base_box.setStyleSheet(f"background-color: {BG_DARK}; border: 1px solid {BORDER_SUBTLE}; border-radius: 6px;")
        b_layout = QVBoxLayout(self.base_box)
        b_layout.setContentsMargins(8, 8, 8, 8)
        b_layout.setSpacing(4)

        self.base_header = QLabel("Base Year: 1989")
        self.base_header.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {AMBER};")
        b_layout.addWidget(self.base_header)

        self.base_img_lbl = QLabel()
        self.base_img_lbl.setAlignment(Qt.AlignCenter)
        self.base_img_lbl.setMinimumSize(220, 200)
        self.base_img_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        b_layout.addWidget(self.base_img_lbl, 1)

        self.base_footer = QLabel("Mouth UTM: 466910m E, 1487143m N")
        self.base_footer.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; font-family: 'Consolas', monospace;")
        b_layout.addWidget(self.base_footer)

        images_row.addWidget(self.base_box, 1)

        # Right: Target Year Box
        self.target_box = QFrame()
        self.target_box.setStyleSheet(f"background-color: {BG_DARK}; border: 1px solid {BORDER_SUBTLE}; border-radius: 6px;")
        t_layout = QVBoxLayout(self.target_box)
        t_layout.setContentsMargins(8, 8, 8, 8)
        t_layout.setSpacing(4)

        self.target_header = QLabel("Target Year: 2026 (AI Projection)")
        self.target_header.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {SOFT_LIME};")
        t_layout.addWidget(self.target_header)

        self.target_img_lbl = QLabel()
        self.target_img_lbl.setAlignment(Qt.AlignCenter)
        self.target_img_lbl.setMinimumSize(220, 200)
        self.target_img_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        t_layout.addWidget(self.target_img_lbl, 1)

        self.target_footer = QLabel("Mouth UTM: 466891m E, 1486580m N")
        self.target_footer.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; font-family: 'Consolas', monospace;")
        t_layout.addWidget(self.target_footer)

        images_row.addWidget(self.target_box, 1)

        card_layout.addLayout(images_row, 1)

        # Difference in Coordinates & Meters Bar
        self.diff_bar = QFrame()
        self.diff_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border: 1px solid {BORDER_SUBTLE};
                border-left: 3px solid {MINT};
                border-radius: 6px;
            }}
        """)
        diff_layout = QHBoxLayout(self.diff_bar)
        diff_layout.setContentsMargins(12, 6, 12, 6)
        diff_layout.setSpacing(16)

        self.diff_lat_lbl = QLabel("ΔLatitude: --")
        self.diff_lat_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {MINT};")
        diff_layout.addWidget(self.diff_lat_lbl)

        self.diff_lon_lbl = QLabel("ΔLongitude: --")
        self.diff_lon_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {SOFT_LIME};")
        diff_layout.addWidget(self.diff_lon_lbl)

        self.diff_meters_lbl = QLabel("Difference in Meters: --")
        self.diff_meters_lbl.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {WARM_IVORY};")
        diff_layout.addWidget(self.diff_meters_lbl)

        diff_layout.addStretch()
        card_layout.addWidget(self.diff_bar)

        # Legend Bar
        legend_row = QHBoxLayout()
        legend_row.setSpacing(14)

        leg1 = QLabel("● Base Mouth Position")
        leg1.setStyleSheet(f"color: {AMBER}; font-size: 11px; font-weight: 600;")
        leg2 = QLabel("● Target Mouth Position")
        leg2.setStyleSheet(f"color: {SOFT_LIME}; font-size: 11px; font-weight: 600;")
        leg3 = QLabel("■ Estuarine Water Body")
        leg3.setStyleSheet(f"color: {TEAL}; font-size: 11px; font-weight: 600;")

        legend_row.addWidget(leg1)
        legend_row.addWidget(leg2)
        legend_row.addWidget(leg3)
        legend_row.addStretch()
        card_layout.addLayout(legend_row)

    def set_comparison(self, dev_data):
        b = dev_data["base_data"]
        t = dev_data["target_data"]
        self.base_pixmap = b["pixmap"]
        self.target_pixmap = t["pixmap"]

        self.base_header.setText(f"Base Year: {dev_data['base_year']} ({b['obs_type']}) • {b['water_area_km2']:.2f} km²")
        self.base_footer.setText(f"Mouth: {b['mouth_utm_x']:.0f}m E, {b['mouth_utm_y']:.0f}m N ({b['mouth_lat']:.4f}°N, {b['mouth_lon']:.4f}°E)")

        self.target_header.setText(f"Target Year: {dev_data['target_year']} ({t['obs_type']}) • {t['water_area_km2']:.2f} km²")
        self.target_footer.setText(f"Mouth: {t['mouth_utm_x']:.0f}m E, {t['mouth_utm_y']:.0f}m N ({t['mouth_lat']:.4f}°N, {t['mouth_lon']:.4f}°E)")

        # Update Difference Banner
        d_lat = dev_data.get("d_lat", t["mouth_lat"] - b["mouth_lat"])
        d_lon = dev_data.get("d_lon", t["mouth_lon"] - b["mouth_lon"])
        dx = dev_data["dx_m"]
        dy = dev_data["dy_m"]
        dist_m = dev_data["displacement_m"]
        ns = "North" if dy > 0 else ("South" if dy < 0 else "")
        ew = "East" if dx > 0 else ("West" if dx < 0 else "")

        self.diff_lat_lbl.setText(f"ΔLatitude: {d_lat:+.6f}° ({dy:+.1f} m {ns})")
        self.diff_lon_lbl.setText(f"ΔLongitude: {d_lon:+.6f}° ({dx:+.1f} m {ew})")
        self.diff_meters_lbl.setText(f"Difference in Meters: {dist_m:.1f} m (Euclidean)")

        self._scale_images()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._scale_images()

    def _scale_images(self):
        if self.base_pixmap and not self.base_pixmap.isNull():
            bw = max(80, self.base_img_lbl.width() - 4)
            bh = max(80, self.base_img_lbl.height() - 4)
            self.base_img_lbl.setPixmap(self.base_pixmap.scaled(bw, bh, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if self.target_pixmap and not self.target_pixmap.isNull():
            tw = max(80, self.target_img_lbl.width() - 4)
            th = max(80, self.target_img_lbl.height() - 4)
            self.target_img_lbl.setPixmap(self.target_pixmap.scaled(tw, th, Qt.KeepAspectRatio, Qt.SmoothTransformation))


# ============================================================================
# Main River-Mouth Deviation Page Widget
# ============================================================================
class RiverMouthDeviationPage(QWidget):
    def __init__(self, stack=None, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.base_year = 1989
        self.target_year = 2026
        self.available_years = []
        self.current_deviation = None

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Vertical Navigation Sidebar
        sidebar = self.build_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Main Scrollable Content Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"background-color: {BG_DARK}; border: none;")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 14, 20, 20)
        self.content_layout.setSpacing(14)

        # Header Toolbar
        header_bar = self.build_header_toolbar()
        self.content_layout.addWidget(header_bar)

        # 5 Summary Cards Row: Meters, Latitude, Longitude, Direction, Water Area
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)

        self.card_disp = DeviationMetricCard("Difference in Meters", TEAL, "Total Euclidean spatial displacement")
        self.card_lat = DeviationMetricCard("Difference in Latitude", MINT, "Northing displacement along meridian")
        self.card_lon = DeviationMetricCard("Difference in Longitude", SOFT_LIME, "Easting displacement along parallel")
        self.card_dir = DeviationMetricCard("Displacement Direction", AMBER, "Azimuth bearing relative to True North")
        self.card_area = DeviationMetricCard("Water Area & Migration", "#1E88E5", "Net channel surface area difference")

        cards_row.addWidget(self.card_disp)
        cards_row.addWidget(self.card_lat)
        cards_row.addWidget(self.card_lon)
        cards_row.addWidget(self.card_dir)
        cards_row.addWidget(self.card_area)
        self.content_layout.addLayout(cards_row)

        # Middle Grid: Comparison Cards (Left) + Time-Series Chart (Right)
        mid_grid = QGridLayout()
        mid_grid.setSpacing(14)

        self.comparison_card = SatelliteComparisonCard()
        self.chart_widget = DeviationTimeSeriesChart()

        mid_grid.addWidget(self.comparison_card, 0, 0)
        mid_grid.addWidget(self.chart_widget, 0, 1)
        mid_grid.setColumnStretch(0, 1)
        mid_grid.setColumnStretch(1, 1)
        self.content_layout.addLayout(mid_grid, 1)

        # Bottom Section: Results Table
        table_container = self.build_table_section()
        self.content_layout.addWidget(table_container)

        scroll_area.setWidget(content_widget)
        root_layout.addWidget(scroll_area, 1)

        # Initialize data
        self.init_data()

    # ========================================================================
    # Navigation Sidebar
    # ========================================================================
    def build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(10)

        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 800;
            color: {MUTED_SAGE};
            letter-spacing: 1.5px;
            padding-bottom: 4px;
        """)
        layout.addWidget(nav_label)

        # 1. Home
        btn_home = DeviationNavButton("home", "Home", "Map & Study Area", self.go_to_home, is_active=False)
        layout.addWidget(btn_home)

        # 2. River Mouth Gallery
        btn_gallery = DeviationNavButton("analysis", "River Mouth", "Satellite Imagery", self.go_to_river_mouth, is_active=False)
        layout.addWidget(btn_gallery)

        # 3. LULC
        btn_lulc = DeviationNavButton("lulc", "LULC", "Land Use & Migration", self.go_to_lulc, is_active=False)
        layout.addWidget(btn_lulc)

        # 4. Weather
        btn_weather = DeviationNavButton("weather", "Weather", "Rainfall & Climate Data", self.go_to_weather, is_active=False)
        layout.addWidget(btn_weather)

        layout.addStretch()

        # Context Card at bottom
        context_card = QFrame()
        context_card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        c_layout = QVBoxLayout(context_card)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(4)

        t_lbl = QLabel("ESTUARINE DYNAMICS")
        t_lbl.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {SOFT_LIME}; letter-spacing: 0.5px;")
        c_layout.addWidget(t_lbl)

        d_lbl = QLabel("Spatio-temporal mouth displacement tracking via georeferenced satellite throat centroids (EPSG:32643).")
        d_lbl.setStyleSheet(f"font-size: 9px; color: {MUTED_SAGE}; line-height: 1.3;")
        d_lbl.setWordWrap(True)
        c_layout.addWidget(d_lbl)

        layout.addWidget(context_card)
        return sidebar

    # ========================================================================
    # Top Header & Controls Toolbar (Button-free, fully automatic)
    # ========================================================================
    def build_header_toolbar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 10px 16px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(14)

        # Title & Subtitle (Clean header, no buttons)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel("River-Mouth Deviation & Morphodynamic Analysis")
        title.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {WARM_IVORY};")

        subtitle = QLabel("Kodi Bengre Estuary • Multi-Decadal Displacement, Directional Azimuth & Channel Geomorphology")
        subtitle.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        layout.addLayout(text_layout)

        layout.addStretch()

        # Base Year Selector (Editable with manual entry)
        lbl_base = QLabel("Base:")
        lbl_base.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {MUTED_SAGE};")
        layout.addWidget(lbl_base)

        val = QIntValidator(1980, 2035, self)

        self.combo_base = QComboBox()
        self.combo_base.setFixedWidth(95)
        self.combo_base.setEditable(True)
        self.combo_base.setValidator(val)
        if self.combo_base.lineEdit():
            self.combo_base.lineEdit().setPlaceholderText("YYYY")
        self.style_combo(self.combo_base)
        layout.addWidget(self.combo_base)

        # Arrow indicator
        arrow_lbl = QLabel("→")
        arrow_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {MINT};")
        layout.addWidget(arrow_lbl)

        # Target Year Selector (Editable with manual entry)
        lbl_target = QLabel("Target:")
        lbl_target.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {MUTED_SAGE};")
        layout.addWidget(lbl_target)

        self.combo_target = QComboBox()
        self.combo_target.setFixedWidth(95)
        self.combo_target.setEditable(True)
        self.combo_target.setValidator(val)
        if self.combo_target.lineEdit():
            self.combo_target.lineEdit().setPlaceholderText("YYYY")
        self.style_combo(self.combo_target)
        layout.addWidget(self.combo_target)

        # Connect both year selectors for instant, automatic analysis on selection/edit
        self.combo_base.currentTextChanged.connect(self.on_year_selection_changed)
        self.combo_target.currentTextChanged.connect(self.on_year_selection_changed)

        return bar

    def style_combo(self, combo: QComboBox):
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox:hover {{
                border-color: {MINT};
            }}
            QComboBox QLineEdit {{
                background: transparent;
                color: {WARM_IVORY};
                border: none;
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                selection-background-color: {PANEL_GREEN};
                selection-color: {SOFT_LIME};
                border: 1px solid {BORDER_COLOR};
                padding: 4px;
            }}
        """)

    # ========================================================================
    # Results & Timeseries Table Section
    # ========================================================================
    def build_table_section(self) -> QFrame:
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Table Header
        h_row = QHBoxLayout()
        t_lbl = QLabel("Historical & Model-Projected River-Mouth Width & Shift Measurements")
        t_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {WARM_IVORY};")
        h_row.addWidget(t_lbl)
        h_row.addStretch()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter...")
        self.filter_input.setFixedWidth(100)
        self.filter_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                color: {WARM_IVORY};
                padding: 3px 8px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border-color: {MINT};
            }}
        """)
        self.filter_input.textChanged.connect(self.on_filter_changed)
        h_row.addWidget(self.filter_input)

        self.table_note = QLabel("1 to 38 of 38 entries")
        self.table_note.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE}; font-family: 'Consolas', monospace;")
        h_row.addWidget(self.table_note)
        layout.addLayout(h_row)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Index", "Year", "Mouth Width (m)", "Longitude", "Latitude",
            "East Shift (m)", "North Shift (m)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(260)
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_SUBTLE};
                gridline-color: {BORDER_SUBTLE};
                border-radius: 6px;
                color: {WARM_IVORY};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {PANEL_GREEN};
                color: {WARM_IVORY};
                font-weight: 700;
                font-size: 11px;
                padding: 6px;
                border: 1px solid {BORDER_SUBTLE};
            }}
            QTableWidget::item:selected {{
                background-color: {PANEL_GREEN};
                color: {MINT};
            }}
        """)
        layout.addWidget(self.table)

        return container

    # ========================================================================
    # Data Initialization & Execution
    # ========================================================================
    def init_data(self):
        self.available_years = deviation_service.get_available_years()
        if not self.available_years:
            self.available_years = [1989, 2026]

        self.combo_base.blockSignals(True)
        self.combo_target.blockSignals(True)
        self.combo_base.clear()
        self.combo_target.clear()

        for y in self.available_years:
            if y != 1995:
                self.combo_base.addItem(str(y))
            self.combo_target.addItem(str(y))

        # Default: Base = 1989, Target = 2026 (or highest year)
        if 1989 in self.available_years:
            self.combo_base.setCurrentText("1989")
        else:
            self.combo_base.setCurrentIndex(0)

        if 2026 in self.available_years:
            self.combo_target.setCurrentText("2026")
        else:
            self.combo_target.setCurrentIndex(len(self.available_years) - 1)

        self.combo_base.blockSignals(False)
        self.combo_target.blockSignals(False)

        self.run_analysis()

    def on_year_selection_changed(self, _=""):
        b_txt = self.combo_base.currentText().strip()
        t_txt = self.combo_target.currentText().strip()
        if b_txt.isdigit() and t_txt.isdigit():
            b_yr = int(b_txt)
            t_yr = int(t_txt)
            if 1980 <= b_yr <= 2035 and 1980 <= t_yr <= 2035:
                if b_yr != self.base_year or t_yr != self.target_year:
                    self.base_year = b_yr
                    self.target_year = t_yr
                    self.run_analysis()

    def on_run_analysis_clicked(self):
        self.on_year_selection_changed()

    def run_analysis(self):
        dev = deviation_service.calculate_deviation(self.base_year, self.target_year)
        if not dev:
            QMessageBox.warning(self, "Analysis Failed", "Could not load spatial data for selected years.")
            return

        self.current_deviation = dev

        # 1. Update 5 Summary Cards: Difference in Meters, Latitude, Longitude, Direction, Water Area
        dist_m = dev["displacement_m"]
        dir_lbl = dev["direction_label"]
        dx = dev["dx_m"]
        dy = dev["dy_m"]
        d_lat = dev.get("d_lat", dev["target_data"]["mouth_lat"] - dev["base_data"]["mouth_lat"])
        d_lon = dev.get("d_lon", dev["target_data"]["mouth_lon"] - dev["base_data"]["mouth_lon"])
        d_area = dev["area_change_km2"]
        d_pct = dev["area_change_pct"]
        rate = dev["annual_rate_m_yr"]
        dt = dev["time_interval_years"]

        ns = "North" if dy > 0 else ("South" if dy < 0 else "Zero")
        ew = "East" if dx > 0 else ("West" if dx < 0 else "Zero")

        # Card 1: Difference in Meters
        self.card_disp.set_content(
            f"{dist_m:.1f} m",
            f"ΔX: {dx:+.1f}m | ΔY: {dy:+.1f}m",
            f"Total Euclidean displacement: {self.base_year} → {self.target_year}"
        )

        # Card 2: Difference in Latitude
        self.card_lat.set_content(
            f"{d_lat:+.6f}°",
            f"ΔY: {dy:+.1f}m ({ns})",
            f"Base: {dev['base_data']['mouth_lat']:.4f}°N → Target: {dev['target_data']['mouth_lat']:.4f}°N"
        )

        # Card 3: Difference in Longitude
        self.card_lon.set_content(
            f"{d_lon:+.6f}°",
            f"ΔX: {dx:+.1f}m ({ew})",
            f"Base: {dev['base_data']['mouth_lon']:.4f}°E → Target: {dev['target_data']['mouth_lon']:.4f}°E"
        )

        # Card 4: Displacement Direction
        self.card_dir.set_content(
            dev["direction_name"],
            f"Azimuth: {dev['azimuth_deg']:.0f}°",
            f"Displacement vector: {dir_lbl}"
        )

        # Card 5: Water Area & Migration Rate
        sign = "+" if d_area > 0 else ""
        self.card_area.set_content(
            f"{sign}{d_area:.2f} km²",
            f"{sign}{d_pct:.1f}% | {rate:.2f} m/yr",
            f"{dev['base_water_area_km2']:.2f} km² → {dev['target_water_area_km2']:.2f} km² (over {dt} yrs)"
        )

        # 2. Update Comparison View
        self.comparison_card.set_comparison(dev)

        # 3. Update Time-Series Chart
        self.chart_widget.set_data(dev)

        # 4. Populate Historical Measurements Table (7-Column Format matching Image 2)
        df_table = deviation_service.load_mouth_width_shift_df()
        if not df_table.empty:
            self.table.setRowCount(len(df_table))
            for r_idx, row in df_table.iterrows():
                idx_val = int(row["Index"])
                yr_val = int(row["Year"])

                # Format Mouth Width (m)
                w_raw = row["Mouth Width (m)"]
                if pd.isna(w_raw):
                    w_str = "NaN"
                elif float(w_raw) == int(float(w_raw)):
                    w_str = f"{float(w_raw):.1f}"
                else:
                    w_str = f"{float(w_raw):.2f}"

                # Format Longitude & Latitude (8 decimals)
                lon_raw = row["Longitude"]
                lon_str = "NaN" if pd.isna(lon_raw) else f"{float(lon_raw):.8f}"

                lat_raw = row["Latitude"]
                lat_str = "NaN" if pd.isna(lat_raw) else f"{float(lat_raw):.8f}"

                # Format East Shift (m) & North Shift (m)
                e_raw = row["East Shift (m)"]
                if pd.isna(e_raw):
                    e_str = "NaN"
                elif float(e_raw) == int(float(e_raw)):
                    e_str = f"{float(e_raw):.1f}"
                else:
                    e_str = f"{float(e_raw):.2f}"

                n_raw = row["North Shift (m)"]
                if pd.isna(n_raw):
                    n_str = "NaN"
                elif float(n_raw) == int(float(n_raw)):
                    n_str = f"{float(n_raw):.1f}"
                else:
                    n_str = f"{float(n_raw):.2f}"

                item_idx = QTableWidgetItem(str(idx_val))
                item_idx.setTextAlignment(Qt.AlignCenter)

                item_yr = QTableWidgetItem(str(yr_val))
                item_yr.setTextAlignment(Qt.AlignCenter)

                item_w = QTableWidgetItem(w_str)
                item_w.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                item_lon = QTableWidgetItem(lon_str)
                item_lon.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                item_lat = QTableWidgetItem(lat_str)
                item_lat.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                item_e = QTableWidgetItem(e_str)
                item_e.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                item_n = QTableWidgetItem(n_str)
                item_n.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                all_items = [item_idx, item_yr, item_w, item_lon, item_lat, item_e, item_n]

                is_base = (yr_val == self.base_year)
                is_target = (yr_val == self.target_year)

                for col_idx, item in enumerate(all_items):
                    if item.text() == "NaN":
                        item.setForeground(QColor(AMBER))
                    elif is_base:
                        item.setBackground(QColor(16, 59, 50, 180))
                        item.setForeground(QColor(SOFT_LIME))
                    elif is_target:
                        item.setBackground(QColor(0, 191, 165, 50))
                        item.setForeground(QColor(MINT))
                    else:
                        item.setForeground(QColor(WARM_IVORY))

                    self.table.setItem(r_idx, col_idx, item)

            self.table_note.setText(f"1 to {len(df_table)} of {len(df_table)} entries")
            if hasattr(self, 'filter_input') and self.filter_input.text():
                self.on_filter_changed(self.filter_input.text())

        # Update application status bar
        if self.main_window and hasattr(self.main_window, "update_status"):
            self.main_window.update_status(
                status_text=f"River-Mouth Deviation: {dist_m:.1f}m ({dir_lbl})",
                mode_text=f"Baseline: {self.base_year} → Target: {self.target_year}",
                readiness=f"Rate {rate:.2f} m/yr | ΔArea {sign}{d_area:.2f} km²",
                data_text=f"Landsat & U-Net (EPSG:32643)"
            )

    def on_filter_changed(self, text):
        query = text.strip().lower()
        visible = 0
        total = self.table.rowCount()
        for r in range(total):
            if not query:
                self.table.setRowHidden(r, False)
                visible += 1
            else:
                match = False
                for c in range(self.table.columnCount()):
                    it = self.table.item(r, c)
                    if it and query in it.text().lower():
                        match = True
                        break
                self.table.setRowHidden(r, not match)
                if match:
                    visible += 1
        if query:
            self.table_note.setText(f"{visible} of {total} entries (filtered)")
        else:
            self.table_note.setText(f"1 to {total} of {total} entries")

    def on_table_cell_clicked(self, row, col):
        yr_item = self.table.item(row, 1)
        if yr_item:
            try:
                yr = int(yr_item.text().strip())
                if yr != self.target_year and 1989 <= yr <= 2026:
                    self.combo_target.setCurrentText(str(yr))
            except Exception:
                pass

    # ========================================================================
    # Export Options Menu (CSV, GeoJSON, Report)
    # ========================================================================
    def show_export_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {PANEL_GREEN};
                color: {MINT};
            }}
        """)

        act_csv = menu.addAction("Export Results Table as CSV (.csv)")
        act_geojson = menu.addAction("Export GIS Vector Geometry as GeoJSON (.geojson)")
        act_report = menu.addAction("Export Scientific Analysis Report (.txt)")

        action = menu.exec(self.btn_export.mapToGlobal(QPointF(0, self.btn_export.height()).toPoint()))
        if action == act_csv:
            self.export_csv_dialog()
        elif action == act_geojson:
            self.export_geojson_dialog()
        elif action == act_report:
            self.export_report_dialog()

    def export_csv_dialog(self):
        default_fn = f"Suvarna_Mouth_Deviation_{self.base_year}_{self.target_year}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export Deviation Table as CSV", default_fn, "CSV Files (*.csv)")
        if not path:
            return
        ok, msg = deviation_service.export_csv(self.base_year, self.target_year, path)
        if ok:
            QMessageBox.information(self, "Export Successful", msg)
        else:
            QMessageBox.warning(self, "Export Failed", msg)

    def export_geojson_dialog(self):
        default_fn = f"Suvarna_Mouth_Vectors_{self.base_year}_{self.target_year}.geojson"
        path, _ = QFileDialog.getSaveFileName(self, "Export GIS Vector as GeoJSON", default_fn, "GeoJSON Files (*.geojson)")
        if not path:
            return
        ok, msg = deviation_service.export_geojson(self.base_year, self.target_year, path)
        if ok:
            QMessageBox.information(self, "Export Successful", msg)
        else:
            QMessageBox.warning(self, "Export Failed", msg)

    def export_report_dialog(self):
        default_fn = f"Suvarna_Mouth_Analysis_Report_{self.base_year}_{self.target_year}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Export Scientific Report", default_fn, "Text Files (*.txt);;Markdown Files (*.md)")
        if not path:
            return
        ok, msg = deviation_service.export_report(self.base_year, self.target_year, path)
        if ok:
            QMessageBox.information(self, "Export Successful", msg)
        else:
            QMessageBox.warning(self, "Export Failed", msg)

    # ========================================================================
    # Navigation Handlers
    # ========================================================================
    def go_to_home(self):
        if self.main_window and hasattr(self.main_window, "go_to_home"):
            self.main_window.go_to_home()
        elif self.stack:
            self.stack.setCurrentIndex(0)

    def go_to_river_mouth(self):
        if self.main_window and hasattr(self.main_window, "go_to_river_mouth"):
            self.main_window.go_to_river_mouth()
        elif self.stack:
            self.stack.setCurrentIndex(4)

    def go_to_lulc(self):
        if self.main_window and hasattr(self.main_window, "go_to_lulc"):
            self.main_window.go_to_lulc()
        elif self.stack:
            self.stack.setCurrentIndex(1)

    def go_to_weather(self):
        if self.main_window and hasattr(self.main_window, "go_to_weather"):
            self.main_window.go_to_weather()
        elif self.stack:
            self.stack.setCurrentIndex(2)
