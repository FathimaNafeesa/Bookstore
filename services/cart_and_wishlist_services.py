from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError,OperationalError,InvalidRequestError,CompileError
from model import User, db, ProductData, Admin,product_data_schema
from services.services import calling_book_details

def find_user_wishlist(username):
    user = User.query.filter_by(username = username).first()
    wishlist = user.wishlist
    return wishlist

def find_user_cart(username):
    user = User.query.filter_by(username = username).first()
    cart = user.cart
    return cart


def display_wishlist_or_cart(username,arg):
    try:
        switcher ={
            0:find_user_wishlist(username),
            1:find_user_cart(username)
        }
        result = switcher.get(arg,"invalid")
        if result:
            result = product_data_schema.dumps(result)
        else:
            result = "empty"
        return result
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)


def add_or_delete_books(id,username,action,arg):

    user = User.query.filter_by(username = username).first()
    book = ProductData.query.filter_by(id=id).first()
    switcher ={
        0:add_or_delete_books_in_wishlist(user,book,action),
        1:add_or_delete_books_in_cart(user,book,action)
    }
    return switcher.get(arg,"invalid")

        


def add_or_delete_books_in_cart(user,book,action):
    try:
        if action == "add":
            book.products_to_order.append(user)
        if action == "delete":
            user.cart.remove(book)
        db.session.commit()
        return True
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)

def add_or_delete_books_in_wishlist(user,book,action):
    try:
        if action == "add":
            book.products.append(user)
        if action == "delete":
            user.wishlist.remove(book)
        db.session.commit()
        return True
    except (InvalidRequestError,OperationalError,CompileError) :
            raise InvalidUsageError('mysql connection or syntax is improper', 500)










    
