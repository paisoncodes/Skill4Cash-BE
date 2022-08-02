from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from .manager import UserManager
import uuid
from django.contrib.postgres.fields import ArrayField


# Create your models here.

ROLES = (
    ("customer", "customer"),
    ("service_provider", "service_provider"),
)


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(
        max_length=100, default="s4k", blank=True, null=True, unique=False
    )
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLES)
    location = models.CharField(max_length=100)
    phone_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    business_name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    service_category = models.CharField(max_length=200, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=225), default=list)
    gallery = ArrayField(models.CharField(max_length=225), default=list)
    card_front = models.CharField(max_length=225, blank=True, null=True)
    card_back = models.CharField(max_length=225, blank=True, null=True)
    pob = models.CharField(
        max_length=225, blank=True, null=True, verbose_name="Proof of business"
    )
    is_verified_business = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def verified(self):

        if (self.phone_verification or self.email_verification) and self.is_verified:
            return True
        return False
