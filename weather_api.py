"""
Weather API Module
Fetches real-time weather data from OpenWeatherMap API.
If connection fails, prints an error message instead of falling back to dummy data.
"""

import requests
from datetime import datetime

# ==================== CONFIGURATION ==================== #
API_KEY = "833e18e3d3df702326c6f5e1b57b3701"  # Your OpenWeatherMap API key
CITY = "Karachi"                              # Change to your city
UNITS = "metric"                              # "metric" for Celsius, "imperial" for Fahrenheit


def get_current_weather():
    """
    Fetch real-time weather data from OpenWeatherMap API.
    
    Returns:
        dict: Weather data (temperature, humidity, condition, timestamp)
    """
    # ✅ Fixed URL formatting
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units={UNITS}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error if response is not OK (e.g., 404 or 401)
        data = response.json()

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except requests.exceptions.ConnectionError:
        print("⚠️  No active internet connection.")
        return None

    except requests.exceptions.Timeout:
        print("⚠️  Weather API request timed out.")
        return None

    except Exception as e:
        print(f"⚠️  Weather API error: {e}")
        return None


def get_weather_string():
    """
    Get weather as a formatted string for display.
    """
    weather = get_current_weather()
    if not weather:
        return "No active connection or failed to fetch weather data."

    return f"Temp: {weather['temperature']}°C, Humidity: {weather['humidity']}%, Condition: {weather['condition']}"


# if __name__ == "__main__":
#     print("Fetching live weather data...\n")
#     print(get_weather_string())
