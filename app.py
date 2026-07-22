#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║  wellcosta-dev / qr-generator                ║
║  Kostyál Árpád · wellcosta.dev               ║
║  QR Code Generator — PyQt6 + qrcode         ║
╚══════════════════════════════════════════════╝
"""

import sys
import io
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QSpinBox, QComboBox,
    QFrame, QStatusBar, QTextEdit, QColorDialog, QStackedWidget,
    QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter, QBrush

import qrcode

# ── WELLCOSTA / WELLTOOLS Design System v1.0 — tokenek ────────────────────────

class C:
    BG_CONTENT = "#26262a"
    BG_PANEL = "#1e1e22"
    BG_DEEP = "#1a1a1e"

    ACCENT = "#06b6d4"
    ACCENT_HOVER = "#0891b2"
    ACCENT_ACTIVE = "#0e7490"

    BORDER = "#333333"
    BORDER_STRONG = "#444444"

    TEXT_WHITE = "#ffffff"
    TEXT_PRIMARY = "#e8e8ec"
    TEXT_SECONDARY = "#aaaaaa"
    TEXT_MUTED = "#666666"
    TEXT_PLACEHOLDER = "#555555"
    LABEL_MUTED = "#888888"

    SUCCESS = "#06b6d4"
    ERROR = "#e74c3c"
    WARNING = "#f59e0b"


SPACE = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "2xl": 24, "3xl": 32}

FONT_STACK = "'Inter', 'Segoe UI', Arial, sans-serif"

QSS = f"""
QMainWindow, #centralWidget {{
    background-color: {C.BG_CONTENT};
}}

QWidget {{
    font-family: {FONT_STACK};
    font-size: 13px;
    color: {C.TEXT_PRIMARY};
}}

/* Header sáv */
QFrame#headerBar {{
    background-color: {C.BG_PANEL};
    border: none;
    border-bottom: 1px solid {C.BORDER};
    border-radius: 0px;
}}
QLabel#headerTitle {{
    font-size: 15px;
    font-weight: 700;
    color: {C.TEXT_WHITE};
    background: transparent;
}}
QLabel#headerSubtitle {{
    font-size: 11px;
    font-weight: 400;
    color: {C.TEXT_MUTED};
    background: transparent;
}}

/* Bal oldali nav */
QPushButton#navItem {{
    background-color: transparent;
    border: none;
    border-left: 2px solid transparent;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    color: {C.TEXT_SECONDARY};
    text-align: left;
    border-radius: 0px;
}}
QPushButton#navItem:hover {{
    color: {C.TEXT_PRIMARY};
}}
QPushButton#navItem:checked {{
    background-color: rgba(6, 182, 212, 0.1);
    border-left: 2px solid {C.ACCENT};
    color: {C.TEXT_WHITE};
}}

/* Label / section fejléc */
QLabel#sectionLabel {{
    font-size: 11px;
    font-weight: 600;
    color: {C.LABEL_MUTED};
    background: transparent;
}}
QLabel#inputLabel {{
    font-size: 11px;
    font-weight: 600;
    color: {C.LABEL_MUTED};
    background: transparent;
}}

/* Divider */
QFrame#divider {{
    background-color: {C.BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

/* Panel / kártya */
QFrame#panel {{
    background-color: {C.BG_CONTENT};
    border: 1px solid {C.BORDER};
    border-radius: 0px;
}}

/* Input mező */
QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    background-color: {C.BG_PANEL};
    border: 1px solid {C.BORDER_STRONG};
    border-radius: 0px;
    color: {C.TEXT_PRIMARY};
    font-size: 13px;
    padding: 8px 12px;
    selection-background-color: {C.ACCENT_ACTIVE};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {C.ACCENT};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    color: {C.TEXT_MUTED};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {C.BG_PANEL};
    border: 1px solid {C.BORDER_STRONG};
    border-radius: 0px;
    color: {C.TEXT_PRIMARY};
    selection-background-color: rgba(6, 182, 212, 0.15);
    selection-color: {C.TEXT_WHITE};
    outline: none;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {C.BG_PANEL};
    border-left: 1px solid {C.BORDER_STRONG};
    width: 16px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {C.BORDER};
}}

