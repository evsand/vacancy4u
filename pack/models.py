from datetime import datetime
from flask_login import UserMixin

from pack import db


class Vacancies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vac_name = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.String(200))
    skills = db.Column(db.PickleType)
    link = db.Column(db.String(200), nullable=False)
    low_rate = db.Column(db.Float)

    def __repr__(self):
        return f'<vacancies  {self.id}>'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    #pr = db.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f'Users {self.email}'



