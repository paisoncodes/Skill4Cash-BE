from django.conf import settings
from rest_framework import serializers

class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    auth_token = serializers.CharField(required=True)
    state = serializers.CharField(required=False, max_length=20)
    city = serializers.CharField(required=False, max_length=20)
    role = serializers.CharField(required=True, max_length=20)

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.fb_validate(auth_token)
        try:
            phone_number = None
            state = None
            city = None
            email = user_data['email']
            name = user_data['name'].split(' ')
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                email=email,
                first_name=name[0],
                last_name=name[-1],
                phone_number=phone_number,
                state=state,
                city=city,
                role=role
            )
        except Exception as e:
            raise serializers.ValidationError(
                'The token as expired, Please login in again.'
            )

    def validate(self, attrs):

        roles = ['customer','service_provider']
        
        if attrs["role"].lower() not in roles:
            raise serializers.ValidationError(
                {"Roles": "Invalid role selected."}
            )
        return attrs

class GoogleSocialAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    state = serializers.CharField(required=False, max_length=20, default='Lagos')
    city = serializers.CharField(required=False, max_length=20, default='Lagos')
    role = serializers.CharField(required=True)
    
    def validate(self, attrs):
        
        validated_role = attrs["role"]

        roles = ['customer','service_provider', "service provider"]
        
        if validated_role.lower() not in roles:
            raise serializers.ValidationError({"Roles": "Invalid role selected."})
        
        return attrs