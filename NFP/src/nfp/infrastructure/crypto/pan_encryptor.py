"""PAN Encryption."""
from cryptography.fernet import Fernet
import keyring

class PanEncryptor:
    """Encrypts and decrypts PANs using Fernet."""
    def __init__(self, service_name: str, username: str):
        key = keyring.get_password(service_name, username)
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(service_name, username, key)
        self.fernet = Fernet(key.encode())

    def encrypt(self, pan: str) -> bytes:
        """Encrypt PAN."""
        return self.fernet.encrypt(pan.encode())

    def decrypt(self, encrypted_pan: bytes) -> str:
        """Decrypt PAN."""
        return self.fernet.decrypt(encrypted_pan).decode()
