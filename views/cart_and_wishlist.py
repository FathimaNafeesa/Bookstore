import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from app import app,api
from flask_jwt_extended import jwt_required,create_access_token,get_jwt_identity
from marshmallow import Schema
from model import product_data_schema,user_schema
from services.login_services import display_wishlist,add_books_to_wishlist
from services.services import calling_book_details


class WishList(Resource):

    #@jwt_required
    def get(self):
        username = 'chachu'
        #get_jwt_identity()
        wishlist = display_wishlist(username)
        return make_response(jsonify({"Wishlist": wishlist }), 200)
        
    #@jwt_required
    def post(self):
        username = 'chachu'
        #get_jwt_identity
        product = request.get_json()
        product_id = product['id']
        add_books_to_wishlist(product_id,username)
        return make_response(jsonify({"Wishlist": "ok" }), 200)

api.add_resource(WishList,'/wishlist')
        