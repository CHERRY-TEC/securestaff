from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Notification
from email_service import send_email

auth = Blueprint('auth', __name__)

COMPANY_EMAIL = 'company@securestaff.com'


@auth.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='company').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.company_dashboard'))
        flash('Invalid email or password')
    return render_template('company_login.html')


@auth.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        company_name = request.form.get('company_name', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('company_register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role='company', phone=phone, company_name=company_name)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.company_login'))
    return render_template('company_register.html')


@auth.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='client').first()
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
        address = request.form.get('address', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('client_register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role='client', phone=phone, address=address)
        db.session.add(user)
        db.session.commit()

        notif = Notification(
            title='New Client Registered',
            message=f'{name} ({email}) has registered. Phone: {phone}. Address: {address}'
        )
        db.session.add(notif)
        db.session.commit()

        send_email(COMPANY_EMAIL, 'New Client Registration',
                   f'New client registered:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}')

        flash('Registration successful. Please login.')
        return redirect(url_for('auth.client_login'))
    return render_template('client_register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
