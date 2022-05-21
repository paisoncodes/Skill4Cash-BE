import uuid
from random import choice

import jwt
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_list_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from src.permissions import IsOwnerOrReadOnly
from src.utils import Utils, otp_session
from src.utils import Utils

from .models import ServiceProvider, User
from .permissions import PostReadAllPermission
from .serializers import (CustomerRegistrationSerializer,
                          SPRegistrationSerializer, UserSerializer)


class CustomerRegisterGetAll(APIView):
    # permission_classes = (PostReadAllPermission,)
    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer

    def get(self, request):
        users_objs = get_list_or_404(User, role="customer")
        users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
        data = {
            "message": "Successfully retrieved customers",
            "data": users_serilizer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            user_data = serializer.data

            user = User.objects.get(email=user_data["email"])

            token = RefreshToken.for_user(user).access_token

            relative_link = reverse("verify_email")

            current_site = get_current_site(request).domain

            absolute_url = f"http://{current_site}{relative_link}?token={str(token)}"

            email_body = f"Hi, {user.first_name},\n    Use the link below to verify your email.\n              {absolute_url}"

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email,
            }

            Utils.send_email(data)

            return_data = dict(serializer.data)
            return_data["verification_link"] = absolute_url

            return Response(return_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Not in use yet. Still needs to be fixed.
class CustomerRetrieveUpdateDelete(APIView):
    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, id, request):

        customer = User.objects.get(id=id)
        serializer = CustomerRegistrationSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, id, request):
        customer = User.objects.get(id=id)
        if customer:
            serializer = CustomerRegistrationSerializer(
                customer, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )

    def delete(self, id, request):
        customer = User.objects.get(id=id)
        if customer:
            customer.delete()
            return Response(
                {
                    "message": "User deleted successfully",
                    "status": status.HTTP_204_NO_CONTENT,
                }
            )
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )


class ServiceProviderRegister(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer
    permission_classes = (PostReadAllPermission,)

    def get(self, request):
        users_objs = get_list_or_404(User, role="service_provider")
        users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
        data = {
            "message": "Successfully retrieved customers",
            "data": users_serilizer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SPRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data

            user = User.objects.get(email=user_data["email"])

            token = RefreshToken.for_user(user).access_token

            relative_link = reverse("verify_email")

            current_site = get_current_site(request).domain

            absolute_url = f"http://{current_site}{relative_link}?token={str(token)}"

            email_body = f"Hi, {user.first_name},\n    Use the link below to verify your email.\n              {absolute_url}"

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email,
            }

            Utils.send_email(data)

            return_data = dict(serializer.data)
            return_data["verification_link"] = absolute_url

            return Response(return_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Not in use yet. Still needs to be fixed.
class ServiceProviderRetrieveUpdateDelete(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer

    def get(self, id, request):

        service_provider = ServiceProvider.objects.get(id=id)
        serializer = SPRegistrationSerializer(service_provider)
        if service_provider:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, id, request):
        service_provider = ServiceProvider.objects.get(id=id)
        if service_provider:
            serializer = SPRegistrationSerializer(
                service_provider, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )

    def delete(self, id, request):
        try:
            service_provider = ServiceProvider.objects.get(id=id)
            service_provider.delete()
            return Response(
                {
                    "message": "User deleted successfully",
                    "status": status.HTTP_204_NO_CONTENT,
                }
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )


class VerifyEmail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_verified:
                user._is_verified = True
                user.save()

            return Response(
                {"email": "user email verified successfully"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Verification link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyPhone(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        otp_code = request.data.get('otp')
        user = User.objects.get(id=request.user.id)

        serializer = CustomerRegistrationSerializer(user, many=False)
        phone_number = serializer.data['phone_number']

        try:
            if not user.phone_verification:
                if not 'code' in request.session.keys():
                    sent_otp = otp_session(request, phone_number)
                    if sent_otp:
                        return Response({
                            'status': status.HTTP_200_OK,
                            'message': 'OTP sent successfully'
                        }
                        )
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        "message": 'Sending OTP Error'
                    }
                    )
                else:
                    if otp_code:
                        if str(otp_code) == str(request.session['code']):
                            user.phone_verification = True
                            user.save()

                            request.session.clear()
                            return Response({
                                'status': status.HTTP_200_OK,
                                'message': 'OTP Code Verified'
                            }
                            )
                        request.session.clear()
                        return Response({
                            'status': status.HTTP_400_BAD_REQUEST,
                            'message': 'OTP Incorrect!'
                        }
                        )
                    request.session.clear()
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid OTP!'
                    }
                    )
            return Response({
                'status': status.HTTP_403_FORBIDDEN,
                'message': 'Phone number already validated'
            }
            )
        except jwt.ExpiredSignatureError:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Verification link expired"
            }
            )
        except jwt.exceptions.DecodeError:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token",
            }
            )


