from rest_framework import serializers
from .models import *



class BaseUserSerializer(serializers.Serializer):
    class Meta:
        model = BaseUserModel
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_verified"
        ]

class ServiceProviderSerializer(serializers.Serializer):
    class Meta:
        model = ServiceProvider
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "business_name",
            "is_verified"
        ]