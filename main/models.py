# main/models.py
from django.conf import settings
from django.db import models

LANG_CHOICES = [("hi","Hindi"),("en","English")]
SOIL_CHOICES = [("alluvial", "Alluvial"), ("loamy", "Loamy"), ("clayey", "Clayey"), ("sandy", "Sandy"), ("laterite", "Laterite"), ("black", "Black"), ("red", "Red"),]
IRIGATION_CHOICES = [("tube_well", "Tube Well"), ("canal", "Canal"), ("rainfed", "Rainfed"), ("drip", "Drip Irrigation"), ("other", "Other")]
WATER_AVAIL = [ ("low", "Low"), ("moderate", "Moderate"), ("sufficient", "Sufficient")]
SELLING_CHANNEL = [ ("mandi", "Local Mandi"), ("direct", "Direct Buyers"), ("fpo", "FPO / Cooperative"), ("other", "Other")]

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
    last_irrigation = models.CharField(max_length=40, blank=True, default="")
    crop_current = models.CharField(max_length=40, blank=True)
    sow_date = models.DateField(null=True, blank=True)
    ph = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    village = models.CharField(max_length=128, blank=True)
    irrigation_source = models.CharField(max_length=50, choices=IRIGATION_CHOICES, blank=True, default="tube_well")
    water_availability = models.CharField(max_length=20, choices=WATER_AVAIL, blank=True, default="low")
    used_fertilizers = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of fertilizers", default="no")
    used_pesticides = models.BooleanField(default=False)
    prefers_organic = models.BooleanField(default=False)
    nearby_mandi = models.CharField(max_length=100, blank=True, default="none")
    selling_channel = models.CharField(max_length=50, choices=SELLING_CHANNEL, blank=True, default="mandi")
    nitrogen = models.IntegerField(default=0, blank=True)
    phosphorus = models.IntegerField(default=0, blank=True)
    potassium = models.IntegerField(default=0, blank=True)
    ph = models.DecimalField(default=0, blank=True, max_digits=2, decimal_places=1)

    def __str__(self): return f"{self.name}"
