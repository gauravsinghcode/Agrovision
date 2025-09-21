from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FarmerProfile, Farm

admin.site.register(FarmerProfile)
admin.site.register(Farm)
