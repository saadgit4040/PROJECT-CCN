"""
Weather API Module
This module handles weather data fetching.
You can modify this later to specify what type of temperature/weather data you want.
"""

import random
import json
from datetime import datetime


def get_current_weather():
    """
    Get current weather data.
    For now, this simulates weather data.
    You can replace this with actual API calls later (OpenWeatherMap, etc.)
    
    Returns:
        dict: Weather data including temperature, humidity, condition
    """
    # Simulated weather data - you can replace this with real API later
    weather_data = {
        "temperature": round(random.uniform(15, 35), 2),  # Temperature in Celsius
        "humidity": round(random.uniform(40, 90), 2),     # Humidity percentage
        "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return weather_data


def get_weather_string():
    """
    Get weather as a formatted string.
    
    Returns:
        str: Formatted weather information
    """
    weather = get_current_weather()
    return f"Temp: {weather['temperature']}°C, Humidity: {weather['humidity']}%, Condition: {weather['condition']}"


# Example: If you want to use real API later, uncomment and modify this:
"""
import requests

def get_current_weather():
    API_KEY = "your_api_key_here"
    CITY = "your_city"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_current_weather()  # Fallback to simulated data
"""

