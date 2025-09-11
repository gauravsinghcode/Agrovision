from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

LANG_CHOICES = [("hi","Hindi"),("en","English")]
SOIL_CHOICES = [("loamy","Loamy"),("clay","Clayey"),("sandy","Sandy"),("alluvial","Alluvial")]
AREA_CHOICES = [("acre","Acre"),("hectare","Hectare")]

class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    username = forms.CharField(max_length=150, help_text="Phone or username")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm = forms.CharField(widget=forms.PasswordInput)
    preferred_language = forms.ChoiceField(choices=LANG_CHOICES)
    village = forms.CharField(max_length=128, required=False)
    district = forms.CharField(max_length=64, required=False)
    state = forms.CharField(max_length=64, required=False)
    pincode = forms.CharField(max_length=6, required=False)
    soil_type = forms.ChoiceField(choices=SOIL_CHOICES)
    area_value = forms.DecimalField(max_digits=6, decimal_places=2)
    area_unit = forms.ChoiceField(choices=AREA_CHOICES)

    def clean(self):
        c = super().clean()
        if c.get("password") != c.get("confirm"):
            raise forms.ValidationError("Passwords do not match")
        return c