from email.policy import default
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

from .manager import UserManager
import uuid
from django.contrib.postgres.fields import ArrayField



class User(AbstractUser):

    ROLES = (
        ("customer", "customer"),
        ("service_provider", "service_provider"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(
        max_length=100, default="Username", blank=True, null=True
    )
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLES)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="everywhere")
    phone_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    profile_picture = models.URLField(default="https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default")
    
    # service provider information
    business_name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    service_category = models.ForeignKey("Category", on_delete=models.CASCADE, null = True, blank=True)
    keywords = ArrayField(models.CharField(max_length=225), default=list, blank=True, null=True)
    gallery = ArrayField(models.URLField(), default=list, blank=True, null=True)
    card_front = models.URLField(default="")
    card_back = models.URLField(default="")
    pob = models.URLField(verbose_name="Proof of Business", default="")
    is_verified_business = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        fullname = f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        return fullname

    @property
    def verified(self):

        if (self.phone_verification or self.email_verification) and self.is_verified:
            return True
        return False

    @property
    def location(self):
        return f"{self.city}, {self.state}"

class Category(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=225, unique=True)
    image = models.URLField(default="https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

class TestImageUpload(models.Model):
    name = models.CharField(max_length=40)
    image1 = models.URLField()
    image2 = models.URLField()
    image3 = models.URLField()