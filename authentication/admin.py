from django.contrib import admin
from .models import User, UserProfile, BusinessProfile


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(BusinessProfile)