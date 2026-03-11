# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based web application for managing a Raspberry Pi 5 security system — cameras, door locks, PIN codes, fingerprint access, and personnel management.

## Setup & Running

All commands run from the `security_system/` directory.

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure credentials via environment variables or edit `config.py` directly:
```bash
export SECRET_KEY="your-very-secret-key"
export DATABASE_URL="mysql+pymysql://secuser:yourpassword@localhost/security_system"
```

MySQL database must exist first:
```sql
CREATE DATABASE security_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
# Initialize DB and seed sample data (run once)
python init_db.py

# Run the development server
python run.py
# → http://localhost:5000
```

Default admin login: `admin@example.com` / `Admin1234!`

## Architecture

**App factory pattern** — `security_system/__init__.py` calls `create_app()`, initializes extensions (`db`, `login_manager`), and registers two blueprints:

- `auth_bp` (`routes/auth.py`) — prefix `/auth`: login, signup, logout, forgot/reset password
- `main_bp` (`routes/main.py`) — no prefix: all protected pages (dashboard, cameras, doors, access codes, fingerprints, personnel, profile, settings)

**Extensions** (`extensions.py`) — `db` (SQLAlchemy) and `login_manager` (Flask-Login) are defined here and imported everywhere to avoid circular imports.

**Models** (`models.py`):
- `User` — has `pin_codes` and `fingerprints` relationships; `role` field (`'administrator'` or `'user'`)
- `Door` — supports two access methods: `method_pin` and `method_fp` flags
- `PinCode` — PIN stored as Werkzeug PBKDF2-SHA256 hash; has optional expiry; linked to doors via `PinCodeDoor` join table
- `Fingerprint` — stores a `template_ref` (sensor slot / file path); linked to doors via `FingerprintDoor` join table
- `AccessLog` — audit trail of door access attempts (method: `'pin'`, `'fingerprint'`, or `'face'`)

**Templates** use Jinja2 with `base.html` providing the sidebar layout. All protected pages extend `base.html`.

## Hardware Integration (Stubbed)

The following hardware integrations are stubbed and need implementation:
- **Fingerprint sensor** (AS608/R307): UART at `/dev/ttyUSB0`, use `pyfingerprint` library
- **Cameras**: CSI or USB, use `picamera2` or OpenCV for MJPEG streaming
- **Matrix Keypad (4×3)**: GPIO pins via `RPi.GPIO`
