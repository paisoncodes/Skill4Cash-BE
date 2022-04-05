from rest_framework.test import APITestCase
from src.utils import send_otp, otp_session
from otp.models import OTPVerification
from authentication.models import User
from rest_framework import status
from django.urls import reverse


class ReadUpdatePhoneViewTests(APITestCase):

    def setUp(self):
        User.objects.get_or_create(
            email="Johndeo@yahoo.com",
            first_name="John",
            last_name="Doe",
            username="Johnny",
            phone_number="+234800000000",
            location='Lagos, Nigeria',
        )

    def test_get_phone_view(self):
        """
        Should read out phone validation details
        of a user in  the current session.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('ReadUpdatePhoneView'))
        res_id = response.data['id']
        otp_id = otp.id.urn.split(":")[2]

 
        self.assertEqual(res_id, otp_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_phone_view_gone_wrong(self):
        """
        Should not read out phone validation details
        of the session user.
        """
        response = self.client.get(reverse('ReadUpdatePhoneView'))

        self.assertNotIsInstance(response, User)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_phone_view_valid_number_given(self):
        """
        Should store number yet to be updated in 
        the current request session after successfully sending
        an otp code.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)

        data = {'number':"+234800000000"}
        #must be connected to the internet
        response = self.client.put(reverse('ReadUpdatePhoneView'), data)    
        _session = dict(response.client.session).values()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 200, 'message': 'OTP sent successfully'})
        self.assertIn(data['number'], _session)
    
    def test_put_phone_view_wrong_number_given(self):
        """
        Should not store number yet to be updated in 
        the current request session after unsuccesfully sending
        an otp code.
        """
        user = User.objects.get(first_name__iexact='John')
        otp = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)

        data = {'wrong data':"this is a wrong number"}
        response = self.client.put(reverse('ReadUpdatePhoneView'), data)    
        _session = dict(response.client.session).values()

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'status':400, 'message':'Invalid Number'})
        self.assertNotIn(data['wrong data'], _session)
    
    # def test_post_phone_view_valid_otp_given(self):
        """
        Should update a user number based on correct otp given 
        and should save it to the database.
        """
        # user = User.objects.get(first_name__iexact='John')
        # otp = OTPVerification.objects.get(user=user)
        # self.client.force_authenticate(user=user)


        # otp = otp_session(self.client, "+234800000000", otp)
        # data = {'otp':otp }
     
        # response = self.client.post(reverse('ReadUpdatePhoneView'),data)
        # print(response.client.session.items())
        # print(response.json())


        # self.assertEqual(otp.otp, data['code'])
        # self.assertEqual(response.status_code, 200)
        # self.assertFalse(dict(response.client.session))
        # # self.assertTrue(otp.is_validated)
        
    def test_is_validated_attribute_after_validation(self):
        pass
        # check is_validated attribute both postive and negative
        # check OTPVerification.phone_num == user.phone_number both + and -


class OTPValidatePhoneViewTests(APITestCase):

    def setUp(self):
        User.objects.get_or_create(
            email="jackfrost@yahoo.com",
            first_name="Jack",
            last_name="Frost",
            username="Jacky",
            phone_number="+234800000000",
            location='Ibadan, Nigeria',
        )

    def test_get_otp_validate_phone_view(self):
        """
            Should send and store an otp code into a database
            for the first time of a phone verification.
            User must be authenticated and user should be in a current session.
        """
        user = User.objects.get(first_name__iexact='Jack')
        before_res = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('OTPValidatePhoneView'))
        after_res = OTPVerification.objects.get(user=user)
        message = {
            'status':status.HTTP_200_OK, 
            'message':'OTP sent successfully'
        }

        self.assertFalse(before_res.otp)
        self.assertTrue(after_res.otp)
        self.assertEqual(response.data, message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_otp_validate_phone_view_phone_already_exist(self):
        """
            Should not send an otp code if phone number is already validated.
            User must be authenticated and user should be in a current session.
        """
        user = User.objects.get(first_name__iexact='Jack')
        otp = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)  
        otp.phone_num = user.phone_number
        otp.is_validated = True
        otp.save()

        response = self.client.get(reverse('OTPValidatePhoneView'))
        message ={
            'status': 403, 
            'message': 'Phone number already validated'
        }

        self.assertTrue(otp.is_validated)
        self.assertEqual(response.data, message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_otp_validate_phone_view_wrong_phone_given(self):
        """
            Should not send otp if User.phone_number instance contain
            invalid number.
            User should be in the current session
        """
        user = User.objects.get(first_name__iexact='Jack')
        otp = OTPVerification.objects.get(user=user)
        self.client.force_authenticate(user=user)  
        user.phone_number = ''
        user.save()

        response = self.client.get(reverse('OTPValidatePhoneView'))
        message ={
            'status': 404, 
            'message':'Invalid number given'
        }

        self.assertEqual(response.data, message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_otp_validate_phone_view_not_user(self):
        """
            Should not send an otp code if user is not in the
            current session.
        """
        response = self.client.get(reverse('OTPValidatePhoneView'))

        self.assertNotIsInstance(response, User)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # testing post method
    def test_post_otp_validate_phone_view(self):
        """
            Should validate the phone number of the current session user 
            if the otp sent matches the one in database.
        """
        user = User.objects.get(first_name__iexact='Jack')
        self.client.force_authenticate(user=user)
        # before calling a post method
        self.client.get(reverse('OTPValidatePhoneView')) 
        before_otp = OTPVerification.objects.get(user=user) 

        data = {'otp': before_otp.otp}
        response = self.client.post(reverse('OTPValidatePhoneView'), data)
        after_otp = OTPVerification.objects.get(user=user) 
        message = {
            'status':status.HTTP_200_OK, 
            'message':'OTP Code Verified'
        }

        self.assertEqual(after_otp.phone_num, user.phone_number)
        self.assertTrue(after_otp.is_validated)
        self.assertEqual(response.data, message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_otp_validate_phone_view_already_validated(self):
        """
            Should not validate the phone number of a current session user 
            if the number is already validated.
        """
        user = User.objects.get(first_name__iexact='Jack')
        self.client.force_authenticate(user=user)
        self.client.get(reverse('OTPValidatePhoneView')) 
        otp = OTPVerification.objects.get(user=user) 
        otp.is_validated = True
        otp.save()

        data = {'otp': otp.otp}
        response = self.client.post(reverse('OTPValidatePhoneView'), data)
        message ={
            'status': 403, 
            'message': 'Phone number already validated'
        }

        self.assertTrue(otp.is_validated)
        self.assertEqual(response.data, message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_otp_validate_phone_view_not_user(self):
        """
            Should not validate phone number if user is not in the
            current session.
        """
        response = self.client.post(reverse('OTPValidatePhoneView'), {'otp': '00000'})

        self.assertNotIsInstance(response, User)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
