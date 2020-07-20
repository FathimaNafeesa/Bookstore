from flask import jsonify


class InvalidUsageError(Exception):  # custom exception class

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        dict_ = {}
        dict_['response'] = self.message
        return dict_
