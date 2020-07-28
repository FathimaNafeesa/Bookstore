import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from app import app, api
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from marshmallow import Schema
from model import product_data_schema, user_schema
from services.cart_and_wishlist_services import display_wishlist_or_cart, add_or_delete_books
from services.services import calling_book_details
from services.jwt_extended_services import jwt_verify


class WishList(Resource):

    @jwt_verify
    def get(self):
        username = get_jwt_identity()
        wishlist = display_wishlist_or_cart(username, 0)
        return make_response(jsonify({"cart": wishlist}), 200)
        

    @jwt_verify
    def post(self):
        username = get_jwt_identity()
        action = request.args['action']
        product = request.get_json()
        product_id = product['id']
        if action:
            status = add_or_delete_books(product_id, username, action, 0)
        if status:
            return make_response(jsonify({"Wishlist": action,
                                          "status": "completed"}), 200)
        else:
            return make_response(jsonify({"response": "action failed"}), 200)


api.add_resource(WishList, '/wishlist')


class Cart(Resource):

    @jwt_required
    def get(self):
        username =  get_jwt_identity()
        result = display_wishlist_or_cart(username, 1)
        return make_response(jsonify({"cart": result[0],"amount": result[1]}), 200)

    @jwt_required
    def post(self):
        username =  get_jwt_identity()
        action = request.args['action']
        product = request.get_json()
        product_id = product['id']
        product_quantity = int(product['quantity'])
        if action:
            status = add_or_delete_books(product_id, username, action, 1,product_quantity)
        if status:
            return make_response(jsonify({"cart": action}), 200)
        else:
            return make_response(jsonify({"response": "action failed or no action specified"}), 200)


api.add_resource(Cart, '/cart')
