"""
CCN Project - Main Server
"""

import threading
import time
from modules.logger import log_event
from modules.server_connection import start_server
from modules.alert_generator import generate_alert
from modules.broadcaster import broadcast_alert
from modules.shutdown import shutdown_server

HOST = '127.0.0.1'
PORT = 8888
MAX_CLIENTS = 10

active_clients = {}
lock = threading.Lock()
server_running = True
server_socket = None

def alert_generator():
    while server_running:
        time.sleep(10)
        if len(active_clients) > 0:
            alert = generate_alert()
            broadcast_alert(alert, active_clients, lock)

if __name__ == "__main__":
    try:
        print(f"{'='*50}\nSERVER STARTING...\n{'='*50}")
        server_socket = start_server(
            HOST,
            PORT,
            MAX_CLIENTS,
            active_clients,
            lock,
            server_running,
            alert_generator
        )

    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)
    except Exception as e:
        log_event("ERROR", f"Fatal error: {e}")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)
