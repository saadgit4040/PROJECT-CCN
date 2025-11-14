"""
Client backend: two-step login flow to match GUI
1) enter_credentials(): connect + send USER:username:password (plain)
   -> waits for AUTH_SUCCESS and then plain ENCRYPTION_KEY:<key>
   -> returns (success, msg_or_key)
2) confirm_key(): user provides key; client sets cipher and sends "CIPHER_OK" (plain)
   -> then expects encrypted welcome and starts receiving alerts
"""

import socket
import json
from modules import encryption as _encryption
from modules.message_handler import send_message, receive_message
from CLIENT.modules_gui import gui_client

HOST = '127.0.0.1'
PORT = 8888

def connect_to_server(host=HOST, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def enter_credentials(client_socket, username, password):
    """
    Step 1:
    Send credentials in plain ("USER:username:password").
    On AUTH_SUCCESS server will send plain "ENCRYPTION_KEY:<keystring>".
    Returns: (True, keystring) on success OR (False, error_message)
    """
    try:
        send_message(client_socket, f"USER:{username}:{password}", use_cipher=False)
        resp = receive_message(client_socket, use_cipher=False)
        if resp != "AUTH_SUCCESS":
            return False, "Authentication failed. Check username/password."

        # receive encryption key plain
        key_msg = receive_message(client_socket, use_cipher=False)
        if not key_msg or not key_msg.startswith("ENCRYPTION_KEY:"):
            return False, "Did not receive encryption key from server."
        key_str = key_msg.split(":", 1)[1]
        return True, key_str

    except Exception as e:
        return False, f"enter_credentials error: {e}"

def confirm_key_and_activate(client_socket, key_str):
    """
    Step 2:
    User pasted key_str. Set local cipher, send CIPHER_OK to server (plain).
    Then wait for encrypted welcome (server will now use encryption).
    Returns (True, welcome_message) or (False, error)
    """
    try:
        # Validate key locally by attempting to set it
        key_bytes = key_str.encode()
        if not _encryption.set_encryption_key(key_bytes):
            return False, "Invalid key format locally."

        # Let server know we set the cipher
        send_message(client_socket, "CIPHER_OK", use_cipher=False)

        # Now receive an encrypted welcome (use_cipher=True)
        welcome = receive_message(client_socket, use_cipher=True)
        if not welcome:
            return False, "Did not receive encrypted welcome from server."
        return True, welcome

    except Exception as e:
        return False, f"confirm_key error: {e}"

def handle_alert(alert_data):
    try:
        alert = json.loads(alert_data)
        msg = f"[{alert['priority']}] {alert['message']} (Time: {alert['timestamp']})"
        return alert['alert_id'], alert['priority'], msg
    except Exception as e:
        return None, "ERROR", f"Error processing alert: {e}"

def receive_alerts(client_socket, gui_console):
    """
    Loop to receive (encrypted) alerts and display to gui_console via gui_console.append(msg, tag)
    """
    while True:
        message = receive_message(client_socket, use_cipher=True)
        if not message:
            gui_console.append("Connection lost!", "error")
            break
        if message == "SERVER_SHUTDOWN":
            gui_console.append("Server shutting down.", "info")
            break
        if message.startswith("ALERT:"):
            alert_id, priority, alert_msg = handle_alert(message.split(":", 1)[1])
            tag = "high" if priority.upper() == "HIGH" else "medium" if priority.upper() == "MEDIUM" else "low"
            gui_console.append(alert_msg, tag)
            if alert_id:
                send_message(client_socket, f"ACK:{alert_id}", use_cipher=True)
        else:
            gui_console.append(f"Server: {message}", "info")

# ----------------- Launcher ----------------- #
if __name__ == "__main__":
    print("🚀 Launching Client GUI...")
    try:
        gui_client. run_gui()
    except Exception as e:
        print(f"❌ Failed to open GUI: {e}")


   
