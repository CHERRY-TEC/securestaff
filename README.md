# SecureStaff

A security job **middleman** web app. You (the admin) appoint security workers to jobs posted by companies.

## Roles
- **Admin (you / middleman):** assign workers to company job postings.
- **Company:** register and post security job openings.
- **Worker:** view assignments and accept/decline them.

## Tech Stack
- Python + Flask
- Flask-SQLAlchemy (SQLite database)
- Flask-Login (authentication)

## Setup
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Default Admin Login
- Email: `admin@staff.com`
- Password: `admin123`

Register workers and companies from the homepage.

## How It Works
1. Companies post security jobs.
2. Admin assigns suitable workers to those jobs.
3. Workers accept or decline assignments.

## Project Structure
```
app.py            # Entry point, creates DB + admin user
extensions.py     # Flask / DB / login setup
models.py         # User, Job, Assignment models
auth.py           # Login / register / logout
main.py           # Dashboards + assign/accept logic
templates/        # HTML pages
requirements.txt  # Python dependencies
```
