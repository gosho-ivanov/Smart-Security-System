# 🔐 Smart Security System

A clean corporate web application for managing a Raspberry Pi 5 security system — cameras, door locks, PIN codes, fingerprint access and personnel management.

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| Backend    | Python 3.11 · Flask 3.0       |
| Database   | MySQL 8 · Flask-SQLAlchemy    |
| Auth       | Flask-Login · Werkzeug hashes |
| Frontend   | Bootstrap 5.3 · Bootstrap Icons |
| Hardware   | Raspberry Pi 5                |

---

## Project Structure

```
security_system/
├── __init__.py          # App factory
├── config.py            # Configuration
├── extensions.py        # db, login_manager
├── models.py            # SQLAlchemy models
├── run.py               # Entry point
├── init_db.py           # DB seed script
├── requirements.txt
├── routes/
│   ├── auth.py          # Login, signup, reset
│   └── main.py          # Dashboard and all pages
├── static/
│   ├── css/style.css    # Full custom stylesheet
│   └── js/main.js
└── templates/
    ├── base.html         # Sidebar layout
    ├── index.html        # Landing page
    ├── auth/
    │   ├── login.html
    │   ├── signup.html
    │   └── reset_password.html
    ├── main/
    │   ├── dashboard.html
    │   ├── cameras.html
    │   ├── doors.html
    │   ├── access_codes.html
    │   ├── fingerprints.html
    │   ├── personnel.html
    │   ├── profile.html
    │   └── settings.html
    └── error/
        └── 403.html
```

---

## Setup

### 1. MySQL Database

```sql
CREATE DATABASE security_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'secuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON security_system.* TO 'secuser'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

Edit `config.py` or set environment variables:

```bash
export SECRET_KEY="your-very-secret-key"
export DATABASE_URL="mysql+pymysql://secuser:yourpassword@localhost/security_system"
```

### 4. Init Database

```bash
python init_db.py
```

Default admin login:
- **Email:** `admin@example.com`
- **Password:** `Admin1234!`

### 5. Run

```bash
python run.py
```

Visit `http://localhost:5000` (or use your Pi's IP on the network).

---

## Pages Overview

| Route                | Description                          |
|----------------------|--------------------------------------|
| `/`                  | Landing page                         |
| `/auth/login`        | Login form                           |
| `/auth/signup`       | Registration form                    |
| `/auth/reset-password` | Password reset                     |
| `/dashboard`         | System overview with stats & feeds   |
| `/cameras`           | Live camera grid                     |
| `/doors`             | Door access control + lock/unlock    |
| `/access-codes`      | PIN code management + keypad UI      |
| `/fingerprints`      | Fingerprint enrollment management    |
| `/personnel`         | Allowed persons registry             |
| `/profile`           | User profile & access history        |
| `/settings`          | Account & system settings            |

---

## Hardware Notes

- **Fingerprint sensor** (AS608 / R307): Connect via UART to `/dev/ttyUSB0`. Enrollment routes are stubbed — integrate with `pyfingerprint` library.
- **Cameras**: Connect via CSI or USB. Integrate with `picamera2` or OpenCV for live MJPEG streaming.
- **Matrix Keypad (4×3)**: Wire to GPIO pins and use `RPi.GPIO` to read key presses. The PIN pad UI mirrors the physical keypad layout.

---

## Security Notes

- PINs are stored **hashed** (Werkzeug PBKDF2-SHA256), never in plain text.
- Passwords use the same hash algorithm.
- All protected routes require `@login_required`.
- Sessions use `HttpOnly` + `SameSite=Lax` cookies.
- For production: enable HTTPS (nginx + Let's Encrypt), set `SESSION_COOKIE_SECURE=True`.
