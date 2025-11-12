"""
Module 6: Client Acknowledgment Handling
Receives "ACK" messages from clients confirming alert delivery.
"""

from modules.logger import log_event
from modules.message_handler import send_message, receive_message

def handle_client_acknowledgment(client_socket, username, address, active_clients, lock, server_running):
    """
    Handle acknowledgment messages from client.
    """
    while server_running:
        try:
            # After login, communications are encrypted
            message = receive_message(client_socket, use_cipher=True)
            if not message:
                break

            if message.startswith("ACK:"):
                alert_id = message.split(":", 1)[1]
                log_event("ACK", f"Received ACK from {username} for alert {alert_id}")
            elif message == "HEARTBEAT":
                send_message(client_socket, "HEARTBEAT_OK", use_cipher=True)
            else:
                log_event("MESSAGE", f"Received from {username}: {message}")

        except Exception as e:
            log_event("ERROR", f"Error handling client {username}: {e}")
            break

    # Client disconnected
    with lock:
        if username in active_clients:
            del active_clients[username]
    log_event("DISCONNECT", f"Client {username} ({address}) disconnected")
