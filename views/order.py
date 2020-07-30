import os
import uuid

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from services.jwt_extended_services import jwt_verify
from services.mail_service import MailService
from services.message_service_for_order import send_order_confirm_message
from app import app, api
from services.order_services import generate_order_id,find_user_for_order,add_order_details,get_user_and_product_details

class Order(Resource):

    #@jwt_verify
    def post(self):
        user_name = "chachu" #get_jwt_identity()
        address = request.get_json()
        order_id = generate_order_id()
        user_id = find_user_for_order(user_name)
        if add_order_details(order_id,address,user_id):
            details = get_user_and_product_details(user_name)
            MailService.send_mail_with_order_details(details)
            send_order_confirm_message(details)

            return make_response(jsonify({"response":"order placed"}), 200)
        else:
            return  make_response(jsonify({"response":""}), 200)


api.add_resource(Order, '/order')