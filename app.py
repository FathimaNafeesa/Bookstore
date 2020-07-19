from flask import Flask,jsonify
from flask_restful import Api
from flask_redis import FlaskRedis

import os
from error_handler_service import InvalidUsageError
app = Flask(__name__)
api=Api(app)

app.config['SECRET_KEY'] = "kdjghodiuthdfpotjkfhdh12jkgkjg"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookstore_db.db"

@app.errorhandler(InvalidUsageError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from views import *