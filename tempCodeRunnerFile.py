"""
CCN Project - Main Server
This is the main server file that uses all 8 modular components.
"""

import threading
import time
from modules.logger import log_event
from modules.encryption import get_encryption_key
from modules.server_connection import start_server
from modules.alert_generator import generate_alert
from modules.broadcaster import broadcast_alert
from modules.shutdown import shutdown_server

# ==================== CONFIGURATION ====================
HOST = '127.0.0.1'  # Localhost
PORT = 8888
MAX_CLIENTS = 10

# ==================== GLOBAL VARIABLES ====================
active_clients = {}  # {username: (socket, address)}
server_socket = None
server_running = True
lock = threading.Lock()  # For thread-safe operations


# ==================== ALERT GENERATOR THREAD ====================
def alert_generator():
    """
    Generate and broadcast alerts periodically.
    This function runs in a separate thread.
    """
    while server_running:
        time.sleep(30)  # Generate alert every 30 seconds
        
        if server_running and len(active_clients) > 0:
            alert = generate_alert()
            broadcast_alert(alert, active_clients, lock)


# ==================== MAIN ====================
if __name__ == "__main__":
    try:
        # Print encryption key (client needs this)
        encryption_key = get_encryption_key()
        print(f"\n{'='*50}")
        print("SERVER STARTING...")
        print(f"{'='*50}")
        print(f"Encryption Key (share with clients): {encryption_key.decode()}")
        print(f"{'='*50}\n")
        
        # Start server
        server_socket = start_server(
            HOST, PORT, MAX_CLIENTS, 
            active_clients, lock, server_running, 
            alert_generator
        )
        
    except KeyboardInterrupt:
        print("\n\nServer interrupted by user")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)
    except Exception as e:
        log_event("ERROR", f"Fatal error: {e}")
        server_running = False
        shutdown_server(server_socket, active_clients, lock)
