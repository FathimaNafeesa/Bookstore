from model import ProductData
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError,OperationalError,InvalidRequestError,CompileError
from services.error_handler_service import InvalidUsageError

class AdminServices:

    def add_book(id,title,author,image,quantity,price,description):
        new_book = ProductData(id = id,title = title,author = author,image = image,quantity = quantity,price = price,description = description)
        db.session.add(new_book)
        de.session.commit()
        return "Done"

    