/* Gomb — elsődleges */
QPushButton#primary {{
    background-color: {C.ACCENT};
    color: #001a20;
    font-size: 12px;
    font-weight: 700;
    padding: 10px 18px;
    border: none;
    border-radius: 0px;
}}
QPushButton#primary:hover {{ background-color: {C.ACCENT_HOVER}; }}
QPushButton#primary:pressed {{ background-color: {C.ACCENT_ACTIVE}; }}
QPushButton#primary:disabled {{ background-color: {C.BORDER}; color: {C.TEXT_MUTED}; }}

/* Gomb — másodlagos */
QPushButton#secondary {{
    background-color: {C.BORDER};
    color: {C.TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 600;
    padding: 8px 18px;
    border: none;
    border-radius: 0px;
}}
QPushButton#secondary:hover {{ background-color: #3f3f3f; color: {C.TEXT_PRIMARY}; }}
QPushButton#secondary:disabled {{ background-color: #2a2a2a; color: {C.TEXT_MUTED}; }}

QPushButton#colorSwatch {{
    border: 1px solid {C.BORDER_STRONG};
    border-radius: 0px;
    min-width: 36px; max-width: 36px;
    min-height: 32px; max-height: 32px;
}}

/* Badge / pill */
QLabel#badgeActive {{
    background-color: {C.ACCENT};
    color: #001a20;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 0px;
}}
QLabel#badgeInactive {{
    background-color: {C.BORDER};
    color: {C.LABEL_MUTED};
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 0px;
}}

QLabel#previewPlaceholder {{
    color: {C.TEXT_PLACEHOLDER};
    font-size: 12px;
    background: transparent;
}}
QFrame#previewBox {{
    background-color: {C.BG_PANEL};
    border: 1px solid {C.BORDER};
    border-radius: 0px;
}}

QStatusBar {{
    background-color: {C.BG_DEEP};
    color: {C.TEXT_MUTED};
    font-size: 11px;
    border-top: 1px solid {C.BORDER};
}}
QStatusBar::item {{ border: none; }}

