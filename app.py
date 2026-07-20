from extensions import app, db
from flask_login import login_manager
from werkzeug.security import generate_password_hash


def create_admin():
    from models import User
    if not User.query.filter_by(email='admin@staff.com').first():
        admin = User(name='Admin', email='admin@staff.com',
                     password=generate_password_hash('admin123'),
                     role='admin')
        db.session.add(admin)
        db.session.commit()


from auth import auth
from main import main
app.register_blueprint(auth)
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
