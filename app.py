#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║  wellcosta-dev / qr-generator                ║
║  Kostyál Árpád · wellcosta.dev               ║
║  QR Code Generator — PyQt6 + qrcode         ║
╚══════════════════════════════════════════════╝
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTabWidget, QFileDialog,
    QSpinBox, QComboBox, QFrame, QStatusBar, QMessageBox,
    QTextEdit, QColorDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QColor
import qrcode
from qrcode.image.pure import PyPNGImage
import io

# ── Stílus (konzisztens az image converter-rel) ──────────────────────────────

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0f0f11;
    color: #e8e8ec;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}

QLabel#subtitle {
    font-size: 12px;
    color: #6b6b7a;
}

QLabel#section {
    font-size: 11px;
    font-weight: 600;
    color: #6b6b7a;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#preview_placeholder {
    color: #2a2a3a;
    font-size: 12px;
}

QFrame#preview_box {
    background-color: #141418;
    border: 1px solid #1e1e28;
    border-radius: 12px;
}

QFrame#divider {
    background-color: #1e1e28;
    max-height: 1px;
}

QTabWidget::pane {
    border: 1px solid #1e1e28;
    border-radius: 8px;
    background-color: #141418;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f0f11;
    color: #6b6b7a;
    padding: 8px 20px;
    border: 1px solid #1e1e28;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #141418;
    color: #ffffff;
    border-bottom: 1px solid #141418;
}

QTabBar::tab:hover:!selected {
    color: #c8c8d4;
    background-color: #141418;
}

QLineEdit, QTextEdit {
    background-color: #1e1e28;
    color: #e8e8ec;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #4f46e5;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #4f46e5;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #3a3a4a;
}

QPushButton#primary {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#primary:hover {
    background-color: #4338ca;
}

QPushButton#primary:pressed {
    background-color: #3730a3;
}

QPushButton#primary:disabled {
    background-color: #2a2a35;
    color: #4a4a5a;
}

QPushButton#secondary {
    background-color: #1e1e28;
    color: #c8c8d4;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
}

QPushButton#secondary:hover {
    background-color: #252532;
    color: #ffffff;
}

QPushButton#color_btn {
    border-radius: 6px;
    border: 1px solid #2a2a35;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
}

QSpinBox, QComboBox {
    background-color: #1e1e28;
    color: #e8e8ec;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    padding: 8px 12px;
    min-width: 80px;
}

QSpinBox:hover, QComboBox:hover {
    border-color: #4f46e5;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a24;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    selection-background-color: #2a2a3e;
    color: #e8e8ec;
}

QCheckBox {
    color: #c8c8d4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid #2a2a35;
    background-color: #1e1e28;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #4f46e5;
}

