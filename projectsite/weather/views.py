import logging
import os

import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)

API_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_CITY = "Puerto Princesa"


def weather_view(request):
    api_key = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
    city_param = request.GET.get("city")

    if city_param is None:
        city = DEFAULT_CITY
    else:
        city = city_param.strip()

    if not api_key:
        weather_data = {
            "error": (
                "The weather service is not configured yet. Add "
                "OPENWEATHER_API_KEY to your .env file and restart the server."
            )
        }
    elif not city:
        weather_data = {"error": "Please enter a city name."}
    else:
        weather_data = fetch_weather(city, api_key)

    return render(request, "weather.html", {"weather": weather_data, "city": city})


def fetch_weather(city, api_key):
    try:
        response = requests.get(
            API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
        }
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code == 401:
            message = (
                "The OpenWeather API rejected the API key. Check the "
                "OPENWEATHER_API_KEY value in your .env file."
            )
        elif status_code in (400, 404):
            message = f"No weather found for '{city}'. Check the city name and try again."
        elif status_code == 429:
            message = "Too many requests right now. Please wait a moment and try again."
        else:
            message = "The weather service returned an error. Please try again."
        logger.warning(
            "OpenWeather request failed for city=%r status=%s", city, status_code
        )
        return {"error": message}
    except requests.exceptions.Timeout:
        logger.warning("OpenWeather request timed out for city=%r", city)
        return {
            "error": "The weather service took too long to respond. Please try again."
        }
    except requests.exceptions.JSONDecodeError:
        logger.warning("OpenWeather returned invalid JSON for city=%r", city)
        return {
            "error": "The weather service returned an unexpected response. Please try again."
        }
    except requests.exceptions.RequestException:
        logger.warning("OpenWeather request error for city=%r", city)
        return {
            "error": "Could not reach the weather service. Check your connection and try again."
        }
    except (KeyError, IndexError, TypeError):
        logger.warning("Unexpected OpenWeather payload for city=%r", city)
        return {
            "error": "The weather service returned an unexpected response. Please try again."
        }
