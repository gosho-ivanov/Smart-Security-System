from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import User, Door, PinCode, PinCodeDoor, Fingerprint, FingerprintDoor, AccessLog

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
        flash('Door name is required.', 'danger')
        return redirect(url_for('main.doors'))

    door = Door(name=name, location=location, method_pin=method_pin, method_fp=method_fp)
    db.session.add(door)
    db.session.commit()
    flash(f'Door "{name}" added successfully.', 'success')
    return redirect(url_for('main.doors'))


@main_bp.route('/doors/<int:door_id>/toggle', methods=['POST'])
@login_required
def toggle_door(door_id):
    door = Door.query.get_or_404(door_id)
    door.is_locked   = not door.is_locked
    door.last_access = datetime.utcnow()
    db.session.commit()
    status = 'locked' if door.is_locked else 'unlocked'
    flash(f'{door.name} has been {status}.', 'success')
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
        flash('PIN must be at least 4 digits.', 'danger')
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
    flash('PIN code added successfully.', 'success')
    return redirect(url_for('main.access_codes'))


@main_bp.route('/access-codes/<int:pin_id>/toggle', methods=['POST'])
@login_required
def toggle_pin(pin_id):
    pin = PinCode.query.get_or_404(pin_id)
    pin.is_active = not pin.is_active
    db.session.commit()
    status = 'enabled' if pin.is_active else 'disabled'
    flash(f'PIN code has been {status}.', 'success')
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
    flash('PIN code updated successfully.', 'success')
    return redirect(url_for('main.access_codes'))


# ── Fingerprints ──────────────────────────────────────────
@main_bp.route('/fingerprints')
@login_required
def fingerprints():
    fps   = Fingerprint.query.join(User).order_by(Fingerprint.enrolled_at.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    doors = Door.query.all()
    return render_template('main/fingerprints.html', fps=fps, users=users, doors=doors)


@main_bp.route('/fingerprints/<int:fp_id>/remove', methods=['POST'])
@login_required
def remove_fingerprint(fp_id):
    fp = Fingerprint.query.get_or_404(fp_id)
    db.session.delete(fp)
    db.session.commit()
    flash('Fingerprint removed successfully.', 'success')
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
        flash('Name is required.', 'danger')
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
    flash(f'{name} added to allowed personnel.', 'success')
    return redirect(url_for('main.personnel'))


@main_bp.route('/personnel/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_personnel(user_id):
    if user_id == current_user.id:
        flash('You cannot remove your own account from here.', 'danger')
        return redirect(url_for('main.personnel'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.name} has been removed.', 'success')
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
    flash('Profile updated successfully.', 'success')
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
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.settings'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.settings'))

    if len(new_pw) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('main.settings'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('main.settings'))


@main_bp.route('/settings/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    current_user.is_active = False
    db.session.commit()
    from flask_login import logout_user
    logout_user()
    flash('Your account has been deactivated.', 'success')
    return redirect(url_for('auth.login'))
