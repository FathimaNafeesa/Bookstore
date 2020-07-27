from functools import wraps
from flask_jwt_extended import get_jwt_identity,verify_jwt_in_request,get_jwt_claims
from app import jwt
from flask import jsonify


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['roles'] != 'admin':
            return (jsonify({"response": "admins only"}), 200)
        else:
            return fn(*args, **kwargs)
    return wrapper


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    if identity == 'admin':
        return {'roles': 'admin'}
    else:
        return {'roles': 'user'}
