from django.test import TestCase
from authentication.models import User

class UserModelTests(TestCase):

    def setUp(self):
        User.objects.create(
            email="Johndeo@yahoo.com",
            first_name="John",
            last_name="Doe",
            username="Johnny",
            phone_number="+234800000000",
            location='Lagos, Nigeria',
        )

    def test_user_model_created(self):
        """Testing an instance of User model created.
			Instance should return the data of email attribute as 
			the '__str__' of the model, class User.
		"""
        user = User.objects.get(first_name__iexact='John')
        res = "Johndeo@yahoo.com"

        self.assertEqual(user.__str__(), res)
        self.assertIsInstance(user, User)
	
    def test_not_user_model_created(self):	
        """
        Testing an instance of a User model is not created.
        """
        user = User.objects.get(first_name__iexact='John')
        not_obj = 'This is just a dummy word'

        self.assertNotIsInstance(not_obj, User) 
        self.assertNotEqual(user.__str__(), not_obj)
    
    def test_not_user_is_verified(self):
        """
        User.is_verified should be False by default.
        Should be False before email Verification
        """
        user = User.objects.get(first_name__iexact='John')

        default = user._meta.get_field('_is_verified').default
        self.assertFalse(default)

    def test_not_user_phone_verification(self):
        """
        user.phone_verification should be False by default.
        Should be False before OTP Verification
        """
        user = User.objects.get(first_name__iexact='John')

        default = user._meta.get_field('phone_verification').default
        self.assertFalse(default)
    
    def test_not_user_email_verification(self):
        """
        user.email_verification should be False by default.
        Should be False before OTP Verification
        """
        user = User.objects.get(first_name__iexact='John')
        
        default = user._meta.get_field('email_verification').default
        self.assertFalse(default)

    def test_user_full_name_property(self):
        """
        user.full_name should return the fullname 
        of a user.
        """
        user = User.objects.get(first_name__iexact='John')
        user = user.full_name
        
        self.assertEqual(user, 'John Doe')

    def test_user_is_verified_property_true(self):
        """
        user.is_verified should return the True if email_verification 
        or phone_verification is True. 
        """
        user = User.objects.get(first_name__iexact='John')
        user.email_verification = True
        user._is_verified = True

        self.assertTrue(user.is_verified)

    def test_user_is_verified_property_false(self):
        """
        user.is_verified should return the False if email_verification 
        or phone_verification is not True. 
        """
        user = User.objects.get(first_name__iexact='John')

        self.assertFalse(user.is_verified)