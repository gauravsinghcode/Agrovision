from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from .models import FarmerProfile, Farm
import requests, json, joblib
from twilio.rest import Client
from .models import FarmerProfile
import openmeteo_requests
import pandas as pd
import numpy as np
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

def home(request):
    return render(request, "main/home.html")


def weather(request):

    return render(request, "main/weather.html")


def register_view(request):
    global weather_main

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
                irrigation_source=data.get("irrigation_source"),
                water_availability=data.get("water_availability"),
                selling_channel=data.get("selling_channel"),
            )

        auth_token = "a37a59913ebff28b5b977d904f8784a9"

        account_sid = 'AC9bb27573ea7f0fa08830b2a7c868dc29'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
        messaging_service_sid='MG78b8761050e7b2a945a04f579aaaf06e',
        body='You are successfully registered with Agro-Vision. We will keep updating you about latest weather conditions and market prices.',
        to=f'+91{data["username"]}'
        )

        execution = client.studio.v2.flows(
            "FW359de38c318a6fd3c81ce2f88403c7ac"
        ).executions.create(to=f"+91{data["username"]}", from_="+14722180372")
        
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
            messaging_service_sid='MG78b8761050e7b2a945a04f579aaaf06e',
            body=body,
            from_="+14722180372",
            to=f"+91{data["username"]}",
        )

        whatsapp_msg = client.messages.create(
            from_='whatsapp:+14155238886',
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            to=f'whatsapp:+91{data["username"]}',
            body="You have been successfully registered with Agro-Vision. We will keep updating you with latest weather conditions, market price and crop recommendations."
        )

        login(request, username) 
        return redirect("dashboard") 
    
    return render(request, "main/register.html") 


def onboard(request):

    return render(request, "main/onboard.html")


def predict_crop(n, p, k, temp, humidity, ph, rainfall):
    features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
    return crop_model.predict(features)[0].capitalize()


def predict_top_crops(n, p, k, temp, humidity, ph, rainfall, top_n=3):
    features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
    proba = (crop_model.predict_proba(features)[0]) * 100
    classes = crop_model.classes_
    
    top_indices = np.argsort(proba)[::-1][:top_n]
    top_crops = [(classes[i].capitalize(), proba[i]) for i in top_indices]
    
    return top_crops


def irrigation_advice(last_irrigation, soil_moisture, rain_prob):

    tasks = []

    days_since = (datetime.now() - last_irrigation).days
    
    if rain_prob >= 60:
         tasks.append("Defer irrigation – high chance of rain.")
    elif soil_moisture < 20:
         tasks.append("Irrigate today – soil moisture is too low.")
    elif days_since >= 7:
         tasks.append("Irrigate now – last irrigation was over a week ago.")
    else:
         tasks.append(f"No irrigation needed. Next expected in {7 - days_since} days.")

    return tasks
    

def crop_advisory(season, soil_type, weather):

    suggestions = []

    if season == "rabi" and soil_type in ["loamy", "alluvial"]:
        suggestions.append({"title": "Wheat", "reason": "Ideal Rabi crop for loamy/alluvial soils."})
    if season == "rabi" and soil_type in ["sandy", "loamy"]:
        suggestions.append({"title": "Mustard", "reason": "Oilseed crop, high price, low water requirement."})
    if season == "kharif" and weather["rainfall"] > 150:
        suggestions.append({"title": "Rice", "reason": "Good rainfall makes rice highly productive."})
    if season == "kharif" and soil_type in ["loamy", "sandy"]:
        suggestions.append({"title": "Maize", "reason": "Less water demand than rice, good market demand."})

    if not suggestions:
        suggestions.append({"title": "Pulses", "reason": "Good nitrogen fixer and suited for mixed soils."})

    return suggestions


def generate_alerts(weather, mandi_price=None):
    alerts = []

    if weather["rain_prob"] > 70:
        alerts.append({
            "type": "weather",
            "message": "High chance of rain (>70%). Avoid irrigation.",
            "severity": "urgent"
        })

    if weather["tmax"] > 38:
        alerts.append({
            "type": "weather",
            "message": "Heatwave alert! Provide extra irrigation.",
            "severity": "high"
        })

    if weather["tmin"] < 5:
        alerts.append({
            "type": "weather",
            "message": "Frost conditions expected. Protect sensitive crops.",
            "severity": "high"
        })

    if weather["soil_moisture"] < 15:
        alerts.append({
            "type": "irrigation",
            "message": "Soil moisture critically low. Immediate irrigation required.",
            "severity": "urgent"
        })

    if mandi_price and mandi_price.get("wheat", 0) < 1800:
        alerts.append({
            "type": "market",
            "message": "Wheat prices dropped. Avoid selling this week.",
            "severity": "medium"
        })

    return alerts



