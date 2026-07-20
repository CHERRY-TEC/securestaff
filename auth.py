from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            if user.role == 'company':
                return redirect(url_for('main.company_dashboard'))
            return redirect(url_for('main.worker_dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'worker')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        details = request.form.get('details', '')
        role = request.form['role']
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html', role=role)
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role=role, phone=phone, details=details)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', role=role)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
