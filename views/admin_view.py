import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from flasgger.utils import swag_from
from app import app,api
from forms import LoginForm,ActivationForm
from services.services import (check_otp, otp_gen, send_otp, store_otp, check_for_admin_in_db,check_admin_otp)
from services.admin_services import add_books,delete_book
from flask_jwt_extended import jwt_required,create_access_token


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

        
    def put(self):
        otp_form = ActivationForm()
        entered_otp = otp_form.otp.data
        phone = otp_form.phone.data
        valid_admin = check_admin_otp(entered_otp,phone)
        if valid_admin:
            access_token = create_access_token(identity=phone)
            return  make_response( jsonify(access_token=access_token),200)
        return make_response(jsonify({"response": "not an admin"}),200)
    

api.add_resource(AdminLogin, '/admin')

class AdminPage(Resource):

    #@jwt_required
    def get(self):
        return make_response(jsonify({"respone": "admin can add and delete books from admin page"}), 200)
    
    #@jwt_required
    def post(self):
        action = request.args['action']
        book_details = request.get_json() 
        if action == 'add':       
            id = book_details['id']
            title = book_details['title']
            author = book_details['author']
            image = book_details['image']
            quantity = book_details['quantity']
            price = book_details['price']
            description = book_details['description']
            status = add_books(id,title,author,image,quantity,price,description)
            if status:
                return make_response(jsonify({"respone": "admin added a book"}), 200)
            return make_response(jsonify({"respone": "action failed"}), 400)
        if action == 'delete':
            id = book_details['id']
            status = delete_book(id)
            if status:
                return make_response(jsonify({"respone": "admin deleted a book"}), 200)
            return make_response(jsonify({"respone": "action failed"}), 400)

api.add_resource(AdminPage, '/adminpage')