def dashboard_view(request):
    global crop_model

    crop_model = joblib.load("main/Models/crop_model.pkl")

    farmer_profile = FarmerProfile.objects.filter(user=request.user).first()
    farm = farmer_profile.farms.first()

    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    geolocation_url = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={farmer_profile.district}&count=1&language=en&format=json"
    )
    data = json.loads(geolocation_url.content)

    lat = data["results"][0]["latitude"]
    long = data["results"][0]["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max"],
        "hourly": ["precipitation", "precipitation_probability", "soil_moisture_0_to_1cm"],
        "current": ["temperature_2m", "relative_humidity_2m", "rain"],
        "timezone": "auto",
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    daily = response.Daily()

    weather_forecast = []
    for i in range(len(daily.Variables(0).ValuesAsNumpy())-2):
        weather_forecast.append({
            "tmax": int(daily.Variables(0).ValuesAsNumpy()[i]),
            "tmin": int(daily.Variables(1).ValuesAsNumpy()[i]),
            "rain_prob": daily.Variables(3).ValuesAsNumpy()[i],
            "desc": "Rainy" if daily.Variables(2).ValuesAsNumpy()[i] > 50 else "Clear"
        })

    weather_data = {
        "tmax": int(daily.Variables(0).ValuesAsNumpy()[0]),
        "tmin": int(daily.Variables(1).ValuesAsNumpy()[0]),
        "humidity": current.Variables(1).Value(),
        "soil_moisture": current.Variables(0).Value(),
        "rain_prob": daily.Variables(3).ValuesAsNumpy()[0],
        "rainfall": daily.Variables(2).ValuesAsNumpy()[0] ,
        "weather_main": "Rain" if current.Variables(2).Value() > 0 else "Clear",
        "daily": weather_forecast
    }

    n = farm.nitrogen if farm.nitrogen else 200
    p = farm.phosphorus if farm.phosphorus else 50
    k = farm.potassium if farm.potassium else 120
    ph = farm.ph if farm.ph else 7

    temp = weather_data["tmax"] - 2
    humidity = weather_data["humidity"]
    rainfall = weather_data["rainfall"]

    features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
    probs = crop_model.predict_proba(features)[0]
    confidence = max(probs) * 100
    top3 = sorted(zip(crop_model.classes_, probs), key=lambda x: x[1], reverse=True)[:3]    

    predicted_crop = predict_crop(n, p, k, temp, humidity, ph, rainfall)
    top_crops = predict_top_crops(n, p, k, temp, humidity, ph, rainfall)

    ml_suggestions = [
        {"title": crop, "reason": f"Predicted with {round(prob*100,1)}% confidence by ML model"}
        for crop, prob in top3
    ]

    month = datetime.now().month
    if 6 <= month <= 10:
        season = "kharif"
    elif 11 <= month or month <= 4:
        season = "rabi"
    else:
        season = "zaid"

    rule_based_suggestions = crop_advisory(season, farm.soil_type.lower(), weather_data)

    mandi_prices = {
        "wheat": 2100,
        "mustard": 5600,
        "rice": 2300,
        "maize": 1850
    }
    
    for s in ml_suggestions:
        crop_name = s["title"].lower()
        if crop_name in mandi_prices:
            s["market_price"] = f"₹{mandi_prices[crop_name]}/qtl"

    last_irrigation = farm.last_irrigation or datetime.now() - timedelta(days=5)

    irrigation_tasks = irrigation_advice(last_irrigation, weather_data["soil_moisture"], weather_data["daily"][0]["rain_prob"])

    alerts = generate_alerts(weather_data, mandi_prices)

    return render(request, "main/dashboard.html", {
        "farmer": farmer_profile,
        "farm": farm,
        "weather": weather_data,
        "alerts": alerts,
        "predicted_crop": predicted_crop,
        "confidence": confidence,
        "top_crops" : top_crops,
        "irrigation_tasks": irrigation_tasks,
    })

