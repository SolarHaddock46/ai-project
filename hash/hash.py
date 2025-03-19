import hashlib

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return hashlib.sha256(password.encode()).hexdigest()