from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator
from .models import User, RoleEnum, ServiceProvider
from src.utils import Utils


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'phone_number', 'username', 'role', 'location')


class CustomerRegistrationSerializer(serializers.ModelSerializer):
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
        del validated_data['password']
        del validated_data['confirm_password']
        user = User.objects.create(
            **validated_data, role=RoleEnum.CUSTOMER.value
        )
        return user


class CustomerRegistrationSerializerUpdate(serializers.ModelSerializer):
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
    user = CustomerRegistrationSerializer()
    sp_id = serializers.CharField(source='pk', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ('user', 'sp_id', 'business_name', 'is_verified')
        read_only_fields = ['is_verified']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'business_name': {'required': True}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # del user_data['password2']
        user_obj = User.objects.create_user(**user_data, role=RoleEnum.SERVICE_PROVIDER.value)
        service_provider = ServiceProvider.objects.create(**validated_data, user=user_obj)
        service_provider.save()
        return service_provider
