import threading
import numpy as np

try:
    import face_recognition as fr
    _FR_AVAILABLE = True
except ImportError:
    _FR_AVAILABLE = False

_faces_lock = threading.Lock()
_latest_faces = []  # list of {'name': str, 'box': (top, right, bottom, left), 'recognized': bool}


def get_latest_faces():
    with _faces_lock:
        return list(_latest_faces)


def set_latest_faces(faces):
    with _faces_lock:
        _latest_faces[:] = faces


def encode_face(frame_bgr):
    """
    Return raw bytes of the 128-d encoding for the first face found in frame_bgr.
    Returns None if no face is detected.
    Raises RuntimeError if the library is not installed.
    """
    if not _FR_AVAILABLE:
        raise RuntimeError("Библиотеката face_recognition не е инсталирана")
    rgb = frame_bgr[:, :, ::-1]
    locs = fr.face_locations(rgb, model='hog')
    if not locs:
        return None
    encs = fr.face_encodings(rgb, locs)
    return encs[0].tobytes() if encs else None


def encoding_from_bytes(data):
    return np.frombuffer(data, dtype=np.float64)


def recognize_faces(frame_bgr, known_records):
    """
    Detect and recognize all faces in frame_bgr.

    known_records: list of dicts with keys:
        name, user_id, face_encoding_id, encoding (np.ndarray), door_ids (list[int])

    Returns list of (record_or_None, (top, right, bottom, left)).
    record is None for unrecognized faces.
    """
    if not _FR_AVAILABLE:
        return []
    rgb = frame_bgr[:, :, ::-1]
    small = rgb[::2, ::2]  # 2× downscale — much faster on Pi
    locs = fr.face_locations(small, model='hog')
    if not locs:
        return []
    encs = fr.face_encodings(small, locs)
    known_encs = [r['encoding'] for r in known_records]
    results = []
    for enc, (t, r, b, l) in zip(encs, locs):
        box = (t * 2, r * 2, b * 2, l * 2)
        if known_encs:
            distances = fr.face_distance(known_encs, enc)
            best = int(np.argmin(distances))
            if distances[best] <= 0.5:
                results.append((known_records[best], box))
                continue
        results.append((None, box))
    return results
