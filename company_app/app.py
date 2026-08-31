from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'company-secret-key'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, '..', 'shared.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(30))
    company_name = db.Column(db.String(120))


class Worker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30))
    skills = db.Column(db.Text)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    client_email = db.Column(db.String(120))
    client_phone = db.Column(db.String(30))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='company').first()
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
        company_name = request.form.get('company_name', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    role='company', phone=phone, company_name=company_name)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    workers = Worker.query.all()
    jobs = Job.query.all()
    assignments = Assignment.query.all()
    unread = Notification.query.filter_by(is_read=False).count()
    return render_template('dashboard.html', notifications=notifications,
                           workers=workers, jobs=jobs, assignments=assignments, unread=unread)


@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)


@app.route('/clients')
@login_required
def clients():
    client_notifs = Notification.query.filter_by(title='New Client Registered').order_by(Notification.created_at.desc()).all()
    return render_template('clients.html', notifications=client_notifs)


@app.route('/workers')
@login_required
def workers_list():
    workers = Worker.query.all()
    return render_template('workers.html', workers=workers)


@app.route('/add-worker', methods=['GET', 'POST'])
@login_required
def add_worker():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        skills = request.form.get('skills', '')
        if Worker.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('add_worker.html')
        w = Worker(name=name, email=email,
                   password=generate_password_hash(password),
                   phone=phone, skills=skills)
        db.session.add(w)
        db.session.commit()
        flash('Worker added')
        return redirect(url_for('workers_list'))
    return render_template('add_worker.html')


@app.route('/jobs')
@login_required
def jobs_list():
    jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)


@app.route('/assign', methods=['POST'])
@login_required
def assign():
    job_id = request.form['job_id']
    worker_id = request.form['worker_id']
    existing = Assignment.query.filter_by(job_id=job_id, worker_id=worker_id).first()
    if not existing:
        a = Assignment(job_id=job_id, worker_id=worker_id, status='pending')
        db.session.add(a)
        db.session.commit()
        flash('Worker assigned to job')
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/api/new-client', methods=['POST'])
def api_new_client():
    data = request.get_json()
    email = data.get('email', '')
    phone = data.get('phone', '')
    notif = Notification(title='New Client Registered',
                         message=f'Contact: {email} | Phone: {phone}')
    db.session.add(notif)
    db.session.commit()
    return {'status': 'ok'}


with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@company.com').first():
        admin = User(name='Admin', email='admin@company.com',
                     password=generate_password_hash('admin123'),
                     role='company', company_name='SecureGuard Services')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
