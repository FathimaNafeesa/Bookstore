import os
import random as r

import redis
from flask import jsonify, make_response
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client
from werkzeug.security import check_password_hash, generate_password_hash

from error_handler_service import InvalidUsageError
from model import User, db

redis_db = redis.Redis(host='localhost', port=6379, db=0)

# function for otp generation


def otp_gen():
    otp = ""
    for i in range(4):
        otp += str(r.randint(1, 9))
    return otp


def send_otp(phone, otp):
    account_sid = os.getenv('account_sid')
    auth_token = os.getenv('auth_token')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=phone,
        from_=os.getenv('from_phone_number'),
        body=otp)

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
    redis_db.set(phone, otp.encode('utf-8'))
    redis_db.expire(phone, 1800)


def check_otp(entered_otp, phone):
    otp = redis_db.get(phone).decode('utf-8')
    user = User.query.filter_by(phone=phone).first()
    if otp == entered_otp:
        user.is_verified = 1
        db.session.commit()
    else:
        return make_response(jsonify({'response': "Invalid otp"}), 400)


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
