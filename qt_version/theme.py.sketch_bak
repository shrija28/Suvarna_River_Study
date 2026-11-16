"""
Theme tokens and stylesheet definitions for Suvarna River GIS Dashboard.
Theme: Premium Dark Emerald & Tropical Coastal GIS
"""

# Color Palette
BG_DARK = "#031B18"         # Deep forest green (Window background)
DARK_EMERALD = "#082B26"    # Dark emerald (Cards, header, sidebar base)
PANEL_GREEN = "#103B32"     # Panel green (Active elements, elevated cards)
PANEL_SURFACE = "#0B2F2A"   # Surface panel background
BORDER_COLOR = "#24574B"    # Standard borders
BORDER_SUBTLE = "#1B473D"   # Subtle dividers
TEAL = "#00BFA5"            # Primary brand teal
MINT = "#74E6B0"            # Mint green accent & highlight
SOFT_LIME = "#C8E889"       # Soft lime accent
WARM_IVORY = "#F4F1E8"      # Primary text (warm ivory)
MUTED_SAGE = "#A8C4B7"      # Secondary / description text
AMBER = "#E9B866"           # Warning / accent amber
INPUT_BG = "#06221D"        # Text inputs background

# Base Application Stylesheet
APP_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
    color: {WARM_IVORY};
}}

QWidget {{
    background-color: transparent;
    color: {WARM_IVORY};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {DARK_EMERALD};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_COLOR};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEAL};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Combo Boxes */
QComboBox {{
    background-color: {INPUT_BG};
    color: {WARM_IVORY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 500;
}}
QComboBox:hover {{
    border: 1px solid {TEAL};
}}
QComboBox:focus {{
    border: 1px solid {MINT};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: 1px solid {BORDER_SUBTLE};
}}
QComboBox QAbstractItemView {{
    background-color: {DARK_EMERALD};
    color: {WARM_IVORY};
    selection-background-color: {PANEL_GREEN};
    selection-color: {MINT};
    border: 1px solid {BORDER_COLOR};
    padding: 4px;
}}

/* Line Edits */
QLineEdit {{
    background-color: {INPUT_BG};
    color: {MINT};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    font-family: "Consolas", monospace;
}}
QLineEdit:focus {{
    border: 1px solid {MINT};
}}
QLineEdit:read-only {{
    background-color: {INPUT_BG};
    color: {MINT};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Push Buttons */
QPushButton {{
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    padding: 8px 14px;
}}
"""
