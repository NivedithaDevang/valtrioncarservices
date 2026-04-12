from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User

auth = Blueprint('auth', __name__)


def ensure_default_admin():
    admin_email = 'admin@valtrion.com'
    admin_password = 'admin123'
    admin_user = User.query.filter_by(email=admin_email).first()
    password_hash = bcrypt.generate_password_hash(admin_password).decode('utf-8')

    if not admin_user:
        admin_user = User(
            name='Valtrion Admin',
            email=admin_email,
            phone='9876543210',
            password=password_hash,
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        return

    updated = False
    if admin_user.role != 'admin':
        admin_user.role = 'admin'
        updated = True
    if not bcrypt.check_password_hash(admin_user.password, admin_password):
        admin_user.password = password_hash
        updated = True
    if updated:
        db.session.commit()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register'))
        user = User(name=name, email=email, phone=phone, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    ensure_default_admin()
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if email == 'admin@valtrion.com' and password == 'admin123' and (not user or user.role != 'admin' or not bcrypt.check_password_hash(user.password, password)):
            ensure_default_admin()
            user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))