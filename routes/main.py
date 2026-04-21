from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import User, Door, PinCode, PinCodeDoor, Fingerprint, FingerprintDoor, AccessLog
from .. import fingerprint_sensor

main_bp = Blueprint('main', __name__)


# ── Landing ───────────────────────────────────────────────
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


# ── Dashboard ─────────────────────────────────────────────
@main_bp.route('/dashboard')
@login_required
def dashboard():
    cameras       = 4
    doors         = Door.query.all()
    active_pins   = PinCode.query.filter_by(is_active=True).count()
    fingerprints  = Fingerprint.query.filter_by(is_active=True).count()
    recent_logs   = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(10).all()

    return render_template(
        'main/dashboard.html',
        cameras=cameras,
        doors=doors,
        active_pins=active_pins,
        fingerprints=fingerprints,
        recent_logs=recent_logs,
    )


# ── Cameras ───────────────────────────────────────────────
@main_bp.route('/cameras')
@login_required
def cameras():
    return render_template('main/cameras.html')


# ── Doors ─────────────────────────────────────────────────
@main_bp.route('/doors')
@login_required
def doors():
    doors = Door.query.all()
    return render_template('main/doors.html', doors=doors)


@main_bp.route('/doors/add', methods=['POST'])
@login_required
def add_door():
    name       = request.form.get('name', '').strip()
    location   = request.form.get('location', '').strip()
    method_pin = bool(request.form.get('method_pin'))
    method_fp  = bool(request.form.get('method_fp'))

    if not name:
        flash('Наименованието на вратата е задължително.', 'danger')
        return redirect(url_for('main.doors'))

    door = Door(name=name, location=location, method_pin=method_pin, method_fp=method_fp)
    db.session.add(door)
    db.session.commit()
    flash(f'Врата "{name}" е добавена успешно.', 'success')
    return redirect(url_for('main.doors'))


@main_bp.route('/doors/<int:door_id>/toggle', methods=['POST'])
@login_required
def toggle_door(door_id):
    door = Door.query.get_or_404(door_id)
    door.is_locked   = not door.is_locked
    door.last_access = datetime.utcnow()
    db.session.commit()
    status = 'заключена' if door.is_locked else 'отключена'
    flash(f'{door.name} е {status}.', 'success')
    return redirect(url_for('main.doors'))


