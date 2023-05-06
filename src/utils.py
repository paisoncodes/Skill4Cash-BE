from cloudinary import uploader, CloudinaryImage

from rest_framework.response import Response
from typing import Any
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
)
from django.http import JsonResponse


class UploadUtil:
    @staticmethod
    def upload_profile_picture(image:str, email:str="skill4cash_user") -> dict:
        try:
            uploader.upload(image, public_id = f"{email}", unique_filename = False, overwrite=True, folder="profile")
            srcURL = CloudinaryImage(f"profile/{email}").build_url()
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": srcURL
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }
    @staticmethod
    def upload_gallery_image(image:str, business_name:str="skill4cash_business_user", image_index:int=0) -> dict:
        try:
            uploader.upload(image, public_id = f"{image_index}", unique_filename = False, overwrite=True, folder=f"gallery/{business_name}")
            srcURL = CloudinaryImage(f"gallery/{business_name}/{image_index}").build_url()
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": srcURL
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
            uploader.upload(document, public_id = f"{document_name}", unique_filename = False, overwrite=True, folder=f"document/{business_name}")
            srcURL = CloudinaryImage(f"document/{business_name}/{document_name}").build_url()
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": srcURL
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
            uploader.upload(category_image, public_id = f"{category_name}", unique_filename = False, overwrite=True, folder=f"category")
            srcURL = CloudinaryImage(f"document/{category_name}").build_url()
            return {
                "success": True,
                "message": "Upload successful",
                "image_url": srcURL
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "image_url": ""
            }
    

def api_response(message: "str", status_code: "int", status: "str", data: "Any" = []) -> Response:

    response = {"message": message, "status": status, "results": data}

    if status_code == 200:
        return JsonResponse(response, status=HTTP_200_OK)

    elif status_code == 201:
        return JsonResponse(response, status=HTTP_201_CREATED)
    elif status_code == 202:
        return JsonResponse(response, status=HTTP_202_ACCEPTED)
    elif status_code == 204:
        return JsonResponse(response, status=HTTP_204_NO_CONTENT)
    elif status_code == 400:
        return JsonResponse(response, status=HTTP_400_BAD_REQUEST)
    elif status_code == 404:
        return JsonResponse(response, status=HTTP_404_NOT_FOUND)
    elif status_code == 406:
        return JsonResponse(response, status=HTTP_406_NOT_ACCEPTABLE)
