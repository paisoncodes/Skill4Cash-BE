from django.http.response import Http404, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from .serializers import (
    CustomerRegistrationSerializer,
    SPRegistrationSerializer
)
from .models import (
    User,
    ServiceProvider
)
from rest_framework_simplejwt.tokens import RefreshToken
from src.utils import Utils
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

class HelloView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        return Response({'message': f"welcome {user}"})


class CustomerRegister(APIView):
    permission_classes=(AllowAny,)

    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer
    
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            user_data = serializer.data

            user = User.objects.get(email=user_data['email'])
                
            token = RefreshToken.for_user(user).access_token
            
            relative_link = reverse("verify_email")
                
            current_site = get_current_site(request).domain

            absolute_url = f"http://{current_site}{relative_link}?token={str(token)}"

            email_body = f"Hi, {user.first_name},\n    Use the link below to verify your email.\n              {absolute_url}"

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email
            }

            Utils.send_email(data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Not in use yet. Still needs to be fixed.
class CustomerRetrieveUpdateDelete(APIView):
    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer

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
            serializer = CustomerRegistrationSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })
    
    def delete(self, id, request):
        customer = User.objects.get(id=id)
        if customer:
            customer.delete()
            return Response({
                "message": "User deleted successfully",
                "status": status.HTTP_204_NO_CONTENT
            })
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })


class ServiceProviderRegister(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer
    permission_classes = (AllowAny,)

    
    def post(self, request):
        serializer = SPRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data

            user = User.objects.get(email=user_data['email'])
                
            token = RefreshToken.for_user(user).access_token
            
            relative_link = reverse("verify_email")
                
            current_site = get_current_site(request).domain

            absolute_url = f"http://{current_site}{relative_link}?token={str(token)}"

            email_body = f"Hi, {user.first_name},\n    Use the link below to verify your email.\n              {absolute_url}"

            data = {
                "email_subject": "Verify your email",
                "email_body": email_body,
                "to_email": user.email
            }

            Utils.send_email(data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Not in use yet. Still needs to be fixed.
class ServiceProviderRetrieveUpdateDelete(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer

    def get(self, id, request):

        customer = ServiceProvider.objects.get(id=id)
        serializer = SPRegistrationSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, id, request):
        customer = ServiceProvider.objects.get(id=id)
        if customer:
            serializer = SPRegistrationSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })
    
    def delete(self, id, request):
        customer = ServiceProvider.objects.get(id=id)
        if customer:
            customer.delete()
            return Response({
                "message": "User deleted successfully",
                "status": status.HTTP_204_NO_CONTENT
            })
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })
class VerifyEmail(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response(
                {"email": "user email verified successfully"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Verification link expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )