from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



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
        user = models.User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data["phone_number"],
            role=models.RoleEnum.CUSTOMER
        )

        
        user.set_password(validated_data['password'])
        user.save()

        return user

class SPRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=models.ServiceProvider.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = models.ServiceProvider
        fields = ('password', 'password2', 'email', 'first_name', 'last_name', 'phone_number','business_name','is_verified')
        read_only_fields = ['is_verified']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'business_name': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"Password": "Password fields didn't match."})

        return attrs
    
    def create(self, validated_data):
        service_provider = models.ServiceProvider.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data["phone_number"],
            business_name=validated_data["business_name"],
            role=models.RoleEnum.SERVICE_PROVIDER
        )

        
        service_provider.set_password(validated_data['password'])
        service_provider.save()

        return service_provider