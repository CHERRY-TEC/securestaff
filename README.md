# SecureStaff

A security staffing platform with **two separate websites** connected via API.

## Two Websites

### Company Website (Port 5000)
- Manage security workers
- View client notifications
- Assign workers to jobs
- Add new workers

### Client Website (Port 5001)
- Register and post security job requests
- Track job status
- Landing page with guard profiles

## How They're Connected
- Client registers on client website → Company gets notification with email & phone
- Company assigns workers → Client sees assignment status

## Tech Stack
- Python + Flask (two separate apps)
- Flask-SQLAlchemy (shared SQLite database)
- Flask-Login (authentication)
- CSS Neomorphism (client dashboard)
- CSS Animations (client homepage)

## Setup
```bash
pip install -r requirements.txt
python run_both.py
```

Or run separately:
```bash
# Terminal 1 - Company
python company_app/app.py

# Terminal 2 - Client
python client_app/app.py
```

## URLs
- Company: http://127.0.0.1:5000
- Client: http://127.0.0.1:5001

## Default Login
- Company: `admin@company.com` / `admin123`

## Project Structure
```
security-staffing/
├── company_app/
│   ├── app.py              # Company Flask app (port 5000)
│   └── templates/          # Company HTML pages
├── client_app/
│   ├── app.py              # Client Flask app (port 5001)
│   └── templates/          # Client HTML pages
├── shared.db               # Shared SQLite database
├── run_both.py             # Script to start both apps
└── requirements.txt        # Python dependencies
```

## Features
- **Company:** Dashboard, notifications, worker management, job assignments
- **Client:** Animated homepage, neomorphism dashboard, job posting
- **API Connection:** Client register triggers company notification
