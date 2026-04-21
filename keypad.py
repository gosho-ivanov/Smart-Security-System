"""
4×3 matrix keypad driver for Raspberry Pi 5.
Uses GPIO.BCM numbering.

Wiring:
  Row 0  (keys 1-2-3)   → GPIO 17
  Row 1  (keys 4-5-6)   → GPIO 27
  Row 2  (keys 7-8-9)   → GPIO 22
  Row 3  (keys *-0-#)   → GPIO 23
  Col 0  (keys 1-4-7-*) → GPIO 24
  Col 1  (keys 2-5-8-0) → GPIO 25
  Col 2  (keys 3-6-9-#) → GPIO  5
"""

import time

ROWS = [17, 27, 22, 23]
COLS = [24, 25, 5]
KEYS = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#'],
]

_DEBOUNCE     = 0.3   # seconds to wait after a key press before scanning again
_POLL_INTERVAL = 0.01  # seconds between full matrix scans


def listen(callback):
    """
    Blocking poll loop. Calls callback(key: str) for every detected key press.

    Cleans up GPIO on exit (KeyboardInterrupt or any other exception).
    Raises ImportError if RPi.GPIO is not installed.
    """
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)

    for r in ROWS:
        GPIO.setup(r, GPIO.OUT)
        GPIO.output(r, GPIO.HIGH)

    for c in COLS:
        GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    try:
        while True:
            for i, r in enumerate(ROWS):
                GPIO.output(r, GPIO.LOW)
                for j, c in enumerate(COLS):
                    if GPIO.input(c) == 0:
                        callback(KEYS[i][j])
                        time.sleep(_DEBOUNCE)
                GPIO.output(r, GPIO.HIGH)
            time.sleep(_POLL_INTERVAL)
    finally:
        GPIO.cleanup()
