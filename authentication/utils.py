"""
Encryption utilities for secure credential storage and retrieval.

This module provides functions for encrypting and decrypting sensitive data
using Fernet symmetric encryption with PBKDF2 key derivation.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from decouple import config


# Global cipher instance (initialized when module is imported)
_cipher = None


def _get_cipher():
    """
    Get or initialize the Fernet cipher instance.

    Returns:
        Fernet: Initialized cipher for encryption/decryption
    """
    global _cipher
    if _cipher is None:
        encryption_key = config('ENCRYPTION_KEY', default='')
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is not set")

        # Use PBKDF2 to derive a proper Fernet key from the environment variable
        password = encryption_key.encode()
        salt = b'e-governance-salt-2025'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # High iteration count for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        _cipher = Fernet(key)

    return _cipher


def encrypt_data(data: str) -> str:
    """
    Encrypt string data using Fernet symmetric encryption.

    Args:
        data (str): Plain text data to encrypt

    Returns:
        str: Base64 encoded encrypted data

    Raises:
        ValueError: If data is not a string or is empty
        Exception: If encryption fails
    """
    if not isinstance(data, str):
        raise ValueError("Data must be a string")
    if not data:
        raise ValueError("Data cannot be empty")

    try:
        cipher = _get_cipher()
        encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt Base64 encoded encrypted data.

    Args:
        encrypted_data (str): Base64 encoded encrypted data

    Returns:
        str: Decrypted plain text data

    Raises:
        ValueError: If encrypted_data is not a string or is empty
        Exception: If decryption fails
    """
    if not isinstance(encrypted_data, str):
        raise ValueError("Encrypted data must be a string")
    if not encrypted_data:
        raise ValueError("Encrypted data cannot be empty")

    try:
        cipher = _get_cipher()
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")


def generate_test_encryption_key() -> str:
    """
    Generate a Fernet key for development/testing purposes.

    Returns:
        str: Base64 encoded Fernet key

    Note:
        This function should only be used for development/testing.
        In production, use a securely generated key from environment variables.
    """
    return Fernet.generate_key().decode('utf-8')


def validate_encryption_key(key: str) -> bool:
    """
    Validate if the provided key can be used for Fernet encryption.

    Args:
        key (str): Base64 encoded key to validate

    Returns:
        bool: True if key is valid, False otherwise
    """
    try:
        Fernet(key.encode('utf-8'))
        return True
    except Exception:
        return False


def hash_sensitive_data(data: str) -> str:
    """
    Create a hash of sensitive data for comparison purposes.

    Args:
        data (str): Data to hash

    Returns:
        str: SHA-256 hash of the data
    """
    import hashlib
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_otp() -> str:
    """
    Generate a 6-digit OTP for testing purposes.

    Returns:
        str: 6-digit numeric OTP
    """
    import random
    return f"{random.randint(100000, 999999)}"


def verify_otp_format(otp: str) -> bool:
    """
    Verify if OTP format is valid (6 digits).

    Args:
        otp (str): OTP to verify

    Returns:
        bool: True if OTP format is valid, False otherwise
    """
    return len(otp) == 6 and otp.isdigit()