from django.test import TestCase
from otp.models import OTPVerification
from authentication.models import User

class OTPVerificationTests(TestCase):

    def setUp(self):
        User.objects.get_or_create(
            email="Johndeo@yahoo.com",
            first_name="John",
            last_name="Doe",
            username="Johnny",
            phone_number="+234800000000",
            location='Lagos, Nigeria',
        )
    
    def test_user_isinstance_of_otpverification_model(self):
        """Testing signals. An instance of a saved User model must 
            create a new instance of an OTPverification model.
        """

        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        
        self.assertEqual(otp.user, user)
        self.assertEqual(otp.user.first_name, 'John')
        
    def test_otpverification_model_created(self):
        """Testing an instance of OTPVerification model created.
			Instance should return the data of is_validated attribute as 
			the '__str__' of the model, class OTPVerification.
		"""
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        res = 'phone number verification is False'

        self.assertEqual(otp.__str__(), res)
        self.assertIsInstance(otp, OTPVerification)
	
    def test_not_otpverification_model_created(self):	
        """
        Testing an instance of a OTPverification models is not created.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        not_obj = 'This is just a dummy word'

        self.assertNotIsInstance(user, OTPVerification) 
        self.assertNotEqual(otp.__str__(), not_obj)
    
    # check weder user phone is equal to otp phone
    def test_user_phone_number_and_otpverification_phone_num(self):
        """
        Phone numbers of both User model and OTPVerification model 
        should be the same after verification.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        otp.phone_num = user.phone_number
        otp.save()

        self.assertEqual(otp.phone_num, '+234800000000')
        self.assertEqual(user.phone_number, otp.phone_num)

    def test_not_user_phone_number_and_otpverification_phone_num(self):
        """
        Phone numbers of both User model and OTPVerification model 
        should not be the same before verification.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)

        self.assertNotEqual(otp.phone_num,'+234800000000')
        self.assertFalse(otp.phone_num)

    def test_not_otpverification_validation(self):
        """
        OTPVerification.is_validated should be False by default.
        Should be False before OTP Verification
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        
        default = otp._meta.get_field('is_validated').default
        self.assertFalse(default)