from drf_yasg import openapi
import jwt
from rest_framework.parsers import MultiPartParser, FormParser
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_list_or_404, get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.permissions import IsOwnerOrReadOnly
from src.settings import HTTP
from src.utils import Utils, api_response
from drf_yasg.utils import swagger_auto_schema
from decouple import config

from .models import User
from .permissions import PostReadAllPermission
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerSerializer,
    ServiceProviderSerializer,
    ServiceProviderRegistrationSerializer,
    TokenRefreshSerializer,
    UpdatePhoneSerializer,
    VerificationSerializer,
    UserSerializer,
    LoginSerializer,
)


class CustomerRegisterGetAll(APIView):
    # permission_classes = (PostReadAllPermission,)
    serializer_class = CustomerRegistrationSerializer

    def get(self, request):
        state = request.GET.get("state", None)
        city = request.GET.get("city", None)
        if state is None and city is None:
            users_objs = get_list_or_404(User, role="customer")
            users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved customers",
                "data": users_serilizer.data,
            }
        elif state is not None and city is None:
            users_objs = get_list_or_404(User, role="customer", state=state)
            users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved customers",
                "data": users_serilizer.data,
            }
        elif state is None and city is not None:
            users_objs = get_list_or_404(User, role="customer", city=city)
            users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved customers",
                "data": users_serilizer.data,
            }
        else:
            users_objs = get_list_or_404(User, role="customer", city=city, state=state)
            users_serilizer = CustomerRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved customers",
                "data": users_serilizer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):

        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            user_data = request.data
            return_data = Utils.send_verification_link(user_data, request, serializer)
            if return_data:
                return api_response(
                    status_code=201,
                    message="Customer created successfully",
                    data=serializer.data,
                    status="Success",
                )
            return api_response(
                status_code=400,
                message="Unable to send verification link",
                status="Failed",
            )
        else:
            return api_response(
                status_code=400,
                message=serializer.errors,
                status="Failed",
            )


class CustomerRetrieveUpdateDelete(APIView):
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    def get(self, request, id):

        if customer := self.get_object(id):
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Invalid User ID"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        if customer := self.get_object(id):
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )

    def delete(self, request, id):
        if customer := self.get_object(id):
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
    serializer_class = ServiceProviderRegistrationSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        users_objs = get_list_or_404(User, role="service_provider")
        users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
        data = {
            "message": "Successfully retrieved sp-customers",
            "data": users_serilizer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            user_data = request.data
            return_data = Utils.send_verification_link(user_data, request, serializer)
            if return_data:
                return api_response(
                    status_code=201,
                    message="Customer created successfully",
                    data=serializer.data,
                    status="Success",
                )
            return api_response(
                status_code=400,
                message="Unable to send verification link",
                status="Failed",
            )
        else:
            return api_response(
                status_code=400,
                message=serializer.errors,
                status="Failed",
            )


class ServiceProviderRetrieveUpdateDelete(APIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    def get(self, request, id, format=None):

        if service_provider := self.get_object(id):
            serializer = ServiceProviderSerializer(service_provider)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )
            
    @swagger_auto_schema(
            operation_id='Create a document',
            operation_description='Create a document by providing file and s3_key',
            manual_parameters=[
                openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Document to be uploaded'),
                openapi.Parameter('s3_key', openapi.IN_FORM, type=openapi.TYPE_STRING, description='S3 Key of the Document '
                                                                                                   '(folders along with name)')
            ],
            responses={
                status.HTTP_200_OK: openapi.Response(
                    'Success', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        'doc_id': openapi.Schema(type=openapi.TYPE_STRING, description='Document ID'),
                        'mime_type': openapi.Schema(type=openapi.TYPE_STRING, description='Mime Type of the Document'),
                        'version_id': openapi.Schema(type=openapi.TYPE_STRING, description='S3 version ID of the document')
                    })
                )
            }
        )
    def put(self, request, id):
        if service_provider := self.get_object(id):
            serializer = ServiceProviderSerializer(service_provider, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Invalid User ID", "status": status.HTTP_404_NOT_FOUND}
            )

    def delete(self, request, id):

        if service_provider := self.get_object(id):
            service_provider.delete()
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


class VerifyEmail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_verified:
                user.is_verified = True
                user.email_verification = True
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
    serializer_class = VerificationSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):

        otp_code = request.data.get("otp")
        user = User.objects.get(id=request.user.id)
        phone_number = user["phone_number"]

        try:
            if not user.phone_verification:
                if not "status_code" in request.session.keys():
                    sent_otp = Utils.otp_session(request, phone_number)
                    if sent_otp:
                        return Response(
                            {
                                "status": status.HTTP_200_OK,
                                "message": "OTP sent successfully",
                            }
                        )
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Sending OTP Error",
                        }
                    )
                else:
                    if otp_code:
                        if str(otp_code) == str(request.session["status_code"]):
                            user.phone_verification = True
                            user.save()

                            request.session.clear()
                            return Response(
                                {
                                    "status": status.HTTP_200_OK,
                                    "message": "OTP Code Verified",
                                }
                            )
                        request.session.clear()
                        return Response(
                            {
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": "OTP Incorrect!",
                            }
                        )
                    request.session.clear()
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Invalid OTP!",
                        }
                    )
            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "Phone number already validated",
                }
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Verification link expired",
                }
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid token",
                }
            )


