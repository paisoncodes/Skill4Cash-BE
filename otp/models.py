from phonenumber_field.modelfields import PhoneNumberField
from authentication.models import User
from django.db import models
import uuid


class OTPVerification(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user         = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_num    = PhoneNumberField(blank=True)
    is_validated = models.BooleanField(default=False)
    otp          = models.CharField(max_length=5, blank=True, null=True)
    updated      = models.DateTimeField(auto_now=True)
    created      = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'phone number verification is {self.is_validated}'