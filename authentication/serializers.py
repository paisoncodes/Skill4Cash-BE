from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator
from .models import User
from phonenumber_field.modelfields import PhoneNumberField
from src.utils import Utils


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "username",
            "role",
            "location",
        )


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[Utils.validate_user_password],
        help_text=""" Password must be at least 8 characters 
                        and must contain at least one uppercase letter, 
                        one smaller letter, one digit, and one special character.
                    """,
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "location",
            "verified",
            "email_verification",
            "phone_verification",
            "role",
            "fullname",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        read_only_fields = [
            "verified",
            "role",
            "email_verification",
            "phone_verification",
            "fullname",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"Password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        del validated_data["confirm_password"]
        user = User.objects.create_user(**validated_data, role="customer")
        return user
    
    def get_fullname(self, obj):
        if hasattr(obj, 'id'):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, 'id'):
            return obj.verified
        return None

class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[Utils.validate_user_password],
        help_text=""" Password must be at least 8 characters 
                        and must contain at least one uppercase letter, 
                        one smaller letter, one digit, and one special character.
                    """,
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "location",
            "verified",
            "email_verification",
            "phone_verification",
            "role",
            'fullname',
            "business_name",
            "is_verified_business",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "business_name": {"required": True},
        }
        read_only_fields = [
            "verified",
            "role",
            "email_verification",
            "phone_verification",
            "is_verified_business",
        ]


    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"Password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        del validated_data["confirm_password"]
        user = User.objects.create_user(**validated_data, role="service_provider")
        return user

    def get_fullname(self, obj):
        if hasattr(obj, 'id'):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, 'id'):
            return obj.verified
        return None

class CustomerSerializer(serializers.ModelSerializer):
    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "location",
            "verified",
            "email_verification",
            "phone_verification",
            "role",
            "fullname",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        read_only_fields = [
            "verified",
            "role",
            "fullname",
            "email_verification",
            "phone_verification",
        ]

    
    def get_fullname(self, obj):
        if hasattr(obj, 'id'):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, 'id'):
            return obj.verified
        return None

class ServiceProviderSerializer(serializers.ModelSerializer):

    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "location",
            "business_name",
            "service_category",
            'keywords',
            'gallery',
            "card_front",
            "card_back",
            "pob",
            "role",
            "fullname",
            "verified",
            "email_verification",
            "phone_verification",
            "is_verified_business",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "business_name": {"required": True},
        }
        read_only_fields = [
            "verified",
            "role",
            "fullname",
            "email_verification",
            "phone_verification",
            "is_verified_business",
        ]

    def get_fullname(self, obj):
        if hasattr(obj, 'id'):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, 'id'):
            return obj.verified
        return None


class VerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)


class UpdatePhoneSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)
    number = serializers.CharField(required=True, write_only=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)