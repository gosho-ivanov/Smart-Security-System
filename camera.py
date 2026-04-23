import threading
import time

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False


class _SharedCamera:
    """Single VideoCapture instance read by a daemon thread; multiple consumers share it."""

    def __init__(self, device=0):
        self._device = device
        self._cap = None
        self._frame = None
        self._lock = threading.Lock()
        self._running = False

    def start(self):
        if not _CV2_AVAILABLE:
            return
        self._cap = cv2.VideoCapture(self._device)
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self._running:
            ok, frame = self._cap.read()
            if ok:
                with self._lock:
                    self._frame = frame
            else:
                time.sleep(0.05)

    def get_frame(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def stop(self):
        self._running = False
        if self._cap:
            self._cap.release()


_camera = _SharedCamera()


def start(device=0):
    global _camera
    _camera = _SharedCamera(device)
    _camera.start()


def get_frame():
    return _camera.get_frame()


def generate_frames():
    """Yield MJPEG frames with face detection overlays drawn on top."""
    if not _CV2_AVAILABLE:
        return

    try:
        from . import face_detector as _fd
    except ImportError:
        _fd = None

    while True:
        frame = _camera.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        if _fd is not None:
            for info in _fd.get_latest_faces():
                t, r, b, l = info['box']
                color = (0, 200, 80) if info['recognized'] else (0, 140, 255)
                cv2.rectangle(frame, (l, t), (r, b), color, 2)
                cv2.rectangle(frame, (l, b - 24), (r, b), color, cv2.FILLED)
                cv2.putText(frame, info['name'], (l + 5, b - 7),
                            cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + buf.tobytes()
            + b'\r\n'
        )
