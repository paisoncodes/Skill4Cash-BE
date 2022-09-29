from django.conf import settings
from rest_framework import serializers

class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    access_token = serializers.CharField(required=True)
    state = serializers.CharField(required=False, max_length=20)
    city = serializers.CharField(required=False, max_length=20)
    role = serializers.CharField(required=True, max_length=15)

    def validate(self, attrs):

        roles = ['customer','service_provider', "service provider"]
        
        if attrs["role"].lower() not in roles:
            raise serializers.ValidationError({"Roles": "Invalid role selected."})
        return attrs

class GoogleSocialAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    state = serializers.CharField(required=False, max_length=20, default='Lagos')
    city = serializers.CharField(required=False, max_length=20, default='Lagos')
    role = serializers.CharField(required=True, max_length=15)
    
    def validate(self, attrs):

        validated_role = attrs["role"]
        roles = ['customer','service_provider', "service provider"]
        
        if validated_role.lower() not in roles:
            raise serializers.ValidationError({"Roles": "Invalid role selected."})
        return attrs