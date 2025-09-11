# main/models.py
from django.conf import settings
from django.db import models

LANG_CHOICES = [("hi","Hindi"),("en","English")]
SOIL_CHOICES = [("loamy","Loamy"),("clay","Clayey"),("sandy","Sandy"),("alluvial","Alluvial")]

class FarmerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    preferred_language = models.CharField(max_length=5, choices=LANG_CHOICES, default="hi")
    state = models.CharField(max_length=64, blank=True)
    district = models.CharField(max_length=64, blank=True)
    village = models.CharField(max_length=128, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    def __str__(self): return self.full_name
    

class Farm(models.Model):
    profile = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="farms")
    name = models.CharField(max_length=80, default="My Farm")
    area_value = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    area_unit = models.CharField(max_length=10, choices=[("acre","Acre"),("hectare","Hectare")], default="acre")
    soil_type = models.CharField(max_length=20, choices=SOIL_CHOICES, default="loamy")
    irrigation = models.CharField(max_length=40, blank=True, default="")
    crop_current = models.CharField(max_length=40, blank=True)
    sow_date = models.DateField(null=True, blank=True)
    ph = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    village = models.CharField(max_length=128, blank=True)
    def __str__(self): return f"{self.name}"
