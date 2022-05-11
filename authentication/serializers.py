from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User, RoleEnum, ServiceProvider


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
        write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number',
                  'password', 'confirm_password', 'location')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        read_only_fields = ['is_verified', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"Password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        # del validated_data['confirm_password']
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            location=validated_data["location"],
            role=RoleEnum.CUSTOMER.value
        )
        user.save()

        return user


class SPRegistrationSerializer(serializers.ModelSerializer):
    user = CustomerRegistrationSerializer()

    class Meta:
        model = ServiceProvider
        fields = ('user', 'business_name', 'is_verified')
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
