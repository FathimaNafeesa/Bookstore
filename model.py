from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app import app
from marshmallow import Schema, fields, ValidationError, pre_load

db = SQLAlchemy(app)
ma = Marshmallow(app)

relationship_table = db.Table('relationship_table', db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                              db.Column('product_id', db.Integer, db.ForeignKey('product_data.id')))

relationship_table_cart = db.Table('relationship_table_cart', db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                   db.Column('product_id', db.Integer, db.ForeignKey('product_data.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, nullable=False)
    wishlist = db.relationship('ProductData', secondary=relationship_table,
                               backref=db.backref('products', lazy='dynamic'))
    cart = db.relationship('ProductData', secondary=relationship_table_cart,
                           backref=db.backref('products_to_order', lazy='dynamic'))


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
class ProductDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductData
        include_fk = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True


product_data_schema = ProductDataSchema(many=True)
user_schema = UserSchema(many=True)
