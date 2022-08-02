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
            "is_verified",
            "email_verification",
            "phone_verification",
            "role",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        read_only_fields = [
            "is_verified",
            "role",
            "email_verification",
            "phone_verification",
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
            "is_verified",
            "email_verification",
            "phone_verification",
            "role",
            "sp_id",
            "business_name",
            "is_verified_business",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "business_name": {"required": True},
        }
        read_only_fields = [
            "is_verified",
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


class CustomerSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    sp_id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "location",
            "is_verified",
            "email_verification",
            "phone_verification",
            "role",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        read_only_fields = [
            "is_verified",
            "role",
            "email_verification",
            "phone_verification",
        ]


class ServiceProviderSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    sp_id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "location",
            "is_verified",
            "email_verification",
            "phone_verification",
            "role",
            "sp_id",
            "business_name",
            "is_verified_business",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "business_name": {"required": True},
        }
        read_only_fields = [
            "is_verified",
            "role",
            "email_verification",
            "phone_verification",
        ]


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