from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        is_staff=False,
        is_active=True,
        is_admin=False,
        **extra_fields
    ):
        if not email:
            raise ValueError("users must have a email")
        if not password:
            raise ValueError("user must have a password")

        user_obj = self.model(email=self.normalize_email(email), **extra_fields)
        user_obj.set_password(password)
        user_obj.staff = False
        user_obj.admin = False
        user_obj.active = False
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_staff=True

        user.save(using = self.db)
        
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_super_user = True

        user.save(using = self.db)
        return user
