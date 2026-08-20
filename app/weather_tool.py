import json
import urllib.parse
import urllib.request


def get_weather(location: str = "Seattle") -> str:
    """Fetches real live weather data for any city or location using Open-Meteo Weather API.

    Args:
        location: City or location name (e.g., 'Seattle', 'San Francisco', 'New York', 'Tokyo').

    Returns:
        A string summarizing real-time live weather conditions, temperature in °F, humidity, and wind speed.
    """
    try:
        encoded_location = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_location}&count=1"
        geo_req = urllib.request.urlopen(geo_url, timeout=5)
        geo_data = json.loads(geo_req.read().decode())

        if not geo_data.get("results"):
            return f"Could not find location data for '{location}'. Please try a major city name."

        res = geo_data["results"][0]
        name = res.get("name", location)
        admin = res.get("admin1", "")
        country = res.get("country", "")
        lat = res["latitude"]
        lon = res["longitude"]

        w_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&temperature_unit=fahrenheit"
        )
        w_req = urllib.request.urlopen(w_url, timeout=5)
        w_data = json.loads(w_req.read().decode())
        current = w_data.get("current", {})

        temp = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")
        code = current.get("weather_code", 0)

        wmo_codes = {
            0: "Clear sky ☀️",
            1: "Mainly clear 🌤️",
            2: "Partly cloudy ⛅",
            3: "Overcast ☁️",
            45: "Foggy 🌫️",
            48: "Depositing rime fog 🌫️",
            51: "Light drizzle 🌧️",
            53: "Moderate drizzle 🌧️",
            55: "Dense drizzle 🌧️",
            61: "Slight rain 🌧️",
            63: "Moderate rain 🌧️",
            65: "Heavy rain 🌧️",
            71: "Slight snow fall ❄️",
            73: "Moderate snow fall ❄️",
            75: "Heavy snow fall ❄️",
            80: "Slight rain showers 🌦️",
            81: "Moderate rain showers 🌦️",
            82: "Violent rain showers ⛈️",
            95: "Thunderstorm 🌩️",
        }
        condition = wmo_codes.get(code, "Clear/Mild ☀️")
        loc_str = (
            f"{name}, {admin} ({country})" if admin else f"{name}, {country}"
        )

        return (
            f"Live weather for {loc_str}:\n"
            f"• Condition: {condition}\n"
            f"• Temperature: {temp}°F\n"
            f"• Humidity: {humidity}%\n"
            f"• Wind Speed: {wind} mph"
        )
    except Exception as e:
        return f"Live weather lookup for '{location}' currently unavailable: {e}"
