"""
Common message send/receive functions for Client & Server
Handles optional encryption using encryption module
"""

from modules import encryption
from modules.logger import log_event

# ---------------- Send Message ---------------- #
def send_message(sock, message_str, use_cipher=True):
    """
    Send a message over the socket.

    Args:
        sock: socket object
        message_str: string message to send
        use_cipher: whether to encrypt the message

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Encrypt only if use_cipher=True and encryption key is set
        if use_cipher and encryption.ENCRYPTION_KEY:
            encrypted = encryption.encrypt_message(message_str)
            if encrypted is None:
                return False
            data = encrypted
        else:
            data = message_str.encode()

        # Send length first (4 bytes big-endian)
        length = len(data)
        sock.sendall(length.to_bytes(4, 'big'))
        sock.sendall(data)
        return True

    except Exception as e:
        log_event("ERROR", f"send_message error: {e}")
        return False

# ---------------- Receive Message ---------------- #
def receive_message(sock, use_cipher=True):
    """
    Receive a message from the socket.

    Args:
        sock: socket object
        use_cipher: whether to decrypt the message

    Returns:
        Decrypted string if successful, None otherwise
    """
    try:
        # --- Step 1: Read 4-byte length ---
        length_data = b''
        while len(length_data) < 4:
            chunk = sock.recv(4 - len(length_data))
            if not chunk:
                return None
            length_data += chunk

        length = int.from_bytes(length_data, 'big')
        if length <= 0:
            return None

        # --- Step 2: Read message data ---
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk

        # --- Step 3: Decrypt if needed ---
        if use_cipher and encryption.ENCRYPTION_KEY:
            decrypted = encryption.decrypt_message(data)
            return decrypted if decrypted is not None else None
        else:
            return data.decode()

    except Exception as e:
        log_event("ERROR", f"receive_message error: {e}")
        return None
