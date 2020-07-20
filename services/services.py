import os
import random as r

import redis
from flask import jsonify, make_response
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client
from werkzeug.security import check_password_hash, generate_password_hash
from services.error_handler_service import InvalidUsageError
from model import User, db, ProductData

redis_db = redis.Redis(host='localhost', port=6379, db=0)

# function for otp generation


def otp_gen():
    try:
        otp = ""
        otp = str(r.randint(1000, 9999))
        return otp
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('sql connection or syntax is improper', 500)

def send_otp(phone, otp):
    try:
        account_sid = os.getenv('account_sid')
        auth_token = os.getenv('auth_token')
        client = Client(account_sid, auth_token)
        message = client.messages.create(
        to=phone,
        from_=os.getenv('from_phone_number'),
        body=otp)
    except Exception:
        return make_response(jsonify({'response': "invalid phone number"}))
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('phone number is improper', 500)


# function for database


def insert_to_user_db(username, email, password, phone):
    try:
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email,
                        password=hashed_password, phone=phone, is_verified=False)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        return make_response(jsonify({'response': "user name or email already exists"}), 400)
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('sql connection or syntax is improper', 500)


def store_otp(phone, otp):
    try:
        redis_db.set(phone, otp.encode('utf-8'))
        redis_db.expire(phone, 1800)
    except Exception:
        raise InvalidUsageError('encoding error,try again', 500)



def check_otp(entered_otp, phone):
    try:
        otp = redis_db.get(phone).decode('utf-8')
        user = User.query.filter_by(phone=phone).first()
        if otp == entered_otp:
            user.is_verified = 1
            db.session.commit()
        else:
            return make_response(jsonify({'response': "Invalid otp or expired otp"}), 400)
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('sql connection or syntax is improper', 500)
    


def check_for_user_in_db(user_name, password):
    try:
        user = User.query.filter_by(username=user_name).first()
        if user:
            if user.is_verified == 1:
                if check_password_hash(user.password, password):
                    return True
            return False
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)

#book sorting
def sort_books(sort_parameter):
    try:
        sorted_books = ProductData.query.order_by(desc(sort_parameter)).all()
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('Not a valid key', 500)

