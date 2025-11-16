"""
Encryption utilities using Fernet

Provides:
- get_encryption_key() -> generates/returns a new Fernet key (per client use)
- set_encryption_key(key_bytes) -> change global key for client process (client uses this)
- encrypt_message / decrypt_message -> encrypt/decrypt using global cipher (client-side)
- encrypt_with_key / decrypt_with_key -> encrypt/decrypt with a provided key (server uses these per-client)
"""

from cryptography.fernet import Fernet
from modules.logger import log_event

# Default global encryption key (used by the client process once it activates)
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)


def get_encryption_key():
    """
    Return a NEW encryption key (bytes). Use this to give a unique key per client.
    (Generates a fresh Fernet key.)
    """
    return Fernet.generate_key()


def set_encryption_key(key_bytes):
    """
    Set the global ENCRYPTION_KEY and update the global cipher (client-side).
    """
    global ENCRYPTION_KEY, cipher
    try:
        ENCRYPTION_KEY = key_bytes
        cipher = Fernet(key_bytes)
        return True
    except Exception as e:
        log_event("ERROR", f"Failed to set encryption key: {e}")
        return False


def encrypt_message(message):
    """
    Encrypt using global cipher (client uses this after set_encryption_key).
    Returns bytes or None on error.
    """
    try:
        return cipher.encrypt(message.encode())
    except Exception as e:
        log_event("ERROR", f"Encryption failed: {e}")
        return None


def decrypt_message(encrypted_data):
    """
    Decrypt using global cipher (client uses this after set_encryption_key).
    Returns string or None on error.
    """
    try:
        return cipher.decrypt(encrypted_data).decode()
    except Exception as e:
        log_event("ERROR", f"Decryption failed: {e}")
        return None


# -------------------- Server-side helpers (stateless) --------------------
def encrypt_with_key(key_bytes, message):
    """
    Encrypt `message` string using the provided key (does not change global cipher).
    Returns bytes or raises exception.
    """
    try:
        temp = Fernet(key_bytes)
        return temp.encrypt(message.encode())
    except Exception as e:
        log_event("ERROR", f"encrypt_with_key failed: {e}")
        return None


def decrypt_with_key(key_bytes, encrypted_data):
    """
    Decrypt bytes using provided key (does not change global cipher).
    Returns string or None.
    """
    try:
        temp = Fernet(key_bytes)
        return temp.decrypt(encrypted_data).decode()
    except Exception as e:
        log_event("ERROR", f"decrypt_with_key failed: {e}")
        return None
