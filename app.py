import os

from flask import Flask, jsonify
from flask_redis import FlaskRedis
from flask_restful import Api

from error_handler_service import InvalidUsageError


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')


@app.errorhandler(InvalidUsageError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from views import *