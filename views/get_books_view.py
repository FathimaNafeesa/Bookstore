import os

from flask import (jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from flask_restful import Resource
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequestKeyError
from services.services import sort_books, calling_book_details, search_books
from flasgger.utils import swag_from
from app import app, api

# @bookstore_blueprint.route('/Books/', methods=['GET', 'POST'])
# @swag_from('books.yml', methods=['GET'])
# @swag_from('books.yml', methods=['POST'])


class Books(Resource):

    def get(self):
        # to sort
        try:
            sort_parameter = request.args['sort_parameter']
            if sort_parameter:
                sorted_list = sort_books(sort_parameter)
                return make_response(jsonify(result=sorted_list))
        except BadRequestKeyError:
            return make_response(jsonify({"response": "unsort book list called"}), 200)

    def post(self):
        try:
            book_form = request.form
            search_parameter = book_form['search_parameter']
            if search_parameter:
                search_result = search_books(search_parameter)
                return make_response(jsonify({"books": search_result}), 200)
        except BadRequestKeyError:
            return make_response(jsonify({"response": "unsort book list called"}), 200)


api.add_resource(Books, '/books')
