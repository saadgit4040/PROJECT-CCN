"""
Encryption utilities using Fernet
"""

from cryptography.fernet import Fernet
from modules.logger import log_event

ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def get_encryption_key():
    return ENCRYPTION_KEY

def set_encryption_key(key_bytes):
    global ENCRYPTION_KEY, cipher
    try:
        ENCRYPTION_KEY = key_bytes
        cipher = Fernet(key_bytes)
        return True
    except Exception as e:
        log_event("ERROR", f"Failed to set encryption key: {e}")
        return False

def encrypt_message(message):
    try:
        return cipher.encrypt(message.encode())
    except Exception as e:
        log_event("ERROR", f"Encryption failed: {e}")
        return None

def decrypt_message(encrypted_data):
    try:
        return cipher.decrypt(encrypted_data).decode()
    except Exception as e:
        log_event("ERROR", f"Decryption failed: {e}")
        return None
