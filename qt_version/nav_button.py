"""
Sidebar Navigation Button - Estuarine Mouth Dynamics GIS Dashboard
Crisp, anti-aliased custom-painted navigation button.
Eliminates OS button bevels, stylesheet layout artifacts, focus outlines,
and vertical line clipping glitches.
Theme: Dark Emerald & Tropical Coastal GIS
"""

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget
from icons import get_pixmap
from theme import (
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
)


class SidebarNavButton(QWidget):
    clicked = Signal()

    def __init__(
        self,
        icon_name: str,
        title: str,
        desc: str,
        on_click=None,
        is_active: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.icon_name = icon_name
        self.title = title
        self.desc = desc
        self.is_active = is_active
        self.is_hovered = False
        self.is_pressed = False

        self.setFixedHeight(54)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setFocusPolicy(Qt.NoFocus)

        if on_click:
            self.clicked.connect(on_click)

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_pressed:
            self.is_pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        # Background & Border state
        if self.is_active:
            bg = QColor(PANEL_GREEN)
            border = QColor(MINT)
            pen_width = 1.2
        elif self.is_pressed:
            bg = QColor(PANEL_SURFACE)
            border = QColor(TEAL)
            pen_width = 1.0
        elif self.is_hovered:
            bg = QColor(PANEL_GREEN)
            border = QColor(MINT)
            pen_width = 1.0
        else:
            bg = QColor(DARK_EMERALD)
            border = QColor(BORDER_SUBTLE)
            pen_width = 1.0

        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, pen_width))
        p.drawRoundedRect(rect, 8.0, 8.0)

        # Icon Rendering
        icon_color = SOFT_LIME if self.is_active else (MINT if self.is_hovered else MINT)
        pix = get_pixmap(self.icon_name, color=icon_color, size=20)
        if pix and not pix.isNull():
            icon_y = (self.height() - pix.height()) / 2.0
            p.drawPixmap(14, int(icon_y), pix)

        # Title Text Rendering
        font_title = QFont()
        font_title.setPointSize(10)
        font_title.setBold(True)
        p.setFont(font_title)
        p.setPen(QColor(SOFT_LIME if self.is_active else WARM_IVORY))
        p.drawText(
            QRectF(46, 8, self.width() - 52, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.title,
        )

        # Description Text Rendering
        font_desc = QFont()
        font_desc.setPointSize(8)
        font_desc.setBold(False)
        p.setFont(font_desc)
        p.setPen(QColor(MUTED_SAGE))
        p.drawText(
            QRectF(46, 28, self.width() - 52, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.desc,
        )

        p.end()

