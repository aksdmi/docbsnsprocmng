from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from datetime import datetime
import enum

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed_docs = db.relationship('Document', backref='confirmer', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ConfirmationStatus(enum.Enum):
    undefined = 'Undefined'
    confirmed = 'Confirmed'
    rejected = 'Rejected'


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    idrref = db.Column(db.String(16), unique=True)
    code = db.Column(db.String(50))
    description = db.Column(db.String(150))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sum = db.Column(db.Numeric(10, 2))
    confirmation_status = db.Column(db.Enum(ConfirmationStatus))
    confirmation_date = db.Column(db.DateTime, default=datetime.utcnow)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
