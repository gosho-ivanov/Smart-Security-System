from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ── Регистрация ───────────────────────────────────────────
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

        if not all([name, username, email, password]):
            flash('Всички полета са задължителни.', 'danger')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash('Паролите не съвпадат.', 'danger')
            return render_template('auth/signup.html')

        if len(password) < 8:
            flash('Паролата трябва да е поне 8 символа.', 'danger')
            return render_template('auth/signup.html')

        if User.query.filter_by(email=email).first():
            flash('Вече съществува акаунт с този имейл.', 'danger')
            return render_template('auth/signup.html')

        if User.query.filter_by(username=username).first():
            flash('Това потребителско име вече е заето.', 'danger')
            return render_template('auth/signup.html')

        user = User(name=name, username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Акаунтът е създаден! Можете да влезете.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


# ── Вход ──────────────────────────────────────────────────
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
            flash('Невалиден имейл или парола.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Този акаунт е деактивиран.', 'danger')
            return render_template('auth/login.html')

        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


# ── Изход ─────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Излязохте от системата.', 'success')
    return redirect(url_for('auth.login'))


# ── Забравена парола ──────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        # Винаги показваме успех, за да предотвратим изброяване на имейли
        flash('Ако имейлът е регистриран, ще получите линк за нулиране.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


# ── Нулиране на парола ────────────────────────────────────
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password     = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if new_password != confirm_password:
            flash('Паролите не съвпадат.', 'danger')
            return render_template('auth/reset_password.html')

        if len(new_password) < 8:
            flash('Паролата трябва да е поне 8 символа.', 'danger')
            return render_template('auth/reset_password.html')

        # В продукция: валидирайте токен, намерете потребител, актуализирайте паролата
        flash('Паролата е актуализирана успешно. Моля, влезте.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')
