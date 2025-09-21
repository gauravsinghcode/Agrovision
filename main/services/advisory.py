import datetime
from .getlocation import resolve_latlon
from .weather import get_forecast
from .model import evaluate_all
from .languages import show_lang
import requests
from geopy.geocoders import Nominatim

from types import SimpleNamespace

def dict_to_obj(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
    
    elif isinstance(d, list):
        return [dict_to_obj(x) for x in d]
    
    return d

def build_dashboard(profile, farm, language="en"):
    lat, lon = resolve_latlon(profile)
    weather = get_forecast(lat, lon)
    location_name = getattr(profile, "village", None) or getattr(profile, "district", None) or "Your Area"

    eval_out = evaluate_all({
        "soil_type": getattr(farm, "soil_type", None),
        "crop_current": getattr(farm, "crop_current", None),
        "sow_date": getattr(farm, "sow_date", None),
        "weather": weather,
    })

    payload = {
        "today": {"title": show_lang(language, "today_tasks"), "items": []},
        "alerts": [],
        "weather": dict_to_obj(weather),   
        "location_name": location_name,
        "crops": eval_out["crops"],
        "ctx": eval_out["ctx"],
    }

    return payload