from twilio.rest import Client
import os

def send_order_confirm_message(details): 
    try:
        #info = "Order Confirmed for {} [ {} ] to shipping address {}." format(details[1], details[2], details[3])
        account_sid = os.getenv('account_sid')
        auth_token = os.getenv('auth_token')
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to=details[6],
            from_=os.getenv('from_phone_number'),
            body="order confirmed!")
    except Exception:
        return make_response(jsonify({'response': "invalid phone number"}))
    except (InvalidRequestError, OperationalError):
        raise InvalidUsageError('phone number is improper', 500)