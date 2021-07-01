from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablenamve__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(128))
    password = db.Column(db.String(128))
