import requests

API_KEY = "579b464db66ec23bdd00000199bd110ee1ad4aa67422f9cc263d5050"
URL = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"

params = {
    "api-key": API_KEY,
    "format": "json",
    "filters[district]": "Agra",
    "filters[commodity]": "Wheat",
    "limit": 50
}

response = requests.get(URL, params=params)
data = response.json()

for key, value in data.items():
    print(f"{key} : {value}")