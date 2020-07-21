from dotenv import load_dotenv
load_dotenv(verbose=True)
import os

from flask import Flask, jsonify,Blueprint
from flask_redis import FlaskRedis
from flask_restful import Api
from flasgger import Swagger
from flasgger.utils import swag_from
from services.error_handler_service import InvalidUsageError
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)






app = Flask(__name__)
#frombookstore_blueprint = Blueprint("bookstore_blueprint", __name__)

api = Api(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')


@app.errorhandler(InvalidUsageError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from views.login_and_registration_view import *
from views.get_books_view import *
from views.admin_view import *