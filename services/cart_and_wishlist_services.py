from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, OperationalError, InvalidRequestError, CompileError
from model import User, db, ProductData, Admin, product_data_schema,relationship_table_cart
from services.services import calling_book_details
from flask import jsonify, make_response
from services.error_handler_service import InvalidUsageError

def find_user_wishlist(username):
    try:
        user = User.query.filter_by(username=username).first()
        wishlist = user.wishlist
        return wishlist
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)


def find_user_cart(username):
    try:
        user = User.query.filter_by(username=username).first()
        cart = user.cart
        return cart
    except (InvalidRequestError, OperationalError, CompileError):
            raise InvalidUsageError('mysql connection or syntax is improper', 500)


def display_wishlist_or_cart(username, arg):
    try:
        switcher = {
            0: find_user_wishlist,
            1: find_user_cart
        }
        result = switcher.get(arg, "invalid")(username)
        if result:
            result = product_data_schema.dumps(result)
        else:
            result = "empty"
        return result
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)


def add_or_delete_books(id, username, action, arg, book_quantity):
    try: 
        user = User.query.filter_by(username=username).first()
        book = ProductData.query.filter_by(id=id).first()  
        switcher = {
            0: add_or_delete_books_in_wishlist,
            1: add_or_delete_books_in_cart
        }

        return switcher.get(arg, "invalid")(user, book, action,book_quantity)
    except (InvalidRequestError, OperationalError, CompileError):
            raise InvalidUsageError('mysql connection or syntax is improper', 500)


def add_or_delete_books_in_cart(user, book, action,book_quantity):
    try:
        if action == "add":
            if book.quantity < book_quantity:
                return make_response(jsonify({'response': "only" + str(book.quantity) + "books available"}))
            book.products_to_order.append(user)
            current_user_id = user.id
            current_product_id = book.id
            db.session.execute('UPDATE relationship_table_cart SET quantity = :quantity WHERE user_id = :user_id and product_id = :product_id',{'quantity': book_quantity,'user_id':current_user_id,'product_id':current_product_id})
        if action == "delete":
            user.cart.remove(book).all()
        db.session.commit()
        return True
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)


def add_or_delete_books_in_wishlist(user, book, action,book_quantity=0):
    try:
        if action == "add":
            book.products.append(user)
        if action == "delete":
            user.wishlist.remove(book)
        db.session.commit()
        return True
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)
