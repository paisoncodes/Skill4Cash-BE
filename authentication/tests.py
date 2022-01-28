from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
class ServiceProviderAccountTest(APIClient):
    def test_create_account(self):
        data = {
            "first_name": "service",
            "last_name": "provider",
            "password": "1234",
            "email": "sp@gmail.com",
        }