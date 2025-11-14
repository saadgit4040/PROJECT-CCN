"""
Dictionary-based client authentication (plain-text exchange)
Server expects plain messages: "USER:username:password"
Sends plain "AUTH_SUCCESS" or "AUTH_FAIL" and then (on success)
sends the encryption key in plain: "ENCRYPTION_KEY:<key_string>"
"""

from modules.logger import log_event
from modules.message_handler import receive_message, send_message

# Predefined username/password dictionary
USER_DICT = {
    "admin": "admin123",
    "user1": "pass123",
    "user2": "pass456"
}

def authenticate_client(client_socket, address, encryption_key):
    """
    Authenticate client using username/password.
    Returns True on success. Sends AUTH_SUCCESS/AUTH_FAIL (plain).
    """
    try:
        # Read plain message from client
        msg = receive_message(client_socket, use_cipher=False)
        if not msg or not msg.startswith("USER:"):
            log_event("AUTH", f"Invalid auth format from {address}: {msg}")
            send_message(client_socket, "AUTH_FAIL", use_cipher=False)
            return False

        _, username, password = msg.split(":", 2)
        log_event("AUTH", f"Received login attempt from {address} ({username})")

        if username in USER_DICT and USER_DICT[username] == password:
            send_message(client_socket, "AUTH_SUCCESS", use_cipher=False)
            log_event("AUTH", f"Authentication success for {address} ({username})")
            return True
        else:
            send_message(client_socket, "AUTH_FAIL", use_cipher=False)
            log_event("AUTH", f"Authentication failed for {address} ({username})")
            return False

    except Exception as e:
        log_event("ERROR", f"Authentication error for {address}: {e}")
        try:
            send_message(client_socket, "AUTH_FAIL", use_cipher=False)
        except Exception:
            pass
        return False
