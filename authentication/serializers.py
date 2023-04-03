from uuid import uuid4
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator

from services.serializers import CategorySerializer
from utils.models import Category, Keyword, Lga, State
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


class CustomerProfileSetUpSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    state = serializers.CharField()
    lga = serializers.CharField()
    user = serializers.UUIDField()

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "state", "lga", "phone_number", "password", "user"]
    
    def create(self, validated_data):
        validated_data["user"] = user = User.objects.filter(id=validated_data["user"]).first()
        validated_data["user_type"] = UserProfile.UserType.CUSTOMER

        user.set_password(validated_data.pop("password"))

        profile = UserProfile.objects.create(**validated_data)

        return profile


class PhotoSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    id = serializers.CharField(default=uuid4, read_only=True)

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ServiceProviderProfileSetUpSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    state = serializers.CharField()
    lga = serializers.CharField()
    business_name = serializers.CharField()
    service_category = serializers.CharField()
    gallery_photos = serializers.ListField(child=PhotoSerializer(), required=False)
    keywords = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField()
    user = serializers.UUIDField(required=False)

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "state", "lga", "profile_picture", "phone_number", "password", "business_name", "service_category", "gallery_photos", "keywords", "description", "user"]
    
    def create(self, validated_data):
        business_profile = {}
        business_profile["user"] = validated_data["user"] = user = User.objects.filter(id=validated_data["user"]).first()

        user.set_password(validated_data.pop("password"))

        user.save()

        business_profile["business_name"] = validated_data.pop('business_name')
        service_category = validated_data.pop('service_category')
        category, created = Category.objects.get_or_create(name=service_category)
        business_profile["service_category"] = category
        business_profile["gallery"] = validated_data.pop('gallery_photos')
        keywords = validated_data.pop('keywords')
        business_profile["description"] = validated_data.pop('description')
        validated_data["state"] = State.objects.get(state__iexact=validated_data['state'])
        validated_data["lga"] = Lga.objects.get(lga__iexact=validated_data['lga'])
        validated_data["user_type"] = UserProfile.UserType.SERVICE_PROVIDER

        profile, created = UserProfile.objects.get_or_create(**validated_data)

        business, created = BusinessProfile.objects.get_or_create(**business_profile)

        for keyword in keywords:
            word, created = Keyword.objects.get_or_create(keyword=keyword)
            business.keywords.add(word)
        business.save()

        

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
    
class UserProfileViewSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )
    state = serializers.StringRelatedField()
    lga = serializers.StringRelatedField()

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
    
class UserBusinessProfileViewSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )
    service_category = serializers.StringRelatedField()
    keywords = serializers.StringRelatedField(many=True)

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
    
class UserBusinessProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )
    service_category = serializers.StringRelatedField()
    keywords = serializers.StringRelatedField(many=True)

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
class UserBusinessProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(
        read_only=True, method_name="get_user_email"
    )
    service_category = serializers.StringRelatedField()
    keywords = serializers.StringRelatedField(many=True)

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


class VerifyTokenSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.EmailField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    user_type = serializers.CharField()

class ResendTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class SendPhoneOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(help_text="Example: 2348012345678")


class VerifyPhoneOtpSerializer(serializers.Serializer):
    code = serializers.IntegerField()

class TestImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestImageUpload
        fields = ["name", "image1", "image2", "image3"]

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"

class LgaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lga
        fields = "__all__"
