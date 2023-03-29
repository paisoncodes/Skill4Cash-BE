from drf_yasg import openapi
import jwt
import json
import os
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_list_or_404, get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from authentication.utility import get_user, update_customer, update_service_provider
from services.serializers import CategorySerializer
from src.permissions import IsOwnerOrReadOnly
from src.settings import BASE_DIR, HTTP
from utils.utils import AuthUtil, UploadUtil, api_response
from drf_yasg.utils import swagger_auto_schema
from decouple import config
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password

from .models import Category, TestImageUpload, User, UserProfile
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerSerializer,
    LoginSerializer,
    ServiceProviderSerializer,
    ServiceProviderRegistrationSerializer,
    TestImageUploadSerializer,
    TokenRefreshSerializer,
    UpdatePhoneSerializer,
    UserProfileSerializer,
    VerificationSerializer,
    UserSerializer,
)

path = os.path.join(BASE_DIR, 'authentication')

class RegisterCustomer(GenericAPIView):
    serializer_class = CustomerRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response("Registration successful", {}, True, 200)
        return api_response("Registration failed", serializer.errors, False, 400)

class ProfileRetrieveUpdateView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = self.serializer_class(profile)

        return api_response("Profile Retrieved", serializer.data, True, 200)
    
    def put(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = self.serializer_class(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        serializer.update(instance=profile, validated_data=serializer.validated_data)
        return api_response("Profile updated", serializer.data, True, 202)


class Login(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = serializer.data
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return Response(
                {"message": "email or password is incorrect", "status": False},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile.user_type.lower() != (data["user_type"]).lower():
            return api_response("Invalid login", {}, False, 400)
        current_password = user.password
        check = check_password(data["password"], current_password)

        if check:
            # if user.email_verified:
                data = {
                    "user_id": user.id,
                    "email": user.email
                }

                refresh = RefreshToken.for_user(user)
                data["access_token"] = str(refresh.access_token)
                if user_profile:
                    data["first_name"] = user_profile.first_name
                    data["last_name"] = user_profile.last_name
                    data["phone_number"] = user_profile.phone_number
                    data["is_verified"] = user.email_verified
                return api_response("Login Successful", data, True, 200)
    
            # else:
            #     return Response(
            #         {
            #             "message": "Account not verified, Please verify your email",
            #             "status": False,
            #         },
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )
        else:
            if user_profile.auth_provider == UserProfile.AuthProvider.GOOGLE:
                return Response(
                    {
                        "message": "Please Sign in with Google",
                        "status": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "message": "email or password is incorrect",
                    "status": False,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
            

class TestImageUploadView(APIView):
    queryset = TestImageUpload.objects.all()
    serializer_class = TestImageUploadSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This is a test endpoint.
        """
        data = request.data
        data["image1"] = (UploadUtil.upload_gallery_image(data["image1"], business_name="Test_business", image_index=1))["image_url"]
        data["image2"] = (UploadUtil.upload_gallery_image(data["image2"], business_name="Test_business", image_index=2))["image_url"]
        data["image3"] = (UploadUtil.upload_gallery_image(data["image3"], business_name="Test_business", image_index=3))["image_url"]
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return api_response("Test successful", 200, "Success", serializer.data)
        else:
            return api_response("Test failed", 400, "Failed", serializer.errors)

class PopulateCategory(APIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get(self, request):
        with open(f"{path}/categories.json") as file:
            categories = json.load(file)
        for key in categories.keys():
            category_name = "-".join(key.split("_"))
            name = " ".join(key.split("_"))
            image_url = (UploadUtil.upload_category_image(f"{path}/{categories[key]}", category_name))["image_url"]
            if Category.objects.filter(name=name).exists():
                continue
            else:
                Category.objects.create(name=name, image=image_url)
        serializer = self.serializer_class(Category.objects.all(), many=True)
        return api_response("Categories uploaded successfully", 201, "Success", serializer.data)

