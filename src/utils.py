from twilio.base.exceptions import TwilioRestException
from django.core.mail import EmailMessage
from twilio.rest import Client
from decouple import config
from random import choice

def send_otp(phone):
    try:
        account_sid = config("ACCOUNT_SID")
        auth_token  = config("AUTH_TOKEN")

        if phone:
            # generating otp_code
            code = [x for x in range(0,9)]
            otp_code = "".join([str(choice(code)) for x in range(5)])
            
            # client = Client(account_sid, auth_token)
            # # sending message
            # client.messages.create(
            #     from_=config('MESSAGE_SERVICE'),
            #     to=config('TO'),
            #     # to=str(phone), 
            #     body=f"Your Skill4Cash verification code is {otp_code}, don't share it with anybody."
            # )
            return otp_code
        
    except TwilioRestException:
        return None

def otp_session(request, number, ins):
    
    otp_code = send_otp(number)

    if otp_code:
        request.session['code'] = otp_code
        request.session['num'] = number
        ins.is_validated = False
        ins.save()
        return True
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