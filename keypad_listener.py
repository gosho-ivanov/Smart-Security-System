"""
Background thread that reads the matrix keypad and verifies PIN codes.

Key protocol:
  Digits   → buffered (up to MAX_PIN_LENGTH digits)
  *        → clears the current buffer (acts as backspace / cancel)
  #        → submits the buffered digits as a PIN attempt

On a correct PIN every door that PIN is assigned to is unlocked and an
AccessLog entry is recorded. On a wrong PIN only the failed attempt is logged.
"""

import threading
import logging

logger = logging.getLogger(__name__)

MAX_PIN_LENGTH = 10  # safety cap so the buffer can't grow unbounded


def start(app):
    """Launch the keypad listener as a daemon thread with a Flask app context."""
    thread = threading.Thread(
        target=_run,
        args=(app,),
        daemon=True,
        name='keypad-listener',
    )
    thread.start()
    logger.info("Keypad listener thread started.")


def _run(app):
    try:
        from . import keypad
    except ImportError:
        logger.warning(
            "RPi.GPIO is not installed — keypad listener will not start. "
            "Install it on the Raspberry Pi with: pip install RPi.GPIO"
        )
        return

    buffer = []

    def handle_key(key):
        if key == '*':
            buffer.clear()
            logger.debug("Keypad buffer cleared.")
        elif key == '#':
            pin = ''.join(buffer)
            buffer.clear()
            if pin:
                with app.app_context():
                    _verify_and_log(pin)
        else:
            if len(buffer) < MAX_PIN_LENGTH:
                buffer.append(key)
                logger.debug("Keypad buffer: %d digit(s).", len(buffer))

    try:
        keypad.listen(handle_key)
    except ImportError:
        logger.warning("RPi.GPIO is not installed — keypad listener stopped.")
        return


def _verify_and_log(raw_pin):
    """Check raw_pin against all active PINs and update doors + access log."""
    from datetime import datetime
    from .models import PinCode, AccessLog
    from .extensions import db

    matched_pin = None
    for pin in PinCode.query.filter_by(is_active=True).all():
        if not pin.is_expired and pin.check_pin(raw_pin):
            matched_pin = pin
            break

    if matched_pin:
        for link in matched_pin.doors:
            door = link.door
            door.is_locked = False
            door.last_access = datetime.utcnow()
            db.session.add(AccessLog(
                door_id=door.id,
                user_id=matched_pin.user_id,
                method='pin',
                success=True,
                notes='Physical keypad',
            ))
            logger.info("PIN accepted — unlocked '%s' for user_id=%s.", door.name, matched_pin.user_id)
    else:
        db.session.add(AccessLog(
            method='pin',
            success=False,
            notes='Physical keypad — wrong PIN',
        ))
        logger.warning("Keypad: wrong PIN entered.")

    db.session.commit()
