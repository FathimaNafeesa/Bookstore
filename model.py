from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, nullable=False)


class ProductData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    title = db.Column(db.String(300))
    image = db.Column(db.String(300))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    description = db.Column(db.String(6000))
