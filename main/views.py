from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from .models import FarmerProfile, Farm
from django.http import JsonResponse
from main.services.advisory import build_dashboard
import os, requests, json
from twilio.rest import Client

def home(request):
    return render(request, "main/home.html")  

def register_view(request):
    if request.method == "POST":
        data = request.POST 

        if (pwd := data.get("password")) != data.get("confirm"):
            messages.error(request, "Passwords do not match")
            return render(request, "main/register.html")
        
        if User.objects.filter(username=data.get("username")).exists():
            messages.error(request, "User already exists")
            return render(request, "main/register.html")
        
        with transaction.atomic(): 
            username = User.objects.create_user(username=data["username"], password=pwd) 
            profile = FarmerProfile.objects.create(
                user=username,
                full_name=data.get("full_name",""),
                preferred_language=data.get("preferred_language","hi"),
                state=data.get("state",""),
                district=data.get("district",""),
                village=data.get("village",""),
                pincode=data.get("pincode",""),
            ) 

            Farm.objects.create(
                profile=profile,
                name="My Farm",
                area_value=data.get("area_value") or 1.0,
                area_unit=data.get("area_unit") or "acre",
                soil_type=data.get("soil_type") or "loamy",
            ) 

        account_sid = "AC9bb27573ea7f0fa08830b2a7c868dc29"
        auth_token = "afee08f775219036362d22bca0903271"
        client = Client(account_sid, auth_token)

        sms = client.messages.create(
            body="You have been successfully registered with Agro-Vision. We will keep updating you with latest weather conditions, market price and crop recommendations.",
            from_="+14722180372",
            to=f"+91{data["username"]}",
        )

        api_key = "c0abe7ede2ef805927c6d1dc0c2178c8"
        api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="+ data["district"] + "&units=metric&appid="+ api_key)
        api = json.loads(api_request.content)

        y = api['main']
        temprature = y['temp']
        humidity = y['humidity']

        x = api['coord']
        longtitude = x['lon']
        latitude = x['lat']

        z = api['sys']
        country = z['country']
        city = api['name']

        weather = api["weather"]
        weather_main = weather[0]["main"]
        weather_description = weather[0]["description"]

        visibility = api["visibility"]
        wind_speed = api["wind"]["speed"]

        # body = f""" मौजूदा मौसम की जानकारी:

        # 🌡️ तापमान: लगभग {temprature} डिग्री सेल्सियस (गर्मी का मौसम है, लेकिन बहुत तेज नहीं)। \n

        # 💧 नमी (Humidity): {humidity}% (हवा में मध्यम नमी है)। \n

        # ☁️ आसमान: बादल छाए हुए हैं। \n

        # 👀 दृश्यता (Visibility): {visibility} किलोमीटर तक साफ दिख रहा है। \n

        # 🌬️ हवा की रफ्तार: करीब {wind_speed} किमी प्रति घंटा (हल्की हवा चल रही है)।\n"""

        body = f""""Current weather conditions: \n
                Temparature: {temprature}\n
                Humidity: {humidity}\n
                Longitude: {longtitude}\n
                Latitude: {latitude}\n
                Country: {country}\n
                City: {city}\n
                Weather: {weather_main}\n
                Description: {weather_description}\n
                Visibility: {visibility}\n
                Wind Speed: {wind_speed}"""

        sms = client.messages.create(
            body=body,
            from_="+14722180372",
            to=f"+91{data["username"]}",
        )

        print(api)

        print("sms send")

        whatsapp_msg = client.messages.create(
            from_='whatsapp:+14155238886',
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            to=f'whatsapp:+91{data["username"]}',
            body="You have been successfully registered with Agro-Vision. We will keep updating you with latest weather conditions, market price and crop recommendations."
        )

        print("whatsapp send")

        login(request, username) 
        return redirect("dashboard") 
    
    return render(request, "main/register.html") 


@login_required
def dashboard(request):
    profile = FarmerProfile.objects.filter(user=request.user).first()
    farm = profile.farms.first() if profile else None

    lang = getattr(profile, "preferred_language", "en") or "en"
    data = build_dashboard(profile, farm, language=lang)

    return render(request, "main/dashboard.html", {"profile": profile, "farm": farm, "adv": data})


@login_required
def dashboard_api(request):
    profile = FarmerProfile.objects.filter(user=request.user).first()
    farm = profile.farms.first() if profile else None
    lang = getattr(profile, "preferred_language", "en") or "en"
    data = build_dashboard(profile, farm, language=lang)
    return JsonResponse(data)