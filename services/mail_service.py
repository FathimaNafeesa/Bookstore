
from flask import render_template
from services.error_handler_service import InvalidUsageError
import os
import jwt
from app import mail, Message
mail_user = os.getenv('EMAIL_USER')


class MailService:

    @staticmethod
    def send_mail_with_order_details(details):
        msg = Message(
            'From Books Store',
            sender=mail_user,
            recipients=[details[0]]
        )
        msg.html = render_template('email.html', details=details)
        mail.send(msg)
