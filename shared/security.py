import hashlib

def hash_password(password: str) -> str:
    """Hashes a password string using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that plain_password hashes to hashed_password."""
    return hash_password(plain_password) == hashed_password

