# 🔐 Умна система за сигурност (Smart Security System)

A Bulgarian-language web application for managing a Raspberry Pi 5 security system — cameras, door locks, PIN codes, fingerprint access and personnel management. The entire UI (all templates, flash messages, navigation, modals, and error pages) is in Bulgarian.

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| Backend    | Python 3.11 · Flask 3.0       |
| Database   | MySQL 8 · Flask-SQLAlchemy    |
| Auth       | Flask-Login · Werkzeug hashes |
| Frontend   | Bootstrap 5.3 · Bootstrap Icons |
| Hardware   | Raspberry Pi 5 · AS608 fingerprint sensor |

---

## Project Structure

```
security_system/
├── __init__.py              # App factory
├── config.py                # Configuration
├── extensions.py            # db, login_manager
├── models.py                # SQLAlchemy models
├── fingerprint_sensor.py    # AS608 sensor wrapper (enroll / delete)
├── keypad.py                # 4×3 matrix keypad GPIO driver
├── keypad_listener.py       # Background thread: keypad → PIN verification
├── run.py                   # Entry point
├── init_db.py               # DB seed script
├── requirements.txt
├── setup_service.sh         # Install app as a systemd boot service
├── security-system.service  # systemd unit template (used by setup_service.sh)
├── routes/
│   ├── auth.py              # Login, signup, reset
│   └── main.py              # Dashboard and all pages
├── static/
│   ├── css/style.css        # Full custom stylesheet
│   └── js/main.js
└── templates/
    ├── base.html            # Sidebar layout
    ├── index.html           # Landing page
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
python3 -m venv venv
source venv/bin/activate
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

Visit `http://localhost:5000` (or your Pi's IP on the network).

---

## Run as a Boot Service (Raspberry Pi)

To have the app start automatically every time the Pi boots, run the setup script once:

```bash
sudo bash setup_service.sh
```

> **Requirement:** The project directory must be named `security_system` on the Pi.  
> If it isn't, rename it first: `mv <current-name> security_system`

The script generates a systemd unit file from `security-system.service`, installs it, and enables it. After that:

```bash
sudo systemctl status  security-system      # check if it's running
sudo systemctl restart security-system      # pick up code changes
sudo systemctl stop    security-system      # stop the service
sudo journalctl -u     security-system -f   # follow live logs
```

---

## Pages Overview

| Route                  | Bulgarian label          | Description                        |
|------------------------|--------------------------|------------------------------------|
| `/`                    | Начална страница         | Landing page                       |
| `/auth/login`          | Вход                     | Login form                         |
| `/auth/signup`         | Регистрация              | Registration form                  |
| `/auth/reset-password` | Нулиране на парола       | Password reset                     |
| `/dashboard`           | Табло                    | System overview with stats & feeds |
| `/cameras`             | Камери                   | Live camera grid                   |
| `/doors`               | Врати                    | Door access control + lock/unlock  |
| `/access-codes`        | Кодове за достъп         | PIN code management + keypad UI    |
| `/fingerprints`        | Отпечатъци               | Fingerprint enrollment management  |
| `/personnel`           | Разрешен персонал        | Allowed persons registry           |
| `/profile`             | Профил                   | User profile & access history      |
| `/settings`            | Настройки                | Account & system settings          |

---

## Fingerprint Sensor (AS608 / R307)

The sensor is integrated via `fingerprint_sensor.py` using the `pyfingerprint` library over UART.

**Wiring (Raspberry Pi 5):**

| Sensor pin | Pi pin           |
|------------|------------------|
| TX         | RXD — GPIO 15 (pin 10) |
| RX         | TXD — GPIO 14 (pin 8)  |
| VCC        | 3.3 V            |
| GND        | GND              |

**Enable UART** in `/boot/firmware/config.txt`:
```
dtoverlay=uart0
```

Then via `raspi-config → Interface Options → Serial Port`:
- Login shell over serial: **No**
- Serial port hardware: **Yes**

Add your user to the `dialout` group and reboot:
```bash
sudo usermod -aG dialout $USER
sudo reboot
```

**How enrollment works:**

1. Open the **Отпечатъци** page and click **Регистриране на отпечатък**.
2. Select a user and assign doors, then click **Започни регистрация**.
3. The server sends two scan requests to the sensor (place finger → lift → place again).
4. On success the template is stored on the sensor and the slot number is saved in the database.

Removing a fingerprint from the web UI deletes the template from the sensor's internal memory as well as the database record.

---

## Matrix Keypad (4×3)

The keypad is integrated via `keypad.py` (GPIO driver) and `keypad_listener.py` (background PIN verification thread). The listener starts automatically with the Flask app.

**Wiring (GPIO.BCM numbering):**

| Keypad pin | GPIO | Pi physical pin |
|------------|------|-----------------|
| Row 0 (1-2-3) | 17 | 11 |
| Row 1 (4-5-6) | 27 | 13 |
| Row 2 (7-8-9) | 22 | 15 |
| Row 3 (*-0-#) | 23 | 16 |
| Col 0 (1-4-7-*) | 24 | 18 |
| Col 1 (2-5-8-0) | 25 | 22 |
| Col 2 (3-6-9-#) |  5 | 29 |

Install `RPi.GPIO` on the Pi (not included in `requirements.txt` because it only installs on Pi hardware):

```bash
pip install RPi.GPIO
```

**How PIN entry works:**

| Key | Action |
|-----|--------|
| `0`–`9` | Append digit to buffer |
| `*` | Clear the buffer (backspace / cancel) |
| `#` | Submit buffer as PIN attempt |

On a correct PIN the app unlocks every door that PIN is assigned to and writes a success `AccessLog` entry. On a wrong PIN only a failed attempt is logged. The same PIN codes managed in the **Кодове за достъп** web page are used — no separate configuration needed.

**Raspberry Pi hardware install note:**

```bash
pip install RPi.GPIO pyfingerprint
```

---

## Hardware Notes

- **Cameras**: Connect via CSI or USB. Integration with `picamera2` or OpenCV for live MJPEG streaming is not yet implemented.

---

## Security Notes

- PINs are stored **hashed** (Werkzeug PBKDF2-SHA256), never in plain text.
- Passwords use the same hash algorithm.
- All protected routes require `@login_required`.
- Sessions use `HttpOnly` + `SameSite=Lax` cookies.
- For production: enable HTTPS (nginx + Let's Encrypt), set `SESSION_COOKIE_SECURE=True`.
