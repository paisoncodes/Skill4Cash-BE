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
from authentication.utility import update_customer, update_service_provider
from services.serializers import CategorySerializer
from src.permissions import IsOwnerOrReadOnly
from src.settings import BASE_DIR, HTTP
from src.utils import AuthUtil, UploadUtil, api_response
from drf_yasg.utils import swagger_auto_schema
from decouple import config

from .models import Category, TestImageUpload, User
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerSerializer,
    EmailLoginSerializer,
    ServiceProviderSerializer,
    ServiceProviderRegistrationSerializer,
    TestImageUploadSerializer,
    TokenRefreshSerializer,
    UpdatePhoneSerializer,
    VerificationSerializer,
    UserSerializer,
)

path = os.path.join(BASE_DIR, 'authentication')

class CustomerRegisterGetAll(APIView):
    serializer_class = CustomerRegistrationSerializer
    def get(self, request):
        """
        This endpoint returns list of existing customers.
        """
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

        return api_response(data["message"], 200, "Success", data["data"])

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint creates a new customer in the database.
        """
        data = request.data
        if "profile_picture" in data.keys():
            data["profile_picture"] = (UploadUtil.upload_profile_picture(data["profile_picture"], email=data["email"]))
        serializer = CustomerRegistrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            user_data = request.data
            return_data = AuthUtil.send_verification_link(user_data, request, serializer)
            if return_data != None:
                response_data = {**serializer.data, **return_data}
                return api_response(
                    status_code=201,
                    message="Customer created successfully",
                    data=response_data,
                    status="Success",
                )
            return api_response(
                status_code=201,
                message="Customer Created. Unable to send verification link",
                data=serializer.data,
                status="Success",
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
        """
        This endpoint returns a customer's details.
        """
        if customer := self.get_object(id):
            serializer = CustomerSerializer(customer)
            return api_response("User retrieved", 200, "Success", serializer.data)
        else:
            return api_response("Invalid User ID", 404, "Failed")
    def put(self, request, id):
        """
        This endpoint updates a customer's information.
        """
        customer = User.objects.get(email=request.user.email)
        data = request.data
        if "profile_picture" in data.keys():
            data["profile_picture"] = (UploadUtil.upload_profile_picture(data["profile_picture"], email = customer.email))["image_url"]
        upload = update_customer((self.serializer_class(customer)).data, data)
        serializer = CustomerSerializer(instance=customer, data=upload)
        if serializer.is_valid():
            serializer.save()
            return api_response("Update successful", 202, "Success", serializer.data)
        else:
            return api_response("Update failed", 400, "Failed", serializer.errors)

    def delete(self, request, id):
        """
        This endpoint deletes a customer record from the database.
        """
        if customer := self.get_object(id):
            customer.delete()
            return api_response("User deleted successfully", 204, "Success")
        else:
            return api_response("Invalid User ID", 404, "Failed")


class ServiceProviderRegister(APIView):
    serializer_class = ServiceProviderRegistrationSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        This endpoint returns list of services registered. You can also filter with location (i.e, state and city), and category.
        """
        state = request.GET.get("state", None)
        city = request.GET.get("city", None)
        service_category = request.GET.get("category", None)
        if state is None and city is None and service_category is None:
            users_objs = get_list_or_404(User, role="service_provider")
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is not None and city is None and service_category is None:
            users_objs = get_list_or_404(User, role="service_provider", state=state)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is not None and city is not None and service_category is None:
            users_objs = get_list_or_404(User, role="service_provider", state=state, city=city)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is None and city is not None and service_category is None:
            users_objs = get_list_or_404(User, role="service_provider", city=city)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is None and city is not None and service_category is not None:
            users_objs = get_list_or_404(User, role="service_provider", city=city, service_category=service_category)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is not None and city is None and service_category is not None:
            users_objs = get_list_or_404(User, role="service_provider", city=city, service_category=service_category)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        elif state is None and city is None and service_category is not None:
            users_objs = get_list_or_404(User, role="service_provider", service_category=service_category)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        else:
            users_objs = get_list_or_404(User, role="service_provider", city=city, state=state, service_category=service_category)
            users_serilizer = ServiceProviderRegistrationSerializer(users_objs, many=True)
            data = {
                "message": "Successfully retrieved service_providers",
                "data": users_serilizer.data,
            }
        return api_response(data["message"], 200, "Success", data["data"])

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint creates a new service provider record in the database.
        """
        s_c = request.data.pop("service_category")
        data = request.data

        if "profile_picture" in data.keys():
            data["profile_picture"] = (UploadUtil.upload_profile_picture(data["profile_picture"], email=data["email"]))
        serializer = ServiceProviderRegistrationSerializer(data=data)

        category = Category.objects.filter(name__iexact=s_c['name'])
        if category.exists():
            service_category = category.first()
        else:
            service_category = Category.objects.create(name=s_c)

        if serializer.is_valid():
            serializer.save(service_category=service_category)

            user_data = request.data
            return_data = AuthUtil.send_verification_link(user_data, request, serializer)
            if return_data != None:
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

    def get(self, request, id):
        """
        This endpoint returns a single service detail. 
        You can get the service by either their id or their name(business name).
        """
        name = request.GET.get("city", None)
        if id is not None and name is None:
            try:
                service_provider = User.objects.get(id=id)
                serializer = ServiceProviderSerializer(service_provider)
                return api_response("Service provider found", 200, "Success", serializer.data)
            except User.DoesNotExist:
                api_response("Service provider not found", 404, "Failed")
        elif id is None and name is not None:
            try:
                service_provider = User.objects.get(business_name=name)
                serializer = ServiceProviderSerializer(service_provider)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return api_response("Service provider not found", 404, "Failed")
        else:
            return api_response("Service provider not found", 404, "Failed")
          
    def put(self, request, id):
        """
        This endpoint updates a service info
        """
        service_provider = User.objects.get(email=request.user.email)
        data= request.data
        if "profile_picture" in data.keys():
            data["profile_picture"] = (UploadUtil.upload_profile_picture(data["profile_picture"], email = service_provider.email))["image_url"]
        upload = update_service_provider((self.serializer_class(service_provider)).data, data)
        serializer = ServiceProviderSerializer(service_provider, data=upload)
        if serializer.is_valid():
            serializer.save()
            return api_response("Update successful", 202, "Success", serializer.data)
        else:
            return api_response("Update failed", 400, "Failed", serializer.errors)

    def delete(self, request, id):
        """
        This endpoint deletes a specified service from the database.
        """
        try:
            service_provider = User.objects.get(id=id)
        except User.DoesNotExist:
            return api_response("Invalid User ID", 404, "Failed")
        service_provider.delete()
        return api_response("User deleted successfully", 204, "Success")


class VerifyEmail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        This endpoint verifies a user's email token.
        """
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_verified:
                user.is_verified = True
                user.email_verification = True
                user.save()

            return api_response("User email verified successfully", 200, "Success")
        except jwt.ExpiredSignatureError:
            return api_response("Verification link expired", 400, "Failed")
        except jwt.exceptions.DecodeError:
            return api_response("Invalid token", 400, "Failed")

