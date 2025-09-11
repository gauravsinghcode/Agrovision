import time, requests, random, datetime
from django.conf import settings

_cache = {} 

def mock(lat=None, lon=None):
    random.seed(int((lat or 28.6)*1000) ^ int((lon or 77.2)*1000))
    daily = []

    for i in range(7):
        tmax = random.randint(28, 35)
        tmin = tmax - random.randint(6, 9)
        rain_prob = random.choice([10,20,30,60,70,80])
        desc = "Rain" if rain_prob >= 60 else ("Cloudy" if rain_prob >= 30 else "Sunny")
        daily.append({"tmax": tmax, "tmin": tmin, "rain_prob": rain_prob, "desc": desc})

    return {"daily": daily, "humidity": random.randint(45,85)}


def get_forecast(lat: float|None, lon: float|None, ttl=3600):
    if not settings.OPENWEATHER_API_KEY or lat is None or lon is None:
        return mock(lat, lon) 
    
    key = f"owm:{round(lat,3)},{round(lon,3)}"
    now = time.time()

    if key in _cache and now - _cache[key] < ttl:
        return _cache[key][1]

    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat, "lon": lon, "exclude": "minutely,hourly,alerts",
        "units": "metric", "appid": settings.OPENWEATHER_API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        j = r.json()
        daily = []

        for d in (j.get("daily") or [])[:7]:
            tmax = round((d.get("temp") or {}).get("max", 0))
            tmin = round((d.get("temp") or {}).get("min", 0))
            rain_prob = round((d.get("pop", 0))*100)
            desc = ((d.get("weather") or [{}]).get("description") or "clouds").title()
            daily.append({"tmax": tmax, "tmin": tmin, "rain_prob": rain_prob, "desc": desc})

        payload = {"daily": daily, "humidity": j.get("current", {}).get("humidity", 60)}

    except Exception:
        payload = mock(lat, lon)
    _cache[key] = (now, payload)
    
    return payload
