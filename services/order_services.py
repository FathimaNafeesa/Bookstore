from sqlalchemy.exc import IntegrityError, OperationalError, InvalidRequestError, CompileError
from model import User, db, ProductData, Admin, product_data_schema,relationship_table_cart,Order
from services.services import calling_book_details
from flask import jsonify, make_response
import random
import string
from services.error_handler_service import InvalidUsageError
import time

def find_user_for_order(username):
    try:
        user = User.query.filter_by(username=username).first()
        user_id = user.id
        return user_id
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)

def generate_order_id():
        order_id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        return order_id

def add_order_details(order_id,address,user_id):
    try:
        order = Order(order_id = order_id,address = address,user = user_id)
        db.session.add(order)
        db.session.commit()
        return True
    except IntegrityError:
        return make_response(jsonify({'response': "user name or email already exists"}), 400)
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('sql connection or syntax is improper', 500)