/* Scrollbar */
QScrollBar:vertical {{
    background: {C.BG_DEEP};
    width: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C.ACCENT};
    border-radius: 0px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {C.ACCENT_HOVER}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    background: {C.BG_DEEP};
    height: 4px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {C.ACCENT};
    border-radius: 0px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{ background: {C.ACCENT_HOVER}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
"""


def set_letter_spacing(widget, px):
    font = widget.font()
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, px)
    widget.setFont(font)


# ── Switch / toggle (design system komponens) ─────────────────────────────────

class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._on_toggle = None
        self.setFixedSize(36, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, value: bool):
        self._checked = bool(value)
        self.update()

    def connect(self, callback):
        self._on_toggle = callback

    def mousePressEvent(self, event):
        self.setChecked(not self._checked)
        if self._on_toggle:
            self._on_toggle(self._checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(Qt.PenStyle.NoPen)

        track_color = QColor(C.ACCENT if self._checked else C.BORDER_STRONG)
        painter.setBrush(QBrush(track_color))
        painter.drawRect(0, 0, 36, 16)

        knob_x = 36 - 2 - 12 if self._checked else 2
        painter.setBrush(QBrush(QColor(C.TEXT_WHITE)))
        painter.drawRect(knob_x, 2, 12, 12)


# ── Toast értesítés (design system komponens) ──────────────────────────────────

class Toast(QFrame):
    BORDER_COLORS = {"success": C.SUCCESS, "error": C.ERROR, "warning": C.WARNING}

    def __init__(self, parent, kind, title, message):
        super().__init__(parent)
        border_color = self.BORDER_COLORS.get(kind, C.SUCCESS)
        self.setObjectName("toast")
        self.setStyleSheet(f"""
            QFrame#toast {{
                background-color: {C.BG_PANEL};
                border: 1px solid {C.BORDER};
                border-left: 3px solid {border_color};
                border-radius: 0px;
            }}
        """)
        self.setMinimumWidth(260)
        self.setMaximumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {C.TEXT_WHITE}; "
            f"background: transparent; border: none;"
        )
        set_letter_spacing(title_label, 0.5)
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"font-size: 12px; color: {C.LABEL_MUTED}; background: transparent; border: none;"
        )
        layout.addWidget(message_label)


class ToastManager:
    def __init__(self, host):
        self.host = host
        self.active = []

    def show(self, kind, title, message, duration=3200):
        toast = Toast(self.host, kind, title, message)
        toast.adjustSize()
        self.active.append(toast)
        toast.show()
        self._reposition()
        QTimer.singleShot(duration, lambda: self._dismiss(toast))

    def _dismiss(self, toast):
        if toast not in self.active:
            return
        self.active.remove(toast)
        toast.deleteLater()
        self._reposition()

    def _reposition(self):
        margin = 16
        y = margin
        for toast in self.active:
            toast.adjustSize()
            x = self.host.width() - toast.width() - margin
            toast.move(max(x, margin), y)
            toast.raise_()
            y += toast.height() + 8

    def reflow(self):
        self._reposition()


# ── Perzisztencia ────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".wellcosta" / "qr_generator.json"


def load_config():
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
    except Exception:
        pass
    return {
        "last_tab": 0,
        "last_output_dir": str(Path.home() / "Pictures"),
        "qr_size": 10,
        "qr_border": 4,
        "qr_format": "PNG",
        "fg_color": "#000000",
        "bg_color": "#ffffff",
        "last_url": "",
        "last_text": "",
        "last_wifi_ssid": "",
        "last_wifi_security": "WPA",
    }


def save_config(cfg):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass


# ── Főablak ──────────────────────────────────────────────────────────────────

class QRGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.current_qr_image = None
        self.fg_color = self.cfg.get("fg_color", "#000000")
        self.bg_color = self.cfg.get("bg_color", "#ffffff")

        self.setWindowTitle("QR Generator — wellcosta-dev")
        self.setMinimumSize(1000, 640)
        self.resize(1080, 700)

        self._build_ui()
        self._restore_state()

    # ── Segédfüggvények ─────────────────────────────────────────────────────

    def _label(self, text, object_name, upper=False, spacing=None):
        lbl = QLabel(text.upper() if upper else text)
        lbl.setObjectName(object_name)
        if spacing:
            set_letter_spacing(lbl, spacing)
        return lbl

    def _divider(self):
        d = QFrame()
        d.setObjectName("divider")
        d.setFrameShape(QFrame.Shape.HLine)
        return d

    def _field(self, label_text, widget):
        box = QVBoxLayout()
        box.setSpacing(6)
        box.addWidget(self._label(label_text, "inputLabel", upper=True, spacing=0.5))
        box.addWidget(widget)
        return box

    # ── UI felépítés ─────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Nézetek előbb, mert a nav rájuk hivatkozik
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_url_page())
        self.stack.addWidget(self._build_text_page())
        self.stack.addWidget(self._build_vcard_page())
        self.stack.addWidget(self._build_wifi_page())

        root.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 16)
        body_layout.setSpacing(SPACE["xl"])

        body_layout.addWidget(self._build_nav())
        body_layout.addWidget(self._build_form_panel(), 1)
        body_layout.addWidget(self._build_preview_panel())

        root.addWidget(body, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Kész · wellcosta-dev")

        self.toasts = ToastManager(central)

    def _build_header(self):
        bar = QFrame()
        bar.setObjectName("headerBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(SPACE["sm"])

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title_block.addWidget(self._label("QR Generátor", "headerTitle", upper=True, spacing=1.0))
        subtitle = QLabel("wellcosta-dev · Kostyál Árpád")
        subtitle.setObjectName("headerSubtitle")
        title_block.addWidget(subtitle)

        layout.addLayout(title_block)
        layout.addStretch()
        layout.addWidget(self._label("v1.0", "badgeInactive", upper=True, spacing=0.5))

        return bar

    def _build_nav(self):
        container = QWidget()
        container.setFixedWidth(168)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_items = [("🔗", "URL"), ("📝", "Szöveg"), ("👤", "vCard"), ("📶", "WiFi")]

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for i, (icon, text) in enumerate(nav_items):
            btn = QPushButton(f"{icon}  {text}".upper())
            btn.setObjectName("navItem")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_group.addButton(btn, i)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        self.nav_buttons[0].setChecked(True)
        self.nav_group.idToggled.connect(self._on_nav_toggled)

        layout.addStretch()
        return container

    def _on_nav_toggled(self, index, checked):
        if checked:
            self.stack.setCurrentIndex(index)
            self.cfg["last_tab"] = index

    def _build_form_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(SPACE["md"])

        layout.addWidget(self.stack, 1)
        layout.addWidget(self._divider())
        layout.addLayout(self._build_settings())
        layout.addWidget(self._divider())

        self.btn_generate = QPushButton("QR kód generálása".upper())
        self.btn_generate.setObjectName("primary")
        self.btn_generate.setFixedHeight(40)
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.generate_qr)
        layout.addWidget(self.btn_generate)

        return panel

    def _build_settings(self):
        box = QVBoxLayout()
        box.setSpacing(SPACE["sm"])
        box.addWidget(self._label("Beállítások", "sectionLabel", upper=True, spacing=0.5))

        row = QHBoxLayout()
        row.setSpacing(SPACE["md"])

        size_col = QVBoxLayout()
        size_col.setSpacing(6)
        size_col.addWidget(self._label("Méret", "inputLabel", upper=True, spacing=0.5))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 40)
        self.size_spin.setValue(self.cfg.get("qr_size", 10))
        self.size_spin.setToolTip("QR kód cellák mérete (1-40)")
        size_col.addWidget(self.size_spin)
        row.addLayout(size_col)

        border_col = QVBoxLayout()
        border_col.setSpacing(6)
        border_col.addWidget(self._label("Keret", "inputLabel", upper=True, spacing=0.5))
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(self.cfg.get("qr_border", 4))
        border_col.addWidget(self.border_spin)
        row.addLayout(border_col)

        fmt_col = QVBoxLayout()
        fmt_col.setSpacing(6)
        fmt_col.addWidget(self._label("Formátum", "inputLabel", upper=True, spacing=0.5))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["PNG", "SVG", "JPG"])
        self.fmt_combo.setCurrentText(self.cfg.get("qr_format", "PNG"))
        fmt_col.addWidget(self.fmt_combo)
        row.addLayout(fmt_col)

        fg_col = QVBoxLayout()
        fg_col.setSpacing(6)
        fg_col.addWidget(self._label("QR szín", "inputLabel", upper=True, spacing=0.5))
        self.fg_btn = QPushButton()
        self.fg_btn.setObjectName("colorSwatch")
        self.fg_btn.setToolTip("QR kód színe")
        self.fg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_btn_color(self.fg_btn, self.fg_color)
        self.fg_btn.clicked.connect(lambda: self._pick_color("fg"))
        fg_col.addWidget(self.fg_btn)
        row.addLayout(fg_col)

        bg_col = QVBoxLayout()
        bg_col.setSpacing(6)
        bg_col.addWidget(self._label("Háttér", "inputLabel", upper=True, spacing=0.5))
        self.bg_btn = QPushButton()
        self.bg_btn.setObjectName("colorSwatch")
        self.bg_btn.setToolTip("Háttér színe")
        self.bg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_btn_color(self.bg_btn, self.bg_color)
        self.bg_btn.clicked.connect(lambda: self._pick_color("bg"))
        bg_col.addWidget(self.bg_btn)
        row.addLayout(bg_col)

        row.addStretch()
        box.addLayout(row)
        return box

    def _build_preview_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(260)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(SPACE["md"])

        header_row = QHBoxLayout()
        header_row.addWidget(self._label("Előnézet", "sectionLabel", upper=True, spacing=0.5))
        header_row.addStretch()
        self.status_badge = self._label("Nincs adat", "badgeInactive", upper=True, spacing=0.5)
        header_row.addWidget(self.status_badge)
        layout.addLayout(header_row)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("previewBox")
        self.preview_frame.setFixedSize(220, 220)
        pv_layout = QVBoxLayout(self.preview_frame)
        pv_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("QR kód itt jelenik meg")
        self.preview_label.setObjectName("previewPlaceholder")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setFixedSize(220, 220)
        self.preview_label.setScaledContents(True)
        pv_layout.addWidget(self.preview_label)

        layout.addWidget(self.preview_frame, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

        self.btn_save = QPushButton("Mentés…".upper())
        self.btn_save.setObjectName("secondary")
        self.btn_save.setEnabled(False)
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.save_qr)
        layout.addWidget(self.btn_save)

        return panel

    # ── Nézet oldalak ────────────────────────────────────────────────────────

    def _build_url_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE["sm"])

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://wellcosta.dev")
        layout.addLayout(self._field("URL cím", self.url_input))
        layout.addStretch()
        return page

    def _build_text_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE["sm"])

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Írja be a szöveget...")
        layout.addLayout(self._field("Szöveg", self.text_input))
        return page

    def _build_vcard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE["sm"])

        fields = [
            ("Teljes név", "vcard_name", "Kostyál Árpád"),
            ("Szervezet", "vcard_org", "Wellcosta"),
            ("Telefon", "vcard_phone", "+36 30 123 4567"),
            ("Email", "vcard_email", "arpi@wellcosta.dev"),
            ("Weboldal", "vcard_url", "https://wellcosta.dev"),
            ("Cím", "vcard_address", "Nyíregyháza, Magyarország"),
        ]

        for label_text, attr, placeholder in fields:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            setattr(self, attr, field)
            layout.addLayout(self._field(label_text, field))

        layout.addStretch()
        return page

    def _build_wifi_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE["sm"])

        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setPlaceholderText("OtthoniWifi")
        layout.addLayout(self._field("Hálózat neve (SSID)", self.wifi_ssid))

        self.wifi_password = QLineEdit()
        self.wifi_password.setPlaceholderText("jelszó")
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addLayout(self._field("Jelszó", self.wifi_password))

        show_row = QHBoxLayout()
        show_row.setSpacing(SPACE["sm"])
        self.show_pw_switch = ToggleSwitch()
        self.show_pw_switch.connect(lambda checked: self.wifi_password.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        ))
        show_row.addWidget(self.show_pw_switch)
        show_label = QLabel("Jelszó megjelenítése")
        show_label.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        show_row.addWidget(show_label)
        show_row.addStretch()
        layout.addLayout(show_row)

        layout.addWidget(self._label("Titkosítás", "inputLabel", upper=True, spacing=0.5))
        self.wifi_security = QComboBox()
        self.wifi_security.addItems(["WPA", "WEP", "Nincs"])
        self.wifi_security.setCurrentText(self.cfg.get("last_wifi_security", "WPA"))
        layout.addWidget(self.wifi_security)

        layout.addStretch()
        return page

    # ── Logika ───────────────────────────────────────────────────────────────

    def _build_qr_data(self):
        tab = self.stack.currentIndex()

        if tab == 0:  # URL
            data = self.url_input.text().strip()
            if not data:
                raise ValueError("Adjon meg egy URL-t.")
            return data

        elif tab == 1:  # Szöveg
            data = self.text_input.toPlainText().strip()
            if not data:
                raise ValueError("Adjon meg szöveget.")
            return data

        elif tab == 2:  # vCard
            name = self.vcard_name.text().strip()
            if not name:
                raise ValueError("A teljes név megadása kötelező.")
            lines = [
                "BEGIN:VCARD",
                "VERSION:3.0",
                f"FN:{name}",
            ]
            if self.vcard_org.text().strip():
                lines.append(f"ORG:{self.vcard_org.text().strip()}")
            if self.vcard_phone.text().strip():
                lines.append(f"TEL:{self.vcard_phone.text().strip()}")
            if self.vcard_email.text().strip():
                lines.append(f"EMAIL:{self.vcard_email.text().strip()}")
            if self.vcard_url.text().strip():
                lines.append(f"URL:{self.vcard_url.text().strip()}")
            if self.vcard_address.text().strip():
                lines.append(f"ADR:;;{self.vcard_address.text().strip()};;;;")
            lines.append("END:VCARD")
            return "\n".join(lines)

        elif tab == 3:  # WiFi
            ssid = self.wifi_ssid.text().strip()
            if not ssid:
                raise ValueError("Adja meg a hálózat nevét.")
            password = self.wifi_password.text()
            security = self.wifi_security.currentText()
            if security == "Nincs":
                security = "nopass"
                password = ""
            return f"WIFI:T:{security};S:{ssid};P:{password};;"

    def generate_qr(self):
        try:
            data = self._build_qr_data()
        except ValueError as e:
            self.toasts.show("warning", "Hiányzó adat", str(e))
            return

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=self.size_spin.value(),
                border=self.border_spin.value(),
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(
                fill_color=self.fg_color,
                back_color=self.bg_color
            ).convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            self.current_qr_image = img
            self.preview_label.setText("")
            self.preview_label.setPixmap(
                pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
            self.btn_save.setEnabled(True)
            self._set_status_badge(True)
            self.status.showMessage("Kész · QR kód generálva")
            self.toasts.show("success", "QR kód generálva", "A kód elkészült, mentheted a gombbal.")
            self._save_state()

        except Exception as e:
            self._set_status_badge(False)
            self.status.showMessage("Hiba történt")
            self.toasts.show("error", "Generálási hiba", str(e))

    def save_qr(self):
        if not self.current_qr_image:
            return

        fmt = self.fmt_combo.currentText()
        ext_filter = f"{fmt} fájlok (*.{fmt.lower()})"
        default_name = f"qr_code.{fmt.lower()}"

        path, _ = QFileDialog.getSaveFileName(
            self, "QR kód mentése",
            str(Path(self.cfg.get("last_output_dir", str(Path.home()))) / default_name),
            ext_filter
        )

        if not path:
            return

        try:
            if fmt == "SVG":
                import qrcode.image.svg
                data = self._build_qr_data()
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=self.size_spin.value(),
                    border=self.border_spin.value(),
                    image_factory=qrcode.image.svg.SvgImage
                )
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image()
                img.save(path)
            else:
                self.current_qr_image.save(path)

            self.cfg["last_output_dir"] = str(Path(path).parent)
            save_config(self.cfg)
            self.status.showMessage(f"Mentve: {path}")
            self.toasts.show("success", "Mentés kész", f"Fájl elmentve: {Path(path).name}")

        except Exception as e:
            self.status.showMessage("Mentési hiba")
            self.toasts.show("error", "Mentési hiba", str(e))

    def _pick_color(self, which):
        current = QColor(self.fg_color if which == "fg" else self.bg_color)
        color = QColorDialog.getColor(current, self, "Szín kiválasztása")
        if color.isValid():
            hex_color = color.name()
            if which == "fg":
                self.fg_color = hex_color
                self._set_btn_color(self.fg_btn, hex_color)
            else:
                self.bg_color = hex_color
                self._set_btn_color(self.bg_btn, hex_color)

    def _set_btn_color(self, btn, hex_color):
        btn.setStyleSheet(
            f"QPushButton#colorSwatch {{ background-color: {hex_color}; "
            f"border: 1px solid {C.BORDER_STRONG}; border-radius: 0px; }}"
        )

    def _set_status_badge(self, ready: bool):
        self.status_badge.setText(("Kész" if ready else "Nincs adat").upper())
        self.status_badge.setObjectName("badgeActive" if ready else "badgeInactive")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    def _restore_state(self):
        idx = self.cfg.get("last_tab", 0)
        if 0 <= idx < len(self.nav_buttons):
            self.nav_buttons[idx].setChecked(True)
        self.url_input.setText(self.cfg.get("last_url", ""))
        self.text_input.setPlainText(self.cfg.get("last_text", ""))
        self.wifi_ssid.setText(self.cfg.get("last_wifi_ssid", ""))
        self.wifi_security.setCurrentText(self.cfg.get("last_wifi_security", "WPA"))

    def _save_state(self):
        self.cfg.update({
            "last_tab": self.stack.currentIndex(),
            "last_url": self.url_input.text(),
            "last_text": self.text_input.toPlainText(),
            "last_wifi_ssid": self.wifi_ssid.text(),
            "last_wifi_security": self.wifi_security.currentText(),
            "qr_size": self.size_spin.value(),
            "qr_border": self.border_spin.value(),
            "qr_format": self.fmt_combo.currentText(),
            "fg_color": self.fg_color,
            "bg_color": self.bg_color,
        })
        save_config(self.cfg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "toasts"):
            self.toasts.reflow()

    def closeEvent(self, event):
        self._save_state()
        super().closeEvent(event)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("QR Generator")
    app.setOrganizationName("wellcosta-dev")

    base_font = QFont()
    base_font.setFamilies(["Inter", "Segoe UI", "Arial"])
    base_font.setPointSize(9)
    app.setFont(base_font)

    app.setStyleSheet(QSS)

    window = QRGenerator()
    window.show()
    sys.exit(app.exec())
