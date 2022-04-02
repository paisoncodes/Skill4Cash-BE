from django.db.models.signals import post_save
from authentication.models import User
from django.dispatch import receiver
from .models import OTPVerification


@receiver(post_save, sender=User)
def post_save_generate_otp_code(sender, instance, created, *args, **kwargs):
	user = instance
	if created:
		OTPVerification.objects.create(user=user)