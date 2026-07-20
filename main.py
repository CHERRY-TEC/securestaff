from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Job, Assignment

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    workers = User.query.filter_by(role='worker').all()
    companies = User.query.filter_by(role='company').all()
    jobs = Job.query.all()
    assignments = Assignment.query.all()
    return render_template('admin_dashboard.html', workers=workers,
                           companies=companies, jobs=jobs, assignments=assignments)


@main.route('/admin/assign', methods=['POST'])
@login_required
def assign_job():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    job_id = request.form['job_id']
    worker_id = request.form['worker_id']
    existing = Assignment.query.filter_by(job_id=job_id, worker_id=worker_id).first()
    if not existing:
        a = Assignment(job_id=job_id, worker_id=worker_id, status='pending')
        db.session.add(a)
        db.session.commit()
        flash('Worker assigned to job')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/company')
@login_required
def company_dashboard():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    jobs = Job.query.filter_by(company_id=current_user.id).all()
    return render_template('company_dashboard.html', jobs=jobs)


@main.route('/company/post', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'company':
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        job = Job(title=request.form['title'],
                  location=request.form.get('location', ''),
                  description=request.form.get('description', ''),
                  company_id=current_user.id, status='open')
        db.session.add(job)
        db.session.commit()
        flash('Job posted')
        return redirect(url_for('main.company_dashboard'))
    return render_template('post_job.html')


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
