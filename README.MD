# wellcosta-dev / qr-generator

> Kostyál Árpád — [wellcosta.dev](https://wellcosta.dev)

QR code generator with a modern dark GUI. Supports URL, text, vCard (contact), and WiFi QR codes. Settings are saved between sessions.

## Features

- **4 QR types** — URL, plain text, vCard (contact card), WiFi credentials
- **Live preview** — see the QR code before saving
- **Custom colors** — set foreground and background color
- **Size & border control** — adjust cell size and quiet zone
- **Export formats** — PNG, JPG, SVG
- **Persistent state** — last used inputs and settings are remembered
- **Dark UI** — consistent with the wellcosta-dev tool suite

## Installation

```bash
pip install -r requirements.txt
python qr_generator.py
```

## Requirements

- Python 3.9+
- PyQt6
- qrcode[pil]
- Pillow

## Config

Settings are saved to `~/.wellcosta/qr_generator.json`

## License

MIT