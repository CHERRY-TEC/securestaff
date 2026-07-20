from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='admin').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.owner_dashboard'))
        flash('Invalid email or password')
    return render_template('owner_login.html')


@auth.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='company').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.client_dashboard'))
        flash('Invalid email or password')
    return render_template('client_login.html')


@auth.route('/client/register', methods=['GET', 'POST'])
def client_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        company_name = request.form.get('company_name', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('client_register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role='company', phone=phone, details=company_name)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.client_login'))
    return render_template('client_register.html')


@auth.route('/owner/register', methods=['GET', 'POST'])
def owner_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('owner_register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role='admin', phone=phone, details='Owner')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.owner_login'))
    return render_template('owner_register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
