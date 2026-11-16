"""
LULC Data Page - Suvarna River Study GIS Dashboard
Connects genuine multi-decadal Land Use and Land Cover (LULC) datasets:
1. Navigation sidebar on left (Home, River Mouth, LULC [active], Weather)
2. Top header toolbar with Year selector dropdown (1989–2026) and CSV Export
3. 4 Summary cards driven by LULC_Master_Counts.csv:
   - Vegetation (Green #2E7D32)
   - Water Body (Blue #1E88E5)
   - Barren Land (Yellow/Tan #E6C654)
   - Built-up Area (Brown/Red #D84315)
4. Comparison Bar Chart across all 37 years (1989–2026):
   - Multi-Decadal Timeseries bar chart across all 37 years with class filters (Water Body, Vegetation, Barren Land, Built-up, Stacked)
   - Interactive bar selection (clicking a year bar jumps to that year)
   - Selected Year 4-class breakdown mode with 100% proportional composition bar
5. LULC Results Viewer:
   - 4-Class Classified GeoTIFF raster map with legend
   - NDWI (Normalized Difference Water Index) satellite raster
   - RGB Natural Color Landsat composite
   - Official Water Body Area Bar Plot (1989–2026)
   - First Opening Channel Width Deviation Plot
6. LULC Files & 37-Year Master Dataset Section:
   - Open official LULC Master PDF report (LULC_Master_Counts.pdf)
   - Download complete 37-year master counts CSV (LULC_Master_Counts.csv)
   - Export First Opening Results (Suvarna_First_Opening_Results.csv)
   - Interactive, searchable 37-year master data table with row synchronization
Theme: Dark Emerald & Tropical Coastal GIS
"""

import os
from PySide6.QtCore import Qt, QRectF, QPointF, QSize, Signal, QUrl
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QPainterPath,
    QLinearGradient,
    QPixmap,
    QDesktopServices,
)
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
    QScrollArea,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
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
from backend.lulc_service import lulc_service
from nav_button import SidebarNavButton

LULCNavButton = SidebarNavButton


# ============================================================================
# 4-Class LULC Summary Card Widget
# ============================================================================
class LULCClassCard(QFrame):
    def __init__(self, class_name: str, color_hex: str, subtitle: str):
        super().__init__()
        self.class_name = class_name
        self.color_hex = color_hex

        self.setStyleSheet(f"""
            LULCClassCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-top: 3px solid {color_hex};
                border-radius: 8px;
                padding: 10px;
            }}
            LULCClassCard:hover {{
                border-color: {MINT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Header row: Swatch + Class Name
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        swatch = QFrame()
        swatch.setFixedSize(12, 12)
        swatch.setStyleSheet(f"background-color: {color_hex}; border-radius: 6px;")
        header_row.addWidget(swatch)

        title_lbl = QLabel(class_name.upper())
        title_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {MUTED_SAGE}; letter-spacing: 0.5px;")
        header_row.addWidget(title_lbl)
        header_row.addStretch()

        self.pct_badge = QLabel("0.0 %")
        self.pct_badge.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {WARM_IVORY};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 700;
        """)
        header_row.addWidget(self.pct_badge)
        layout.addLayout(header_row)

        # Large Area Number
        self.area_lbl = QLabel("0.00 km²")
        self.area_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {WARM_IVORY}; margin-top: 2px;")
        layout.addWidget(self.area_lbl)

        # Subtitle / Details
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE};")
        sub_lbl.setWordWrap(True)
        layout.addWidget(sub_lbl)

    def update_values(self, area_km2: float, percentage: float):
        self.area_lbl.setText(f"{area_km2:.2f} km²")
        self.pct_badge.setText(f"{percentage:.1f} %")


