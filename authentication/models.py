from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.db import models
from utils.models import BaseModel, Category, Keyword, Lga, State
from django.utils.translation import gettext_lazy as _


def images_default_value():
    return [{"url": "", "id": ""}]

class User(AbstractUser, BaseModel):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        max_length=100, default='Username', blank=True, null=True
    )
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

class UserProfile(BaseModel):

    class UserType(models.TextChoices):
        SERVICE_PROVIDER = 'service_provider', "SERVICE_PROVIDER"
        CUSTOMER = 'customer', "CUSTOMER"

    class AuthProvider(models.TextChoices):
        FACEBOOK = 'facebook', "FACEBOOK"
        GOOGLE = 'google', "GOOGLE"
        EMAIL = 'email', "EMAIL"
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey(Lga, null=True, on_delete=models.SET_NULL)
    user_type = models.CharField(max_length=20, choices=UserType.choices)
    profile_picture = models.URLField(default="https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default")
    auth_provider = models.CharField(max_length=255, default=AuthProvider.EMAIL, choices=AuthProvider.choices)
    phone_number = models.CharField(max_length=13, unique=True)
    
    phone_verified = models.BooleanField(default=False)
    meta = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BusinessProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    business_name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    service_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword)
    gallery = models.JSONField(default=images_default_value)
    card_front = models.URLField(default=str)
    card_back = models.URLField(default=str)
    pob = models.URLField(verbose_name="Proof of Business", default=str)
    is_verified_business = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.business_name}"

class BusinessGallery(models.Model):
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    image_ur = models.URLField()
    title = models.CharField(max_length=225)

    def __str__(self):
        return f"{self.business.business_name} - {self.title}"

class Verification(BaseModel):
    user = models.OneToOneField(
        User, related_name="otp", unique=True, on_delete=models.CASCADE
    )
    code = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email

class TestImageUpload(models.Model):
    name = models.CharField(max_length=40)
    image1 = models.URLField()
    image2 = models.URLField()
    image3 = models.URLField()