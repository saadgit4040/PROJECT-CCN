"""
Handle client connections & authentication threads
"""

import threading
import socket
from modules.logger import log_event
from modules.authentication import authenticate_client, USER_DICT
from modules.message_handler import send_message
from modules.acknowledgment import handle_client_acknowledgment
import random

def handle_client_connection(client_socket, address, active_clients, lock, server_running, encryption_key):
    """
    Handles authentication and starts acknowledgment thread for each client.
    """
    log_event("CONNECTION", f"New connection from {address}")

    # Step 1: Send login credentials + encryption key together
    try:
        username, password = random.choice(list(USER_DICT.items()))
        send_message(
            client_socket,
            f"LOGIN_PAIR:{username}:{password}:KEY:{encryption_key.decode()}",
            use_cipher=False
        )
        log_event("AUTH", f"Sent LOGIN_PAIR and key to {address}")
    except Exception as e:
        log_event("ERROR", f"Failed to send LOGIN_PAIR to {address}: {e}")
        client_socket.close()
        return

    # Step 2: Authenticate client (waits for username/password)
    success = authenticate_client(client_socket, address, encryption_key)
    if not success:
        client_socket.close()
        log_event("CONNECTION", f"Connection closed from {address} (auth failed)")
        return

    # Step 3: Add authenticated client to active list
    client_id = f"{address[0]}:{address[1]}"
    with lock:
        active_clients[client_id] = client_socket

    log_event("CONNECTION", f"Client {client_id} added. Total active clients: {len(active_clients)}")

    # Step 4: Send welcome message (encrypted now)
    send_message(client_socket, f"Welcome {client_id}! You are connected to the server.", use_cipher=True)

    # Step 5: Start acknowledgment listener thread
    ack_thread = threading.Thread(
        target=handle_client_acknowledgment,
        args=(client_socket, client_id, address, active_clients, lock, server_running),
        daemon=True
    )
    ack_thread.start()

    # Wait until acknowledgment thread finishes
    ack_thread.join()


def start_server(HOST, PORT, MAX_CLIENTS, active_clients, lock, server_running, alert_generator_func, encryption_key):
    """
    Initializes the server, listens for clients, and spawns threads per client.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        log_event("SERVER", f"Server started on {HOST}:{PORT}")
        log_event("SERVER", "Waiting for clients...")

        # Start alert generator thread
        alert_thread = threading.Thread(target=alert_generator_func, daemon=True)
        alert_thread.start()

        # Accept clients in loop
        while server_running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=handle_client_connection,
                    args=(client_socket, address, active_clients, lock, server_running, encryption_key),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if server_running:
                    log_event("ERROR", f"Error accepting connection: {e}")

    except Exception as e:
        log_event("ERROR", f"Server error: {e}")

    return server_socket
