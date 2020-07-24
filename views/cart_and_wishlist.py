import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from app import app,api
from flask_jwt_extended import jwt_required,create_access_token,get_jwt_identity
from marshmallow import Schema
from model import product_data_schema,user_schema
from services.login_services import display_wishlist,add_books_to_wishlist,delete_book_from_cart
from services.services import calling_book_details


class WishList(Resource):

    @jwt_required
    def get(self):
        username = get_jwt_identity()
        wishlist = display_wishlist(username,wishlist)
        return make_response(jsonify({"Wishlist": wishlist }), 200)
        
    @jwt_required
    def post(self):
        username = get_jwt_identity()
        action = request.args['action']
        product = request.get_json()
        product_id = product['id']
        if action == "add":
            status = add_books_to_wishlist(product_id,username)
        if status:        
            return make_response(jsonify({"Wishlist": action }), 200)
        else:
            return make_response(jsonify({"response" : "action failed"}), 200)


api.add_resource(WishList,'/wishlist')

class Cart(Resource):

    @jwt_required
    def get(self):
        username = get_jwt_identity()
        cart = display_cart(username)
        return make_response(jsonify({"cart": cart }), 200)

            
    @jwt_required
    def post(self):
        username = get_jwt_identity()
        action = request.args['action']
        product = request.get_json()
        product_id = product['id']
        if action == "add":
            status = add_books_to_cart(product_id,username)
        if action == "delete":
            status = delete_book_from_cart(product_id,username)
        if status:        
            return make_response(jsonify({"cart": action }), 200)
        else:
            return make_response(jsonify({"response" : "action failed"}), 200)
    

api.add_resource(Cart,'/cart')

    
