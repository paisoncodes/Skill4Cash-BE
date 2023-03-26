from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.db import models
from django.contrib.postgres.fields import JSONField
from utils.models import BaseModel, Category, Lga, State




class User(AbstractUser, BaseModel):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(
        max_length=100, default="Username", blank=True, null=True
    )
    phone_number = PhoneNumberField(unique=True)
    
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"


class UserProfile(BaseModel):

    class UserRole(models.TextChoices):
        SERVICE_PROVIDER = 'service_provider', "SERVICE_PROVIDER"
        CUSTOMER = 'customer', "CUSTOMER"

    class AuthProvider(models.TextChoices):
        FACEBOOK = 'facebook', "FACEBOOK"
        GOOGLE = 'google', "GOOGLE"
        EMAIL = 'email', "EMAIL"
    
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey(Lga, null=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    profile_picture = models.URLField(default="https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default")
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=255, default=AuthProvider.EMAIL, choices=AuthProvider.choices)
    meta = JSONField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    

class BusinessProfile(BaseModel):
    id = models.BigAutoField(primary_key=True)
    business_name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    service_category = models.ForeignKey(Category, on_delete=models.CASCADE, null = True, blank=True)
    # TODO: make this a many to many relationship
    keywords = JSONField
    # TODO: make this a many to one relationship
    gallery = JSONField
    card_front = models.URLField(default=str, blank=True, null=True)
    card_back = models.URLField(default=str, blank=True, null=True)
    pob = models.URLField(verbose_name="Proof of Business", default=str, blank=True, null=True)
    is_verified_business = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.business_name}"



class Verification(BaseModel):
    user = models.OneToOneField(
        User, related_name="otp", unique=True, on_delete=models.CASCADE
    )
    code = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email