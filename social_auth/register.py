from rest_framework.exceptions import AuthenticationFailed
from authentication.models import User
from django.conf import settings
from src.utils import AuthUtil
from random import randint


def generate_number():

    num = '+23490000'
    num += "".join([str(randint(0,9)) for x in range(5)])
    if not User.objects.filter(phone_number=num).exists():
        return num
    else:
        return generate_number()


def register_social_user(provider, email, first_name, last_name, username, role, state, city):
    
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:

            registered_user = AuthUtil.create_token(
            						password=settings.SOCIAL_SECRET,
            						email=email
                                )
            if not 'error' in registered_user.keys():
                registered_user['email'] = email
                return registered_user
            raise AuthenticationFailed('500 Error! Invalid Password')

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' +
                filtered_user_by_email[0].auth_provider
            )

    else:
        user = {
            'email': email,
            'phone_number': generate_number(),
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_SECRET,
            'auth_provider':provider,
            'state':state,
            'city':city,
            'role': role,
            'is_verified':True,
            'email_verification':True
        }

        user = User.objects.create_user(**user)
        user.save()

        registered_user = AuthUtil.create_token(
        	password=settings.SOCIAL_SECRET,
        	email=email,
        	phone_number=None
        )
        
        registered_user['email'] = email
        return registered_user

