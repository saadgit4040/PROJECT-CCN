"""
Module 4: Alert Generation and Priority System
Generates alerts with priority levels (Low, Medium, High) based on environmental data.
"""

import time
from datetime import datetime
import weather_api
from modules.logger import log_event


def generate_alert():
    """
    Generate random alert with priority based on weather data.
    
    Returns:
        dict: Alert data with priority, message, and timestamp
        
    Example:
        alert = generate_alert()
        # Returns: {
        #     "priority": "HIGH",
        #     "message": "Weather Alert: Temp: 32°C...",
        #     "timestamp": "2024-01-01 12:00:00",
        #     "alert_id": 1234567890
        # }
    """
    weather = weather_api.get_current_weather()
    
    # Determine priority based on weather conditions
    if weather["temperature"] > 30 or weather["humidity"] > 80:
        priority = "HIGH"
    elif weather["temperature"] > 25 or weather["humidity"] > 60:
        priority = "MEDIUM"
    else:
        priority = "LOW"
    
    alert = {
        "priority": priority,
        "message": f"Weather Alert: {weather_api.get_weather_string()}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_id": int(time.time())  # Unique ID based on timestamp
    }
    
    log_event("ALERT", f"Generated {priority} priority alert: {alert['message']}")
    return alert

