from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User

auth = Blueprint('auth', __name__)

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
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
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