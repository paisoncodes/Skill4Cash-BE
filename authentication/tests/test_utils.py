from src.utils import send_otp, otp_session
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
	
	def test_otp_session_function(self):
		"""
			Should return True after populating a request session 
			with otp code and number respectively if there is no  
			connnection error.
		"""
		result = otp_session(self.client, "+234000000000")
		self.assertTrue(result)

	def test_otp_session_function_wrong(self):
		"""
			Should return None if no phone number was given.
		"""
		result = otp_session(self.client, False)

		self.assertFalse(result)
		self.assertIsNone(None)

