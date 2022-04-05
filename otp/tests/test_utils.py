from src.utils import send_otp, otp_session
from otp.models import OTPVerification
from authentication.models import User
from django.test import TestCase
import unittest


class SendOtpTest(unittest.TestCase):

	def test_send_otp_function(self):
		"""
		Should send an Otp code if there is no
		connection error
		"""

		result = send_otp("+234000000000")

		self.assertTrue(result)
		self.assertIsInstance(result, str)

	def test_send_otp_function_went_wrong(self):
		"""
		Should not send an OTP code but return None
		"""

		result = send_otp(False)

		self.assertFalse(result)
		self.assertNotIsInstance(result, str)
		self.assertIsNone(result)


class  OtpSessionTests(TestCase):

	def setUp(self):
		User.objects.create(
		    email="jackfrost@yahoo.com",
		    first_name="Jack",
		    last_name="Frost",
		    username="Jacky",
		    phone_number="+234800000000",
		    location='Ibadan, Nigeria',
		)
	
	def test_otp_session_function(self):
		"""
			Should return True after populating a request session 
			with otp code and number respectively if there is no  
			connnection error.
		"""
		user = User.objects.get(first_name__iexact='Jack')
		ins = OTPVerification.objects.get(user=user)

		result = otp_session(self.client, "+234000000000", ins)

		self.assertTrue(result)

	def test_otp_session_function_wrong(self):
		"""
			Should return None.
		"""
		user = User.objects.get(first_name__iexact='Jack')
		ins = OTPVerification.objects.get(user=user)

		result = otp_session(self.client, False, ins)

		self.assertFalse(result)
		self.assertIsNone(None)

