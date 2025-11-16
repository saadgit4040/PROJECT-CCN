"""
Module 5: Broadcasting System
Sends each alert simultaneously to all connected clients using each client's unique key.
active_clients must be {client_id: (client_socket, client_key_bytes)}
"""

import json
from modules.logger import log_event
from modules.encryption import encrypt_with_key
from modules.message_handler import send_bytes

def broadcast_alert(alert, active_clients, lock):
    """
    Send alert to all connected clients using their individual key.
    """
    alert_json = json.dumps(alert)
    disconnected = []

    with lock:
        for client_id, val in list(active_clients.items()):
            try:
                # val = (socket, key_bytes) OR earlier mapping - guard
                if isinstance(val, tuple) and len(val) >= 2:
                    client_socket, client_key = val[0], val[1]
                else:
                    # if old format still present, assume val is socket
                    client_socket = val
                    client_key = None

                if client_key is None:
                    # fallback: send unencrypted (shouldn't happen in new design)
                    send_bytes(client_socket, f"ALERT:{alert_json}".encode())
                else:
                    encrypted = encrypt_with_key(client_key, f"ALERT:{alert_json}")
                    if encrypted is None:
                        raise Exception("encrypt_with_key failed")
                    send_bytes(client_socket, encrypted)

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
