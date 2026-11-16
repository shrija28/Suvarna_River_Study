"""
Modern Authentication & Login Page
Estuarine Mouth Dynamics - Path Deviation Prediction System

Features:
- Signature Dark Emerald & Teal GIS theme.
- Authentic Project Logo, Title, and Subtitle.
- Username/Email and Password input fields with inline validation.
- Interactive Show/Hide password toggle.
- "Remember Me" credential preservation.
- "Forgot Password" quick reset workflow.
- "Create Account" registration tab for new researchers and administrators.
- Real-time error and status feedback banner.
"""

import os
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen, QFont
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QStackedWidget,
    QSizePolicy,
    QScrollArea,
)

from theme import (
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
    INPUT_BG,
)
from icons import get_icon, get_pixmap
from backend.auth_service import auth_service


class LoginPage(QWidget):
    """
    Primary Authentication Screen displayed on application launch.
    Directs the user to the Main Application upon successful credential verification.
    """
    login_success = Signal(dict)  # Emits authenticated user dictionary

    def __init__(self, parent=None, on_login_success=None):
        super().__init__(parent)
        self.on_login_success_callback = on_login_success
        if on_login_success:
            self.login_success.connect(on_login_success)

        self.setObjectName("LoginPage")
        self.setStyleSheet(f"""
            QWidget#LoginPage {{
                background-color: {BG_DARK};
            }}
        """)

        self._build_ui()
        self._load_remembered_credentials()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll area to ensure accessibility on all screen heights
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background-color: {BG_DARK}; border: none;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_DARK};")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 30, 20, 30)
        c_layout.setAlignment(Qt.AlignCenter)

        # --------------------------------------------------------------------
        # Center Login Card (Max width 480px)
        # --------------------------------------------------------------------
        self.card = QFrame()
        self.card.setFixedWidth(460)
        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_EMERALD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 14px;
            }}
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(14)

        # 1. Header: Logo, Title, Subtitle
        header_box = QVBoxLayout()
        header_box.setSpacing(6)
        header_box.setAlignment(Qt.AlignCenter)

        # Logo Box
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(64, 64)
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png"))
        if os.path.exists(logo_path):
            src_pix = QPixmap(logo_path)
            if not src_pix.isNull():
                rounded_logo = QPixmap(64, 64)
                rounded_logo.fill(Qt.transparent)
                p = QPainter(rounded_logo)
                p.setRenderHint(QPainter.Antialiasing)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                path = QPainterPath()
                path.addRoundedRect(2, 2, 60, 60, 14, 14)
                p.setClipPath(path)
                p.fillRect(2, 2, 60, 60, QColor("#FFFFFF"))
                scaled = src_pix.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                p.drawPixmap((64 - scaled.width()) // 2, (64 - scaled.height()) // 2, scaled)
                p.setClipping(False)
                p.setPen(QPen(QColor(BORDER_COLOR), 1.5))
                p.drawRoundedRect(2, 2, 60, 60, 14, 14)
                p.end()
                logo_lbl.setPixmap(rounded_logo)
        header_box.addWidget(logo_lbl, alignment=Qt.AlignCenter)

        # Project Title
        title_lbl = QLabel("Estuarine Mouth Dynamics")
        title_lbl.setStyleSheet(f"""
            font-size: 21px;
            font-weight: 800;
            color: {WARM_IVORY};
            letter-spacing: 0.5px;
            border: none;
            background: transparent;
        """)
        title_lbl.setAlignment(Qt.AlignCenter)
        header_box.addWidget(title_lbl)

        # Subtitle
        sub_lbl = QLabel("Path Deviation Prediction System")
        sub_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {MINT};
            border: none;
            background: transparent;
        """)
        sub_lbl.setAlignment(Qt.AlignCenter)
        header_box.addWidget(sub_lbl)

        # Tagline Chip
        tagline = QLabel("Geospatial Analysis  •  Remote Sensing  •  ML Morphodynamics")
        tagline.setStyleSheet(f"""
            font-size: 10px;
            color: {MUTED_SAGE};
            border: none;
            background: transparent;
        """)
        tagline.setAlignment(Qt.AlignCenter)
        header_box.addWidget(tagline)

        card_layout.addLayout(header_box)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {BORDER_SUBTLE}; max-height: 1px; border: none;")
        card_layout.addWidget(divider)

        # Mode Tab Switcher (Sign In vs Register)
        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)
        self.tab_signin_btn = QPushButton("Sign In")
        self.tab_signin_btn.setCursor(Qt.PointingHandCursor)
        self.tab_signin_btn.clicked.connect(self.show_signin_view)

        self.tab_register_btn = QPushButton("Create Account")
        self.tab_register_btn.setCursor(Qt.PointingHandCursor)
        self.tab_register_btn.clicked.connect(self.show_register_view)

        tab_row.addWidget(self.tab_signin_btn)
        tab_row.addWidget(self.tab_register_btn)
        card_layout.addLayout(tab_row)

        # Error / Feedback Banner
        self.feedback_banner = QLabel()
        self.feedback_banner.setWordWrap(True)
        self.feedback_banner.setAlignment(Qt.AlignCenter)
        self.feedback_banner.setVisible(False)
        card_layout.addWidget(self.feedback_banner)

        # --------------------------------------------------------------------
        # Form Stack (Index 0: Sign In, Index 1: Register, Index 2: Forgot Password)
        # --------------------------------------------------------------------
        self.form_stack = QStackedWidget()
        self.form_stack.setStyleSheet("background: transparent; border: none;")

        self.signin_widget = self._create_signin_view()
        self.register_widget = self._create_register_view()
        self.forgot_widget = self._create_forgot_password_view()

        self.form_stack.addWidget(self.signin_widget)    # 0: Sign In
        self.form_stack.addWidget(self.register_widget)  # 1: Register
        self.form_stack.addWidget(self.forgot_widget)    # 2: Forgot Password

        card_layout.addWidget(self.form_stack)

        # Footer: Study Area & Security Notice
        footer_lbl = QLabel("Protected Scientific Research Environment • Kodi Bengre, Udupi")
        footer_lbl.setAlignment(Qt.AlignCenter)
        footer_lbl.setStyleSheet(f"""
            font-size: 10px;
            color: {MUTED_SAGE};
            border: none;
            background: transparent;
            padding-top: 6px;
        """)
        card_layout.addWidget(footer_lbl)

        c_layout.addWidget(self.card)
        scroll.setWidget(container)
        root_layout.addWidget(scroll)

        # Set default active tab
        self.show_signin_view()

    # ========================================================================
    # View 1: Sign In View
    # ========================================================================
    def _create_signin_view(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(12)

        # Username / Email Input
        layout.addWidget(self._create_field_label("Username or Email"))
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Enter your username or email")
        self.input_username.setStyleSheet(self._input_style())
        self.input_username.returnPressed.connect(self.handle_login)
        layout.addWidget(self.input_username)

        # Password Input
        layout.addWidget(self._create_field_label("Password"))
        pwd_box = QHBoxLayout()
        pwd_box.setSpacing(6)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Enter your password")
        self.input_password.setStyleSheet(self._input_style())
        self.input_password.returnPressed.connect(self.handle_login)
        pwd_box.addWidget(self.input_password, 1)

        self.btn_toggle_pwd = QPushButton()
        self.btn_toggle_pwd.setFixedSize(36, 36)
        self.btn_toggle_pwd.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pwd.setIcon(get_icon("eye", color=MUTED_SAGE, size=16))
        self.btn_toggle_pwd.setToolTip("Show / Hide Password")
        self.btn_toggle_pwd.setStyleSheet(self._icon_btn_style())
        self.btn_toggle_pwd.clicked.connect(self.toggle_password_visibility)
        pwd_box.addWidget(self.btn_toggle_pwd)
        layout.addLayout(pwd_box)

        # Row: Remember Me & Forgot Password
        opt_row = QHBoxLayout()
        self.chk_remember = QCheckBox("Remember Me")
        self.chk_remember.setCursor(Qt.PointingHandCursor)
        self.chk_remember.setStyleSheet(f"""
            QCheckBox {{
                color: {WARM_IVORY};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {TEAL};
                border-color: {MINT};
                image: url('none');
            }}
        """)
        opt_row.addWidget(self.chk_remember)
        opt_row.addStretch()

        btn_forgot = QPushButton("Forgot Password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet(f"""
            QPushButton {{
                color: {MINT};
                font-size: 11px;
                background: transparent;
                border: none;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {SOFT_LIME};
            }}
        """)
        btn_forgot.clicked.connect(self.show_forgot_view)
        opt_row.addWidget(btn_forgot)
        layout.addLayout(opt_row)

        # Primary Login Button
        self.btn_login = QPushButton("Log In to System")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet(self._primary_button_style())
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        return w

    # ========================================================================
    # View 2: Registration View
    # ========================================================================
    def _create_register_view(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        # Full Name
        layout.addWidget(self._create_field_label("Full Name"))
        self.reg_fullname = QLineEdit()
        self.reg_fullname.setPlaceholderText("e.g. Dr. Ramesh Rao")
        self.reg_fullname.setStyleSheet(self._input_style())
        layout.addWidget(self.reg_fullname)

        # Username
        layout.addWidget(self._create_field_label("Username"))
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose a unique username")
        self.reg_username.setStyleSheet(self._input_style())
        layout.addWidget(self.reg_username)

        # Email
        layout.addWidget(self._create_field_label("Official Email Address"))
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("e.g. ramesh@estuary-research.org")
        self.reg_email.setStyleSheet(self._input_style())
        layout.addWidget(self.reg_email)

        # Password
        layout.addWidget(self._create_field_label("Password (min 6 characters)"))
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setPlaceholderText("Create a secure password")
        self.reg_password.setStyleSheet(self._input_style())
        layout.addWidget(self.reg_password)

        # Confirm Password
        layout.addWidget(self._create_field_label("Confirm Password"))
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setPlaceholderText("Re-type password")
        self.reg_confirm.setStyleSheet(self._input_style())
        layout.addWidget(self.reg_confirm)

        # Submit Register Button
        self.btn_submit_reg = QPushButton("Create Researcher Account")
        self.btn_submit_reg.setFixedHeight(42)
        self.btn_submit_reg.setCursor(Qt.PointingHandCursor)
        self.btn_submit_reg.setStyleSheet(self._primary_button_style())
        self.btn_submit_reg.clicked.connect(self.handle_register)
        layout.addWidget(self.btn_submit_reg)

        return w

    # ========================================================================
    # View 3: Forgot Password View
    # ========================================================================
    def _create_forgot_password_view(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(11)

        info = QLabel("Reset Account Password\nEnter your registered username/email and specify a new password.")
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 11px; color: {MUTED_SAGE};")
        layout.addWidget(info)

        layout.addWidget(self._create_field_label("Username or Registered Email"))
        self.fp_user = QLineEdit()
        self.fp_user.setPlaceholderText("Enter username or email")
        self.fp_user.setStyleSheet(self._input_style())
        layout.addWidget(self.fp_user)

        layout.addWidget(self._create_field_label("New Password"))
        self.fp_new_pwd = QLineEdit()
        self.fp_new_pwd.setEchoMode(QLineEdit.Password)
        self.fp_new_pwd.setPlaceholderText("New password (min 6 characters)")
        self.fp_new_pwd.setStyleSheet(self._input_style())
        layout.addWidget(self.fp_new_pwd)

        layout.addWidget(self._create_field_label("Confirm New Password"))
        self.fp_confirm_pwd = QLineEdit()
        self.fp_confirm_pwd.setEchoMode(QLineEdit.Password)
        self.fp_confirm_pwd.setPlaceholderText("Confirm new password")
        self.fp_confirm_pwd.setStyleSheet(self._input_style())
        layout.addWidget(self.fp_confirm_pwd)

        btn_reset = QPushButton("Update Password")
        btn_reset.setFixedHeight(40)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet(self._primary_button_style())
        btn_reset.clicked.connect(self.handle_reset_password)
        layout.addWidget(btn_reset)

        btn_cancel = QPushButton("← Return to Sign In")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MUTED_SAGE};
                font-size: 11px;
                border: none;
            }}
            QPushButton:hover {{
                color: {WARM_IVORY};
            }}
        """)
        btn_cancel.clicked.connect(self.show_signin_view)
        layout.addWidget(btn_cancel)

        return w

    # ========================================================================
    # View Switching & Tab Styling
    # ========================================================================
    def show_signin_view(self):
        self.form_stack.setCurrentIndex(0)
        self._update_tab_styles(active_tab="signin")
        self.clear_feedback()

    def show_register_view(self):
        self.form_stack.setCurrentIndex(1)
        self._update_tab_styles(active_tab="register")
        self.clear_feedback()

    def show_forgot_view(self):
        self.form_stack.setCurrentIndex(2)
        self._update_tab_styles(active_tab="forgot")
        self.clear_feedback()

    def _update_tab_styles(self, active_tab: str):
        active_style = f"""
            QPushButton {{
                background-color: {PANEL_GREEN};
                color: {MINT};
                font-weight: 700;
                font-size: 12px;
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 12px;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {MUTED_SAGE};
                font-weight: 500;
                font-size: 12px;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {INPUT_BG};
                color: {WARM_IVORY};
            }}
        """
        if active_tab == "signin":
            self.tab_signin_btn.setStyleSheet(active_style)
            self.tab_register_btn.setStyleSheet(inactive_style)
        elif active_tab == "register":
            self.tab_signin_btn.setStyleSheet(inactive_style)
            self.tab_register_btn.setStyleSheet(active_style)
        else:
            self.tab_signin_btn.setStyleSheet(inactive_style)
            self.tab_register_btn.setStyleSheet(inactive_style)

    # ========================================================================
    # Interactive Actions
    # ========================================================================
    def toggle_password_visibility(self):
        if self.input_password.echoMode() == QLineEdit.Password:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pwd.setIcon(get_icon("eye_off", color=MINT, size=16))
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pwd.setIcon(get_icon("eye", color=MUTED_SAGE, size=16))

    def handle_login(self):
        """Processes login submission."""
        self.clear_feedback()
        username_or_email = self.input_username.text()
        password = self.input_password.text()
        remember_me = self.chk_remember.isChecked()

        user, err = auth_service.authenticate(username_or_email, password, remember_me=remember_me)
        if err:
            self.show_error(err)
            return

        # Login Succeeded
        self.show_success(f"Welcome, {user.get('full_name') or user['username']}! Opening dashboard...")
        self.input_password.clear()
        self.login_success.emit(user)

    def handle_register(self):
        """Processes user account creation."""
        self.clear_feedback()
        fn = self.reg_fullname.text()
        u = self.reg_username.text()
        em = self.reg_email.text()
        p = self.reg_password.text()
        cp = self.reg_confirm.text()

        success, err = auth_service.register(u, em, p, cp, fn, role="Researcher")
        if not success:
            self.show_error(err)
            return

        # Registration succeeded: switch to sign in with pre-filled username
        self.show_signin_view()
        self.input_username.setText(u)
        self.input_password.clear()
        self.show_success("Account created successfully! Please sign in with your password.")

    def handle_reset_password(self):
        """Processes password reset."""
        self.clear_feedback()
        u = self.fp_user.text()
        p = self.fp_new_pwd.text()
        cp = self.fp_confirm_pwd.text()

        success, err = auth_service.reset_password(u, p, cp)
        if not success:
            self.show_error(err)
            return

        self.show_signin_view()
        self.input_username.setText(u)
        self.input_password.clear()
        self.show_success("Password updated successfully! Please sign in with your new password.")

    # ========================================================================
    # Feedback & UI Helpers
    # ========================================================================
    def show_error(self, message: str):
        self.feedback_banner.setText(f"⚠  {message}")
        self.feedback_banner.setStyleSheet(f"""
            background-color: #2D1414;
            color: #FF8A80;
            border: 1px solid #B71C1C;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        self.feedback_banner.setVisible(True)

    def show_success(self, message: str):
        self.feedback_banner.setText(f"✓  {message}")
        self.feedback_banner.setStyleSheet(f"""
            background-color: #062B22;
            color: {MINT};
            border: 1px solid {TEAL};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        self.feedback_banner.setVisible(True)

    def clear_feedback(self):
        self.feedback_banner.clear()
        self.feedback_banner.setVisible(False)

    def _load_remembered_credentials(self):
        rem_user = auth_service.get_remembered_username()
        if rem_user:
            self.input_username.setText(rem_user)
            self.chk_remember.setChecked(True)
            self.input_password.setFocus()
        else:
            self.input_username.setFocus()

    def reset_for_logout(self):
        """Called when a user logs out to cleanly reset fields."""
        self.clear_feedback()
        self.input_password.clear()
        self.show_signin_view()
        self.show_success("You have been logged out successfully.")
        self._load_remembered_credentials()

    def _create_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {WARM_IVORY};
            border: none;
            background: transparent;
        """)
        return lbl

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background-color: {INPUT_BG};
                color: {WARM_IVORY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {TEAL};
            }}
            QLineEdit:focus {{
                border: 1px solid {MINT};
                background-color: #082D26;
            }}
        """

    def _icon_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 4px;
            }}
            QPushButton:hover {{
                border-color: {MINT};
                background-color: {PANEL_GREEN};
            }}
        """

    def _primary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {TEAL}, stop:1 {MINT});
                color: #031B18;
                font-size: 13px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D2B4, stop:1 {SOFT_LIME});
            }}
            QPushButton:pressed {{
                background: {TEAL};
            }}
        """
