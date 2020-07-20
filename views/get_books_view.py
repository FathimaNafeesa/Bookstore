import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource

from app import api, app

class Books(Resource):
    def get(self):
        #to sort
        sort_parameter = request.args['sort_parameter']
        if sort_parameter:
            make_response(jsonify({"response": "sort book list called"}), 200)
        else:
            make_response(jsonify({"response": "unsort book list called"}), 200)