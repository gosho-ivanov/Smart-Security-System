from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ── Sign Up ───────────────────────────────────────────────
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name             = request.form.get('name', '').strip()
        username         = request.form.get('username', '').strip().lower()
        email            = request.form.get('email', '').strip().lower()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([name, username, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/signup.html')

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/signup.html')

        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
            return render_template('auth/signup.html')

        user = User(name=name, username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


# ── Log In ────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('This account has been deactivated.', 'danger')
            return render_template('auth/login.html')

        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


# ── Log Out ───────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


# ── Forgot Password ───────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        # Always show success to prevent email enumeration
        flash('If that email is registered, a reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


# ── Reset Password ────────────────────────────────────────
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password     = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html')

        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/reset_password.html')

        # In production: validate token, find user, update password
        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')
