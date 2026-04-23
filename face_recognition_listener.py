import logging
import threading
import time

log = logging.getLogger(__name__)

_RECOGNITION_INTERVAL = 1.0   # seconds between recognition passes
_UNLOCK_COOLDOWN      = 15.0  # seconds before the same user can unlock again

_last_unlock = {}   # user_id → float timestamp
_lock = threading.Lock()


def _load_known_records(app):
    from .models import FaceEncoding
    from . import face_detector
    with app.app_context():
        records = FaceEncoding.query.filter_by(is_active=True).all()
        return [
            {
                'name':             r.user.name if r.user else r.label,
                'user_id':          r.user_id,
                'face_encoding_id': r.id,
                'encoding':         face_detector.encoding_from_bytes(r.encoding),
                'door_ids':         [fd.door_id for fd in r.doors],
            }
            for r in records
        ]


def _run(app):
    from . import camera, face_detector
    from .models import Door, AccessLog
    from .extensions import db

    log.info("Слушателят за разпознаване на лица стартира")

    while True:
        time.sleep(_RECOGNITION_INTERVAL)

        frame = camera.get_frame()
        if frame is None:
            continue

        try:
            known = _load_known_records(app)
            results = face_detector.recognize_faces(frame, known)

            # Update overlay state
            overlay = []
            for record, box in results:
                overlay.append({
                    'name':       record['name'] if record else 'Непознат',
                    'box':        box,
                    'recognized': record is not None,
                })
            face_detector.set_latest_faces(overlay)

            if not results:
                continue

            now = time.time()
            with app.app_context():
                changed = False
                for record, _box in results:
                    if record is None:
                        continue
                    uid = record['user_id']
                    with _lock:
                        if now - _last_unlock.get(uid, 0) < _UNLOCK_COOLDOWN:
                            continue
                        _last_unlock[uid] = now

                    for door_id in record['door_ids']:
                        door = Door.query.get(door_id)
                        if door is None or not door.method_face:
                            continue
                        door.is_locked = False
                        door.last_access = db.func.now()
                        db.session.add(AccessLog(
                            door_id=door_id,
                            user_id=uid,
                            method='face',
                            success=True,
                        ))
                        changed = True
                        log.info("Лице отключи врата %s за потребител %s", door.name, record['name'])

                if changed:
                    db.session.commit()

        except Exception:
            log.exception("Грешка при разпознаване на лица")


def start(app):
    from . import face_detector
    if not face_detector._FR_AVAILABLE:
        log.warning("face_recognition не е инсталиран — разпознаването на лица е изключено")
        return
    threading.Thread(target=_run, args=(app,), daemon=True).start()
