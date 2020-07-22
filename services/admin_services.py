from model import ProductData, db
from sqlalchemy.exc import IntegrityError, OperationalError, InvalidRequestError, CompileError
from services.error_handler_service import InvalidUsageError


def add_books(id, title, author, image, quantity, price, description):
    try:
        new_book = ProductData(id=id, title=title, author=author, image=image,
                               quantity=quantity, price=price, description=description)
        db.session.add(new_book)
        db.session.commit()
        return "Done"
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)


def delete_book(id):
    try:
        book = ProductData.query.filter_by(id=id).delete()
        db.session.commit()
        return "Done"
    except (InvalidRequestError, OperationalError, CompileError):
        raise InvalidUsageError('mysql connection or syntax is improper', 500)
