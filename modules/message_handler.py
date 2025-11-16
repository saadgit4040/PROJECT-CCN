"""
Common message send/receive functions for Client & Server
Handles plain and encrypted messages, plus helper to send/receive raw bytes
"""

from modules import encryption
from modules.logger import log_event

# ---------------- Send Message (string) ---------------- #
def send_message(sock, message_str, use_cipher=True):
    """
    Send a string message. If use_cipher=True and the global encryption key is set,
    the message is encrypted (client-side) before sending.
    """
    try:
        if use_cipher and encryption.ENCRYPTION_KEY:
            encrypted = encryption.encrypt_message(message_str)
            if encrypted is None:
                return False
            data = encrypted
        else:
            data = message_str.encode()

        length = len(data)
        sock.sendall(length.to_bytes(4, 'big'))
        sock.sendall(data)
        return True
    except Exception as e:
        log_event("ERROR", f"send_message error: {e}")
        return False


# ---------------- Receive Message (string) ---------------- #
def receive_message(sock, use_cipher=True):
    """
    Receive a length-prefixed message and return a string.
    If use_cipher=True and the global key is set, decryption is attempted.
    """
    try:
        # Read length
        length_data = recv_exact(sock, 4)
        if not length_data:
            return None
        length = int.from_bytes(length_data, 'big')
        if length <= 0:
            return None

        data = recv_exact(sock, length)
        if data is None:
            return None

        if use_cipher and encryption.ENCRYPTION_KEY:
            return encryption.decrypt_message(data)
        else:
            return data.decode()
    except Exception as e:
        log_event("ERROR", f"receive_message error: {e}")
        return None


# ---------------- Raw bytes helpers (for server to send per-client encrypted bytes) ---------------- #
def send_bytes(sock, data_bytes):
    """
    Send raw bytes with 4-byte length prefix.
    """
    try:
        length = len(data_bytes)
        sock.sendall(length.to_bytes(4, 'big'))
        sock.sendall(data_bytes)
        return True
    except Exception as e:
        log_event("ERROR", f"send_bytes error: {e}")
        return False


def recv_exact(sock, n):
    """
    Receive exactly n bytes from socket (or None if connection closed).
    """
    try:
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf
    except Exception as e:
        log_event("ERROR", f"recv_exact error: {e}")
        return None


def recv_bytes(sock):
    """
    Receive length-prefixed bytes and return raw bytes (no decryption).
    """
    try:
        length_data = recv_exact(sock, 4)
        if not length_data:
            return None
        length = int.from_bytes(length_data, 'big')
        if length <= 0:
            return None
        data = recv_exact(sock, length)
        return data
    except Exception as e:
        log_event("ERROR", f"recv_bytes error: {e}")
        return None
