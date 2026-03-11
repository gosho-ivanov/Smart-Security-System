from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


# ── User ──────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(40),  default='user')
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)

    # Relationships
    pin_codes    = db.relationship('PinCode',     backref='user', lazy=True, cascade='all, delete-orphan')
    fingerprints = db.relationship('Fingerprint', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.name.split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Door ──────────────────────────────────────────────────
class Door(db.Model):
    __tablename__ = 'doors'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    location     = db.Column(db.String(200))
    is_locked    = db.Column(db.Boolean, default=True)
    method_pin   = db.Column(db.Boolean, default=True)
    method_fp    = db.Column(db.Boolean, default=False)
    last_access  = db.Column(db.DateTime)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    pin_codes    = db.relationship('PinCodeDoor',  backref='door', lazy=True, cascade='all, delete-orphan')
    fp_access    = db.relationship('FingerprintDoor', backref='door', lazy=True, cascade='all, delete-orphan')
    access_logs  = db.relationship('AccessLog', backref='door', lazy=True)

    @property
    def status_text(self):
        return 'Locked' if self.is_locked else 'Unlocked'

    def __repr__(self):
        return f'<Door {self.name}>'


# ── PinCode ───────────────────────────────────────────────
class PinCode(db.Model):
    __tablename__ = 'pin_codes'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pin_hash   = db.Column(db.String(256), nullable=False)   # store hashed PIN
    is_active  = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doors = db.relationship('PinCodeDoor', backref='pin_code', lazy=True, cascade='all, delete-orphan')

    def set_pin(self, raw_pin):
        self.pin_hash = generate_password_hash(str(raw_pin))

    def check_pin(self, raw_pin):
        return check_password_hash(self.pin_hash, str(raw_pin))

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f'<PinCode user_id={self.user_id}>'


# ── PinCodeDoor (many-to-many) ────────────────────────────
class PinCodeDoor(db.Model):
    __tablename__ = 'pin_code_doors'
    pin_code_id = db.Column(db.Integer, db.ForeignKey('pin_codes.id'), primary_key=True)
    door_id     = db.Column(db.Integer, db.ForeignKey('doors.id'),     primary_key=True)


# ── Fingerprint ───────────────────────────────────────────
class Fingerprint(db.Model):
    __tablename__ = 'fingerprints'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_ref = db.Column(db.String(200))   # reference to sensor slot / template file
    is_active    = db.Column(db.Boolean, default=True)
    enrolled_at  = db.Column(db.DateTime, default=datetime.utcnow)

    doors = db.relationship('FingerprintDoor', backref='fingerprint', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Fingerprint user_id={self.user_id}>'


# ── FingerprintDoor (many-to-many) ────────────────────────
class FingerprintDoor(db.Model):
    __tablename__ = 'fingerprint_doors'
    fingerprint_id = db.Column(db.Integer, db.ForeignKey('fingerprints.id'), primary_key=True)
    door_id        = db.Column(db.Integer, db.ForeignKey('doors.id'),        primary_key=True)


# ── AccessLog ─────────────────────────────────────────────
class AccessLog(db.Model):
    __tablename__ = 'access_logs'

    id          = db.Column(db.Integer, primary_key=True)
    door_id     = db.Column(db.Integer, db.ForeignKey('doors.id'))
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    method      = db.Column(db.String(20))     # 'pin', 'fingerprint', 'face'
    success     = db.Column(db.Boolean)
    notes       = db.Column(db.String(300))
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='access_logs')

    def __repr__(self):
        return f'<AccessLog door={self.door_id} success={self.success}>'
