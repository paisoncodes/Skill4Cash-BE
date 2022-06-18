from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator
from .models import User, RoleEnum, ServiceProvider
from phonenumber_field.modelfields import PhoneNumberField
from src.utils import Utils


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'phone_number', 'username', 'role', 'location')

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[Utils.validate_user_password],
        help_text=""" Password must be at least 8 characters 
                        and must contain at least one uppercase letter, 
                        one smaller letter, one digit, and one special character.
                    """)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'confirm_password',
            'location',
            'is_verified',
            'email_verification',
            'phone_verification',
            'role'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        read_only_fields = ['is_verified', 'role',
                            'email_verification', 'phone_verification']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"Password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        del validated_data['confirm_password']
        user = User.objects.create_user(
            **validated_data, 
            role=RoleEnum.CUSTOMER.value
        )
        return user

class CustomerSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'location',
            'is_verified',
            'email_verification',
            'phone_verification',
            'role'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        read_only_fields = ['is_verified', 'role',
                            'email_verification', 'phone_verification']

class SPRegistrationSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    user = CustomerRegistrationSerializer()
    sp_id = serializers.CharField(source='pk', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ('user', 'sp_id', 'business_name', 'is_verified_business')
        read_only_fields = ['is_verified_business',]
        extra_kwargs = {
            'business_name': {'required': True}
        }

    def create(self, validated_data):

        user_data = validated_data.pop('user')
        user_data.pop('confirm_password')
        user_obj = User.objects.create_user(**user_data, role=RoleEnum.SERVICE_PROVIDER.value)
        service_provider = ServiceProvider.objects.create(**validated_data, user=user_obj)
        return service_provider

class SPSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(unique=True)
    user = CustomerSerializer()
    sp_id = serializers.CharField(source='pk', read_only=True)
    
    class Meta:
        model = ServiceProvider
        fields = ('user','sp_id', 'business_name', 'is_verified_business')
        read_only_fields = ['is_verified_business']
        extra_kwargs = {
            'business_name': {'required': True}
        }

    def update(self, instance, validated_data):
        user = validated_data.pop('user')
        user_ins = instance.user
        user_ins.email = user.get('email', user_ins.email)
        user_ins.first_name = user.get('first_name', user_ins.first_name)
        user_ins.last_name = user.get('last_name', user_ins.last_name)
        user_ins.location = user.get('location', user_ins.location)
        instance.business_name = validated_data.get('business_name', instance.business_name)
        user_ins.save()

        return instance

class VerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)


class UpdatePhoneSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, write_only=True)
    number = serializers.CharField(required=True, write_only=True)