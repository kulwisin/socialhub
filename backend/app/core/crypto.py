"""Fernet symmetric encryption for sensitive fields (access tokens, etc.)."""
from __future__ import annotations

from cryptography.fernet import Fernet

from app.core.config import settings

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return _fernet


def encrypt(plaintext: str) -> str:
    """Encrypt a string. Returns a base64 ciphertext string."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string. Raises InvalidToken if tampered."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
