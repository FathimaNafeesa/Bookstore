import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from flasgger.utils import swag_from
from app import app,api
from forms import LoginForm,ActivationForm
from services.services import (check_otp, otp_gen, send_otp, store_otp, check_for_admin_in_db,check_admin_otp)
from services.admin_services import add_books
from flask_jwt_extended import jwt_required


class AdminLogin(Resource):

    def get(self):
        return make_response(jsonify({"respone": "get request called for admin login"}), 200)
    
    def post(self):
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
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        return make_response(jsonify({"response": "not an admin"}))
    

api.add_resource(AdminLogin, '/admin')

class AdminPage(Resource):

    @jwt_required
    def get(self):
        return make_response(jsonify({"respone": "admin can add and delete books from admin page"}), 200)
    
    @jwt_required
    def post(self):
        book_details = request.get_json()
        id = book_details.get['id']
        title = book_details.get['title']
        author = book_details.get['author']
        image = book_details.get['image']
        quantity = book_details.get['quantity']
        price = book_details.get['price']
        description = book_details.get['description']
        status = add_book(id,title,author,image,quantity,price,description)

