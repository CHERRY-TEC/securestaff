from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Job, Assignment, Notification

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/company-home')
def company_home():
    return render_template('company_home.html')


@main.route('/client-home')
def client_home():
    return render_template('client_home.html')


# ── Company Routes ──

@main.route('/company')
@login_required
def company_dashboard():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    workers = User.query.filter_by(role='worker').all()
    clients = User.query.filter_by(role='client').all()
    jobs = Job.query.all()
    assignments = Assignment.query.all()
    unread = Notification.query.filter_by(is_read=False).count()
    return render_template('company_dashboard.html', notifications=notifications,
                           workers=workers, clients=clients, jobs=jobs,
                           assignments=assignments, unread=unread)


@main.route('/company/notifications')
@login_required
def company_notifications():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('company_notifications.html', notifications=notifications)


@main.route('/company/clients')
@login_required
def company_clients():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    clients = User.query.filter_by(role='client').all()
    return render_template('company_clients.html', clients=clients)


@main.route('/company/workers')
@login_required
def company_workers():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    workers = User.query.filter_by(role='worker').all()
    return render_template('company_workers.html', workers=workers)


@main.route('/company/assign', methods=['POST'])
@login_required
def company_assign():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    job_id = request.form['job_id']
    worker_id = request.form['worker_id']
    existing = Assignment.query.filter_by(job_id=job_id, worker_id=worker_id).first()
    if not existing:
        a = Assignment(job_id=job_id, worker_id=worker_id, status='pending')
        db.session.add(a)
        db.session.commit()
        flash('Worker assigned to job')
    return redirect(url_for('main.company_dashboard'))


@main.route('/company/jobs')
@login_required
def company_jobs():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    jobs = Job.query.all()
    return render_template('company_jobs.html', jobs=jobs)


# ── Client Routes ──

@main.route('/client')
@login_required
def client_dashboard():
    if current_user.role != 'client':
        return redirect(url_for('main.index'))
    jobs = Job.query.filter_by(client_id=current_user.id).all()
    return render_template('client_dashboard.html', jobs=jobs)


@main.route('/client/post', methods=['GET', 'POST'])
@login_required
def client_post_job():
    if current_user.role != 'client':
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        job = Job(title=request.form['title'],
                  location=request.form.get('location', ''),
                  description=request.form.get('description', ''),
                  client_id=current_user.id, status='pending')
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully')
        return redirect(url_for('main.client_dashboard'))
    return render_template('client_post_job.html')


# ── Worker Routes ──

@main.route('/worker')
@login_required
def worker_dashboard():
    if current_user.role != 'worker':
        return redirect(url_for('main.index'))
    assignments = Assignment.query.filter_by(worker_id=current_user.id).all()
    return render_template('worker_dashboard.html', assignments=assignments)


@main.route('/worker/respond/<int:assignment_id>/<action>')
@login_required
def respond_assignment(assignment_id, action):
    if current_user.role != 'worker':
        return redirect(url_for('main.index'))
    a = Assignment.query.get_or_404(assignment_id)
    if a.worker_id != current_user.id:
        return redirect(url_for('main.index'))
    a.status = 'accepted' if action == 'accept' else 'declined'
    if a.status == 'accepted':
        a.job.status = 'assigned'
    db.session.commit()
    flash('Response recorded')
    return redirect(url_for('main.worker_dashboard'))