# ── Access Codes ──────────────────────────────────────────
@main_bp.route('/access-codes')
@login_required
def access_codes():
    pins  = PinCode.query.join(User).order_by(PinCode.created_at.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    doors = Door.query.all()
    return render_template('main/access_codes.html', pins=pins, users=users, doors=doors)


@main_bp.route('/access-codes/add', methods=['POST'])
@login_required
def add_pin():
    raw_pin   = request.form.get('pin_code', '')
    user_id   = request.form.get('user_id')
    door_ids  = request.form.getlist('doors')
    expiry_str = request.form.get('expiry', '')

    if not raw_pin or len(raw_pin) < 4:
        flash('PIN кодът трябва да е поне 4 цифри.', 'danger')
        return redirect(url_for('main.access_codes'))

    expiry = None
    if expiry_str:
        try:
            expiry = datetime.strptime(expiry_str, '%Y-%m-%d')
        except ValueError:
            pass

    pin = PinCode(user_id=user_id, expires_at=expiry)
    pin.set_pin(raw_pin)
    db.session.add(pin)
    db.session.flush()

    for door_id in door_ids:
        db.session.add(PinCodeDoor(pin_code_id=pin.id, door_id=int(door_id)))

    db.session.commit()
    flash('PIN кодът е добавен успешно.', 'success')
    return redirect(url_for('main.access_codes'))


@main_bp.route('/access-codes/<int:pin_id>/toggle', methods=['POST'])
@login_required
def toggle_pin(pin_id):
    pin = PinCode.query.get_or_404(pin_id)
    pin.is_active = not pin.is_active
    db.session.commit()
    status = 'активиран' if pin.is_active else 'деактивиран'
    flash(f'PIN кодът е {status}.', 'success')
    return redirect(url_for('main.access_codes'))


@main_bp.route('/access-codes/<int:pin_id>/edit', methods=['POST'])
@login_required
def edit_pin(pin_id):
    pin = PinCode.query.get_or_404(pin_id)
    raw_pin  = request.form.get('pin_code', '')
    door_ids = request.form.getlist('doors')
    expiry_str = request.form.get('expiry', '')

    if raw_pin:
        pin.set_pin(raw_pin)

    if expiry_str:
        try:
            pin.expires_at = datetime.strptime(expiry_str, '%Y-%m-%d')
        except ValueError:
            pass

    # Update door assignments
    PinCodeDoor.query.filter_by(pin_code_id=pin.id).delete()
    for door_id in door_ids:
        db.session.add(PinCodeDoor(pin_code_id=pin.id, door_id=int(door_id)))

    db.session.commit()
    flash('PIN кодът е актуализиран успешно.', 'success')
    return redirect(url_for('main.access_codes'))


# ── Fingerprints ──────────────────────────────────────────
@main_bp.route('/fingerprints')
@login_required
def fingerprints():
    fps   = Fingerprint.query.join(User).order_by(Fingerprint.enrolled_at.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    doors = Door.query.all()
    return render_template('main/fingerprints.html', fps=fps, users=users, doors=doors)


@main_bp.route('/fingerprints/enroll', methods=['POST'])
@login_required
def enroll_fingerprint():
    user_id  = request.form.get('user_id')
    door_ids = request.form.getlist('doors')

    if not user_id:
        flash('Моля, изберете потребител.', 'danger')
        return redirect(url_for('main.fingerprints'))

    try:
        slot = fingerprint_sensor.enroll()
    except ImportError as e:
        flash(str(e), 'danger')
        return redirect(url_for('main.fingerprints'))
    except RuntimeError as e:
        flash(f'Регистрацията е неуспешна: {e}', 'danger')
        return redirect(url_for('main.fingerprints'))

    fp = Fingerprint(user_id=user_id, template_ref=str(slot))
    db.session.add(fp)
    db.session.flush()

    for door_id in door_ids:
        db.session.add(FingerprintDoor(fingerprint_id=fp.id, door_id=int(door_id)))

    db.session.commit()
    flash('Отпечатъкът е регистриран успешно.', 'success')
    return redirect(url_for('main.fingerprints'))


@main_bp.route('/fingerprints/<int:fp_id>/remove', methods=['POST'])
@login_required
def remove_fingerprint(fp_id):
    fp = Fingerprint.query.get_or_404(fp_id)

    if fp.template_ref:
        try:
            fingerprint_sensor.delete(fp.template_ref)
        except Exception as e:
            flash(f'Предупреждение: отпечатъкът не може да бъде премахнат от сензора ({e}). Записът е изтрит от базата данни.', 'warning')

    db.session.delete(fp)
    db.session.commit()
    flash('Отпечатъкът е премахнат.', 'success')
    return redirect(url_for('main.fingerprints'))


# ── Allowed Personnel ─────────────────────────────────────
@main_bp.route('/personnel')
@login_required
def personnel():
    users = User.query.order_by(User.name).all()
    doors = Door.query.all()
    return render_template('main/personnel.html', users=users, doors=doors)


@main_bp.route('/personnel/add', methods=['POST'])
@login_required
def add_personnel():
    name       = request.form.get('name', '').strip()
    email      = request.form.get('email', '').strip().lower()
    method_pin = bool(request.form.get('method_pin'))
    method_fp  = bool(request.form.get('method_fp'))
    status     = request.form.get('status', 'active') == 'active'

    if not name:
        flash('Името е задължително.', 'danger')
        return redirect(url_for('main.personnel'))

    user = User(
        name=name,
        username=email.split('@')[0] if email else name.lower().replace(' ', ''),
        email=email or f'{name.lower().replace(" ", "")}@local',
        role='user',
        is_active=status,
    )
    user.set_password('ChangeMe123!')
    db.session.add(user)
    db.session.commit()
    flash(f'{name} е добавен/а в разрешения персонал.', 'success')
    return redirect(url_for('main.personnel'))


@main_bp.route('/personnel/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_personnel(user_id):
    if user_id == current_user.id:
        flash('Не можете да премахнете собствения си акаунт от тук.', 'danger')
        return redirect(url_for('main.personnel'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.name} е премахнат/а.', 'success')
    return redirect(url_for('main.personnel'))


# ── Profile ───────────────────────────────────────────────
@main_bp.route('/profile')
@login_required
def profile():
    logs = AccessLog.query.filter_by(user_id=current_user.id)\
                    .order_by(AccessLog.timestamp.desc()).limit(10).all()
    return render_template('main/profile.html', logs=logs)


@main_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    current_user.name     = request.form.get('name', current_user.name).strip()
    current_user.username = request.form.get('username', current_user.username).strip()
    current_user.email    = request.form.get('email', current_user.email).strip()
    db.session.commit()
    flash('Профилът е актуализиран успешно.', 'success')
    return redirect(url_for('main.profile'))


# ── Settings ──────────────────────────────────────────────
@main_bp.route('/settings')
@login_required
def settings():
    return render_template('main/settings.html')


@main_bp.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw  = request.form.get('current_password', '')
    new_pw      = request.form.get('new_password', '')
    confirm_pw  = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        flash('Текущата парола е неправилна.', 'danger')
        return redirect(url_for('main.settings'))

    if new_pw != confirm_pw:
        flash('Новите пароли не съвпадат.', 'danger')
        return redirect(url_for('main.settings'))

    if len(new_pw) < 8:
        flash('Паролата трябва да е поне 8 символа.', 'danger')
        return redirect(url_for('main.settings'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Паролата е актуализирана успешно.', 'success')
    return redirect(url_for('main.settings'))


@main_bp.route('/settings/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    current_user.is_active = False
    db.session.commit()
    from flask_login import logout_user
    logout_user()
    flash('Акаунтът ви е деактивиран.', 'success')
    return redirect(url_for('auth.login'))
