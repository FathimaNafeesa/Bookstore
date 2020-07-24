from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError,OperationalError,InvalidRequestError,CompileError
from model import User, db, ProductData, Admin
from services.services import calling_book_details

def display_wishlist(username):
    try:
        user = User.query.filter_by(username = username).first()
        wishlist = user.wishlist
        if wishlist:
            wishlist = calling_book_details(wishlist)
        else:
            wishlist = "empty"
        return wishlist
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)


def add_books_to_wishlist(id,username):
    try:
        user = User.query.filter_by(username = username).first()
        book = ProductData.query.filter_by(id=id).first()
        book.products.append(user)
        db.session.commit()
        return True
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)

def display_cart(username):
    try:
        user = User.query.filter_by(username = username).first()
        cart = user.cart
        if cart:
            cart = calling_book_details(cart)
        else:
            cart = "empty"
        return cart
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500) 

def add_or_delete_books_to_cart(id,username,action)
    try:
        user = User.query.filter_by(username = username).first()
        book = ProductData.query.filter_by(id=id).first()
        if action == "add":
            book.products_to_order.append(user)
        if action == "delete":
            user.car.remove(book)
        db.session.commit()
        return True
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)







    
