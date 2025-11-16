"""
Server connection handling.
Authenticate client (plain), send unique encryption key (plain),
wait for client's CIPHER_OK (plain), then switch to encrypted comms.
"""


"""
Server connection handling.

Flow:
- Accept connection
- Authenticate client via authenticate_client(client_socket, address, encryption_key)
- Generate unique key per client (get_encryption_key())
- Send plain ENCRYPTION_KEY:<key>
- Wait for client 'CIPHER_OK' (plain)
- Add to active_clients with tuple (socket, key_bytes)
- Send encrypted welcome using client's unique key (encrypt_with_key + send length+bytes)
- Start ACK handler thread (which will use client's key to decrypt)
"""

import threading
from modules.logger import log_event
from modules.authentication import authenticate_client
from modules.message_handler import send_bytes,  send_message, receive_message
from modules.acknowledgment import handle_client_acknowledgment
from modules.encryption import get_encryption_key, encrypt_with_key

def handle_client_connection(client_socket, address, active_clients, lock, server_running):
    log_event("CONNECTION", f"New connection from {address}")

    # Generate unique key for this client
    encryption_key = get_encryption_key()
    # Print the key in server terminal
    print(f"[{address}] Generated encryption key for client: {encryption_key.decode()}")

    # Step 1: Authenticate (plain) -> authenticate_client expects encryption_key param in your latest file
    try:
        auth_ok = authenticate_client(client_socket, address, encryption_key)
    except TypeError:
        # fallback if authenticate_client signature doesn't expect encryption_key
        auth_ok = authenticate_client(client_socket, address)
    except Exception as e:
        log_event("ERROR", f"Authentication exception for {address}: {e}")
        client_socket.close()
        return

    if not auth_ok:
        client_socket.close()
        log_event("CONNECTION", f"Connection closed from {address} (auth failed)")
        return

    # Step 2: Send the unique encryption key to the client (plain)
    try:
        send_message(client_socket, f"ENCRYPTION_KEY:{encryption_key.decode()}", use_cipher=False)
        log_event("AUTH", f"Encryption key sent to {address}")
    except Exception as e:
        log_event("ERROR", f"Failed to send ENCRYPTION_KEY to {address}: {e}")
        client_socket.close()
        return

    # Step 3: Wait for client's confirmation ("CIPHER_OK")
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

    # Step 4: Add client to active clients with its unique key
    client_id = f"{address[0]}:{address[1]}"
    with lock:
        # store tuple (socket, key_bytes)
        active_clients[client_id] = (client_socket, encryption_key)

    log_event("CONNECTION", f"Client {client_id} added. Total active clients: {len(active_clients)}")

    # Step 5: Send welcome message encrypted using this client's key
    try:
        welcome_msg = f"Welcome {client_id}! You are connected to the server."
        encrypted = encrypt_with_key(encryption_key, welcome_msg)
        if encrypted is None:
            raise Exception("encrypt_with_key returned None")
        send_bytes(client_socket, encrypted)
    except Exception as e:
        log_event("ERROR", f"Failed sending encrypted welcome to {client_id}: {e}")

    # Step 6: Start ACK listener thread (which must use client's key to decrypt incoming messages)
    ack_thread = threading.Thread(
        target=handle_client_acknowledgment,
        args=(client_socket, client_id, address, active_clients, lock, server_running),
        daemon=True
    )
    ack_thread.start()
    ack_thread.join()


def start_server(HOST, PORT, MAX_CLIENTS, active_clients, lock, server_running, alert_generator_func):
    """
    Start server and accept clients. active_clients shall be a mapping of client_id -> (socket, key_bytes)
    """
    import socket
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
                    args=(client_socket, address, active_clients, lock, server_running),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if server_running:
                    log_event("ERROR", f"Error accepting connection: {e}")

    except Exception as e:
        log_event("ERROR", f"Server error: {e}")

    return server_socket
