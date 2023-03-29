from uuid import uuid4
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator

from services.serializers import CategorySerializer
from utils.models import Lga, State
from .models import BusinessProfile, TestImageUpload, User, UserProfile
from phonenumber_field.modelfields import PhoneNumberField
from utils.utils import AuthUtil


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
            "state",
            "city",
            "profile_picture",
        )


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    state = serializers.CharField()
    lga = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "state", "lga", "phone_number", "password"]
    
    def create(self, validated_data):
        data = validated_data.copy()
        validated_data.pop('first_name')
        validated_data.pop('last_name')
        data["state"] = State.objects.get(state__iexact=validated_data.pop('state'))
        data["lga"] = Lga.objects.get(lga__iexact=validated_data.pop('lga'))
        validated_data.pop('phone_number')

        user = User.objects.create_user(**validated_data)
        data.pop('email')
        data.pop('password')
        data["user"] = user
        data["user_type"] = UserProfile.UserType.CUSTOMER

        UserProfile.objects.create(**data)

        return user


class PhotoSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    id = serializers.CharField(default=uuid4, read_only=True)


class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    state = serializers.CharField()
    lga = serializers.CharField()
    profile_picture = serializers.URLField()
    business_name = serializers.CharField()
    service_category = serializers.CharField()
    gallery_photos = serializers.ListField(child=PhotoSerializer(), required=False)
    keywords = serializers.ListField(child=serializers.IntegerField())
    description = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "state", "lga", "profile_picture", "phone_number", "password", "business_name", "service_category", "gallery_photos", "keywords", "description"]
    
    def create(self, profile_data):
        business_profile = {}
        business_profile["user"] = profile_data["user"] = user = User.objects.filter(id=profile_data["user"])

        user.set_password(profile_data.pop("password"))

        business_profile["business_name"] = profile_data.pop('business_name')
        business_profile["service_category"] = profile_data.pop('service_category')
        business_profile["gallery_photos"] = profile_data.pop('gallery_photos')
        business_profile["keywords"] = profile_data.pop('keywords')
        business_profile["description"] = profile_data.pop('description')
        profile_data["user_type"] = UserProfile.UserType.SERVICE_PROVIDER

        profile = UserProfile.objects.create(**profile_data)

        BusinessProfile.objects.create(**business_profile)

        

        return profile

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )

    class Meta:
        model = UserProfile
        exclude = (
            "user",
            "id",
            "date_created",
            "last_update"
        )
        
    def get_user_email(self, instance):
        return instance.user.email
    
class UserBusinessProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )

    class Meta:
        model = BusinessProfile
        exclude = (
            "user",
            "id",
            "date_created",
            "last_update"
        )
        
    def get_user_email(self, instance):
        return instance.user.email

class CustomerSerializer(serializers.ModelSerializer):
    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "state",
            "city",
            "profile_picture",
            "verified",
            "email_verification",
            "phone_verification",
            "role",
            "fullname",
        )
        read_only_fields = [
            "verified",
            "role",
            "fullname",
            "email_verification",
            "phone_verification",
        ]

    def get_fullname(self, obj):
        if hasattr(obj, "id"):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, "id"):
            return obj.verified
        return None


class ServiceProviderSerializer(serializers.ModelSerializer):

    verified = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "state",
            "city",
            "business_name",
            "service_category",
            "profile_picture",
            "keywords",
            "gallery",
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

    # def update(self, instance, validated_data):
    #     if "gallery" in validated_data.keys():

    #     return super().update(instance, validated_data)
    def get_fullname(self, obj):
        if hasattr(obj, "id"):
            return obj.get_full_name()
        return None

    def get_verified(self, obj):
        if hasattr(obj, "id"):
            return obj.verified
        return None


class VerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)


class UpdatePhoneSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)
    number = serializers.CharField(required=True, write_only=True)


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField()
    password = serializers.CharField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    user_type = serializers.CharField()

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class TestImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestImageUpload
        fields = ["name", "image1", "image2", "image3"]

