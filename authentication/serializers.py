import phonenumbers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from . import models


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=models.User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    
    class Meta:
        model = models.User
        fields = ('password', 'password2', 'email', 'first_name', 'last_name', 'phone_number','location','role','is_verified')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        read_only_fields = ['is_verified','role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"Password": "Password fields didn't match."})

        return attrs
    
    def create(self, validated_data):
        del validated_data['password2']
        user = models.User.objects.create_user(role=models.RoleEnum.CUSTOMER, **validated_data)
        user.save()

        return user

class SPRegistrationSerializer(serializers.ModelSerializer):
    user = CustomerRegistrationSerializer()
    class Meta:
        model = models.ServiceProvider
        fields = ('user', 'business_name','is_verified')
        read_only_fields = ['is_verified']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'business_name': {'required': True}
        }
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        del user_data['password2']
        user_obj = models.User.objects.create_user(**user_data, role = models.RoleEnum.SERVICE_PROVIDER.value)        
        service_provider = models.ServiceProvider.objects.create(**validated_data, user=user_obj)
        service_provider.save()
        return service_provider