"""
Dictionary-based client authentication (LOGIN_PAIR sent in plain text)
"""

from modules.logger import log_event
from modules.message_handler import send_message, receive_message

# Predefined username/password dictionary
USER_DICT = {
    "admin": "admin123",
    "user1": "pass123",
    "user2": "pass456"
}

def authenticate_client(client_socket, address, encryption_key):
    """
    Authenticate client using username/password.
    Encryption key is sent along in LOGIN_PAIR but actual cipher
    activation is done manually by client after successful login.
    """
    try:
        # Receive username from client
        client_username = receive_message(client_socket, use_cipher=False)
        if not client_username:
            log_event("AUTH", f"No username received from {address}")
            return False

        # Receive password from client
        client_password = receive_message(client_socket, use_cipher=False)
        if not client_password:
            log_event("AUTH", f"No password received from {address}")
            return False

        # Verify credentials
        if client_username in USER_DICT and client_password == USER_DICT[client_username]:
            # Send AUTH_SUCCESS (no need to send key again, client already has it)
            send_message(client_socket, "AUTH_SUCCESS", use_cipher=False)
            log_event("AUTH", f"Client {address} logged in successfully as {client_username}")
            return True
        else:
            send_message(client_socket, "AUTH_FAILED", use_cipher=False)
            log_event(
                "AUTH",
                f"Client {address} failed login. Entered: {client_username}/{client_password}"
            )
            return False

    except Exception as e:
        log_event("ERROR", f"Authentication error with {address}: {e}")
        return False
