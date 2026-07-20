from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'client-secret-key'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, '..', 'shared.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

COMPANY_API = 'http://127.0.0.1:5000'


class Client(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    client_email = db.Column(db.String(120))
    client_phone = db.Column(db.String(30))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Client, int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Client.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        if Client.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        user = Client(name=name, email=email,
                      password=generate_password_hash(password),
                      phone=phone, address=address)
        db.session.add(user)
        db.session.commit()

        try:
            requests.post(f'{COMPANY_API}/api/new-client', json={
                'email': email,
                'phone': phone
            }, timeout=3)
        except Exception:
            pass

        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(client_email=current_user.email).all()
    return render_template('dashboard.html', jobs=jobs)


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        job = Job(title=request.form['title'],
                  location=request.form.get('location', ''),
                  description=request.form.get('description', ''),
                  client_email=current_user.email,
                  client_phone=current_user.phone,
                  status='pending')
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully')
        return redirect(url_for('dashboard'))
    return render_template('post_job.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
