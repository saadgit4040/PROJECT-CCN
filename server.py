"""
CCN Project - Main Server
This is the main server file that uses all modular components.
"""

import threading
import time
from modules.logger import log_event
from modules.encryption import get_encryption_key
from modules.server_connection import start_server
from modules.alert_generator import generate_alert
from modules.broadcaster import broadcast_alert
from modules.shutdown import shutdown_server

# ==================== CONFIGURATION ==================== #
HOST = '127.0.0.1'
PORT = 8888
MAX_CLIENTS = 10

# Shared resources
active_clients = {}
lock = threading.Lock()
server_running = True
server_socket = None


# ==================== ALERT GENERATOR THREAD ==================== #
def alert_generator():
    """
    Periodically generates alerts and broadcasts them to all active clients.
    """
    while server_running:
        time.sleep(30)  # Every 30 seconds, generate a new alert
        if len(active_clients) > 0:
            alert = generate_alert()
            broadcast_alert(alert, active_clients, lock)


# ==================== MAIN SERVER EXECUTION ==================== #
if __name__ == "__main__":
    try:
        encryption_key = get_encryption_key()
        print(f"{'='*50}\nSERVER STARTING...\n{'='*50}")
        print("Encryption Key (share with clients exactly):")
        print(f"  As bytes: {repr(encryption_key)}")
        print(f"  As string: {encryption_key.decode()}")
        print(f"{'='*50}\n")

        # Start the server
        server_socket = start_server(
            HOST,
            PORT,
            MAX_CLIENTS,
            active_clients,
            lock,
            server_running,
            alert_generator,
            encryption_key
        )

    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)

    except Exception as e:
        log_event("ERROR", f"Fatal error in main server: {e}")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)
