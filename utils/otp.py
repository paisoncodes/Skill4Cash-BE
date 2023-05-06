from datetime import timedelta
from authentication.models import User, Verification
from utils.utils import random_with_n_digits
from django.utils import timezone
from django.shortcuts import get_object_or_404


def get_otp(user: User):
    randomcode = random_with_n_digits(6)
    verification, created = Verification.objects.get_or_create(user=user)
    verification.code = randomcode
    created_date = timezone.now()
    verification.created_date = created_date
    expiry_date = created_date + timedelta(seconds=300)
    verification.expiry_date = expiry_date
    verification.save()
    return randomcode


def verify_otp(user: User, code: int):
    if Verification.objects.filter(user=user, code=code).exists():
        verification = get_object_or_404(Verification, user=user, code=code)
        today = timezone.now()
        if verification.expiry_date >= today:
            return True
        return False
    else:
        return False