"""
Module 5: Broadcasting System
Sends each alert simultaneously to all connected clients.
"""

import json
from modules.logger import log_event
from modules.message_handler import send_message

def broadcast_alert(alert, active_clients, lock):
    """
    Send alert to all connected clients.

    Args:
        alert: Alert dictionary
        active_clients: Dictionary of active clients {client_id: client_socket}
        lock: Threading lock for thread-safe operations
    """
    alert_json = json.dumps(alert)
    disconnected = []

    with lock:
        for client_id, client_socket in list(active_clients.items()):
            try:
                # Alerts should be encrypted now
                send_message(client_socket, f"ALERT:{alert_json}", use_cipher=True)
                log_event("BROADCAST", f"Alert sent to {client_id}")
            except Exception as e:
                log_event("ERROR", f"Failed to send alert to {client_id}: {e}")
                disconnected.append(client_id)

        for client_id in disconnected:
            try:
                del active_clients[client_id]
                log_event("DISCONNECT", f"Removed disconnected client: {client_id}")
            except KeyError:
                pass
