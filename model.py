from flask_sqlalchemy import SQLAlchemy
from app import app
from marshmallow import Schema, fields, ValidationError, pre_load

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

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    phone = db.Column(db.String(10), unique=True)

# # SCHEMAS


class ProductDataSchema(Schema):
    id = fields.Int(required=True)
    author = fields.Str(required=True)
    title = fields.Str(required=True)
    image = fields.Str(required=True)
    quantity = fields.Int(required=True)
    price = fields.Int(required=True )
    description = fields.Str(required=True)
    
product_data_schema = ProductDataSchema()
#product_data_schema = ProductDataSchema(many=True)