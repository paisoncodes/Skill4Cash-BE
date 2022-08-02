from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, 
                    is_staff=False, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError("users must have an email address")
        if not password:
            raise ValueError("user must have a password")

        user_obj = self.model(email=self.normalize_email(email), **extra_fields)
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            **extra_fields
        )
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )
        return user
