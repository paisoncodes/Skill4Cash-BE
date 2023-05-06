import json
from random import randint
from cloudinary import uploader, CloudinaryImage
from rest_framework.response import Response
from typing import Any
from rest_framework import status as status_code

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

def create_token(email:str, password:str) -> dict:
    user = authenticate(email=email, password=password)
    if user.is_verified:
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
    else:
        return {
            "error": "User not verified"
        }
    
class UploadUtil:
    @staticmethod
    def upload_profile_picture(image:str, email:str="skill4cash_user") -> dict:
        try:
            response = uploader.upload(image, public_id = f"{email}", unique_filename = True, overwrite=True, folder="profile")
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": response.get("secure_url")
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }
    @staticmethod
    def upload_gallery_image(image:str, business_name:str="skill4cash_business_user") -> dict:
        try:
            response = uploader.upload(image, unique_filename = True, overwrite=True, folder=f"gallery/{business_name}")
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": response.get("secure_url")
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }

    @staticmethod
    def upload_document_image(document:str, document_name:str, business_name:str="skill4cash_business_document") -> dict:
        try:
            response = uploader.upload(document, public_id = f"{document_name}", unique_filename = True, overwrite=True, folder=f"document/{business_name}")
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": response.get("secure_url")
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }
    
    @staticmethod
    def upload_category_image(category_image:str, category_name:str) -> dict:
        try:
            response = uploader.upload(category_image, public_id = f"{category_name}", unique_filename = True, overwrite=True, folder=f"category")
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": response.get("secure_url")
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }
    

def api_response(message:str, data:json, status:bool, code:int)->Response:
    response = {
        "message": message,
        "data": data,
        "status": status,
    }
    if code == 200:
        return Response(response, status=status_code.HTTP_200_OK)
    elif code == 201:
        return Response(response, status=status_code.HTTP_201_CREATED)
    elif code == 202:
        return Response(response, status=status_code.HTTP_202_ACCEPTED)
    elif code == 400:
        return Response(response, status=status_code.HTTP_400_BAD_REQUEST)
    elif code == 401:
        return Response(response, status=status_code.HTTP_401_UNAUTHORIZED)
    else:
        return Response(response, status=status_code.HTTP_500_INTERNAL_SERVER_ERROR)

def validate_phone_number(phone_number:str)->bool:
    if len(phone_number) > 13:
        return False
    if len(phone_number) < 13:
        return False
    if phone_number[:3] != "234":
        return False
    return True


def random_with_n_digits(n=12):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)