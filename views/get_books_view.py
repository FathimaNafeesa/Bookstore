import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequestKeyError

from app import api, app

class Books(Resource):
    def get(self):
        #to sort
        try:
            sort_parameter = request.args['sort_parameter']

            return make_response(jsonify({"response": "sort book list called"}), 200)
        except BadRequestKeyError:
            return make_response(jsonify({"response": "unsort book list called"}), 200)

            

api.add_resource(Books, '/books')