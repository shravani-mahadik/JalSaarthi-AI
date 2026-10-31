import requests
from datetime import date, timedelta

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "JalSaarthiAI-EducationalPrototype/1.0"}

def search_locations(place: str):
    response = requests.get(
        GEO_URL,
        params={"name": place, "count": 5, "language": "en", "format": "json"},
        headers=HEADERS,
        timeout=18,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return [{
        "label": ", ".join(str(v) for v in [x.get("name"), x.get("admin1"), x.get("country")] if v),
        "lat": x["latitude"],
        "lon": x["longitude"],
        "timezone": x.get("timezone", "auto"),
    } for x in results]

def fetch_forecast(lat: float, lon: float, timezone: str):
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat, "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration",
            "forecast_days": 7, "timezone": timezone or "auto",
        },
        headers=HEADERS,
        timeout=22,
    )
    response.raise_for_status()
    payload = response.json()
    daily = payload.get("daily")
    required = ["time", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "et0_fao_evapotranspiration"]
    if not daily or any(k not in daily for k in required):
        raise ValueError("Weather provider returned incomplete daily forecast fields.")
    if not daily["time"]:
        raise ValueError("No forecast dates were returned for this location.")
    return payload

def demo_forecast():
    """Clearly labelled synthetic data for offline UI demonstration only."""
    today = date.today()
    return {"daily": {
        "time": [(today + timedelta(days=i)).isoformat() for i in range(7)],
        "temperature_2m_max": [31, 32, 31, 30, 29, 31, 32],
        "temperature_2m_min": [21, 22, 21, 20, 20, 21, 22],
        "precipitation_sum": [0.0, 0.0, 2.0, 0.0, 4.0, 0.0, 0.0],
        "et0_fao_evapotranspiration": [5.2, 5.4, 5.0, 4.8, 4.6, 5.1, 5.3],
    }}
