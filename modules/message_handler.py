"""
Common message send/receive functions for Client & Server
Handles optional encryption using modules.encryption
"""

from modules import encryption
from modules.logger import log_event

def send_message(sock, message_str, use_cipher=True):
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

def receive_message(sock, use_cipher=True):
    try:
        length_data = b''
        while len(length_data) < 4:
            chunk = sock.recv(4 - len(length_data))
            if not chunk:
                return None
            length_data += chunk

        length = int.from_bytes(length_data, 'big')
        if length <= 0:
            return None

        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk

        if use_cipher and encryption.ENCRYPTION_KEY:
            return encryption.decrypt_message(data)
        else:
            return data.decode()
    except Exception as e:
        log_event("ERROR", f"receive_message error: {e}")
        return None
