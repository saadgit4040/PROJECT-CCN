"""
Main Client Backend
Handles connection, login, encryption, alert handling
"""

import threading
from modules import encryption as _encryption
from modules.message_handler import send_message, receive_message
from CLIENT.modules_gui import gui_client
import socket
import json

HOST = '127.0.0.1'
PORT = 8888

# ---------------- Backend Functions ---------------- #

def connect_to_server(host=HOST, port=PORT):
    """Connect to the server and return the client socket."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def receive_login_pair(client_socket):
    """
    Receives LOGIN_PAIR from server.
    Returns (server_user, server_pass, server_key) or raises Exception.
    """
    message = receive_message(client_socket, use_cipher=False)
    if not message or not message.startswith("LOGIN_PAIR:"):
        raise Exception("Failed to receive login pair from server.")
    parts = message.split(":")
    if len(parts) < 5:
        raise Exception("Invalid login packet format from server.")
    _, server_user, server_pass, _, server_key = parts
    return server_user, server_pass, server_key

def login(client_socket, username, password, key_bytes):
    """
    Handles login and encryption setup.
    Returns (success: bool, message: str)
    """
    try:
        # Send credentials to server
        send_message(client_socket, username, use_cipher=False)
        send_message(client_socket, password, use_cipher=False)

        response = receive_message(client_socket, use_cipher=False)
        if response and response.startswith("AUTH_SUCCESS"):
            if _encryption.set_encryption_key(key_bytes):
                return True, "Authentication successful!"
            else:
                return False, "Invalid decryption key."
        else:
            return False, "Authentication failed."
    except Exception as e:
        return False, f"Login error: {e}"

def handle_alert(alert_data):
    """
    Parse alert JSON and return alert ID, priority, and formatted message.
    """
    try:
        alert = json.loads(alert_data)
        msg = f"[{alert['priority']}] {alert['message']} (Time: {alert['timestamp']})"
        return alert['alert_id'], alert['priority'], msg
    except Exception as e:
        return None, "ERROR", f"Error processing alert: {e}"

def receive_alerts(client_socket, gui_console):
    """
    Loop to receive alerts and send ACKs.
    gui_console must have an append(msg, tag) method.
    """
    while True:
        message = receive_message(client_socket)
        if not message:
            gui_console.append("Connection lost!", "error")
            break
        if message == "SERVER_SHUTDOWN":
            gui_console.append("Server shutting down. Disconnecting...", "info")
            break
        elif message == "HEARTBEAT_OK":
            continue
        elif message.startswith("ALERT:"):
            alert_id, priority, alert_msg = handle_alert(message.split(":", 1)[1])
            tag = "high" if priority.upper() == "HIGH" else "medium" if priority.upper() == "MEDIUM" else "low"
            gui_console.append(alert_msg, tag)
            if alert_id:
                send_message(client_socket, f"ACK:{alert_id}")
        else:
            gui_console.append(f"Server: {message}", "info")

# ---------------- GUI Launcher ---------------- #

if __name__ == "__main__":
    gui_client.run_gui()
