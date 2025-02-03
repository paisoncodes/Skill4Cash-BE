import json
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password

from services.serializers import CategorySerializer

from .models import BusinessProfile, Category, User, UserProfile
from .serializers import (
    ChangePasswordSerializer,
    CustomerProfileSetUpSerializer,
    CustomLoginSerializer,
    ImageSerializer,
    ResendTokenSerializer,
    ServiceProviderProfileSetUpSerializer,
    UserBusinessProfileSerializer,
    UserBusinessProfileViewSerializer,
    UserProfileViewSerializer,
    UserRegistrationSerializer,
    VerifyTokenSerializer,
    UserProfileSerializer,
)
from utils.otp import get_otp, verify_otp
from utils.utils import UploadUtil, api_response


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_classes = {
        "register": UserRegistrationSerializer,
        "login": CustomLoginSerializer,
        "verify_otp": VerifyTokenSerializer,
        "resend_otp": ResendTokenSerializer,
        "change_password": ChangePasswordSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: OpenApiResponse(description="User registered successfully")},
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                **serializer.validated_data, password="new_user"
            )
            otp = get_otp(user)
            subject = "Please Verify Your Email"
            message = f"Your Skill4Cash code is {otp}."
            # send_mail(user.email, subject=subject, body=message)
            data = {'message': "User account creation successful", 'otp': otp}
            return api_response("Registration successful", data, True, 201)
        return api_response("Registration failed", serializer.errors, False, 400)

    @extend_schema(
        request=CustomLoginSerializer,
        responses={200: OpenApiResponse(description="Login successful")},
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        data = serializer.validated_data

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

    @extend_schema(
        request=VerifyTokenSerializer,
        responses={200: OpenApiResponse(description="OTP verified successfully")},
    )
    @action(detail=False, methods=["post"])
    def verify_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            email = serializer.validated_data["email"]
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

    @extend_schema(
        request=ResendTokenSerializer,
        responses={200: OpenApiResponse(description="OTP resent successfully")},
    )
    @action(detail=False, methods=["post"])
    def resend_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = get_object_or_404(User, email=email)
            if user.email_verified:
                return Response(
                    {"message": "Email already verified", "status": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                otp = get_otp(user)
                subject = "Please Verify Your Email"
                message = f"Your Aquiline Alerts code is {otp}."

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

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Password changed successfully")},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, pk=request.user.pk)
        data = serializer.validated_data
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


class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_classes = {
        "customer_profile": CustomerProfileSetUpSerializer,
        "service_provider_profile": ServiceProviderProfileSetUpSerializer,
        "retrieve_profile": UserProfileSerializer,
        "update_profile": UserProfileSerializer,
        "business_profile": UserBusinessProfileSerializer,
        "update_business_profile": UserBusinessProfileSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        request=CustomerProfileSetUpSerializer,
        responses={
            201: OpenApiResponse(description="Customer profile setup successful")
        },
    )
    @action(detail=False, methods=["post"])
    def customer_profile(self, request):
        data = request.data
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()
            data = UserProfileSerializer(profile)
            return api_response("Profile Updated", data.data, True, 201)
        return api_response("Registration failed", serializer.errors, False, 400)

    @extend_schema(
        request=ServiceProviderProfileSetUpSerializer,
        responses={
            200: OpenApiResponse(
                description="Service provider profile setup successful"
            )
        },
    )
    @action(detail=False, methods=["post"])
    def service_provider_profile(self, request):
        data = request.data
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()
            business_profile = (
                UserBusinessProfileViewSerializer(
                    BusinessProfile.objects.filter(user=profile.user).first()
                )
            ).data
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
                "gallery": business_profile["gallery"],
            }
            return api_response("Profile updated", data, True, 200)
        return api_response("Profile update failed", serializer.errors, False, 400)

    @extend_schema(
        responses={200: OpenApiResponse(description="Profile retrieved successfully")},
    )
    @action(detail=False, methods=["get"])
    def retrieve_profile(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileViewSerializer(profile)
        return api_response("Profile Retrieved", serializer.data, True, 200)

    @extend_schema(
        request=UserProfileSerializer,
        responses={202: OpenApiResponse(description="Profile updated successfully")},
    )
    @action(detail=False, methods=["put"])
    def update_profile(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = self.get_serializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        serializer.update(instance=profile, validated_data=serializer.validated_data)
        return api_response("Profile updated", serializer.data, True, 202)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Business profile retrieved successfully")
        },
    )
    @action(detail=False, methods=["get"])
    def business_profile(self, request):
        user = request.user
        profile = get_object_or_404(BusinessProfile, user=user)
        serializer = self.get_serializer(profile)
        return api_response("Profile Retrieved", serializer.data, True, 200)

    @extend_schema(
        request=UserBusinessProfileSerializer,
        responses={
            202: OpenApiResponse(description="Business profile updated successfully")
        },
    )
    @action(detail=False, methods=["put"])
    def update_business_profile(self, request):
        user = request.user
        profile = get_object_or_404(BusinessProfile, user=user)
        serializer = self.get_serializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("ERROR", serializer.errors, False, 400)
        serializer.update(instance=profile, validated_data=serializer.validated_data)
        return api_response("Profile updated", serializer.data, True, 202)


class ImageUploadViewSet(viewsets.GenericViewSet):
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ImageSerializer,
        responses={201: OpenApiResponse(description="Image(s) uploaded successfully")},
    )
    @action(detail=False, methods=["post"])
    def upload(self, request, filetype):
        name = request.user.get("email") if request.user.is_authenticated else ""
        if filetype.upper() not in [settings.GALLERY, settings.PROFILE_PICTURE, settings.DOCUMENT]:
            return api_response("Invalid filetype, '%s'" % filetype, {}, False, 400)
        images = [x for x in request.FILES.keys()]
        serializer = self.get_serializer(data=request.data, images=images)
        if serializer.is_valid():
            image_urls = []
            for image in serializer.validated_data.values():
                if filetype.upper() == settings.GALLERY:
                    url = (UploadUtil.upload_gallery_image(image, business_name=name))
                    image_urls.append(url)
                elif filetype.upper() == settings.PROFILE_PICTURE:
                    url = (UploadUtil.upload_profile_picture(image, email=name))["image_url"]
                else:
                    pass
            return api_response("Image(s) uploaded", {"urls": image_urls}, True, 201)
        return api_response("Error", serializer.errors, False, 400)
