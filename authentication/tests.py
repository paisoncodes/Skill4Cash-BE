from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.
class ServiceProviderAccountTest(APITestCase):
    def test_create_account_success(self):
        data = {
            "user":{
                "first_name": "service",
                "last_name": "provider",
                "password": "computer1668",
                "password2": "computer1668",
                "email": "sp@gmail.com",
                "phone_number": "+2347068360667",
                "location":"Abuja"  
            },
            "business_name": "sp_ventures"
        }
        
        response = self.client.post("/api/v1/sp/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_response = response.json()
        self.assertEqual(type(data_response), dict)
        self.assertEqual(data_response["user"]['email'], data['user']["email"])
        self.assertEqual(data_response['is_verified'], False)
        
    