class UpdatePhone(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):

        otp_code, new_number = request.data.get(
            'otp'), request.data.get('number')
        user = User.objects.get(id=request.user.id)
        print(user.is_verified)
        try:
            if not User.objects.filter(
                    phone_number__iexact=new_number).exists():

                if not 'code' in request.session.keys():
                    sent_otp = otp_session(request, new_number)
                    if sent_otp:
                        return Response({
                            'status': status.HTTP_200_OK,
                            'message': 'OTP sent successfully'
                        }
                        )
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        "message": 'Sending OTP Error'
                    }
                    )

                else:
                    if otp_code:
                        if str(otp_code) == str(request.session['code']):
                            user.phone_verification = True
                            user.phone_number = new_number
                            user.save()

                            request.session.clear()
                            return Response({
                                'status': status.HTTP_200_OK,
                                'message': 'OTP Code Verified'
                            }
                            )
                        request.session.clear()
                        return Response({
                            'status': status.HTTP_400_BAD_REQUEST,
                            'message': 'OTP Incorrect!'
                        }
                        )
                    request.session.clear()
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid OTP!'
                    }
                    )

            return Response({
                'status': status.HTTP_403_FORBIDDEN,
                'message': 'Phone number already Exist'
            }
            )

        except jwt.ExpiredSignatureError:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Verification link expired"
            }
            )
        except jwt.exceptions.DecodeError:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token",
            }
            )


class PopulateUser(APIView):

    permission_classes = (AllowAny,)

    def get(self, request):

        name = ['JAMES PETER', 'JOHN DOE']
        location = ['Lagos', 'Ibadan', 'Kano', 'Abeokuta', 'Benin']
        role = ['customer', 'service_provider']

        if not (users := User.objects.all()):

            for x in range(1, 11):
                names = choice(name).split()

                User.objects.create(
                    email=f"test{x}@yahoomail.com",
                    first_name=names[0],
                    last_name=names[1],
                    username=f"username{x}",
                    phone_number=f'090{x}-000-000{x}',
                    _is_verified=True,
                    role=choice(role),
                    location=choice(location)
                )
        serialized = UserSerializer(users, many=True)
        return Response(serialized.data)


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(
            serializer.data,
            status = status.HTTP_200_OK
        )
    
    def put(self, request):
        data = {}
        old_password = request.data["old_password"]
        password = request.data["password"]
        password2 = request.data["password2"]

        user_id = request.GET.get("user_id")

        obj = User.objects.get(id=user_id)
        self.check_object_permissions(request, obj)

        # serializer = ChangePasswordSerializer(data=data)

        email = request.user.email

        user = authenticate(email=email, password=old_password)

        if user:
            password_validity = Utils.validate_password(password=password)
            if password_validity["status"]:
                if password == password2:
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.save()
                    return Response(
                        {"message": "Password changed successfully"},
                        status = status.HTTP_202_ACCEPTED
                    )
                else:
                    return Response(
                    {"password": "passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"password": password_validity["message"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"old password": "Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResetPasswordEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            relative_link = reverse("reset_password")
                    
            current_site = get_current_site(request).domain

            absolute_url = f"http://{current_site}{relative_link}"

            email_body = f"Hi, {user.first_name},\n    Use the link below to verify your email.\n                 {absolute_url}"

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email
            }

            Utils.send_email(data)

            return Response(
                {
                    "message": "Password Reset email sent",
                    "Reset password link": absolute_url
                },
                status = status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Invalid user email"},
                status = status.HTTP_406_NOT_ACCEPTABLE
            )

class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        password2 = request.data["password2"]

        password_validity = Utils.validate_password(password)
        
        if password_validity["status"]:
            if password2 == password:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.save()

                    return Response(
                        {"message": "Password reset successful"},
                        status = status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {"message": e},
                        status = status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"password": "Passwords do not match"},
                    status = status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"password": password_validity["message"]},
                status = status.HTTP_400_BAD_REQUEST
            )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
