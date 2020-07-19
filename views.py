from flask_restful import Resource
from flask import make_response,render_template,request,jsonify,redirect,url_for,session
from services import otp_gen,send_otp,insert_to_user_db,store_otp,check_otp,check_for_user_in_db
from flask import make_response
import os
from app import app,api
from forms import ActivationForm,RegisterForm,LoginForm



class Register(Resource):
    def get(self):
        return make_response(jsonify({"respone" : "get request called for register"}),200)

    def post(self):
        form = RegisterForm(request.form)             
        user_name = form.username.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        OTP = otp_gen()
        send_otp(phone,OTP)
        store_otp(phone,OTP)
        insert_to_user_db(user_name,email,password,phone)
        return make_response( redirect(url_for('activation')))
        
        
        
api.add_resource(Register,'/')

class Activation(Resource):
    def get(self):
        return make_response(jsonify({"response": "otp verification request"}),200)
    
    def post(self):
        form_1 = ActivationForm()
        entered_otp = form_1.otp.data
        phone = form_1.phone.data
        check_otp(entered_otp,phone)
        return make_response(jsonify({"response": "otp verifiction complete"}),200)

api.add_resource(Activation,'/activation')

class Login(Resource):

    def get(self):
        return make_response(jsonify({"response": "login request"}))

    def post(self):
        form = LoginForm(request.form)
        user_name = form.username.data
        password = form.password.data
        present_in_db = check_for_user_in_db(user_name,password)
        if present_in_db:
            return  make_response(jsonify({"response": "logged in"}))
        return make_response(jsonify({"response": "not a user"}))

    
api.add_resource(Login,'/login')
        



