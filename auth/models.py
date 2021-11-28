from django.db import models
import uuid


# Create your models here.


class BaseUserModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "username"
    EmailField = "email"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ServiceProvider(BaseUserModel):
    business_name = models.CharField(max_length=200, unique=True)