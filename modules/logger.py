"""
Module 7: Logging and Monitoring
Handles logging operations with timestamps.
"""

from datetime import datetime

def log_event(event_type, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{event_type}] {message}\n"

    # Console output
    print(log_message.strip())

    # Save to log file
    try:
        with open("server_log.txt", "a") as f:
            f.write(log_message)
    except Exception as e:
        print(f"Logging error: {e}")
