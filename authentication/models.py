from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .manager import UserManager
import uuid


# Create your models here.


class Customer(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)

    
    
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

class ServiceProvider(Customer):
    business_name = models.CharField(max_length=200, unique=True)