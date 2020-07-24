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



    
