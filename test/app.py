from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    body = db.Column(db.Text, nullabe=False)
    pub_date = db.Column(db.Datetime, nullabe=False, default=datetime.utcnow())

    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullabe=False)
    category = db.relationship(
        'Category', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title
