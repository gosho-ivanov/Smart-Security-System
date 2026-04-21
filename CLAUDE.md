# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Bulgarian-language Flask web application for managing a Raspberry Pi 5 security system — cameras, door locks, PIN codes, fingerprint access, and personnel management. The entire UI is in Bulgarian.

## Setup & Running

All commands run from the project root (the directory containing `run.py`).

```bash
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
python init_db.py   # create tables + seed sample data (run once)
python run.py       # → http://localhost:5000
```

Default admin login: `admin@example.com` / `Admin1234!`

There is **no test suite, no linting configuration, and no migration system**. Schema changes require dropping and recreating tables via `init_db.py`.

Pi-only packages (`RPi.GPIO`, `pyfingerprint`) are commented out in `requirements.txt` — install them manually on the Pi only.

## Architecture

**App factory pattern** — `__init__.py` exports `create_app()`, which initializes extensions, registers blueprints, and starts the keypad listener thread.

**Two blueprints:**
- `auth_bp` (`routes/auth.py`) — prefix `/auth`: login, signup, logout, forgot/reset password
- `main_bp` (`routes/main.py`) — no prefix: all protected pages behind `@login_required`

**Extensions** (`extensions.py`) — `db` (SQLAlchemy) and `login_manager` (Flask-Login) are instantiated here and imported everywhere else. Never import them from `__init__.py` — that causes circular imports.

**Models** (`models.py`) — seven models:
- `User` — `role` is `'administrator'` or `'user'`; **role is not enforced in any route**
- `Door` — `method_pin` and `method_fp` booleans control which access methods are active per door
- `PinCode` — PIN stored as Werkzeug PBKDF2-SHA256 hash; `expires_at` nullable; `is_expired` property; linked to doors via `PinCodeDoor` join table
- `Fingerprint` — `template_ref` holds the AS608 sensor slot number (as a string); linked to doors via `FingerprintDoor` join table
- `PinCodeDoor`, `FingerprintDoor` — explicit many-to-many join tables
- `AccessLog` — audit trail; `method` is `'pin'`, `'fingerprint'`, or `'face'`

Cascade deletes: User → PinCode and User → Fingerprint.

## Routes

`/auth`: `signup`, `login`, `logout`, `forgot-password` (always returns success — prevents email enumeration), `reset-password` (no token validation — stub).

`main` (all `@login_required`): `dashboard`, `cameras` (UI only — no live stream), `doors` (list + lock/unlock toggle + add), `access-codes` (add/edit/toggle PINs), `fingerprints` (list + enroll via sensor + remove), `personnel` (add/remove users), `profile` (edit + access log), `settings` (change password + deactivate account).

## Hardware Integration

### Fingerprint Sensor (AS608 / R307) — implemented

`fingerprint_sensor.py` wraps `pyfingerprint` over UART (`/dev/ttyAMA0`, 57600 baud).

- `enroll(timeout=15)` — two-scan blocking enrollment; returns the sensor slot integer
- `delete(slot)` — removes template from sensor memory

The `/fingerprints/enroll` route calls `enroll()` synchronously (blocks for up to ~30 s while the user scans). Both `ImportError` (library not installed) and `RuntimeError` (sensor failure) are caught and shown as flash messages without crashing the app.

`remove_fingerprint` deletes from the sensor first, then the DB. If the sensor delete fails (hardware offline) it shows a warning flash and still removes the DB record.

### Matrix Keypad (4×3) — implemented

`keypad.py` — GPIO polling driver (BCM: rows 17/27/22/23, cols 24/25/5).

`keypad_listener.py` — daemon thread started by `create_app()`:
- Digits buffer up to 10 characters
- `*` clears the buffer
- `#` submits: checks against all active, non-expired `PinCode` rows using `check_pin()`; on match unlocks all assigned doors and logs success; on failure logs the attempt
- If `RPi.GPIO` is not installed the thread logs a warning and exits silently

The Werkzeug reloader guard in `__init__.py` prevents the thread from starting twice in debug mode:
```python
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    keypad_listener.start(app)
```

### Cameras — not yet implemented

UI exists; no live stream. Planned: `picamera2` or OpenCV MJPEG.

## Templates & Frontend

All templates are in Bulgarian. All protected pages extend `base.html` (sidebar layout). The active nav item is set by comparing `request.endpoint` in the template. `base.html` uses `current_user.initials`, `current_user.name`, and a role ternary (`'administrator'` → `'Администратор'`) — there are no hardcoded names.

Flash message categories: `'success'`, `'danger'`, `'warning'`, `'info'` (Bootstrap 5.3).

CSS custom properties in `static/css/style.css` (`:root` variables) control all colors and spacing. `static/js/main.js` is minimal — flash dismissal and a notification helper only.

## Boot Service (Raspberry Pi)

```bash
sudo bash setup_service.sh
```

The script fills `security-system.service` template with real paths and installs it as a systemd unit. **Requires the project directory to be named `security_system`** (Python package name must match the `from security_system import create_app` import in `run.py`).
