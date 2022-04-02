from email import message
from django.core.mail import EmailMessage
from twilio.rest import Client
from decouple import config
from random import choice

def send_otp(phone):

    account_sid = config("ACCOUNT_SID")
    auth_token  = config("AUTH_TOKEN")

    if phone:
        # generating otp_code
        code = [x for x in range(0,9)]
        otp_code = "".join([str(choice(code)) for x in range(5)])
        
        client = Client(account_sid, auth_token)
        # sending message
        client.messages.create(
            messaging_service_sid=config('MESSAGE_SERVICE'),
            to=str(phone), 
            body=f"Your verification code is {otp_code}, don't share it with anybody."
        )
        return otp_code
        # catch this in an error handling block instead
    return None

class Utils:

    @staticmethod
    def send_email(data):
        
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=(data["to_email"],)
        )
        email.send()