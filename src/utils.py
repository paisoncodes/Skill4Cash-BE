import re
import string
from datetime import time
from random import choice

import jwt
from django.conf import settings
from django.core.exceptions import ValidationError
from twilio.base.exceptions import TwilioRestException
from rest_framework.response import Response
from typing import Any
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User
from django.contrib.auth import authenticate
from django.urls import reverse

import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse

allowed_characters = set(string.ascii_letters +
                         string.digits + string.punctuation)
client = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION
)



class Utils:

    @staticmethod
    def sending_email(data):
        try:
            response = client.send_email(
                # using user's email after amazon verification
                Destination={'ToAddresses': [settings.RECIPIENT,], },
                Message={
                    'Body': {'Html': {'Charset': settings.CHARSET, 'Data': data['email_body'], },
                             'Text': {'Charset': settings.CHARSET, 'Data': data['email_body'], },
                             },
                    'Subject': {'Charset': settings.CHARSET, 'Data': data['email_subject'], },
                },
                Source=settings.SENDER,
            )
        except ClientError as e:
            return (e.response['Error']['Message'])
        else:
            return response['MessageId']

    @staticmethod
    def validate_user_password(password):
        if (len(password) < 8):
            raise ValidationError("password is too short")
        if any(pass_char not in allowed_characters for pass_char in password):
            raise ValidationError("password contains illegal characters")

        if not any(pass_char.isdigit() for pass_char in password):
            raise ValidationError("password must have at least one number")

        if not any(pass_char.isupper() for pass_char in password):
            raise ValidationError(
                "password must have at least one uppercase letter")

        if not any(pass_char.islower() for pass_char in password):
            raise ValidationError(
                "password must have at least one lowercase letter")

        if not any(pass_char in string.punctuation for pass_char in password):
            raise ValidationError(
                "password must have at least one special character")

        return True

    @staticmethod
    def validate_password(password):
        if (len(password) < 8):
            return {"status": False, "message": "password is too short"}
        if any(pass_char not in allowed_characters for pass_char in password):
            return {"status": False, "message": "password contains illegal characters"}

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
    def authenticate_user(token: str):
        try:
            dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            exp = int("{}".format(dt['exp']))
            if time.time() < exp:
                email = jwt.decode(token, settings.SECRET_KEY,
                                   algorithms=["HS256"])["username"]
                user = User.objects.get(email=email)
                return {"status": True, "message": "authenticated", "user": user}
            else:
                return {"status": False, "message": "token expired", "user": User()}
        except Exception as e:
            return {"status": False, "message": e, "user": User()}

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
    
    @staticmethod
    def create_token(email:str, password:str) -> dict:
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        else:
            return {
                "error": "Invalid login details"
            }
            
    @staticmethod
    def refresh_token(refresh:str) -> dict:
        try:
            payload = jwt.decode(
                refresh, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            token = RefreshToken.for_user(user)
            return {
                'access': str(token.access_token)
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}

        except jwt.exceptions.DecodeError:
            return {"error": "Invalid token"}
    
    @staticmethod
    def get_token_user(token:str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            return {
                'user': user
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}

        except jwt.exceptions.DecodeError:
            return {"error": "Invalid token"}

    @staticmethod
    def send_verification_link(user_data,request,serializer):
        
        token = Utils.create_token(
                            user_data['email'], 
                            user_data['password']
                        )
        if "error" not in token.keys():
            token = token['access']
            relative_link = reverse("verify_email")
            current_site = request.get_host()
            absolute_url = (
                f"{settings.HTTP}{current_site}{relative_link}?token={str(token)}"
            )
            email_body = f"""
                    <h2>Hi, <small>{user_data['first_name']}</small></h2>    
                    <h4>Use the link below to verify your email.</h4>
                    <p>{absolute_url}</p>
                    """

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user_data['email'],
            }

            # result a message id, if sent successfully
            message_id = Utils.sending_email(data)

            return_data = dict(serializer.data)
            return_data["verification_link"] = absolute_url
            return_data['message_sent'] = dict(message_id=message_id)
            return return_data
        else:
            return None
    
    @staticmethod
    def otp_session(number):
        
        # generating otp_code
        code = [x for x in range(0, 9)]
        otp_code = "".join([str(choice(code)) for x in range(5)])
        # sending message
        # try:
        #     client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        #     client.messages.create(
        #         from_= settings.MESSAGE_SERVICE,
        #         to=settings.TO,
        #         to=str(number), 
        #         body=f"Your Skill4Cash verification code is {otp_code}, don't share it with anybody."
        #     )
        # except TwilioRestException:
        #     return None
        return otp_code

def api_response(message: "str", status_code: "int", status: "str", data: "Any" = []) -> Response:

    response = {"message": message, "status": status, "results": data}

    if status_code == 200:
        return JsonResponse(response, status=HTTP_200_OK)

    elif status_code == 201:
        return JsonResponse(response, status=HTTP_201_CREATED)
    elif status_code == 400:
        return JsonResponse(response, status=HTTP_400_BAD_REQUEST)
    elif status_code == 404:
        return JsonResponse(response, status=HTTP_404_NOT_FOUND)
