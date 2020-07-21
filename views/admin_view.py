import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from flasgger.utils import swag_from
from app import app,api
from forms import LoginForm,ActivationForm
from services.services import (check_for_user_in_db, check_otp, insert_to_user_db,
                      otp_gen, send_otp, store_otp,check_for_admin_in_db,check_admin_otp)


class AdminLogin(Resource):

    def get(self):
        return make_response(jsonify({"respone": "get request called for admin login"}), 200)
    
    def post(self):
        print("ddd")
        form=LoginForm(request.form)
        admin_username = form.username.data
        phone = check_for_admin_in_db(admin_username)
        OTP = otp_gen()
        send_otp(phone,OTP)
        store_otp(phone,OTP)
        return make_response(jsonify({"response": "otp send"}),200)

        
    def put(self,phone):
        otp_form = ActivationForm(request.form)
        entered_otp = otp_form.otp.data
        valid_admin = check_admin_otp(entered_otp,phone)
        if valid_admin:
            return make_response(jsonify({"response": "logged in"}),200)
        return make_response(jsonify({"response": "not an admin"}))
    

api.add_resource(AdminLogin, '/admin')