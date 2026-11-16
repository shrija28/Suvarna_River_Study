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
    QDoubleSpinBox,
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
from icons import get_icon


class PredictionPage(QWidget):
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
        t = QLabel("Hybrid AI River Path Deviation Prediction Model")
        t.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WARM_IVORY};")
        sub = QLabel("Spatial CNN + Temporal Bi-LSTM for estuarine channel migration & spit morphodynamics")
        sub.setStyleSheet(f"font-size: 12px; color: {MUTED_SAGE};")
        title_box.addWidget(t)
        title_box.addWidget(sub)
        header_row.addLayout(title_box)
        header_row.addStretch()

        layout.addLayout(header_row)

        # Main Grid Layout
        grid = QGridLayout()
        grid.setSpacing(14)

        # Card 1: Hybrid AI Architecture
        c1 = self.create_card("1. Neural Architecture Configuration")
        c1_layout = QVBoxLayout(c1)
        c1_layout.setContentsMargins(14, 14, 14, 14)
        c1_layout.setSpacing(10)

        c1_layout.addWidget(QLabel("Deep Learning Backbone:"))
        model_combo = QComboBox()
        model_combo.addItems([
            "Hybrid CNN + Bi-Directional LSTM (Spatial-Temporal)",
            "ConvLSTM2D (Recurrent Spatiotemporal Convolutions)",
            "U-Net + Temporal Attention (Segmentation Driven)",
            "Random Forest + Spatial Cellular Automata (Baseline)"
        ])
        c1_layout.addWidget(model_combo)

        c1_layout.addWidget(QLabel("Temporal Sequence Length (Years):"))
        seq_combo = QComboBox()
        seq_combo.addItems(["5-Year Historical Sliding Window", "10-Year Multi-Decadal Window", "Full 35-Year Timeseries (1989-2024)"])
        c1_layout.addWidget(seq_combo)

        info_box = QFrame()
        info_box.setStyleSheet(f"background-color: {DARK_EMERALD}; border: 1px solid {BORDER_SUBTLE}; border-radius: 6px; padding: 10px;")
        ib_l = QVBoxLayout(info_box)
        ib_l.setSpacing(4)
        ib_l.addWidget(QLabel("<b>Model Specs:</b> 4 Conv2D Layers + 2 BiLSTM (128 units)"))
        ib_l.addWidget(QLabel("<b>Loss Function:</b> Weighted Dice + Mean Hausdorff Distance"))
        ib_l.addWidget(QLabel("<b>Spatial Resolution:</b> 30m / pixel (Landsat Grid)"))
        c1_layout.addWidget(info_box)

        c1_layout.addStretch()
        grid.addWidget(c1, 0, 0)

        # Card 2: Contributing Environmental Factors
        c2 = self.create_card("2. Estuarine & Hydrological Factors")
        c2_layout = QVBoxLayout(c2)
        c2_layout.setContentsMargins(14, 14, 14, 14)
        c2_layout.setSpacing(10)

        c2_layout.addWidget(QLabel("Peak Monsoon River Discharge (m³/s):"))
        sb_q = QDoubleSpinBox()
        sb_q.setRange(50.0, 5000.0)
        sb_q.setValue(850.0)
        sb_q.setStyleSheet(f"background: {DARK_EMERALD}; color: {MINT}; border: 1px solid {BORDER_COLOR}; padding: 4px; border-radius: 4px;")
        c2_layout.addWidget(sb_q)

        c2_layout.addWidget(QLabel("Littoral Drift & Sediment Influx (tonnes/yr):"))
        sb_s = QDoubleSpinBox()
        sb_s.setRange(1000.0, 500000.0)
        sb_s.setValue(125000.0)
        sb_s.setStyleSheet(f"background: {DARK_EMERALD}; color: {MINT}; border: 1px solid {BORDER_COLOR}; padding: 4px; border-radius: 4px;")
        c2_layout.addWidget(sb_s)

        c2_layout.addWidget(QLabel("Arabian Sea Tidal Wave Range (m):"))
        sb_t = QDoubleSpinBox()
        sb_t.setRange(0.5, 4.0)
        sb_t.setValue(1.8)
        sb_t.setStyleSheet(f"background: {DARK_EMERALD}; color: {MINT}; border: 1px solid {BORDER_COLOR}; padding: 4px; border-radius: 4px;")
        c2_layout.addWidget(sb_t)

        c2_layout.addStretch()
        grid.addWidget(c2, 0, 1)

        # Card 3: Model Execution & Target Horizon
        c3 = self.create_card("3. Prediction Simulation")
        c3_layout = QVBoxLayout(c3)
        c3_layout.setContentsMargins(14, 14, 14, 14)
        c3_layout.setSpacing(12)

        c3_layout.addWidget(QLabel("Forecast Horizon:"))
        horizon_combo = QComboBox()
        horizon_combo.addItems([
            "Year 2026 (Short-Term: +2 Years)",
            "Year 2030 (Medium-Term: +6 Years)",
            "Year 2035 (Decadal Projection: +11 Years)",
            "Custom Multi-Year Simulation"
        ])
        c3_layout.addWidget(horizon_combo)

        run_pred_btn = QPushButton("Run Hybrid AI Deviation Forecast")
        run_pred_btn.setIcon(get_icon("analysis", color=DARK_EMERALD, size=18))
        run_pred_btn.setCursor(Qt.PointingHandCursor)
        run_pred_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {TEAL}, stop:1 {MINT});
                color: {DARK_EMERALD};
                font-weight: 700;
                padding: 12px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {SOFT_LIME};
            }}
        """)
        run_pred_btn.clicked.connect(self.go_to_results)
        c3_layout.addWidget(run_pred_btn)

        status_lbl = QLabel("Model state: Pretrained weights verified (R² = 0.892, RMSE = 18.4m)")
        status_lbl.setStyleSheet(f"font-size: 11px; color: {MINT};")
        status_lbl.setAlignment(Qt.AlignCenter)
        c3_layout.addWidget(status_lbl)

        c3_layout.addStretch()
        grid.addWidget(c3, 0, 2)

        layout.addLayout(grid)

        # Bottom Bar
        bottom_box = QFrame()
        bottom_box.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 10px 14px;
            }}
        """)
        bb_layout = QHBoxLayout(bottom_box)
        bb_layout.addWidget(QLabel("<b>Swarna Estuary Morphometry:</b> Kodi Bengre sandspit migration exhibits westward littoral accretion."))
        bb_layout.addStretch()

        view_res_btn = QPushButton("View Results & Visualization →")
        view_res_btn.setCursor(Qt.PointingHandCursor)
        view_res_btn.setStyleSheet(f"""
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
        view_res_btn.clicked.connect(self.go_to_results)
        bb_layout.addWidget(view_res_btn)

        layout.addWidget(bottom_box)

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

    def go_to_results(self):
        if self.main_window and hasattr(self.main_window, "navigate_to_page"):
            self.main_window.navigate_to_page(3)
        else:
            self.stack.setCurrentIndex(1)
