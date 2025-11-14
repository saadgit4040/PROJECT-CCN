"""
Server connection handling.
Authenticate client (plain), send encryption key (plain),
wait for client's CIPHER_OK (plain), then switch to encrypted comms.
"""

import threading
import socket
from modules.logger import log_event
from modules.authentication import authenticate_client
from modules.message_handler import send_message, receive_message
from modules.acknowledgment import handle_client_acknowledgment

def handle_client_connection(client_socket, address, active_clients, lock, server_running, encryption_key):
    log_event("CONNECTION", f"New connection from {address}")

    # Step 1: Authenticate (plain)
    auth_ok = authenticate_client(client_socket, address, encryption_key)
    if not auth_ok:
        client_socket.close()
        log_event("CONNECTION", f"Connection closed from {address} (auth failed)")
        return

    # Step 2: Send encryption key (plain), client will paste and send CIPHER_OK after it sets cipher locally
    try:
        send_message(client_socket, f"ENCRYPTION_KEY:{encryption_key.decode()}", use_cipher=False)
        log_event("AUTH", f"Encryption key sent to {address}")
    except Exception as e:
        log_event("ERROR", f"Failed to send ENCRYPTION_KEY to {address}: {e}")
        client_socket.close()
        return

    # Step 3: Wait for client's confirmation that it set the cipher
    try:
        confirmation = receive_message(client_socket, use_cipher=False)
        if confirmation != "CIPHER_OK":
            log_event("AUTH", f"Client {address} did not confirm cipher (received: {confirmation})")
            client_socket.close()
            return
    except Exception as e:
        log_event("ERROR", f"Error waiting for CIPHER_OK from {address}: {e}")
        client_socket.close()
        return

    # Step 4: Add to active clients and send encrypted welcome
    client_id = f"{address[0]}:{address[1]}"
    with lock:
        active_clients[client_id] = client_socket

    log_event("CONNECTION", f"Client {client_id} added. Total active clients: {len(active_clients)}")

    # Send welcome encrypted (server side encryption module must already be using same key)
    try:
        send_message(client_socket, f"Welcome {client_id}! You are connected to the server.", use_cipher=True)
    except Exception as e:
        log_event("ERROR", f"Failed sending encrypted welcome to {client_id}: {e}")

    # Start ACK listener thread (it will use encrypted receive once cipher is active)
    ack_thread = threading.Thread(
        target=handle_client_acknowledgment,
        args=(client_socket, client_id, address, active_clients, lock, server_running),
        daemon=True
    )
    ack_thread.start()
    ack_thread.join()


def start_server(HOST, PORT, MAX_CLIENTS, active_clients, lock, server_running, alert_generator_func, encryption_key):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        log_event("SERVER", f"Server started on {HOST}:{PORT}")
        log_event("SERVER", "Waiting for clients...")

        # Start alert generator
        alert_thread = threading.Thread(target=alert_generator_func, daemon=True)
        alert_thread.start()

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