# ============================================================================
# Comparison Bar Chart Across All 37 Years & Selected Year Breakdown
# ============================================================================
class LULCComparisonChartWidget(QFrame):
    year_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = 1989
        self.data = None
        self.all_records = []
        self.chart_mode = "timeseries"  # "timeseries" or "breakdown"
        self.metric_filter = "water_body"  # "water_body", "vegetation", "barren_land", "built_up", "stacked"
        self.bar_rects = {}  # year -> QRectF

        self.setMinimumHeight(380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"""
            LULCComparisonChartWidget {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Top Control Row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.title_lbl = QLabel("Multi-Decadal Comparison Bar Chart (1989–2026)")
        self.title_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {WARM_IVORY};")
        ctrl_row.addWidget(self.title_lbl)
        ctrl_row.addStretch()

        # Mode Toggle Buttons
        self.btn_mode_ts = QPushButton("37-Year Timeseries")
        self.btn_mode_bd = QPushButton("Year Breakdown")
        for b in [self.btn_mode_ts, self.btn_mode_bd]:
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._button_style(False))

        self.btn_mode_ts.clicked.connect(lambda: self.set_chart_mode("timeseries"))
        self.btn_mode_bd.clicked.connect(lambda: self.set_chart_mode("breakdown"))
        self.btn_mode_ts.setStyleSheet(self._button_style(True))

        ctrl_row.addWidget(self.btn_mode_ts)
        ctrl_row.addWidget(self.btn_mode_bd)
        layout.addLayout(ctrl_row)

        # Sub-filter bar for 37-Year Timeseries
        self.filter_bar = QFrame()
        self.filter_bar.setStyleSheet("background: transparent; border: none;")
        f_layout = QHBoxLayout(self.filter_bar)
        f_layout.setContentsMargins(0, 0, 0, 0)
        f_layout.setSpacing(6)

        lbl_f = QLabel("Metric Filter:")
        lbl_f.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {MUTED_SAGE};")
        f_layout.addWidget(lbl_f)

        self.f_btns = {}
        filters = [
            ("water_body", "Water Body", "#1E88E5"),
            ("vegetation", "Vegetation", "#2E7D32"),
            ("barren_land", "Barren Land", "#E6C654"),
            ("built_up", "Built-up", "#D84315"),
            ("stacked", "All Classes (Stacked)", "#00BFA5"),
        ]
        for key, label, col in filters:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._filter_style(key == self.metric_filter, col))
            btn.clicked.connect(lambda checked=False, k=key: self.set_metric_filter(k))
            self.f_btns[key] = (btn, col)
            f_layout.addWidget(btn)

        f_layout.addStretch()
        layout.addWidget(self.filter_bar)

        # Canvas Area for custom painting
        self.canvas = QWidget()
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.paintEvent = self._paint_canvas
        self.canvas.mousePressEvent = self._canvas_mouse_press
        layout.addWidget(self.canvas, 1)

    def _button_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background-color: {PANEL_GREEN};
                    color: {SOFT_LIME};
                    border: 1px solid {MINT};
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MUTED_SAGE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {WARM_IVORY};
                border-color: {MINT};
            }}
        """

    def _filter_style(self, active: bool, color_hex: str) -> str:
        if active:
            return f"""
                QPushButton {{
                    background-color: {DARK_EMERALD};
                    color: {WARM_IVORY};
                    border: 1px solid {color_hex};
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 10px;
                    font-weight: 700;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {BG_DARK};
                color: {MUTED_SAGE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {WARM_IVORY};
                border-color: {color_hex};
            }}
        """

    def set_chart_mode(self, mode: str):
        self.chart_mode = mode
        self.btn_mode_ts.setStyleSheet(self._button_style(mode == "timeseries"))
        self.btn_mode_bd.setStyleSheet(self._button_style(mode == "breakdown"))
        self.filter_bar.setVisible(mode == "timeseries")
        if mode == "timeseries":
            self.title_lbl.setText("Multi-Decadal Comparison Bar Chart across all 37 Observation Years")
        else:
            self.title_lbl.setText(f"Class Area Breakdown & Proportional Composition • Year {self.current_year}")
        self.canvas.update()

    def set_metric_filter(self, metric: str):
        self.metric_filter = metric
        for k, (b, col) in self.f_btns.items():
            b.setStyleSheet(self._filter_style(k == metric, col))
        self.canvas.update()

    def set_data(self, lulc_data: dict, current_year: int = 1989):
        self.data = lulc_data
        self.current_year = current_year
        if not self.all_records:
            self.all_records = lulc_service.get_all_master_records()
        if self.chart_mode == "breakdown":
            self.title_lbl.setText(f"Class Area Breakdown & Proportional Composition • Year {self.current_year}")
        self.canvas.update()

    def _canvas_mouse_press(self, event):
        if self.chart_mode == "timeseries" and self.bar_rects:
            pos = event.position()
            for yr, r in self.bar_rects.items():
                if r.left() - 2 <= pos.x() <= r.right() + 2:
                    self.year_selected.emit(yr)
                    break

    def _paint_canvas(self, event):
        p = QPainter(self.canvas)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.canvas.width()
        h = self.canvas.height()

        p.fillRect(0, 0, w, h, QColor(DARK_EMERALD))

        if self.chart_mode == "timeseries":
            self._paint_timeseries_bars(p, w, h)
        else:
            self._paint_year_breakdown(p, w, h)
        p.end()

    def _paint_timeseries_bars(self, p: QPainter, w: int, h: int):
        self.bar_rects.clear()
        if not self.all_records:
            self.all_records = lulc_service.get_all_master_records()

        if not self.all_records:
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "No multi-decadal LULC data loaded")
            return

        pad_left = 65
        pad_right = 30
        pad_top = 28
        pad_bottom = 35

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)

        # Determine max value for Y scaling
        if self.metric_filter == "water_body":
            vals = [r["water_km2"] for r in self.all_records]
            bar_color = QColor(30, 136, 229)
            unit_title = "Water Body Area (km²)"
        elif self.metric_filter == "vegetation":
            vals = [r["vegetation_km2"] for r in self.all_records]
            bar_color = QColor(46, 125, 50)
            unit_title = "Vegetation Area (km²)"
        elif self.metric_filter == "barren_land":
            vals = [r["barren_km2"] for r in self.all_records]
            bar_color = QColor(230, 198, 84)
            unit_title = "Barren Land / Sandspit (km²)"
        elif self.metric_filter == "built_up":
            vals = [r["builtup_km2"] for r in self.all_records]
            bar_color = QColor(216, 67, 21)
            unit_title = "Built-up Infrastructure (km²)"
        else:  # stacked
            vals = [r["total_km2"] for r in self.all_records]
            bar_color = QColor(0, 191, 165)
            unit_title = "Total Study Area (km²) - Stacked"

        max_val = max(vals) if vals else 1000.0
        y_max = ((int(max_val) // 100) + 1) * 100.0
        if y_max < 10.0:
            y_max = 10.0

        # Draw Gridlines & Y-Axis Labels
        p.setFont(QFont("Segoe UI", 9))
        grid_steps = 4
        for gi in range(grid_steps + 1):
            val = (gi / grid_steps) * y_max
            y_pos = pad_top + plot_h - (gi / grid_steps) * plot_h

            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(pad_left, int(y_pos), pad_left + plot_w, int(y_pos))

            p.setPen(QColor(MUTED_SAGE))
            p.drawText(QRectF(0, y_pos - 8, pad_left - 8, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val:.0f}")

        # Axis Lines
        p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
        p.drawLine(pad_left, pad_top + plot_h, pad_left + plot_w, pad_top + plot_h)
        p.drawLine(pad_left, pad_top, pad_left, pad_top + plot_h)

        # Draw Title on plot
        p.setPen(QColor(WARM_IVORY))
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(pad_left + 6, pad_top - 10, f"{unit_title} • 37 Observation Years (1989–2026)")

        # Render 37 Bars
        num_bars = len(self.all_records)
        slot_w = plot_w / num_bars
        bar_w = max(3.0, min(16.0, slot_w * 0.75))

        active_rect = None
        active_val = 0.0

        for i, rec in enumerate(self.all_records):
            yr = rec["year"]
            cx = pad_left + (i + 0.5) * slot_w
            bx = cx - bar_w / 2

            if self.metric_filter == "stacked":
                # Draw stacked segments: Water, Veg, Barren, Builtup
                tot = rec["total_km2"]
                w_h = (rec["water_km2"] / y_max) * plot_h
                v_h = (rec["vegetation_km2"] / y_max) * plot_h
                b_h = (rec["barren_km2"] / y_max) * plot_h
                u_h = (rec["builtup_km2"] / y_max) * plot_h

                curr_y = pad_top + plot_h
                # Water
                curr_y -= w_h
                p.fillRect(QRectF(bx, curr_y, bar_w, w_h), QColor(30, 136, 229))
                # Vegetation
                curr_y -= v_h
                p.fillRect(QRectF(bx, curr_y, bar_w, v_h), QColor(46, 125, 50))
                # Barren
                curr_y -= b_h
                p.fillRect(QRectF(bx, curr_y, bar_w, b_h), QColor(230, 198, 84))
                # Built-up
                curr_y -= u_h
                p.fillRect(QRectF(bx, curr_y, bar_w, u_h), QColor(216, 67, 21))

                bar_rect = QRectF(bx, curr_y, bar_w, pad_top + plot_h - curr_y)
                val_num = tot
            else:
                if self.metric_filter == "water_body":
                    val_num = rec["water_km2"]
                elif self.metric_filter == "vegetation":
                    val_num = rec["vegetation_km2"]
                elif self.metric_filter == "barren_land":
                    val_num = rec["barren_km2"]
                else:
                    val_num = rec["builtup_km2"]

                bh = (val_num / y_max) * plot_h
                by = pad_top + plot_h - bh
                bar_rect = QRectF(bx, by, bar_w, bh)

                # Gradient
                grad = QLinearGradient(bx, by, bx, by + bh)
                if yr == self.current_year:
                    grad.setColorAt(0.0, QColor(MINT))
                    grad.setColorAt(1.0, bar_color.lighter(130))
                else:
                    grad.setColorAt(0.0, bar_color.lighter(115))
                    grad.setColorAt(1.0, bar_color)

                p.setBrush(QBrush(grad))
                p.setPen(QPen(bar_color.lighter(120), 0.5))
                p.drawRoundedRect(bar_rect, 2, 2)

            self.bar_rects[yr] = bar_rect

            # If current year, save for indicator
            if yr == self.current_year:
                active_rect = bar_rect
                active_val = val_num

            # X-axis label for milestone years
            if yr in [1989, 1995, 2000, 2005, 2010, 2015, 2020, 2026] or yr == self.current_year:
                p.setFont(QFont("Segoe UI", 8, QFont.Bold if yr == self.current_year else QFont.Normal))
                p.setPen(QColor(SOFT_LIME if yr == self.current_year else MUTED_SAGE))
                p.drawText(QRectF(cx - 16, pad_top + plot_h + 4, 32, 16), Qt.AlignCenter, str(yr))

        # Highlight Current Year with Pin Indicator
        if active_rect:
            p.setPen(QPen(QColor(MINT), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(active_rect.adjusted(-1, -1, 1, 1), 2, 2)

            # Indicator pin above bar
            pin_x = active_rect.center().x()
            pin_y = active_rect.top() - 6
            p.setBrush(QBrush(QColor(MINT)))
            p.setPen(Qt.NoPen)
            poly = [QPointF(pin_x - 4, pin_y - 6), QPointF(pin_x + 4, pin_y - 6), QPointF(pin_x, pin_y)]
            p.drawPolygon(poly)

            # Value tooltip text
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.setPen(QColor(WARM_IVORY))
            badge_txt = f"{self.current_year}: {active_val:.1f} km²"
            p.drawText(QRectF(pin_x - 50, pin_y - 20, 100, 14), Qt.AlignCenter, badge_txt)

    def _paint_year_breakdown(self, p: QPainter, w: int, h: int):
        self.bar_rects.clear()
        if not self.data or "classes" not in self.data:
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "No LULC data loaded")
            return

        classes = [
            ("Vegetation", self.data["classes"]["vegetation"], QColor(46, 125, 50)),
            ("Water Body", self.data["classes"]["water_body"], QColor(30, 136, 229)),
            ("Barren Land", self.data["classes"]["barren_land"], QColor(230, 198, 84)),
            ("Built-up Area", self.data["classes"]["built_up"], QColor(216, 67, 21)),
        ]

        pad_left = 120
        pad_right = 140
        pad_top = 25
        pad_bottom = 60

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)

        max_area = max(max(c[1]["area_km2"] for c in classes), 1.0)
        y_max = max(10.0, ((int(max_area) // 10) + 1) * 10.0)

        # Draw vertical gridlines & scale
        num_grid = 4
        p.setFont(QFont("Segoe UI", 9))
        for g_idx in range(num_grid + 1):
            val = (g_idx / num_grid) * y_max
            x_pos = pad_left + (g_idx / num_grid) * plot_w

            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(int(x_pos), pad_top, int(x_pos), pad_top + plot_h)

            p.setPen(QColor(MUTED_SAGE))
            p.drawText(int(x_pos) - 15, pad_top + plot_h + 16, f"{val:.0f} km²")

        # Baseline axis lines
        p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
        p.drawLine(pad_left, pad_top + plot_h, pad_left + plot_w, pad_top + plot_h)
        p.drawLine(pad_left, pad_top, pad_left, pad_top + plot_h)

        # Draw Horizontal Bars
        bar_count = len(classes)
        bar_slot = plot_h / bar_count
        bar_thickness = max(18, min(30, int(bar_slot * 0.55)))

        for idx, (c_name, c_info, c_color) in enumerate(classes):
            slot_center = pad_top + (idx + 0.5) * bar_slot
            bar_y = int(slot_center - bar_thickness / 2)
            akm2 = c_info["area_km2"]
            pct = c_info["percentage"]
            bar_length = (akm2 / y_max) * plot_w

            p.setPen(QColor(WARM_IVORY))
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(QRectF(10, bar_y - 2, pad_left - 18, bar_thickness + 4), Qt.AlignRight | Qt.AlignVCenter, c_name)

            p.fillRect(pad_left, bar_y, plot_w, bar_thickness, QColor(0, 0, 0, 40))

            grad = QLinearGradient(pad_left, bar_y, pad_left + bar_length, bar_y)
            grad.setColorAt(0.0, c_color.lighter(115))
            grad.setColorAt(1.0, c_color)
            p.setBrush(QBrush(grad))
            p.setPen(QPen(c_color.lighter(130), 1))
            p.drawRoundedRect(QRectF(pad_left, bar_y, bar_length, bar_thickness), 4, 4)

            p.setPen(QColor(WARM_IVORY))
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(int(pad_left + bar_length + 10), int(bar_y + bar_thickness * 0.75), f"{akm2:.2f} km² ({pct:.1f}%)")

        # Stacked Proportional Distribution Bar (100% Total)
        stack_y = h - 28
        stack_h = 14
        stack_w = w - 32
        stack_x = 16

        p.setPen(QColor(MUTED_SAGE))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(stack_x, stack_y - 5, "Total Study Area Distribution (100% Proportional Composition):")

        curr_x = float(stack_x)
        for idx, (c_name, c_info, c_color) in enumerate(classes):
            pct = c_info["percentage"]
            seg_w = (pct / 100.0) * stack_w
            if seg_w > 0:
                p.fillRect(QRectF(curr_x, stack_y, seg_w, stack_h), c_color)
                curr_x += seg_w

        p.setPen(QPen(QColor(BORDER_COLOR), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(stack_x, stack_y, stack_w, stack_h), 3, 3)


# ============================================================================
# LULC Results & Map Display Card
# ============================================================================
class LULCMapDisplayCard(QFrame):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.active_view = "classified"  # "classified", "ndwi", "rgb", "water_plot", "width_plot"

        self.setStyleSheet(f"""
            LULCMapDisplayCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        # Header Row: Title & Badge
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        self.title_lbl = QLabel("Classified LULC Map")
        self.title_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {WARM_IVORY};")
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()

        self.chip_status = QLabel("Multi-Spectral Landsat")
        self.chip_status.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            color: {MINT};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)
        header_row.addWidget(self.chip_status)
        card_layout.addLayout(header_row)

        # View Mode Switcher Toolbar
        view_bar = QHBoxLayout()
        view_bar.setSpacing(6)

        self.v_btns = {}
        views = [
            ("classified", "4-Class Map"),
            ("ndwi", "NDWI Water"),
            ("rgb", "RGB Landsat"),
            ("water_plot", "Water Plot (1989-2026)"),
            ("width_plot", "Channel Width Plot"),
        ]
        for key, text in views:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._btn_style(key == self.active_view))
            btn.clicked.connect(lambda checked=False, k=key: self.set_active_view(k))
            self.v_btns[key] = btn
            view_bar.addWidget(btn)

        view_bar.addStretch()
        card_layout.addLayout(view_bar)

        # Image Display Container
        self.image_container = QLabel()
        self.image_container.setAlignment(Qt.AlignCenter)
        self.image_container.setMinimumSize(400, 320)
        self.image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_container.setStyleSheet(f"""
            background-color: {BG_DARK};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 6px;
        """)
        card_layout.addWidget(self.image_container, 1)

        # Matching Dynamic Legend Container
        self.legend_frame = QFrame()
        self.legend_frame.setStyleSheet(f"""
            background-color: {DARK_EMERALD};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 6px;
            padding: 4px 8px;
        """)
        self.leg_layout = QHBoxLayout(self.legend_frame)
        self.leg_layout.setContentsMargins(8, 4, 8, 4)
        self.leg_layout.setSpacing(14)
        card_layout.addWidget(self.legend_frame)

        self.meta_chip = QLabel("Res: 30m • EPSG:32643")
        self.meta_chip.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; font-family: 'Consolas', monospace;")

        self._render_legend()

    def _btn_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background-color: {PANEL_GREEN};
                    color: {SOFT_LIME};
                    border: 1px solid {MINT};
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 10px;
                    font-weight: 700;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MUTED_SAGE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {WARM_IVORY};
                border-color: {MINT};
            }}
        """

    def set_active_view(self, view_key: str):
        self.active_view = view_key
        for k, b in self.v_btns.items():
            b.setStyleSheet(self._btn_style(k == view_key))
        self._render_legend()
        self._scale_and_render()

    def set_lulc_data(self, data: dict):
        self.current_data = data
        self._render_legend()
        self._scale_and_render()

    def _render_legend(self):
        # Clear existing legend items
        while self.leg_layout.count():
            item = self.leg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # recursively clear sub-layout
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        year = self.current_data.get("year", "--") if self.current_data else "--"

        if self.active_view == "classified":
            self.title_lbl.setText(f"Classified 4-Class LULC Map • Year {year}")
            self.chip_status.setText("Ground Truth Landsat")
            legends = [
                ("Vegetation", "#2E7D32"),
                ("Water Body", "#1E88E5"),
                ("Barren Land", "#E6C654"),
                ("Built-up Area", "#D84315"),
            ]
            for name, color_hex in legends:
                box = QHBoxLayout()
                box.setSpacing(5)
                dot = QFrame()
                dot.setFixedSize(12, 12)
                dot.setStyleSheet(f"background-color: {color_hex}; border-radius: 6px; border: 1px solid #FFFFFF33;")
                box.addWidget(dot)
                lbl = QLabel(name)
                lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {WARM_IVORY};")
                box.addWidget(lbl)
                self.leg_layout.addLayout(box)

        elif self.active_view == "ndwi":
            self.title_lbl.setText(f"NDWI Water Index Raster • Year {year}")
            self.chip_status.setText("Normalized Difference Water Index")
            ndwi_items = [
                ("Estuarine Water Body (>0.0)", "#00BFA5"),
                ("Terrestrial Land (<=0.0)", "#1B3B36"),
            ]
            for name, color_hex in ndwi_items:
                box = QHBoxLayout()
                box.setSpacing(5)
                dot = QFrame()
                dot.setFixedSize(12, 12)
                dot.setStyleSheet(f"background-color: {color_hex}; border-radius: 6px;")
                box.addWidget(dot)
                lbl = QLabel(name)
                lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {WARM_IVORY};")
                box.addWidget(lbl)
                self.leg_layout.addLayout(box)

        elif self.active_view == "rgb":
            self.title_lbl.setText(f"Natural Color Landsat Composite • Year {year}")
            self.chip_status.setText("True Color Surface Reflectance")
            lbl = QLabel("True Color RGB Composite (Bands 4-3-2 / 3-2-1)")
            lbl.setStyleSheet(f"font-size: 10px; color: {WARM_IVORY}; font-weight: 600;")
            self.leg_layout.addWidget(lbl)

        elif self.active_view == "water_plot":
            self.title_lbl.setText("Water Body Area Multi-Decadal Bar Plot (1989–2026)")
            self.chip_status.setText("Official Publication Figure")
            lbl = QLabel("Ground-truth estuarine water coverage trend across 37 observation years")
            lbl.setStyleSheet(f"font-size: 10px; color: {SOFT_LIME}; font-weight: 600;")
            self.leg_layout.addWidget(lbl)

        elif self.active_view == "width_plot":
            self.title_lbl.setText("First Opening Channel Width vs Year (1989–2026)")
            self.chip_status.setText("Estuarine Dynamics")
            lbl = QLabel("River-mouth width measurements and spit migration dynamics")
            lbl.setStyleSheet(f"font-size: 10px; color: {SOFT_LIME}; font-weight: 600;")
            self.leg_layout.addWidget(lbl)

        self.leg_layout.addStretch()
        self.meta_chip.setText("Res: 30m • EPSG:32643")
        self.leg_layout.addWidget(self.meta_chip)

    def _scale_and_render(self):
        pix = None
        if self.active_view == "classified":
            pix = self.current_data.get("pixmap") if self.current_data else None
        elif self.active_view == "ndwi":
            pix = self.current_data.get("ndwi_pixmap") if self.current_data else None
        elif self.active_view == "rgb":
            pix = self.current_data.get("rgb_pixmap") if self.current_data else None
        elif self.active_view == "water_plot":
            pix = lulc_service.get_water_body_plot_pixmap()
        elif self.active_view == "width_plot":
            pix = lulc_service.get_width_plot_pixmap()

        if pix and not pix.isNull():
            cw = max(100, self.image_container.width() - 8)
            ch = max(100, self.image_container.height() - 8)
            scaled = pix.scaled(cw, ch, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_container.setPixmap(scaled)
        else:
            self.image_container.setText("No imagery available for this view")
            self.image_container.setStyleSheet(f"color: {MUTED_SAGE}; font-size: 12px; background-color: {BG_DARK};")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._scale_and_render()


# ============================================================================
# LULC Files & 37-Year Master Dataset Table Card
# ============================================================================
class LULCFilesCard(QFrame):
    year_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = 1989
        self.records = []

        self.setStyleSheet(f"""
            LULCFilesCard {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        # Header Row
        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(10)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        t_lbl = QLabel("LULC Project Files & 37-Year Master Dataset (1989–2026)")
        t_lbl.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {WARM_IVORY};")
        s_lbl = QLabel("Ground-truth classification counts (LULC_Master_Counts.csv), documentation report, and river mouth opening measurements")
        s_lbl.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        title_box.addWidget(t_lbl)
        title_box.addWidget(s_lbl)
        hdr_row.addLayout(title_box)

        hdr_row.addStretch()

        # Action Buttons
        self.btn_open_pdf = QPushButton("Open Master PDF")
        self.btn_open_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_open_pdf.setStyleSheet(self._action_btn_style())
        self.btn_open_pdf.clicked.connect(self._open_master_pdf)
        hdr_row.addWidget(self.btn_open_pdf)

        self.btn_export_csv = QPushButton("Download 37-Yr CSV")
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.setStyleSheet(self._action_btn_style())
        self.btn_export_csv.clicked.connect(self._export_master_csv)
        hdr_row.addWidget(self.btn_export_csv)

        self.btn_opening_csv = QPushButton("Opening Results")
        self.btn_opening_csv.setCursor(Qt.PointingHandCursor)
        self.btn_opening_csv.setStyleSheet(self._action_btn_style())
        self.btn_opening_csv.clicked.connect(self._export_opening_results)
        hdr_row.addWidget(self.btn_opening_csv)

        layout.addLayout(hdr_row)

        # Interactive Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Year",
            "Vegetation (km²)",
            "Vegetation (%)",
            "Water Body (km²)",
            "Water Body (%)",
            "Barren Land (km²)",
            "Barren Land (%)",
            "Built-up (km²)",
            "Built-up (%)",
            "Total Area (km²)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setMinimumHeight(240)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                gridline-color: {BORDER_SUBTLE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {PANEL_SURFACE};
                color: {MINT};
                font-weight: 700;
                border: 1px solid {BORDER_SUBTLE};
                padding: 6px 4px;
                font-size: 11px;
            }}
            QTableWidget::item:selected {{
                background-color: {PANEL_GREEN};
                color: {SOFT_LIME};
                font-weight: 700;
            }}
        """)
        self.table.itemClicked.connect(self._on_table_item_clicked)
        layout.addWidget(self.table)

        self._populate_table()

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                border: 1px solid {MINT};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {PANEL_GREEN};
                color: {SOFT_LIME};
                border-color: {SOFT_LIME};
            }}
        """

    def _populate_table(self):
        self.records = lulc_service.get_all_master_records()
        self.table.setRowCount(len(self.records))

        for row_idx, r in enumerate(self.records):
            yr = r["year"]
            vals = [
                str(yr),
                f"{r['vegetation_km2']:.2f}",
                f"{r['vegetation_pct']:.1f}%",
                f"{r['water_km2']:.2f}",
                f"{r['water_pct']:.1f}%",
                f"{r['barren_km2']:.2f}",
                f"{r['barren_pct']:.1f}%",
                f"{r['builtup_km2']:.2f}",
                f"{r['builtup_pct']:.1f}%",
                f"{r['total_km2']:.2f}",
            ]
            for col_idx, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                # Apply class colors to cells
                if col_idx in [1, 2]:
                    item.setForeground(QColor(116, 230, 176))  # Veg Mint/Green
                elif col_idx in [3, 4]:
                    item.setForeground(QColor(77, 182, 252))  # Water Cyan
                elif col_idx in [5, 6]:
                    item.setForeground(QColor(245, 215, 110))  # Barren Gold
                elif col_idx in [7, 8]:
                    item.setForeground(QColor(255, 138, 101))  # Builtup Coral
                self.table.setItem(row_idx, col_idx, item)

        self.highlight_year(self.current_year)

    def highlight_year(self, year: int):
        self.current_year = year
        for r_idx, r in enumerate(self.records):
            if r["year"] == year:
                self.table.selectRow(r_idx)
                self.table.scrollToItem(self.table.item(r_idx, 0))
                break

    def _on_table_item_clicked(self, item):
        row = item.row()
        if 0 <= row < len(self.records):
            yr = self.records[row]["year"]
            self.year_selected.emit(yr)

    def _open_master_pdf(self):
        files = lulc_service.get_lulc_files()
        pdf_path = files.get("master_pdf", "")
        if pdf_path and os.path.isfile(pdf_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(pdf_path)))
        else:
            QMessageBox.warning(self, "PDF Report", "LULC_Master_Counts.pdf could not be located in project directory.")

    def _export_master_csv(self):
        default_name = "Suvarna_LULC_Master_Counts_1989_2026.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Save 37-Year LULC Master Table", default_name, "CSV Files (*.csv)")
        if path:
            ok, msg = lulc_service.export_all_years_csv(path)
            if ok:
                QMessageBox.information(self, "Export Successful", f"Exported complete 37-year LULC master table to:\n{path}")
            else:
                QMessageBox.warning(self, "Export Failed", f"Could not export CSV:\n{msg}")

    def _export_opening_results(self):
        files = lulc_service.get_lulc_files()
        csv_path = files.get("opening_results_csv", "")
        if csv_path and os.path.isfile(csv_path):
            default_name = "Suvarna_First_Opening_Results.csv"
            path, _ = QFileDialog.getSaveFileName(self, "Export First Opening Results", default_name, "CSV Files (*.csv)")
            if path:
                try:
                    import shutil
                    shutil.copyfile(csv_path, path)
                    QMessageBox.information(self, "Export Successful", f"Saved First Opening Results to:\n{path}")
                except Exception as e:
                    QMessageBox.warning(self, "Export Failed", f"Error saving file: {e}")
        else:
            QMessageBox.warning(self, "Opening Results", "First opening results CSV not found in project directory.")


# ============================================================================
# Main Result / LULC Page
# ============================================================================
class ResultPage(QWidget):
    def __init__(self, stack=None, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.current_year = 1989
        self.available_years = []

        # Root Horizontal Layout (Sidebar on Left + Content on Right)
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Vertical Navigation Sidebar
        sidebar = self.build_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Right Main Content Area inside ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"background-color: {BG_DARK}; border: none;")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 16, 20, 20)
        self.content_layout.setSpacing(16)

        # Top Header & Control Toolbar
        header_bar = self.build_header_toolbar()
        self.content_layout.addWidget(header_bar)

        # 4 Summary Cards Row in exact order: (Vegetation, Water Body, Barren Land, Built-up Area)
        self.card_veg = LULCClassCard("Vegetation", "#2E7D32", "Mangrove forest, coastal vegetation & wetland canopy")
        self.card_water = LULCClassCard("Water Body", "#1E88E5", "Suvarna river mouth channel, estuarine flow & Arabian Sea")
        self.card_barren = LULCClassCard("Barren Land", "#E6C654", "Kodi Bengre sandspit, beach sediments & exposed terrain")
        self.card_built = LULCClassCard("Built-up Area", "#D84315", "Settlements, coastal roads, ports & paved infrastructure")

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        cards_row.addWidget(self.card_veg)
        cards_row.addWidget(self.card_water)
        cards_row.addWidget(self.card_barren)
        cards_row.addWidget(self.card_built)
        self.content_layout.addLayout(cards_row)

        # Middle Split: LULC Results & Map (Left) + Comparison Chart Across All 37 Years (Right)
        mid_grid = QGridLayout()
        mid_grid.setSpacing(14)

        self.map_card = LULCMapDisplayCard()
        self.chart_widget = LULCComparisonChartWidget()
        self.chart_widget.year_selected.connect(self.select_year_from_child)

        mid_grid.addWidget(self.map_card, 0, 0)
        mid_grid.addWidget(self.chart_widget, 0, 1)
        mid_grid.setColumnStretch(0, 1)
        mid_grid.setColumnStretch(1, 1)
        self.content_layout.addLayout(mid_grid)

        # Bottom Section: LULC Files & 37-Year Master Dataset Table
        self.files_card = LULCFilesCard()
        self.files_card.year_selected.connect(self.select_year_from_child)
        self.content_layout.addWidget(self.files_card)

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
        btn_home = LULCNavButton(
            icon_name="home",
            title="Home",
            desc="Map & Study Area",
            on_click=self.go_to_home,
            is_active=False
        )
        layout.addWidget(btn_home)

        # 2. River Mouth Gallery
        btn_gallery = LULCNavButton(
            icon_name="analysis",
            title="River Mouth",
            desc="Satellite Imagery",
            on_click=self.go_to_river_mouth,
            is_active=False
        )
        layout.addWidget(btn_gallery)

        # 3. LULC (Active)
        btn_lulc = LULCNavButton(
            icon_name="lulc",
            title="LULC",
            desc="Land Use & Migration",
            on_click=lambda: None,
            is_active=True
        )
        layout.addWidget(btn_lulc)

        # 4. Weather
        btn_weather = LULCNavButton(
            icon_name="weather",
            title="Weather",
            desc="Rainfall & Climate Data",
            on_click=self.go_to_weather,
            is_active=False
        )
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

        t_lbl = QLabel("LULC ANALYSIS")
        t_lbl.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {SOFT_LIME}; letter-spacing: 0.5px;")
        c_layout.addWidget(t_lbl)

        d_lbl = QLabel("Multi-temporal classification of estuarine dynamics, sandspit geomorphology, and water-land boundaries.")
        d_lbl.setStyleSheet(f"font-size: 9px; color: {MUTED_SAGE}; line-height: 1.3;")
        d_lbl.setWordWrap(True)
        c_layout.addWidget(d_lbl)

        layout.addWidget(context_card)
        return sidebar

    # ========================================================================
    # Top Header & Toolbar
    # ========================================================================
    def build_header_toolbar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(14)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel("Land Use & Land Cover (LULC) Classification")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {WARM_IVORY};")

        subtitle = QLabel("Suvarna River Estuary • 4-Class Multi-Spectral & Deep Learning Classification (1989–2026)")
        subtitle.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        layout.addLayout(text_layout)

        layout.addStretch()

        # Year Selector
        lbl_year = QLabel("Select Year:")
        lbl_year.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {WARM_IVORY};")
        layout.addWidget(lbl_year)

        self.year_combo = QComboBox()
        self.year_combo.setFixedWidth(115)
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_EMERALD};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 700;
            }}
            QComboBox:hover {{
                border: 1px solid {MINT};
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
        self.year_combo.currentTextChanged.connect(self.on_year_selected)
        layout.addWidget(self.year_combo)

        # Download CSV Button for active year
        self.btn_download = QPushButton("Export Year CSV")
        self.btn_download.setIcon(get_icon("download", color=WARM_IVORY, size=16))
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.clicked.connect(self.export_csv_dialog)
        self.btn_download.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PANEL_GREEN}, stop:1 {DARK_EMERALD});
                color: {WARM_IVORY};
                border: 1px solid {MINT};
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {TEAL};
                color: {BG_DARK};
                border: 1px solid {SOFT_LIME};
            }}
            QPushButton:pressed {{
                background: {DARK_EMERALD};
            }}
        """)
        layout.addWidget(self.btn_download)

        return bar

    # ========================================================================
    # Data Initialization & Updates
    # ========================================================================
    def init_data(self):
        """Loads available years and selects baseline year."""
        self.available_years = lulc_service.get_available_years()
        if not self.available_years:
            self.available_years = [1989]

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for y in self.available_years:
            self.year_combo.addItem(str(y))
        self.year_combo.blockSignals(False)

        # Set default year
        if 1989 in self.available_years:
            self.current_year = 1989
            self.year_combo.setCurrentText("1989")
        else:
            self.current_year = self.available_years[0]
            self.year_combo.setCurrentIndex(0)

        self.load_year(self.current_year)

    def select_year_from_child(self, year: int):
        """Called when a year is clicked in chart or table."""
        if year in self.available_years:
            self.year_combo.setCurrentText(str(year))
        else:
            self.load_year(year)

    def on_year_selected(self, year_str):
        if not year_str or not year_str.isdigit():
            return
        year = int(year_str)
        self.current_year = year
        self.load_year(year)

    def load_year(self, year: int):
        """Computes and updates cards, map, chart, and table for the selected year."""
        data = lulc_service.process_year(year)
        if not data:
            return

        classes = data.get("classes", {})

        # 1. Update 4 Summary Cards (Vegetation, Water Body, Barren Land, Built-up Area)
        if "vegetation" in classes:
            self.card_veg.update_values(classes["vegetation"]["area_km2"], classes["vegetation"]["percentage"])
        if "water_body" in classes:
            self.card_water.update_values(classes["water_body"]["area_km2"], classes["water_body"]["percentage"])
        if "barren_land" in classes:
            self.card_barren.update_values(classes["barren_land"]["area_km2"], classes["barren_land"]["percentage"])
        if "built_up" in classes:
            self.card_built.update_values(classes["built_up"]["area_km2"], classes["built_up"]["percentage"])

        # 2. Update LULC Results & Map Display
        self.map_card.set_lulc_data(data)

        # 3. Update Comparison Chart across all 37 years
        self.chart_widget.set_data(data, current_year=year)

        # 4. Highlight Table Row
        if hasattr(self, "files_card"):
            self.files_card.highlight_year(year)

        # Update application status bar
        if self.main_window and hasattr(self.main_window, "update_status"):
            tot_km2 = data.get("total_area_km2", 0.0)
            self.main_window.update_status(
                status_text=f"LULC Observation: Year {year} (Total Area: {tot_km2:.2f} km²)",
                mode_text="4-Class Satellite Classification",
                readiness=f"Vegetation {classes.get('vegetation',{}).get('percentage',0):.1f}% | Water {classes.get('water_body',{}).get('percentage',0):.1f}%",
                data_text=f"Landsat 30m / EPSG:32643 ({year})"
            )

    def export_csv_dialog(self):
        """File dialog to export current year's LULC data."""
        default_filename = f"Suvarna_Estuary_LULC_{self.current_year}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export LULC Summary for Year {self.current_year}",
            default_filename,
            "CSV Files (*.csv)"
        )
        if not path:
            return

        success, msg = lulc_service.export_csv(self.current_year, path)
        if success:
            QMessageBox.information(self, "Export Successful", f"Saved LULC summary for {self.current_year} to:\n{path}")
        else:
            QMessageBox.warning(self, "Export Failed", f"Could not export CSV:\n{msg}")

    # ========================================================================
    # Backward Compatibility for Pipeline Calls
    # ========================================================================
    def load_analysis(self, base_year, target_year, aoi_coords=None):
        """Called when user runs analysis from home page."""
        target = int(target_year) if str(target_year).isdigit() else 1989
        if target in self.available_years:
            self.year_combo.setCurrentText(str(target))
        else:
            self.load_year(target)

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

    def go_to_weather(self):
        if self.main_window and hasattr(self.main_window, "go_to_weather"):
            self.main_window.go_to_weather()
        elif self.stack:
            self.stack.setCurrentIndex(2)
