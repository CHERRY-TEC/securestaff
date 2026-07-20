import smtplib
from email.mime.text import MIMEText


def send_email(to_email, subject, body):
    sender = 'securestaff@noreply.com'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    try:
        with smtplib.SMTP('localhost', 587) as server:
            server.starttls()
            server.send_message(msg)
        return True
    except Exception:
        return False
