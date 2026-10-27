from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


class ResultPage(QWidget):

    def __init__(self, stack):
        super().__init__()

        self.stack = stack

        main_layout = QVBoxLayout(self)

        # ============================
        # Top Layout
        # ============================

        top_layout = QHBoxLayout()

        back = QPushButton("← Back")

        back.setFixedSize(120, 40)

        back.setStyleSheet("""
            QPushButton{
                background:#1976D2;
                color:white;
                font-size:15px;
                font-weight:bold;
                border:none;
                border-radius:8px;
            }

            QPushButton:hover{
                background:#1565C0;
            }
        """)

        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        top_layout.addWidget(back)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # ============================
        # Title
        # ============================

        title = QLabel("Prediction Result")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
        """)

        main_layout.addStretch()
        main_layout.addWidget(title)

        # ============================
        # Result Text
        # ============================

        result = QLabel("Prediction output will be displayed here.")

        result.setAlignment(Qt.AlignCenter)

        result.setStyleSheet("""
            font-size:16px;
        """)

        main_layout.addSpacing(20)

        main_layout.addWidget(result)

        main_layout.addStretch()