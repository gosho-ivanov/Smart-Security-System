"""
Thin wrapper around PyFingerprint for the AS608/R307 sensor.

UART wiring on Raspberry Pi 5:
  Sensor TX  → Pi RXD  (GPIO 15, pin 10)
  Sensor RX  → Pi TXD  (GPIO 14, pin  8)
  Sensor VCC → 3.3 V or 5 V (check your module label)
  Sensor GND → GND

Enable UART in /boot/firmware/config.txt:
  dtoverlay=uart0

Disable the serial login shell via raspi-config → Interface Options → Serial Port.
Add your user to the dialout group: sudo usermod -aG dialout $USER
"""

import time

UART_PORT  = "/dev/ttyAMA0"
BAUD_RATE  = 57600
_ADDR      = 0xFFFFFFFF
_PASSWORD  = 0x00000000
_TIMEOUT   = 15  # seconds to wait for a finger per scan


def _get_sensor():
    """Return a connected, password-verified PyFingerprint instance."""
    try:
        from pyfingerprint.pyfingerprint import PyFingerprint
    except ImportError:
        raise ImportError(
            "pyfingerprint is not installed. Run: pip install pyfingerprint"
        )

    sensor = PyFingerprint(UART_PORT, BAUD_RATE, _ADDR, _PASSWORD)
    if not sensor.verifyPassword():
        raise RuntimeError("Sensor password verification failed. Check wiring.")
    return sensor


def _wait_for_finger(sensor, timeout=_TIMEOUT):
    """Block until a finger is placed or timeout expires. Raises RuntimeError on timeout."""
    deadline = time.time() + timeout
    while not sensor.readImage():
        if time.time() > deadline:
            raise RuntimeError("Timed out waiting for finger. No finger detected.")
        time.sleep(0.1)


def enroll(timeout=_TIMEOUT):
    """
    Two-scan enrollment sequence.

    Blocks for up to 2 × timeout seconds while waiting for the user's finger.
    Returns the integer sensor slot where the template was stored.
    Raises RuntimeError or ImportError on failure.
    """
    sensor = _get_sensor()

    # First scan
    _wait_for_finger(sensor, timeout)
    sensor.convertImage(0x01)

    # Give the user time to lift their finger
    time.sleep(2)

    # Second scan
    _wait_for_finger(sensor, timeout)
    sensor.convertImage(0x02)

    if sensor.createTemplate() != 0:
        raise RuntimeError(
            "The two fingerprint scans did not match. Please try again."
        )

    slot = sensor.storeTemplate()
    return slot


def delete(slot):
    """
    Delete the template stored at *slot* from the sensor's internal memory.

    Raises RuntimeError or ImportError on failure.
    """
    sensor = _get_sensor()
    if not sensor.deleteTemplate(int(slot)):
        raise RuntimeError(f"Failed to delete template at slot {slot}.")
