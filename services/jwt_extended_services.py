from functools import wraps
from flask_jwt_extended import get_jwt_identity,verify_jwt_in_request,get_jwt_claims,get_raw_jwt
from app import jwt
from flask import jsonify,make_response
from services.services import redis_db


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['roles'] != 'admin':
            return make_response((jsonify({"response": "admins only"}), 200))
        else:
            return fn(*args, **kwargs)
    return wrapper

def jwt_verify(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jti = get_raw_jwt()['jti']
        entry = redis_db.get(jti).decode('utf-8')
        if entry == "blacklisted":
            return make_response(jsonify({"response": "blacklisted"}), 200)
        else:
            return fn(*args, **kwargs)
    return wrapper


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    if identity == 'admin':
        return {'roles': 'admin'}
    else:
        return {'roles': 'user'}