class UpdatePhone(APIView):
    serializer_class = UpdatePhoneSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):

        otp_code, new_number = request.data.get("otp"), request.data.get("number")
        user = User.objects.get(id=request.user.id)
        try:
            if not User.objects.filter(phone_number__iexact=new_number).exists():

                if not "status_code" in request.session.keys():
                    sent_otp = Utils.otp_session(request, new_number)
                    if sent_otp:
                        return Response(
                            {
                                "status": status.HTTP_200_OK,
                                "message": "OTP sent successfully",
                            }
                        )
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Sending OTP Error",
                        }
                    )

                else:
                    if otp_code:
                        if str(otp_code) == str(request.session["status_code"]):
                            user.phone_verification = True
                            user.phone_number = new_number
                            user.save()

                            request.session.clear()
                            return Response(
                                {
                                    "status": status.HTTP_200_OK,
                                    "message": "OTP Code Verified",
                                }
                            )
                        request.session.clear()
                        return Response(
                            {
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": "OTP Incorrect!",
                            }
                        )
                    request.session.clear()
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Invalid OTP!",
                        }
                    )

            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "Phone number already Exist",
                }
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Verification link expired",
                }
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid token",
                }
            )


class CustomerLogin(APIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        if "email" not in request.data.keys() or "password" not in request.data.keys():
            return Response(
                {
                    "status_code": 400,
                    "status": "Failed",
                    "message": "Please enter your email address and password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user = get_object_or_404(User, email=request.data["email"])
            if user.role == "customer":
                response = Utils.create_token(
                    email=request.data["email"], password=request.data["password"]
                )
                if "error" in response.keys():
                    return Response(
                        {"status_code": 400, "status": "Failed", "message": response},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return api_response(
                        status_code=200,
                        message="Login successful",
                        data=response,
                        status="Success",
                    )
            else:
                return Response(
                    {
                        "status_code": 400,
                        "status": "Failed",
                        "message": "You're not a customer. Try the logging in as a service provider",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class ServiceProviderLogin(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        if "email" not in request.data.keys() or "password" not in request.data.keys():
            return Response(
                {
                    "status_code": 400,
                    "status": "Failed",
                    "message": "Please enter your email address and password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user = get_object_or_404(User, email=request.data["email"])
            if user.role == "service_provider":
                response = Utils.create_token(
                    email=request.data["email"], password=request.data["password"]
                )
                if "error" in response.keys():
                    return Response(
                        {"status_code": 400, "status": "Failed", "message": response},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return api_response(
                        status_code=200,
                        message="Login successful",
                        data=response,
                        status="Success",
                    )
            else:
                return Response(
                    {
                        "status_code": 400,
                        "status": "Failed",
                        "message": "You're not a service_provider. Try the logging in as a customer",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class RefreshToken(APIView):
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        if "refresh" not in request.POST:
            return Response(
                {
                    "status_code": 400,
                    "status": "Failed",
                    "message": "Refresh token not provided",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            response = Utils.refresh_token(refresh=request.data.get("refresh"))
            if "error" in response.keys():
                return Response(
                    {"status_code": 401, "status": "Failed", "message": response},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            else:
                return Response(
                    {"status_code": 200, "status": "Success", "message": response},
                    status=status.HTTP_200_OK,
                )


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                        status=status.HTTP_202_ACCEPTED,
                    )
                else:
                    return Response(
                        {"password": "passwords do not match"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {"password": password_validity["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"old password": "Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            relative_link = reverse("reset_password")

            current_site = request.get_host()
            absolute_url = f"{HTTP}{current_site}{relative_link}"

            email_body = f"""
                        <h2>Hi, <small>{user.first_name}</small></h2>    
                        <h4>Use the link below to verify your email.</h4>
                        <p>{absolute_url}</p>
                        
                        """
            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email,
            }

            Utils.sending_email(data)

            return Response(
                {
                    "message": "Password Reset email sent",
                    "Reset password link": absolute_url,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Invalid user email"}, status=status.HTTP_406_NOT_ACCEPTABLE
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
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"password": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"password": password_validity["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

class DecodeToken(APIView):
    def post(self, request):
        token = request.data['token']
        data = jwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])
        user = UserSerializer(User.objects.get(id=data["user_id"])).data
        return api_response(status_code=200, message="successful", status="success", data=user)