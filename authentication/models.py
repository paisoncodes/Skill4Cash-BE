from enum import Enum
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .manager import UserManager
from phonenumber_field.modelfields import PhoneNumberField
import uuid


# Create your models here.

class RoleEnum(Enum):
    CUSTOMER = "customer"
    SERVICE_PROVIDER = "service_provider"
    
    def __str__(self):
        return self.value

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in RoleEnum])
    location = models.CharField(max_length=100)

    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return True 

    def has_module_perms(self, app_label):
        return True 

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin
    
    
class ServiceProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_provider")
    business_name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    service_category = models.CharField(max_length=200, blank=True, null=True)
    keywords = models.JSONField(null = True, default = list)
    gallery = models.JSONField(null = True, default = list)
    is_verified = models.BooleanField(default=False)