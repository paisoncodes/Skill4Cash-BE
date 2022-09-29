from django.conf import settings
from src.utils import api_response
from . google import Google
from authentication.models import User
from .register import register_social_user
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import AuthenticationFailed
from .serializers import GoogleSocialAuthSerializer, FacebookSocialAuthSerializer


class GoogleSocialAuthView(GenericAPIView):

    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """
        POST with "id_token"
        Send an idtoken as from google to get user information
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            validated_token = serializer.validated_data.get('id_token')
            validated_state = serializer.validated_data.get('state')
            validated_city = serializer.validated_data.get('city')
            validated_role = serializer.validated_data.get('role')

            user_data = Google.gg_validate(validated_token)
            if user_data is None:
                raise AuthenticationFailed('Invalid or Expired Token.')
            
            usn = user_data['email'].split('@')[0]
            user_info = register_social_user(provider='google', email=user_data['email'], 
                                            first_name='John', last_name="Doe", username=usn,
                                            role=validated_role.lower(),state=validated_state, 
                                            city=validated_city)
            if User.objects.get(email=user_data['email']).role[0] == 's':
                message = "Service Provider Successfully Created or Logged In"
            else:
                message = "Customer Successfully Created or Logged In"
            return api_response(
                    status_code=200, message=message,
                    data=user_info, status="Success")


class FacebookSocialAuthView(GenericAPIView):

    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an access token as from facebook to get user information
        """

        serializer = FacebookSocialAuthSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            # authenticate user
            return api_response(
                    status_code=200,
                    message="Customer created successfully",
                    data=data,
                    status="Success",
                )
        return api_response(
                status_code=400,
                message=serializer.errors,
                status="Failed",
            )


