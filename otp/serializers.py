from rest_framework import serializers
from .models import OTPVerification 

class OTPSerializers(serializers.ModelSerializer):
	class Meta:
		model = OTPVerification
		exclude = ('otp',)