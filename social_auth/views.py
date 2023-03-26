from utils.utils import api_response
from authentication.models import User
from social_auth.google import Google
from social_auth.facebook import Facebook
from rest_framework.generics import GenericAPIView
from social_auth.register import register_social_user
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

        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            validated_token = serializer.validated_data.get('access_token')
            validated_state = serializer.validated_data.get('state')
            validated_city = serializer.validated_data.get('city')
            validated_role = serializer.validated_data.get('role')

            user_data = Facebook.fb_validate(validated_token)
            if user_data is None:
                raise AuthenticationFailed('Invalid or Expired Token.')
            
            usn = user_data['email'].split('@')[0]
            user_info = register_social_user(
                            provider='facebook', email=user_data['email'],
                            first_name=user_data['first_name'],last_name=user_data['last_name'], 
                            username=usn, state=validated_state,
                            city=validated_city, role=validated_role.lower())
            
            if User.objects.get(email=user_data['email']).role[0] == 's':
                message = "Service Provider Successfully Created or Logged In"
            else:
                message = "Customer Successfully Created or Logged In"
            return api_response(
                    status_code=200, message=message,
                    data=user_info, status="Success")

