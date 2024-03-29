import json
import os
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from services.serializers import CategorySerializer
from src.settings import BASE_DIR
from utils.otp import get_otp, verify_otp
from utils.utils import UploadUtil, api_response, validate_phone_number
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.response import Response

from .models import BusinessProfile, Category, TestImageUpload, User, UserProfile
from .serializers import (
    ChangePasswordSerializer,
    CustomerProfileSetUpSerializer,
    CustomLoginSerializer,
    ImageSerializer,
    ResendTokenSerializer,
    SendPhoneOtpSerializer,
    ServiceProviderProfileSetUpSerializer,
    UserBusinessProfileSerializer,
    UserBusinessProfileViewSerializer,
    UserProfileViewSerializer,
    UserRegistrationSerializer,
    VerifyPhoneOtpSerializer,
    VerifyTokenSerializer,
    TestImageUploadSerializer,
    UserProfileSerializer,
)


class SetUpCustomerProfile(GenericAPIView):
    serializer_class = CustomerProfileSetUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        data["user"] = request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            profile = serializer.save()
            data = UserProfileSerializer(profile)
            return api_response("Profile Updated", data.data, True, 201)
        return api_response("Registration failed", serializer.errors, False, 400)

class ProfileRetrieveUpdateView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileViewSerializer(profile)

        return api_response("Profile Retrieved", serializer.data, True, 200)
    
    def put(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = self.serializer_class(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        serializer.update(instance=profile, validated_data=serializer.validated_data)
        return api_response("Profile updated", serializer.data, True, 202)

class RegisterUser(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.data, password="new_user")
            otp = get_otp(user)
            subject = "Please Verify Your Email"
            message = f"Your Skill4Cash code is {otp}."
            # send_mail(user.email, subject=subject, body=message)
            data = {'message': "User account creation successful", 'otp': otp}
            return api_response("Registration successful", data, True, 201)
        return api_response("Registration failed", serializer.errors, False, 400)

class SetUpServiceProviderProfile(GenericAPIView):
    serializer_class = ServiceProviderProfileSetUpSerializer
    permission = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        data["user"] = request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            profile = serializer.save()
            business_profile = (UserBusinessProfileViewSerializer(BusinessProfile.objects.filter(user=profile.user).first())).data
            data = {
                "email": request.user.email,
                "full_name": f"{profile.first_name} {profile.last_name}",
                "phone_number": profile.phone_number,
                "user_type": profile.user_type,
                "profile_picture": profile.profile_picture,
                "state": profile.state.state,
                "lga": profile.lga.lga,
                "verified": request.user.email_verified,
                "phone_verified": profile.phone_verified,
                "business_name": business_profile["business_name"],
                "description": business_profile["description"],
                "category": business_profile["service_category"],
                "keywords": business_profile["keywords"],
                "gallery": business_profile["gallery"]
            }
            return api_response("Profile updated", data, True, 200)
        return api_response("Profile update failed", serializer.errors, False, 400)

class BusinessProfileRetrieveUpdateView(GenericAPIView):
    serializer_class = UserBusinessProfileSerializer
    permission = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = get_object_or_404(BusinessProfile, user=user)
        serializer = self.serializer_class(profile)

        return api_response("Profile Retrieved", serializer.data, True, 200)
    
    def put(self, request):
        user = request.user
        profile = get_object_or_404(BusinessProfile, user=user)
        serializer = self.serializer_class(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        serializer.update(instance=profile, validated_data=serializer.validated_data)
        return api_response("Profile updated", serializer.data, True, 202)
    
class Login(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        data = serializer.data

        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return api_response("Email or Password is incorrect", {}, False, 400)
        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile.user_type.lower() != (data["user_type"]).lower():
            return api_response("Invalid login", {}, False, 400)
        current_password = user.password
        check = check_password(data["password"], current_password)

        if check:
            if user.email_verified:
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
    
            else:
                return Response(
                    {
                        "message": "Account not verified, Please verify your email",
                        "status": False,
                        "data": {}
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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

class VerifyOtp(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.data["code"]
            email = serializer.data["email"]
            user = get_object_or_404(User, email=email)
            if verify_otp(user, code):
                user.is_active = True
                user.email_verified = True
                user.save()
                data = {
                    "user_id": user.id,
                    "email": user.email
                }

                refresh = RefreshToken.for_user(user)
                data["access_token"] = str(refresh.access_token)
                return api_response("VerificationSuccessful", data, True, 200)
            else:
                return Response(
                    {"message": "Code invalid or expired", "status": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )            

class ResendOtp(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            user = get_object_or_404(User, email=email)
            if user.email_verified:
                return Response(
                    {"message": "Email already verified", "status": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                otp = get_otp(user)
                subject = "Please Verify Your Email"
                message =  f"Your Aquiline Alerts code is {otp}."

                # send_mail(user.email, subject=subject, body=message)
                return Response(
                    {
                        "message": "Email Sent" if True else "Email not sent",
                        "status": True,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

class VerifyPhoneNumberOtp(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyPhoneOtpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.data["code"]
            user = get_object_or_404(User, pk=request.user.pk)
            if verify_otp(user, code):
                user.is_active = True
                user.phone_verified = True
                user.save()
                return Response(
                    {"message": "Phone Number verified", "status": True},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Code invalid or expired", "status": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

class SendPhoneNumberOtp(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SendPhoneOtpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        phone_number = serializer.data["phone_number"]
        check_phone = validate_phone_number(phone_number)
        if not check_phone:
            return api_response("Invalid phone number", {}, False, 400)
        user = request.user
        user.phone_number = phone_number
        user.save()
        otp = get_otp(user)
        message = f"Your Aquiline Alerts code is {otp}."

        # send_message(phone_number, message, user.email)
        
        return Response(
            {"message": "OTP sent to phone number", "status": True},
            status=status.HTTP_200_OK,
        )

class ChangePassword(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, pk=request.user.pk)
        data = serializer.data
        check = check_password(data["old_password"], user.password)
        if check:
            user.password = make_password(data["new_password"])
            user.save()
            return Response(
                {
                    "message": "Password Change Successful",
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "old password is incorrect",
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class TestImageUploadView(GenericAPIView):
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

class PopulateCategory(GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get(self, request):
        with open(f"{settings.PATH}/categories.json") as file:
            categories = json.load(file)
        for key in categories.keys():
            category_name = "-".join(key.split("_"))
            name = " ".join(key.split("_"))
            image_url = (UploadUtil.upload_category_image(f"{settings.PATH}/{categories[key]}", category_name))["image_url"]
            if Category.objects.filter(name=name).exists():
                continue
            else:
                Category.objects.create(name=name, image=image_url)
        serializer = self.serializer_class(Category.objects.all(), many=True)
        return api_response("Categories uploaded successfully", 201, "Success", serializer.data)


response_schema_dict = {
"201": openapi.Response(
    description="Image(s) uploaded",
    examples={
        "application/json": {
            "urls": [""],
        }
    }
)
}

class UploadPictures(GenericAPIView):
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses=response_schema_dict
    )
    def post(self, request, filetype):
        name = request.user.get("email") if request.user.is_authenticated else ""
        if filetype.upper() not in [settings.GALLERY, settings.PROFILE_PICTURE, settings.DOCUMENT]:
            return api_response("Invalid filetype, '%s'" %filetype, {}, False, 400)
        images = [x for x in request.FILES.keys()]
        serializer = self.serializer_class(data=request.data, images=images)
        if serializer.is_valid():
            image_urls = []
            for image in serializer.validated_data.values():
                if filetype.upper() == settings.GALLERY:
                    url = (UploadUtil.upload_gallery_image(image, business_name=name))
                    image_urls.append(url)
                elif filetype.upper() == settings.PROFILE_PICURE:
                    url = (UploadUtil.upload_profile_picture(image, email=name))["image_url"]
                else:
                    pass
            return api_response("Image(s) uploaded", {"urls": image_urls}, True, 201)
        return api_response("Error", serializer.errors, False, 400)