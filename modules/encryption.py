"""
Module: Secure Communication
Handles encryption and decryption of messages using Fernet (AES)
Compatible with GUI client and terminal client
"""

from cryptography.fernet import Fernet
from modules.logger import log_event

# ---------------- Global Encryption Setup ---------------- #
# Default encryption key (generated once at server start)
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# ---------------- Get Encryption Key ---------------- #
def get_encryption_key():
    """
    Return the current encryption key (for server to share with client)
    """
    return ENCRYPTION_KEY

# ---------------- Set Encryption Key ---------------- #
def set_encryption_key(key_bytes):
    """
    Set encryption key dynamically (used when client pastes server key)
    
    Args:
        key_bytes: bytes of the Fernet key
    Returns:
        True if key set successfully, False otherwise
    """
    global ENCRYPTION_KEY, cipher
    try:
        ENCRYPTION_KEY = key_bytes
        cipher = Fernet(key_bytes)
        return True
    except Exception as e:
        log_event("ERROR", f"Failed to set encryption key: {e}")
        return False

# ---------------- Encrypt Message ---------------- #
def encrypt_message(message):
    """
    Encrypt message string to bytes using Fernet

    Args:
        message: string message
    Returns:
        encrypted bytes or None if failed
    """
    try:
        return cipher.encrypt(message.encode())
    except Exception as e:
        log_event("ERROR", f"Encryption failed: {e}")
        return None

# ---------------- Decrypt Message ---------------- #
def decrypt_message(encrypted_data):
    """
    Decrypt bytes to string using Fernet

    Args:
        encrypted_data: bytes
    Returns:
        decrypted string or None if failed
    """
    try:
        return cipher.decrypt(encrypted_data).decode()
    except Exception as e:
        log_event("ERROR", f"Decryption failed: {e}")
        return None