class GetOTP(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        This endpoint sends OTP to users.
        """
        user = get_object_or_404(User, id=request.user.id)
        phone_number = user.phone_number.raw_input
        
        if  phone_number is not None:
            if (sent_otp := AuthUtil.otp_session(phone_number)):
                request.session['num'] = phone_number
                request.session['code'] = sent_otp
                return api_response(
                        status_code=200,
                        message="OTP sent successfully",
                        status="Success",
                    )
            return api_response(
                status_code=404, 
                message="Sending OTP Error",
                status="Failed"
            )
        return api_response(
            status_code=400,
            message="Phone number is Invalid",
            status='Check Number'
        )

class VerifyPhone(APIView):
    serializer_class = VerificationSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint verfies users' phone number.
        """
        user = get_object_or_404(User, id=request.user.id)
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data.get('otp')
            
            if not user.phone_verification:
                try:
                    session_code = request.session.pop('code')
                    
                    if str(otp_code) == str(session_code):
                        user.phone_verification = True
                        user.save()
                        return api_response(status_code=200,
                            message="OTP Code Verified",
                            status="Success")                    
                    return api_response(status_code=400,
                            message="OTP Incorrect!",
                            status='Failed')              
                except KeyError:
                    return api_response(
                        status_code=404,
                        message="OTP code expired",
                        status='Failed'
                    )

            return api_response(status_code=400,
                message="Phone number already validated",
                status='Already Verified')

        return api_response(
            status_code=400,
            message="Error!",
            status='Failed'
        )

class UpdatePhone(APIView):
    serializer_class = UpdatePhoneSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint updates user's phone number.
        """
        user = get_object_or_404(User, id=request.user.id)

        serializer = UpdatePhoneSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data.get('otp')
            new_number = serializer.validated_data.get('number')
        
            if not User.objects.filter(phone_number__iexact=new_number).exists():
                if not "code" in request.session.keys():            
                    return api_response(
                        status_code=400,
                        message="Generate New OTP",
                        status='Failed'
                    )
                else:
                    try:
                        session_code = request.session.pop('code')
                    
                        if str(otp_code) == str(session_code):
                            user.phone_verification = True
                            user.phone_number = new_number
                            user.save()
                        return api_response(status_code=200,
                            message="Phone number changed sucessfully",
                            status="Success") 
                    except KeyError:
                        return api_response(
                            status_code=403,
                            message="OTP code expired",
                            status='Failed')                                
            return api_response(
                status_code=400,
                message="Phone number already Exist",
                status='Failed')
        return api_response(
            status_code=400,
            message="Error!",
            status='Failed'
        )

class CustomerLogin(APIView):
    serializer_class = EmailLoginSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint logs customers in with their email/phone number and password.
        """
        if ("email" in request.data.keys() and "password" in request.data.keys()) or ("phone_number" in request.data.keys() and "password" in request.data.keys()):
            pass
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")
        if "email" in request.data.keys():
            try:
                user = User.objects.get(email=request.data["email"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        elif "phone_number" in request.data.keys():
            try:
                user = User.objects.get(phone_number=request.data["phone_number"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")
        if user.role == "customer":
            response = AuthUtil.create_token(request,
                email=user.email, password=request.data["password"]
            )
            if "error" in response.keys():
                return api_response(response["error"], 400, "Failed")
            else:
                return api_response(
                    status_code=200,
                    message="Login successful",
                    data=response,
                    status="Success",
                )
        else:
            return api_response("You're not a customer. Try the logging in as a service provider", 400, "Failed")

class SPLogin(APIView):
    serializer_class = EmailLoginSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """
        This endpoint logs service providers in with their email/phone number and password.
        """
        if ("email" in request.data.keys() and "password" in request.data.keys()) or ("phone_number" in request.data.keys() and "password" in request.data.keys()):
            pass
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")
        if "email" in request.data.keys():
            try:
                user = User.objects.get(email=request.data["email"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        elif "phone_number" in request.data.keys():
            try:
                user = User.objects.get(phone_number=request.data["phone_number"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")

        if user.role == "service_provider":
            response = AuthUtil.create_token(request,
                email=user.email, password=request.data["password"]
            )
            if "error" in response.keys():
                return api_response(response["error"], 400, "Failed")
            else:
                return api_response(
                    status_code=200,
                    message="Login successful",
                    data=response,
                    status="Success",
                )
        else:
            return api_response("You're not a service provider. Try the logging in as a customer", 400, "Failed")

class ServiceProviderLogin(APIView):
    serializer_class = EmailLoginSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        """This endpoint logs services in with their email/phone number and password.
        """
        if ("email" in request.data.keys() and "password" in request.data.keys()) or ("phone_number" in request.data.keys() and "password" in request.data.keys()):
            pass
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")
        if "email" in request.data.keys():
            print("email")
            try:
                user = User.objects.get(email=request.data["email"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        elif "phone_number" in request.data.keys():
            print("phone")
            try:
                user = User.objects.get(phone_number=request.data["phone_number"])
            except User.DoesNotExist:
                return api_response("Invalid login details", 400, "Failed")
        else:
            return api_response("Please enter your email/phone number and password.", 400, "Failed")
        if user.role == "service_provider":
            response = AuthUtil.create_token(
                email=user.email, password=request.data["password"]
            )
            if "error" in response.keys():
                return api_response(response["error"], 400, "Failed")
            else:
                return api_response(
                    status_code=200,
                    message="Login successful",
                    data=response,
                    status="Success",
                )
        else:
            return api_response("You're not a service provider. Try the logging in as a customer", 400, "Failed")

class RefreshToken(APIView):
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        """
        This endpoint generates a new accesstoken for users.
        """
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
            response = AuthUtil.refresh_token(refresh=request.data.get("refresh"))
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
        """
        This endpoint changes the user's password.
        """
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
            password_validity = AuthUtil.validate_password(password=password)
            if password_validity["status"]:
                if password == password2:
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.save()
                    return api_response("Password changed successfully", 202, "Success")
                else:
                    return api_response("Passwords do not match", 400, "Failed")
            return api_response(password_validity["message"], 400, "Failed")
        else:
            return api_response("Incorrect password", 400, "Failed")

class ResetPasswordEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        This endpoint sends a reset token to users' emails.
        """
        email = request.data["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            relative_link = reverse("reset_password")

            current_site = request.get_host()
            absolute_url = f"{HTTP}{current_site}{relative_link}"

            email_body = f"""Hi, {(user.first_name).title}\n\nUse the link below to verify your email.\n{absolute_url}"""
            data = {
                "subject": "Verify your email",
                "message": email_body,
                "recipients": [user.email],
            }

            sent = AuthUtil.gmail_send_email(data)

            if sent:
                return api_response("Password Reset email sent", 200, "Success")
            else:
                return api_response("An error occured", 400, "Failed")
        else:
            return api_response("Invalid user email", 406, "Failed")

class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        This endpoint resets a user's password.
        """
        email = request.data["email"]
        password = request.data["password"]
        password2 = request.data["password2"]

        password_validity = AuthUtil.validate_password(password)

        if password_validity["status"]:
            if password2 == password:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.save()

                    return api_response("Password reset successful", 200, "Success")
                except Exception as e:
                    return api_response(str(e), 400, "Failed")
            else:
                return api_response("Passwords do not match", 400, "Failed")
        else:
            return api_response(password_validity["message"], 400, "Failed")

class DecodeToken(APIView):
    def post(self, request):
        token = request.data['token']
        data = jwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])
        user = UserSerializer(User.objects.get(id=data["user_id"])).data
        return api_response(status_code=200, message="successful", status="success", data=user)

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

class ServiceProviderGalleryUpload(APIView):
    queryset = User.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        """
        This endpoint updates services' galleries.
        """
        service_provider = User.objects.get(email=request.user.email)
        incoming = request.data
        
        if "image1" in request.data.keys():
            incoming["image1"] = (UploadUtil.upload_gallery_image(incoming["image1"], business_name=service_provider.business_name, image_index=1))["image_url"]
        else:
            incoming["image1"] = service_provider.gallery[0]
        if "image2" in request.data.keys():
            incoming["image2"] = (UploadUtil.upload_gallery_image(incoming["image2"], business_name=service_provider.business_name, image_index=2))["image_url"]
        else:
            incoming["image2"] = service_provider.gallery[1]
        if "image3" in request.data.keys():
            incoming["image3"] = (UploadUtil.upload_gallery_image(incoming["image3"], business_name=service_provider.business_name, image_index=3))["image_url"]
        else:
            incoming["image3"] = service_provider.gallery[2]
        if "image4" in request.data.keys():
            incoming["image4"] = (UploadUtil.upload_gallery_image(incoming["image4"], business_name=service_provider.business_name, image_index=4))["image_url"]
        else:
            incoming["image4"] = service_provider.gallery[3]
        if "image5" in request.data.keys():
            incoming["image5"] = (UploadUtil.upload_gallery_image(incoming["image5"], business_name=service_provider.business_name, image_index=5))["image_url"]
        else:
            incoming["image5"] = service_provider.gallery[4]
        
        data = {
            "gallery": [incoming["image1"],incoming["image2"],incoming["image3"],incoming["image4"],incoming["image5"],]
        }
        upload = update_service_provider((self.serializer_class(service_provider)).data, data)
        serializer = self.serializer_class(service_provider, data=upload)
        if serializer.is_valid():
            serializer.save()
            return api_response("Gallery updated", 202, "Success", serializer.data)
        else:
            return api_response("Gallery not updated", 400, "Failed", serializer.errors)

class ServiceProviderDocumentUpload(APIView):
    queryset = User.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        """
        This endpoints updates services' documents.
        """
        service_provider = User.objects.get(email=request.user.email)
        print(request.data)
        incoming = request.data
        if "card_front" in incoming.keys():
            incoming["card_front"] = (UploadUtil.upload_document_image(incoming["card_front"], "card_front", business_name=service_provider.business_name))["image_url"]
        if "card_back" in incoming.keys():
            incoming["card_back"] = (UploadUtil.upload_document_image(incoming["card_back"], "card_back", business_name=service_provider.business_name))["image_url"]
        if "pob" in incoming.keys():
            incoming["pob"] = (UploadUtil.upload_document_image(incoming["pob"], "pob", business_name=service_provider.business_name))["image_url"]
        
        upload = update_service_provider((self.serializer_class(service_provider)).data, incoming)

        serializer = self.serializer_class(service_provider, data=upload)
        if serializer.is_valid():
            serializer.save()
            return api_response("Document uploaded", 202, "Success", serializer.data)
        else:
            return api_response("Document not uploaded", 400, "Failed", serializer.errors)

class ResendVerification(APIView):
    pass

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

