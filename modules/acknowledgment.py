"""
Module 6: Client Acknowledgment Handling
Now decrypts incoming encrypted messages using client's individual key
(active_clients mapping contains (socket, key_bytes))
"""

from modules.logger import log_event
from modules.message_handler import recv_bytes, send_bytes
from modules.encryption import decrypt_with_key,encrypt_with_key

def handle_client_acknowledgment(client_socket, client_id, address, active_clients, lock, server_running):
    """
    Handle acknowledgment messages from client.
    client_id is the identifier (string "ip:port")
    active_clients maps client_id -> (socket, key_bytes)
    """
    # get the client's key
    client_key = None
    try:
        with lock:
            val = active_clients.get(client_id)
            if isinstance(val, tuple) and len(val) >= 2:
                client_key = val[1]
    except Exception as e:
        log_event("ERROR", f"Ack handler couldn't get key for {client_id}: {e}")

    if client_key is None:
        log_event("ERROR", f"No key for client {client_id}, closing ack handler.")
        return

    while server_running:
        try:
            # Receive raw bytes (length-prefixed)
            data = recv_bytes(client_socket)
            if not data:
                break

            # Decrypt using client's key
            message = decrypt_with_key(client_key, data)
            if message is None:
                log_event("ERROR", f"Could not decrypt message from {client_id}")
                continue

            if message.startswith("ACK:"):
                alert_id = message.split(":", 1)[1]
                log_event("ACK", f"Received ACK from {client_id} for alert {alert_id}")
            elif message == "HEARTBEAT":
                # reply with HEARTBEAT_OK encrypted with client's key
                reply = "HEARTBEAT_OK"
                enc = encrypt_with_key(client_key, reply)
                if enc:
                    send_bytes(client_socket, enc)
            else:
                log_event("MESSAGE", f"Received from {client_id}: {message}")

        except Exception as e:
            log_event("ERROR", f"Error handling client {client_id}: {e}")
            break

    # Client cleanup
    with lock:
        if client_id in active_clients:
            try:
                del active_clients[client_id]
            except KeyError:
                pass
    log_event("DISCONNECT", f"Client {client_id} ({address}) disconnected")
