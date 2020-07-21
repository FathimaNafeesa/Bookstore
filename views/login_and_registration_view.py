
from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from flasgger.utils import swag_from
from app import app,api
from forms import ActivationForm, LoginForm, RegisterForm
from services.services import (check_for_user_in_db, check_otp, insert_to_user_db,
                      otp_gen, send_otp, store_otp)

# @bookstore_blueprint.route('/register/', methods=['GET', 'POST'])
# @swag_from('register.yml', methods=['GET'])
# @swag_from('register.yml', methods=['POST'])
class Register(Resource):

    def get(self):
        return make_response(jsonify({"respone": "get request called for register"}), 200)
    
    def post(self):
        form = RegisterForm(request.form)
        user_name = form.username.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        OTP = otp_gen()
        send_otp(phone, OTP)
        store_otp(phone, OTP)
        insert_to_user_db(user_name, email, password, phone)
        return make_response(redirect(url_for('activation')))


api.add_resource(Register, '/')

#@bookstore_blueprint.route('/Activation/', methods=['GET', 'POST'])
#@swag_from('activation.yml', methods=['GET'])
#@swag_from('activation.yml', methods=['POST'])
class Activation(Resource):
    
    def get(self):
        return make_response(jsonify({"response": "otp verification request"}), 200)

    
    def post(self):
        form_1 = ActivationForm()
        entered_otp = form_1.otp.data
        phone = form_1.phone.data
        check_otp(entered_otp, phone)
        return make_response(jsonify({"response": "otp verifiction complete"}), 200)


api.add_resource(Activation, '/activation')

# @bookstore_blueprint.route('/Login/', methods=['GET', 'POST'])
# @swag_from('login.yml', methods=['GET'])
# @swag_from('login.yml', methods=['POST'])
class Login(Resource):
    
    def get(self):
        return make_response(jsonify({"response": "login request"}))

    
    def post(self):
        form = LoginForm(request.form)
        user_name = form.username.data
        password = form.password.data
        present_in_db = check_for_user_in_db(user_name, password)
        if present_in_db:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        return make_response(jsonify({"response": "not a user"}))


api.add_resource(Login, '/login')
