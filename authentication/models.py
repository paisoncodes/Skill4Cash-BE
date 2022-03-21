from enum import Enum
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from django.contrib.postgres.fields import ArrayField


# Create your models here.

class RoleEnum(Enum):
    CUSTOMER = "customer"
    SERVICE_PROVIDER = "service_provider"
    
    def __str__(self):
        return self.value

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, editable=False)
    last_name = models.CharField(max_length=100, editable=False)
    username = models.CharField(max_length=100, unique=True)
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in RoleEnum])
    location = models.CharField(max_length=100)

    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    
    
class ServiceProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_provider")
    business_name = models.CharField(max_length=200, unique=True)
    service_category = models.CharField(max_length=200, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=225), blank=True, null=True)
    gallery = ArrayField(models.CharField(max_length=225), blank=True, null=True)
    card_front = models.CharField(max_length=225, blank=True, null=True)
    card_back = models.CharField(max_length=225, blank=True, null=True)
    pob = models.CharField(max_length=225, blank=True, null=True, verbose_name="Proof of business")
    is_verified = models.BooleanField(default=False)