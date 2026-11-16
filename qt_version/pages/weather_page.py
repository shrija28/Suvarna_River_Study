"""
Weather Data Page - Suvarna River Study GIS Dashboard
Displays comprehensive annual meteorological dataset (1989-2026) for Suvarna River Estuary:
- Fixed vertical navigation sidebar on left (Home, River Mouth, LULC, Weather)
- Filterable year range selection (1989–2026)
- Tabular display of:
  * Year
  * Average Temperature (°C)
  * Average Relative Humidity (%)
  * Annual Rainfall (mm)
  * Data Completeness Status (clearly marking partial years like 2026)
- High-performance, anti-aliased custom QPainter charts:
  * Annual Rainfall (mm) bar chart with period baseline
  * Average Temperature (°C) line chart
  * Average Relative Humidity (%) line chart
  * Combined Multi-Variable comparative trends
- Download button to export filtered annual table to CSV
Theme: Dark Emerald & Tropical Coastal GIS
"""

import os
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QPainterPath,
    QLinearGradient,
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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
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
from backend.weather_service import weather_service
from nav_button import SidebarNavButton

# Use crisp custom-painted navigation button to eliminate all border/clipping line glitches
WeatherNavButton = SidebarNavButton


# ============================================================================
# Interactive Multi-Metric Weather Chart Canvas
# ============================================================================
class AnnualWeatherChartCanvas(QWidget):
    """
    Custom QPainter canvas that renders:
    - Mode 'rain': Annual Rainfall (mm) Bar Chart
    - Mode 'temp': Average Temperature (°C) Line Chart
    - Mode 'hum': Average Relative Humidity (%) Line Chart
    - Mode 'all': Multi-Axis Combined Trend Chart
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_records = []
        self.mode = "rain"  # "rain", "temp", "hum", "all"
        self.hover_index = -1
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(240)
        self.setMouseTracking(True)

    def set_data(self, records, mode=None):
        self.data_records = records or []
        if mode:
            self.mode = mode
        self.hover_index = -1
        self.update()

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def mouseMoveEvent(self, event):
        if not self.data_records:
            return
        w = self.width()
        pad_left = 65
        pad_right = 25
        plot_w = w - pad_left - pad_right
        n = len(self.data_records)
        if n <= 0 or plot_w <= 0:
            return

        x = event.position().x()
        if pad_left <= x <= w - pad_right:
            idx = int((x - pad_left) / (plot_w / n))
            if 0 <= idx < n:
                if self.hover_index != idx:
                    self.hover_index = idx
                    self.update()
                    return
        if self.hover_index != -1:
            self.hover_index = -1
            self.update()

    def leaveEvent(self, event):
        if self.hover_index != -1:
            self.hover_index = -1
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Canvas background
        p.fillRect(0, 0, w, h, QColor(DARK_EMERALD))

        if not self.data_records:
            p.setPen(QColor(MUTED_SAGE))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "No weather data records in selected year range")
            p.end()
            return

        pad_left = 65
        pad_right = 25
        pad_top = 35
        pad_bottom = 35
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        if plot_w <= 10 or plot_h <= 10:
            p.end()
            return

        n = len(self.data_records)
        years = [r["year"] for r in self.data_records]

        # Draw Base Axes
        p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
        p.drawLine(pad_left, pad_top + plot_h, w - pad_right, pad_top + plot_h)
        p.drawLine(pad_left, pad_top, pad_left, pad_top + plot_h)

        if self.mode == "rain":
            self._draw_rainfall_chart(p, pad_left, pad_top, plot_w, plot_h, n)
        elif self.mode == "temp":
            self._draw_temp_chart(p, pad_left, pad_top, plot_w, plot_h, n)
        elif self.mode == "hum":
            self._draw_humidity_chart(p, pad_left, pad_top, plot_w, plot_h, n)
        else:
            self._draw_combined_chart(p, pad_left, pad_top, plot_w, plot_h, n)

        # X-Axis Year Labels (Subsampled for clean readability)
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(MUTED_SAGE))
        step = max(1, n // 10)
        for i in range(0, n, step):
            rec = self.data_records[i]
            x_pos = pad_left + (i + 0.5) * (plot_w / n) if self.mode == "rain" else pad_left + i * (plot_w / max(1, n - 1))
            p.drawText(int(x_pos - 18), pad_top + plot_h + 18, str(rec["year"]))

        # Tooltip Overlay when hovering
        if 0 <= self.hover_index < n:
            h_rec = self.data_records[self.hover_index]
            self._draw_tooltip(p, h_rec, pad_left, pad_top, plot_w, plot_h, n)

        p.end()

    def _draw_rainfall_chart(self, p, x0, y0, pw, ph, n):
        # Y-Axis range: 0 to max_rain + 500
        rains = [r["annual_rainfall_mm"] or 0.0 for r in self.data_records]
        max_rain = max(rains) if rains else 5000.0
        y_max = max(4500.0, ((int(max_rain) // 1000) + 1) * 1000.0)

        # Grid lines and Y labels
        p.setFont(QFont("Segoe UI", 9))
        for y_tick in range(0, int(y_max) + 1, 1000):
            y_pos = y0 + ph - (y_tick / y_max) * ph
            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(x0, int(y_pos), x0 + pw, int(y_pos))
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(x0 - 54, int(y_pos + 4), f"{y_tick:,}")

        # Unit Label
        p.drawText(x0 - 54, y0 - 10, "(mm)")

        # Guideline: Period Mean Rainfall
        mean_rain = sum(rains) / max(1, len(rains))
        y_mean = y0 + ph - (mean_rain / y_max) * ph
        p.setPen(QPen(QColor(AMBER), 1.2, Qt.DashLine))
        p.drawLine(x0, int(y_mean), x0 + pw, int(y_mean))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.setPen(QColor(AMBER))
        p.drawText(x0 + pw - 120, int(y_mean - 4), f"Mean: {mean_rain:,.0f} mm")

        # Bars
        bar_slot = pw / n
        bar_w = max(4.0, bar_slot * 0.65)
        for i, rec in enumerate(self.data_records):
            val = rec["annual_rainfall_mm"] or 0.0
            bh = (val / y_max) * ph
            bx = x0 + i * bar_slot + (bar_slot - bar_w) / 2.0
            by = y0 + ph - bh

            # Gradient bar
            grad = QLinearGradient(bx, by, bx, y0 + ph)
            if rec.get("is_incomplete"):
                grad.setColorAt(0, QColor(AMBER))
                grad.setColorAt(1, QColor(DARK_EMERALD))
            else:
                grad.setColorAt(0, QColor(0, 191, 165))  # TEAL
                grad.setColorAt(1, QColor(8, 43, 38))    # DARK_EMERALD

            p.setBrush(QBrush(grad))
            p.setPen(QPen(QColor(MINT if i == self.hover_index else TEAL), 1))
            p.drawRoundedRect(QRectF(bx, by, bar_w, bh), 3, 3)

    def _draw_temp_chart(self, p, x0, y0, pw, ph, n):
        temps = [r["avg_temp"] for r in self.data_records if r["avg_temp"] is not None]
        y_min = 25.5
        y_max = 28.5

        # Grid lines
        p.setFont(QFont("Segoe UI", 9))
        for step_idx in range(7):
            t_val = y_min + step_idx * 0.5
            y_pos = y0 + ph - ((t_val - y_min) / (y_max - y_min)) * ph
            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(x0, int(y_pos), x0 + pw, int(y_pos))
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(x0 - 45, int(y_pos + 4), f"{t_val:.1f}°")

        p.drawText(x0 - 45, y0 - 10, "(°C)")

        # Coordinates
        pts = []
        for i, rec in enumerate(self.data_records):
            val = rec["avg_temp"]
            if val is not None:
                cx = x0 + i * (pw / max(1, n - 1))
                cy = y0 + ph - ((val - y_min) / (y_max - y_min)) * ph
                pts.append((cx, cy, rec))

        # Shaded area under line
        if len(pts) > 1:
            area = QPainterPath()
            area.moveTo(pts[0][0], y0 + ph)
            for x, y, _ in pts:
                area.lineTo(x, y)
            area.lineTo(pts[-1][0], y0 + ph)
            area.closeSubpath()
            grad = QLinearGradient(0, y0, 0, y0 + ph)
            grad.setColorAt(0, QColor(233, 184, 102, 70))
            grad.setColorAt(1, QColor(8, 43, 38, 0))
            p.fillPath(area, QBrush(grad))

        # Main Line
        p.setPen(QPen(QColor(AMBER), 2.5))
        for i in range(len(pts) - 1):
            p.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i + 1][0], pts[i + 1][1]))

        # Points
        for i, (x, y, rec) in enumerate(pts):
            p.setBrush(QBrush(QColor(AMBER if i == self.hover_index else WARM_IVORY)))
            p.setPen(QPen(QColor(DARK_EMERALD), 1.5))
            r_dot = 4 if i == self.hover_index else 2.5
            p.drawEllipse(QPointF(x, y), r_dot, r_dot)

    def _draw_humidity_chart(self, p, x0, y0, pw, ph, n):
        y_min = 74.0
        y_max = 82.0

        p.setFont(QFont("Segoe UI", 9))
        for step_idx in range(9):
            h_val = y_min + step_idx * 1.0
            y_pos = y0 + ph - ((h_val - y_min) / (y_max - y_min)) * ph
            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(x0, int(y_pos), x0 + pw, int(y_pos))
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(x0 - 45, int(y_pos + 4), f"{h_val:.0f}%")

        p.drawText(x0 - 45, y0 - 10, "(%)")

        pts = []
        for i, rec in enumerate(self.data_records):
            val = rec["avg_humidity"]
            if val is not None:
                cx = x0 + i * (pw / max(1, n - 1))
                cy = y0 + ph - ((val - y_min) / (y_max - y_min)) * ph
                pts.append((cx, cy, rec))

        # Shaded area under line
        if len(pts) > 1:
            area = QPainterPath()
            area.moveTo(pts[0][0], y0 + ph)
            for x, y, _ in pts:
                area.lineTo(x, y)
            area.lineTo(pts[-1][0], y0 + ph)
            area.closeSubpath()
            grad = QLinearGradient(0, y0, 0, y0 + ph)
            grad.setColorAt(0, QColor(116, 230, 176, 70))
            grad.setColorAt(1, QColor(8, 43, 38, 0))
            p.fillPath(area, QBrush(grad))

        # Main Line
        p.setPen(QPen(QColor(MINT), 2.5))
        for i in range(len(pts) - 1):
            p.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i + 1][0], pts[i + 1][1]))

        # Points
        for i, (x, y, rec) in enumerate(pts):
            p.setBrush(QBrush(QColor(MINT if i == self.hover_index else WARM_IVORY)))
            p.setPen(QPen(QColor(DARK_EMERALD), 1.5))
            r_dot = 4 if i == self.hover_index else 2.5
            p.drawEllipse(QPointF(x, y), r_dot, r_dot)

    def _draw_combined_chart(self, p, x0, y0, pw, ph, n):
        """Draws normalized multi-series comparative trend."""
        # Grid lines (0% to 100% normalized scale)
        p.setFont(QFont("Segoe UI", 9))
        for pct in [0, 25, 50, 75, 100]:
            y_pos = y0 + ph - (pct / 100.0) * ph
            p.setPen(QPen(QColor(BORDER_SUBTLE), 1, Qt.DashLine))
            p.drawLine(x0, int(y_pos), x0 + pw, int(y_pos))
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(x0 - 45, int(y_pos + 4), f"{pct}%")

        p.drawText(x0 - 45, y0 - 10, "Norm.")

        # Helper to normalize series
        def normalize_series(vals, v_min, v_max):
            rng = max(0.001, v_max - v_min)
            return [y0 + ph - ((v - v_min) / rng) * ph for v in vals]

        rains = [r["annual_rainfall_mm"] or 0.0 for r in self.data_records]
        temps = [r["avg_temp"] or 26.0 for r in self.data_records]
        hums = [r["avg_humidity"] or 76.0 for r in self.data_records]

        y_r = normalize_series(rains, 2000.0, 4600.0)
        y_t = normalize_series(temps, 26.0, 27.8)
        y_h = normalize_series(hums, 75.0, 81.0)

        # Draw Rain line in Teal
        p.setPen(QPen(QColor(TEAL), 2))
        for i in range(n - 1):
            x1 = x0 + i * (pw / max(1, n - 1))
            x2 = x0 + (i + 1) * (pw / max(1, n - 1))
            p.drawLine(QPointF(x1, y_r[i]), QPointF(x2, y_r[i + 1]))

        # Draw Temp line in Amber
        p.setPen(QPen(QColor(AMBER), 2))
        for i in range(n - 1):
            x1 = x0 + i * (pw / max(1, n - 1))
            x2 = x0 + (i + 1) * (pw / max(1, n - 1))
            p.drawLine(QPointF(x1, y_t[i]), QPointF(x2, y_t[i + 1]))

        # Draw Humidity line in Mint
        p.setPen(QPen(QColor(MINT), 2))
        for i in range(n - 1):
            x1 = x0 + i * (pw / max(1, n - 1))
            x2 = x0 + (i + 1) * (pw / max(1, n - 1))
            p.drawLine(QPointF(x1, y_h[i]), QPointF(x2, y_h[i + 1]))

    def _draw_tooltip(self, p, rec, x0, y0, pw, ph, n):
        slot = pw / n if self.mode == "rain" else pw / max(1, n - 1)
        cur_x = x0 + (self.hover_index + 0.5) * slot if self.mode == "rain" else x0 + self.hover_index * slot

        # Vertical tracking line
        p.setPen(QPen(QColor(MINT), 1, Qt.DotLine))
        p.drawLine(int(cur_x), y0, int(cur_x), y0 + ph)

        # Tooltip bubble
        if self.mode == "rain":
            tw, th = 225, 96
        else:
            tw, th = 175, 75
        tx = cur_x + 10
        if tx + tw > x0 + pw:
            tx = cur_x - tw - 10
        ty = y0 + 15

        p.setBrush(QBrush(QColor(11, 47, 42, 245)))
        p.setPen(QPen(QColor(MINT), 1))
        p.drawRoundedRect(QRectF(tx, ty, tw, th), 6, 6)

        p.setPen(QColor(WARM_IVORY))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        yr_txt = f"Year: {rec['year']}" + (" (Partial)" if rec.get("is_incomplete") else "")
        p.drawText(int(tx + 8), int(ty + 18), yr_txt)

        p.setFont(QFont("Segoe UI", 8.5))
        if self.mode == "rain":
            r_val = rec['annual_rainfall_mm']
            m_val = rec.get('monsoon_rainfall_mm', 0.0)
            m_rate = rec.get('monsoon_avg_mm_day', 0.0)
            m_days = rec.get('monsoon_days', 0)
            pre_val = rec.get('pre_monsoon_rainfall_mm', 0.0)
            post_val = rec.get('post_monsoon_rainfall_mm', 0.0)

            p.setPen(QColor(TEAL))
            p.drawText(int(tx + 8), int(ty + 34), f"Annual Rainfall: {r_val:,.1f} mm" if r_val else "Rain: N/A")
            p.setPen(QColor(SOFT_LIME))
            p.drawText(int(tx + 8), int(ty + 50), f"Monsoon: {m_val:,.1f} mm ({m_rate:.2f} mm/d, {m_days}d)")
            p.setPen(QColor(MINT))
            p.drawText(int(tx + 8), int(ty + 66), f"Pre-monsoon: {pre_val:,.1f} mm")
            p.setPen(QColor(MUTED_SAGE))
            p.drawText(int(tx + 8), int(ty + 82), f"Post-monsoon: {post_val:,.1f} mm")
        else:
            p.setPen(QColor(TEAL))
            r_val = rec['annual_rainfall_mm']
            p.drawText(int(tx + 8), int(ty + 34), f"Rainfall: {r_val:,.1f} mm" if r_val else "Rain: N/A")

            p.setPen(QColor(AMBER))
            t_val = rec['avg_temp']
            p.drawText(int(tx + 8), int(ty + 49), f"Temp: {t_val:.2f} °C" if t_val else "Temp: N/A")

            p.setPen(QColor(MINT))
            h_val = rec['avg_humidity']
            p.drawText(int(tx + 8), int(ty + 64), f"Humidity: {h_val:.2f} %" if h_val else "Humidity: N/A")


# ============================================================================
# Main Weather Data Page
# ============================================================================
class WeatherPage(QWidget):
    def __init__(self, stack, main_window=None):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.min_year = 1989
        self.max_year = 2026
        self.filtered_records = []
        self.build_ui()
        self.load_weather_dataset()

    def build_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --------------------------------------------------------------------
        # 1. Left Vertical Navigation Sidebar (Home, River Mouth, LULC, Weather)
        # --------------------------------------------------------------------
        sidebar = self.build_sidebar()
        root_layout.addWidget(sidebar)

        # --------------------------------------------------------------------
        # 2. Main Content Area
        # --------------------------------------------------------------------
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 14, 20, 14)
        main_layout.setSpacing(12)

        # Header Row: Title, Subtitle, Year Range Filter & Download Button
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Estuarine Weather & Climate Contributing Factors")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {WARM_IVORY};")
        sub_title = QLabel(
            "Annual Meteorological Time-Series (1989–2026) • Ground Truth Reanalysis Dataset (Kodi Bengre Delta)"
        )
        sub_title.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        title_box.addWidget(title)
        title_box.addWidget(sub_title)
        header_row.addLayout(title_box)

        header_row.addStretch()

        # Year Range Filter Controls
        filter_box = QHBoxLayout()
        filter_box.setSpacing(6)

        range_lbl = QLabel("Year Range:")
        range_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {MUTED_SAGE};")
        filter_box.addWidget(range_lbl)

        self.start_combo = QComboBox()
        self.start_combo.setFixedHeight(30)
        self.start_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {INPUT_BG};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        filter_box.addWidget(self.start_combo)

        to_lbl = QLabel("to")
        to_lbl.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        filter_box.addWidget(to_lbl)

        self.end_combo = QComboBox()
        self.end_combo.setFixedHeight(30)
        self.end_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {INPUT_BG};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        filter_box.addWidget(self.end_combo)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedHeight(30)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_EMERALD};
                color: {MUTED_SAGE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                padding: 2px 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                border-color: {MINT};
                color: {WARM_IVORY};
            }}
        """)
        reset_btn.clicked.connect(self.reset_year_range)
        filter_box.addWidget(reset_btn)

        header_row.addLayout(filter_box)

        # Download CSV Button in Upper-Right
        self.download_btn = QPushButton("Download CSV")
        self.download_btn.setIcon(get_icon("download", color=DARK_EMERALD, size=16))
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setFixedHeight(34)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MINT};
                color: {DARK_EMERALD};
                font-size: 12px;
                font-weight: 800;
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
        self.download_btn.clicked.connect(self.download_csv)
        header_row.addWidget(self.download_btn)

        main_layout.addLayout(header_row)

        # --------------------------------------------------------------------
        # 3. Split Area: Table (Left) + Charts (Right)
        # --------------------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1B473D;
                width: 2px;
            }
        """)

        # Left Panel: Annual Data Table
        table_panel = QFrame()
        table_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_layout.setSpacing(8)

        t_header = QLabel("Annual Weather Records Table")
        t_header.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {MINT};")
        table_layout.addWidget(t_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Year",
            "Avg Temp (°C)",
            "Avg Humidity (%)",
            "Annual Rain (mm)",
            "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_DARK};
                alternate-background-color: {DARK_EMERALD};
                gridline-color: {BORDER_SUBTLE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 4px;
                color: {WARM_IVORY};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {DARK_EMERALD};
                color: {MINT};
                font-weight: 700;
                font-size: 11px;
                border: 1px solid {BORDER_COLOR};
                padding: 6px 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {PANEL_GREEN};
                color: {MINT};
            }}
        """)
        table_layout.addWidget(self.table, 1)

        splitter.addWidget(table_panel)

        # Right Panel: Interactive Charts
        chart_panel = QFrame()
        chart_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        chart_layout = QVBoxLayout(chart_panel)
        chart_layout.setContentsMargins(12, 10, 12, 10)
        chart_layout.setSpacing(8)

        # Chart Mode Selector Buttons
        mode_bar = QHBoxLayout()
        mode_bar.setSpacing(6)

        c_title = QLabel("Annual Time-Series Visualization")
        c_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {WARM_IVORY};")
        mode_bar.addWidget(c_title)
        mode_bar.addStretch()

        self.btn_mode_rain = QPushButton("Rainfall (mm)")
        self.btn_mode_temp = QPushButton("Temperature (°C)")
        self.btn_mode_hum = QPushButton("Humidity (%)")
        self.btn_mode_all = QPushButton("Combined")

        self.chart_mode_buttons = [
            (self.btn_mode_rain, "rain"),
            (self.btn_mode_temp, "temp"),
            (self.btn_mode_hum, "hum"),
            (self.btn_mode_all, "all")
        ]

        for btn, m_id in self.chart_mode_buttons:
            btn.setFixedHeight(26)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda ch=False, m=m_id: self.switch_chart_mode(m))
            mode_bar.addWidget(btn)

        chart_layout.addLayout(mode_bar)

        # Canvas Widget
        self.chart_canvas = AnnualWeatherChartCanvas()
        chart_layout.addWidget(self.chart_canvas, 1)

        # Chart Legend / Notes
        self.legend_lbl = QLabel(
            "● Teal Bars: Annual Precipitation (mm)  |  --- Amber Line: Period Mean Baseline  |  Hover chart for exact readings"
        )
        self.legend_lbl.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE};")
        chart_layout.addWidget(self.legend_lbl)

        splitter.addWidget(chart_panel)
        splitter.setSizes([480, 720])

        main_layout.addWidget(splitter, 1)

        # --------------------------------------------------------------------
        # 4. Bottom Summary Statistics Bar
        # --------------------------------------------------------------------
        summary_bar = QFrame()
        summary_bar.setFixedHeight(54)
        summary_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_SURFACE};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        sum_layout = QHBoxLayout(summary_bar)
        sum_layout.setContentsMargins(16, 6, 16, 6)
        sum_layout.setSpacing(20)

        self.stat_span = QLabel("Period: 1989 – 2026 (38 Years)")
        self.stat_span.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {WARM_IVORY};")
        sum_layout.addWidget(self.stat_span)

        self.stat_rain = QLabel("Mean Rainfall: -- mm/yr")
        self.stat_rain.setStyleSheet(f"font-size: 11px; color: {TEAL}; font-weight: 600;")
        sum_layout.addWidget(self.stat_rain)

        self.stat_temp = QLabel("Mean Temp: -- °C")
        self.stat_temp.setStyleSheet(f"font-size: 11px; color: {AMBER}; font-weight: 600;")
        sum_layout.addWidget(self.stat_temp)

        self.stat_hum = QLabel("Mean Humidity: -- %")
        self.stat_hum.setStyleSheet(f"font-size: 11px; color: {MINT}; font-weight: 600;")
        sum_layout.addWidget(self.stat_hum)

        sum_layout.addStretch()

        self.stat_peak = QLabel("Peak Inflow Year: --")
        self.stat_peak.setStyleSheet(f"font-size: 11px; color: {SOFT_LIME}; font-weight: 600;")
        sum_layout.addWidget(self.stat_peak)

        main_layout.addWidget(summary_bar)
        root_layout.addWidget(main_content, 1)

        self.update_chart_mode_styles()

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

        # 1. Home
        btn_home = WeatherNavButton(
            icon_name="home",
            title="Home",
            desc="Map & Study Area",
            on_click=self.go_to_home,
            is_active=False
        )
        layout.addWidget(btn_home)

        # 2. River Mouth Gallery
        btn_gallery = WeatherNavButton(
            icon_name="map_source",
            title="River Mouth",
            desc="Satellite Imagery",
            on_click=self.go_to_river_mouth,
            is_active=False
        )
        layout.addWidget(btn_gallery)

        # 3. LULC
        btn_lulc = WeatherNavButton(
            icon_name="lulc",
            title="LULC",
            desc="Land Use & Migration",
            on_click=self.go_to_lulc,
            is_active=False
        )
        layout.addWidget(btn_lulc)

        # 4. Weather (Active)
        btn_weather = WeatherNavButton(
            icon_name="weather",
            title="Weather",
            desc="Rainfall & Climate Data",
            on_click=lambda: None,
            is_active=True
        )
        layout.addWidget(btn_weather)

        layout.addStretch()

        # Bottom Context Card
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

        tag = QLabel("DELTA METEOROLOGY")
        tag.setStyleSheet(f"font-size: 9px; font-weight: 800; color: {MINT}; letter-spacing: 0.5px;")
        c_desc = QLabel("ERA5 Reanalysis combined with ground rainfall records driving estuarine channel shift.")
        c_desc.setWordWrap(True)
        c_desc.setStyleSheet(f"font-size: 10px; color: {MUTED_SAGE}; line-height: 1.3;")

        c_layout.addWidget(tag)
        c_layout.addWidget(c_desc)
        layout.addWidget(context_card)

        return sidebar

    # ========================================================================
    # Data Loading & Range Updating
    # ========================================================================
    def load_weather_dataset(self):
        try:
            self.min_year, self.max_year = weather_service.get_year_bounds()
        except Exception as e:
            print("Weather dataset load exception:", e)
            self.min_year, self.max_year = 1989, 2026

        self.start_combo.blockSignals(True)
        self.end_combo.blockSignals(True)
        self.start_combo.clear()
        self.end_combo.clear()

        for yr in range(self.min_year, self.max_year + 1):
            self.start_combo.addItem(str(yr))
            self.end_combo.addItem(str(yr))

        self.start_combo.setCurrentText(str(self.min_year))
        self.end_combo.setCurrentText(str(self.max_year))

        self.start_combo.blockSignals(False)
        self.end_combo.blockSignals(False)

        self.start_combo.currentIndexChanged.connect(self.on_range_changed)
        self.end_combo.currentIndexChanged.connect(self.on_range_changed)

        self.refresh_data()

    def reset_year_range(self):
        self.start_combo.setCurrentText(str(self.min_year))
        self.end_combo.setCurrentText(str(self.max_year))

    def on_range_changed(self):
        try:
            sy = int(self.start_combo.currentText())
            ey = int(self.end_combo.currentText())
            if sy > ey:
                # Keep bounds valid
                self.end_combo.setCurrentText(str(sy))
        except ValueError:
            pass
        self.refresh_data()

    def refresh_data(self):
        sy = int(self.start_combo.currentText())
        ey = int(self.end_combo.currentText())

        self.filtered_records = weather_service.get_annual_records(sy, ey)

        # 1. Populate Table
        self.table.setRowCount(len(self.filtered_records))
        for row, rec in enumerate(self.filtered_records):
            # Year item
            y_item = QTableWidgetItem(str(rec["year"]))
            y_item.setTextAlignment(Qt.AlignCenter)
            if rec.get("is_incomplete"):
                y_item.setForeground(QColor(AMBER))
            else:
                y_item.setForeground(QColor(WARM_IVORY))

            # Temp item
            t_val = rec["avg_temp"]
            t_txt = f"{t_val:.2f}" if t_val is not None else "--"
            t_item = QTableWidgetItem(t_txt)
            t_item.setTextAlignment(Qt.AlignCenter)
            t_item.setForeground(QColor(AMBER))

            # Humidity item
            h_val = rec["avg_humidity"]
            h_txt = f"{h_val:.2f}" if h_val is not None else "--"
            h_item = QTableWidgetItem(h_txt)
            h_item.setTextAlignment(Qt.AlignCenter)
            h_item.setForeground(QColor(MINT))

            # Rainfall item
            r_val = rec["annual_rainfall_mm"]
            r_txt = f"{r_val:,.2f}" if r_val is not None else "--"
            r_item = QTableWidgetItem(r_txt)
            r_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            r_item.setForeground(QColor(TEAL))
            if r_val is not None:
                r_item.setToolTip(
                    f"Annual Total: {r_val:,.2f} mm\n"
                    f"• Monsoon: {rec.get('monsoon_rainfall_mm', 0.0):,.2f} mm ({rec.get('monsoon_avg_mm_day', 0.0):.3f} mm/day across {rec.get('monsoon_days', 0)} days)\n"
                    f"• Pre-monsoon: {rec.get('pre_monsoon_rainfall_mm', 0.0):,.2f} mm ({rec.get('pre_monsoon_avg_mm_day', 0.0):.3f} mm/day across {rec.get('pre_monsoon_days', 0)} days)\n"
                    f"• Post-monsoon: {rec.get('post_monsoon_rainfall_mm', 0.0):,.2f} mm ({rec.get('post_monsoon_avg_mm_day', 0.0):.3f} mm/day across {rec.get('post_monsoon_days', 0)} days)"
                )

            # Status item
            st_txt = "Partial (Jan–Aug)*" if rec.get("is_incomplete") else "Complete"
            st_item = QTableWidgetItem(st_txt)
            st_item.setTextAlignment(Qt.AlignCenter)
            st_item.setForeground(QColor(AMBER if rec.get("is_incomplete") else MUTED_SAGE))
            st_item.setToolTip(rec.get("status_note", ""))

            self.table.setItem(row, 0, y_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, h_item)
            self.table.setItem(row, 3, r_item)
            self.table.setItem(row, 4, st_item)

        # 2. Update Chart Canvas
        self.chart_canvas.set_data(self.filtered_records)

        # 3. Update Summary Statistics
        n_years = len(self.filtered_records)
        self.stat_span.setText(f"Period: {sy} – {ey} ({n_years} Years)")

        rains = [r["annual_rainfall_mm"] for r in self.filtered_records if r["annual_rainfall_mm"] is not None]
        temps = [r["avg_temp"] for r in self.filtered_records if r["avg_temp"] is not None]
        hums = [r["avg_humidity"] for r in self.filtered_records if r["avg_humidity"] is not None]

        if rains:
            m_rain = sum(rains) / len(rains)
            self.stat_rain.setText(f"Mean Rainfall: {m_rain:,.1f} mm/yr")
            peak_rec = max(self.filtered_records, key=lambda r: r["annual_rainfall_mm"] or 0.0)
            self.stat_peak.setText(f"Peak Rainfall: {peak_rec['year']} ({peak_rec['annual_rainfall_mm']:,.1f} mm)")
        else:
            self.stat_rain.setText("Mean Rainfall: --")
            self.stat_peak.setText("Peak Rainfall: --")

        if temps:
            m_temp = sum(temps) / len(temps)
            self.stat_temp.setText(f"Mean Temp: {m_temp:.2f} °C")
        else:
            self.stat_temp.setText("Mean Temp: --")

        if hums:
            m_hum = sum(hums) / len(hums)
            self.stat_hum.setText(f"Mean Humidity: {m_hum:.2f} %")
        else:
            self.stat_hum.setText("Mean Humidity: --")

    # ========================================================================
    # Chart Mode Switching
    # ========================================================================
    def switch_chart_mode(self, mode_id: str):
        self.chart_canvas.set_mode(mode_id)
        if mode_id == "rain":
            self.legend_lbl.setText("● Teal Bars: Annual Precipitation (mm)  |  --- Amber Line: Period Mean Baseline  |  Hover chart for readings")
        elif mode_id == "temp":
            self.legend_lbl.setText("● Amber Line: Annual Mean Surface Temperature (°C)  |  Hover chart for readings")
        elif mode_id == "hum":
            self.legend_lbl.setText("● Mint Line: Annual Mean Relative Humidity (%)  |  Maritime humidity range (74%–82%)")
        else:
            self.legend_lbl.setText("● Teal: Rainfall  |  ● Amber: Temperature  |  ● Mint: Humidity (Normalized 0–100% comparative scale)")
        self.update_chart_mode_styles()

    def update_chart_mode_styles(self):
        current = self.chart_canvas.mode
        for btn, m_id in self.chart_mode_buttons:
            is_active = (m_id == current)
            bg = PANEL_GREEN if is_active else DARK_EMERALD
            col = SOFT_LIME if is_active else MUTED_SAGE
            border = MINT if is_active else BORDER_SUBTLE
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {col};
                    font-size: 11px;
                    font-weight: {'700' if is_active else '500'};
                    border: 1px solid {border};
                    border-radius: 4px;
                    padding: 2px 10px;
                }}
                QPushButton:hover {{
                    border-color: {MINT};
                    color: {WARM_IVORY};
                }}
            """)

    # ========================================================================
    # CSV Download Handler
    # ========================================================================
    def download_csv(self):
        sy = int(self.start_combo.currentText())
        ey = int(self.end_combo.currentText())
        default_fn = f"Suvarna_Estuary_Annual_Weather_{sy}_{ey}.csv"
        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Annual Weather Table as CSV",
            os.path.join(os.path.expanduser("~"), default_fn),
            "CSV Files (*.csv)"
        )
        if not dest_path:
            return

        try:
            count = weather_service.export_csv(dest_path, sy, ey)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {count} annual weather records to:\n\n{dest_path}"
            )
            if self.main_window and hasattr(self.main_window, "update_status"):
                self.main_window.update_status(
                    status_text=f"Exported {count} annual weather records"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Could not export CSV file:\n{e}"
            )

    # ========================================================================
    # Navigation Actions
    # ========================================================================
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
