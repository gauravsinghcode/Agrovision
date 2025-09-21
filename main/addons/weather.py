import requests
import json
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from main.models import FarmerProfile

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

location = FarmerProfile.get

geolocation_url = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json")
data = json.loads(geolocation_url.content)

lat = data["results"][0]["latitude"]
long = data["results"][0]["longitude"]
name = data["results"][0]["name"]

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": lat,
    "longitude": long,
    "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "rain_sum", "showers_sum", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max"],
    "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "visibility", "evapotranspiration", "wind_speed_10m", "wind_direction_10m", "temperature_80m", "temperature_120m", "temperature_180m", "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm"],
    "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
    "timezone": "auto",
    }

responses = openmeteo.weather_api(url, params=params)

response = responses[0]

current = response.Current()
hourly = response.Hourly()
daily = response.Daily()

    # current_temperature_2m = current.Variables(0).Value()
    # current_relative_humidity_2m = current.Variables(1).Value()
    # current_apparent_temperature = current.Variables(2).Value()
    # current_precipitation = current.Variables(3).Value()
    # current_rain = current.Variables(4).Value()
    # current_weather_code = current.Variables(5).Value()
    # current_cloud_cover = current.Variables(6).Value()
    # current_pressure_msl = current.Variables(7).Value()
    # current_surface_pressure = current.Variables(8).Value()
    # current_wind_speed_10m = current.Variables(9).Value()
    # current_wind_direction_10m = current.Variables(10).Value()

    # hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    # hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    # hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
    # hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
    # hourly_rain = hourly.Variables(4).ValuesAsNumpy()
    # hourly_visibility = hourly.Variables(5).ValuesAsNumpy()
    # hourly_evapotranspiration = hourly.Variables(6).ValuesAsNumpy()
    # hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()
    # hourly_wind_direction_10m = hourly.Variables(8).ValuesAsNumpy()
    # hourly_temperature_80m = hourly.Variables(9).ValuesAsNumpy()
    # hourly_temperature_120m = hourly.Variables(10).ValuesAsNumpy()
    # hourly_temperature_180m = hourly.Variables(11).ValuesAsNumpy()
    # hourly_soil_temperature_0cm = hourly.Variables(12).ValuesAsNumpy()
    # hourly_soil_temperature_6cm = hourly.Variables(13).ValuesAsNumpy()
    # hourly_soil_temperature_18cm = hourly.Variables(14).ValuesAsNumpy()
    # hourly_soil_moisture_0_to_1cm = hourly.Variables(15).ValuesAsNumpy()
    # hourly_soil_moisture_1_to_3cm = hourly.Variables(16).ValuesAsNumpy()
    # hourly_soil_moisture_3_to_9cm = hourly.Variables(17).ValuesAsNumpy()
    # hourly_soil_moisture_9_to_27cm = hourly.Variables(18).ValuesAsNumpy()

    # Hourly Weather

    # hourly_data = {"date": pd.date_range(
    #     start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    #     end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    #     freq = pd.Timedelta(seconds = hourly.Interval()),
    #     inclusive = "left"
    # )}

    # hourly_data["temperature_2m"] = hourly_temperature_2m
    # hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    # hourly_data["dew_point_2m"] = hourly_dew_point_2m
    # hourly_data["precipitation"] = hourly_precipitation
    # hourly_data["rain"] = hourly_rain
    # hourly_data["visibility"] = hourly_visibility
    # hourly_data["evapotranspiration"] = hourly_evapotranspiration
    # hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    # hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    # hourly_data["temperature_80m"] = hourly_temperature_80m
    # hourly_data["temperature_120m"] = hourly_temperature_120m
    # hourly_data["temperature_180m"] = hourly_temperature_180m
    # hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
    # hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
    # hourly_data["soil_temperature_18cm"] = hourly_soil_temperature_18cm
    # hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
    # hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
    # hourly_data["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
    # hourly_data["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm

    # hourly_dataframe = pd.DataFrame(data = hourly_data)

# Daily Weather

# def daily_weather(location):

#     get_weather_details(location)

    
    # daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    # daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    # daily_sunrise = daily.Variables(2).ValuesInt64AsNumpy()
    # daily_sunset = daily.Variables(3).ValuesInt64AsNumpy()
    # daily_rain_sum = daily.Variables(4).ValuesAsNumpy()
    # daily_showers_sum = daily.Variables(5).ValuesAsNumpy()
    # daily_precipitation_sum = daily.Variables(6).ValuesAsNumpy()
    # daily_precipitation_probability_max = daily.Variables(7).ValuesAsNumpy()
    # daily_wind_speed_10m_max = daily.Variables(8).ValuesAsNumpy()

    # daily_data = {"date": pd.date_range(
    #     start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
    #     end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
    #     freq = pd.Timedelta(seconds = daily.Interval()),
    #     inclusive = "left"
    # )}

    # daily_data["temperature_2m_max"] = daily_temperature_2m_max
    # daily_data["temperature_2m_min"] = daily_temperature_2m_min
    # daily_data["sunrise"] = daily_sunrise
    # daily_data["sunset"] = daily_sunset
    # daily_data["rain_sum"] = daily_rain_sum
    # daily_data["showers_sum"] = daily_showers_sum
    # daily_data["precipitation_sum"] = daily_precipitation_sum
    # daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    # daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max

    # daily_dataframe = pd.DataFrame(data = daily_data)