QStatusBar {
    background-color: #0a0a0d;
    color: #6b6b7a;
    font-size: 11px;
    border-top: 1px solid #1e1e28;
}
"""

# ── Perzisztencia ────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".wellcosta" / "qr_generator.json"

def load_config():
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
    except:
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
    except:
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
        self.setMinimumSize(820, 580)
        self.resize(920, 640)
        self.setStyleSheet(DARK_STYLE)

        self._build_ui()
        self._restore_state()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(24, 24, 24, 16)
        main.setSpacing(16)

        # ── Header
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title = QLabel("QR Generator")
        title.setObjectName("title")
        subtitle = QLabel("wellcosta-dev · URL · Szöveg · vCard · WiFi")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block)
        header.addStretch()
        version = QLabel("v1.0")
        version.setStyleSheet("color: #2a2a3a; font-size: 11px;")
        header.addWidget(version)
        main.addLayout(header)

        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.HLine)
        main.addWidget(div)

        # ── Tartalom
        content = QHBoxLayout()
        content.setSpacing(20)

        # ── Bal oldal: input tabek
        left = QVBoxLayout()
        left.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_url_tab(), "🔗  URL")
        self.tabs.addTab(self._build_text_tab(), "📝  Szöveg")
        self.tabs.addTab(self._build_vcard_tab(), "👤  vCard")
        self.tabs.addTab(self._build_wifi_tab(), "📶  WiFi")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        left.addWidget(self.tabs)

        # Beállítások
        settings_label = QLabel("BEÁLLÍTÁSOK")
        settings_label.setObjectName("section")
        left.addWidget(settings_label)

        settings_row = QHBoxLayout()
        settings_row.setSpacing(12)

        # Méret
        size_col = QVBoxLayout()
        size_col.setSpacing(4)
        size_col.addWidget(QLabel("Méret"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 40)
        self.size_spin.setValue(self.cfg.get("qr_size", 10))
        self.size_spin.setToolTip("QR kód cellák mérete (1-40)")
        size_col.addWidget(self.size_spin)
        settings_row.addLayout(size_col)

        # Keret
        border_col = QVBoxLayout()
        border_col.setSpacing(4)
        border_col.addWidget(QLabel("Keret"))
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(self.cfg.get("qr_border", 4))
        border_col.addWidget(self.border_spin)
        settings_row.addLayout(border_col)

        # Formátum
        fmt_col = QVBoxLayout()
        fmt_col.setSpacing(4)
        fmt_col.addWidget(QLabel("Formátum"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["PNG", "SVG", "JPG"])
        self.fmt_combo.setCurrentText(self.cfg.get("qr_format", "PNG"))
        fmt_col.addWidget(self.fmt_combo)
        settings_row.addLayout(fmt_col)

        # Előtér szín
        fg_col = QVBoxLayout()
        fg_col.setSpacing(4)
        fg_col.addWidget(QLabel("QR szín"))
        self.fg_btn = QPushButton()
        self.fg_btn.setObjectName("color_btn")
        self.fg_btn.setToolTip("QR kód színe")
        self._set_btn_color(self.fg_btn, self.fg_color)
        self.fg_btn.clicked.connect(lambda: self._pick_color("fg"))
        fg_col.addWidget(self.fg_btn)
        settings_row.addLayout(fg_col)

        # Háttér szín
        bg_col = QVBoxLayout()
        bg_col.setSpacing(4)
        bg_col.addWidget(QLabel("Háttér"))
        self.bg_btn = QPushButton()
        self.bg_btn.setObjectName("color_btn")
        self.bg_btn.setToolTip("Háttér színe")
        self._set_btn_color(self.bg_btn, self.bg_color)
        self.bg_btn.clicked.connect(lambda: self._pick_color("bg"))
        bg_col.addWidget(self.bg_btn)
        settings_row.addLayout(bg_col)

        settings_row.addStretch()
        left.addLayout(settings_row)

        # Generálás gomb
        self.btn_generate = QPushButton("QR kód generálása")
        self.btn_generate.setObjectName("primary")
        self.btn_generate.setFixedHeight(42)
        self.btn_generate.clicked.connect(self.generate_qr)
        left.addWidget(self.btn_generate)

        content.addLayout(left, 3)

        # ── Jobb oldal: preview
        right = QVBoxLayout()
        right.setSpacing(12)
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        preview_label = QLabel("ELŐNÉZET")
        preview_label.setObjectName("section")
        right.addWidget(preview_label)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("preview_box")
        self.preview_frame.setFixedSize(260, 260)
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_label = QLabel("QR kód itt jelenik meg")
        self.preview_label.setObjectName("preview_placeholder")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)

        right.addWidget(self.preview_frame)
        right.addStretch()

        # Mentés gomb
        self.btn_save = QPushButton("Mentés…")
        self.btn_save.setObjectName("secondary")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_qr)
        right.addWidget(self.btn_save)

        content.addLayout(right, 1)
        main.addLayout(content)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Kész · wellcosta-dev")

    # ── Tab építők ───────────────────────────────────────────────────────────

    def _build_url_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(QLabel("URL cím"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://wellcosta.dev")
        layout.addWidget(self.url_input)
        layout.addStretch()
        return w

    def _build_text_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(QLabel("Szöveg"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Írja be a szöveget...")
        layout.addWidget(self.text_input)
        return w

    def _build_vcard_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        fields = [
            ("Teljes név", "vcard_name", "Kostyál Árpád"),
            ("Szervezet", "vcard_org", "Wellcosta"),
            ("Telefon", "vcard_phone", "+36 30 123 4567"),
            ("Email", "vcard_email", "arpi@wellcosta.dev"),
            ("Weboldal", "vcard_url", "https://wellcosta.dev"),
            ("Cím", "vcard_address", "Nyíregyháza, Magyarország"),
        ]

        for label, attr, placeholder in fields:
            layout.addWidget(QLabel(label))
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            setattr(self, attr, field)
            layout.addWidget(field)

        layout.addStretch()
        return w

    def _build_wifi_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Hálózat neve (SSID)"))
        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setPlaceholderText("OtthoniWifi")
        layout.addWidget(self.wifi_ssid)

        layout.addWidget(QLabel("Jelszó"))
        self.wifi_password = QLineEdit()
        self.wifi_password.setPlaceholderText("jelszó")
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.wifi_password)

        show_pw = QCheckBox("Jelszó megjelenítése")
        show_pw.toggled.connect(lambda checked: self.wifi_password.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        ))
        layout.addWidget(show_pw)

        layout.addWidget(QLabel("Titkosítás"))
        self.wifi_security = QComboBox()
        self.wifi_security.addItems(["WPA", "WEP", "Nincs"])
        self.wifi_security.setCurrentText(self.cfg.get("last_wifi_security", "WPA"))
        layout.addWidget(self.wifi_security)

        layout.addStretch()
        return w

    # ── Logika ───────────────────────────────────────────────────────────────

    def _build_qr_data(self):
        tab = self.tabs.currentIndex()

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
            self.status.showMessage(f"⚠ {e}")
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

            # PIL image → QPixmap
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            raw = buffer.getvalue()

            pixmap = QPixmap()
            pixmap.loadFromData(raw)

            self.current_qr_image = img
            self.preview_label.setText("")
            self.preview_label.setPixmap(
                pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
            self.btn_save.setEnabled(True)
            self.status.showMessage("✓ QR kód generálva")
            self._save_state()

        except Exception as e:
            self.status.showMessage(f"✗ Hiba: {e}")
            QMessageBox.critical(self, "Hiba", str(e))

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
            self.status.showMessage(f"✓ Mentve: {path}")

        except Exception as e:
            self.status.showMessage(f"✗ Mentési hiba: {e}")
            QMessageBox.critical(self, "Mentési hiba", str(e))

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
            f"QPushButton {{ background-color: {hex_color}; border-radius: 6px; "
            f"border: 1px solid #2a2a35; min-width: 36px; min-height: 36px; "
            f"max-width: 36px; max-height: 36px; }}"
        )

    def _on_tab_changed(self, index):
        self.cfg["last_tab"] = index

    def _restore_state(self):
        self.tabs.setCurrentIndex(self.cfg.get("last_tab", 0))
        self.url_input.setText(self.cfg.get("last_url", ""))
        self.text_input.setPlainText(self.cfg.get("last_text", ""))
        self.wifi_ssid.setText(self.cfg.get("last_wifi_ssid", ""))
        self.wifi_security.setCurrentText(self.cfg.get("last_wifi_security", "WPA"))

    def _save_state(self):
        self.cfg.update({
            "last_tab": self.tabs.currentIndex(),
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

    def closeEvent(self, event):
        self._save_state()
        super().closeEvent(event)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("QR Generator")
    app.setOrganizationName("wellcosta-dev")
    window = QRGenerator()
    window.show()
    sys.exit(app.exec())