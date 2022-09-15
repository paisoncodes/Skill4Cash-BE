from email.policy import default
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

from services.models import Category
from .manager import UserManager
import uuid
from django.contrib.postgres.fields import ArrayField


def upload_to_card_front(instance, filename):
    return f"cardfront-img/{filename}"


def upload_to_card_back(instance, filename):
    return f"cardback-img/{filename}"


def upload_to_pob(instance, filename):
    return f"pob-img/{filename}"


def upload_to_gallery(instance, filename):
    return f"gallery-img/{filename}"


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

    # service provider information
    business_name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    service_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    keywords = ArrayField(models.CharField(max_length=225), default=list)
    gallery = ArrayField(
        models.ImageField(upload_to=upload_to_gallery, blank=True, null=True),
        default=list,
    )
    card_front = models.ImageField(
        upload_to=upload_to_card_front, blank=True, null=True
    )
    card_back = models.ImageField(upload_to=upload_to_card_back, blank=True, null=True)
    pob = models.ImageField(
        verbose_name="Proof of business", upload_to=upload_to_pob, blank=True, null=True
    )
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
