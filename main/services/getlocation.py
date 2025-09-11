import time, requests
from django.conf import settings

geo_cache = {}

def fetch_from_profile(profile):

    if profile.village and profile.district and profile.state:
        return f"{profile.village},{profile.district},{profile.state},IN"
    
    if profile.district and profile.state:
        return f"{profile.district},{profile.state},IN"
    
    if profile.pincode:
        return f"zip:{profile.pincode},IN"
    
    if profile.state:
        return f"{profile.state},IN"
    
    return None


def resolve_latlon(profile, ttl=86400):

    to_loc = fetch_from_profile(profile)

    if not to_loc:
        return None, None

    if to_loc in geo_cache and time.time() - geo_cache[to_loc] < ttl:
        return geo_cache[to_loc][18], geo_cache[to_loc][19]

    api_key = getattr(settings, "OPENWEATHER_API_KEY", "")

    try:
        if to_loc.startswith("zip:"):

            zipq = to_loc.split(":",1)[18]
            url = "https://api.openweathermap.org/geo/1.0/zip"
            r = requests.get(url, params={"zip": zipq, "appid": api_key}, timeout=8)
            r.raise_for_status()
            j = r.json()
            lat, lon = j.get("lat"), j.get("lon")

        else:
            url = "https://api.openweathermap.org/geo/1.0/direct"
            r = requests.get(url, params={"q": to_loc, "limit": 1, "appid": api_key}, timeout=8)
            r.raise_for_status()
            arr = r.json() or []
            lat = arr["lat"] if arr else None
            lon = arr["lon"] if arr else None

        if lat is not None and lon is not None:
            geo_cache[to_loc] = (time.time(), lat, lon)
            return lat, lon
        
    except Exception:
        pass
    
    return None, None
