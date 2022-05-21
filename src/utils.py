import re
import string
from datetime import time
from random import choice

import jwt
from decouple import config
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from authentication.models import User


allowed_characters = set(string.ascii_letters + string.digits + string.punctuation)

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
            #     # to=config('TO'),
            #     to=str(phone), 
            #     body=f"Your Skill4Cash verification code is {otp_code}, don't share it with anybody."
            # )
            return otp_code
        
    except TwilioRestException:
        return None

def otp_session(request, number):
    
    otp_code = send_otp(number)

    if otp_code:
        request.session['code'] = otp_code
        request.session['num'] = number
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
    
    @staticmethod
    def validate_user_password(password):
        if (len(password) < 8):
            raise ValidationError("password is too short")
        if any(pass_char not in allowed_characters for pass_char in password):
            raise ValidationError("password contains illegal characters")

        if not any(pass_char.isdigit() for pass_char in password):
            raise ValidationError("password must have at least one number")

        if not any(pass_char.isupper() for pass_char in password):
            raise ValidationError("password must have at least one uppercase letter")

        if not any(pass_char.islower() for pass_char in password):
            raise ValidationError("password must have at least one lowercase letter")

        if not any(pass_char in string.punctuation for pass_char in password):
            raise ValidationError("password must have at least one special character")

        return True
    
    @staticmethod
    def validate_password(password):
        if (len(password) < 8):
            return {"status": False, "message":"password is too short"}
        if any(pass_char not in allowed_characters for pass_char in password):
            return {"status": False, "message":"password contains illegal characters"}

        if not any(pass_char.isdigit() for pass_char in password):
            return {"status": False, "message": "password must have at least one number"}

        if not any(pass_char.isupper() for pass_char in password):
            return {"status": False, "message": "password must have at least one uppercase letter"}

        if not any(pass_char.islower() for pass_char in password):
            return {"status": False, "message": "password must have at least one lowercase letter"}

        if not any(pass_char in string.punctuation for pass_char in password):
            return {"status": False, "message": "password must have at least one special character"}

        return {"status": True}

    @staticmethod
    def authenticate_user(token:str):
        try:
            dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            exp = int("{}".format(dt['exp']))
            if time.time() < exp:
                email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
                user = User.objects.get(email=email)
                return {"status":True, "message": "authenticated", "user":user}
            else:
                return {"status":False, "message": "token expired", "user":User()}
        except Exception as e:
            return {"status":False, "message": e, "user":User()}

    @staticmethod
    def validate_email(email):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if(re.search(regex, email)):
            if User.objects.filter(email=email).exists():
                return {"status": False, "message": "E-mail Already in use"}
            else:
                return {"status": True, "message": "Email ok"}
        else:
            return {"status": False, "message": "Enter Valid E-mail"}
