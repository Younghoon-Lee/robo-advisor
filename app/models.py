from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os

dirname = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db = SQLAlchemy()


engine = create_engine('sqlite:///{}'.format(dirname), echo=True)


class User(db.Model):
    __tablenamve__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(128))
    password = db.Column(db.String(128))
