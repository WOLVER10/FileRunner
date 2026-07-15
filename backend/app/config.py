import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def _resolve_password_hash() -> str:
    """Hash the plaintext ADMIN_PASSWORD on startup."""
    plaintext = os.getenv("ADMIN_PASSWORD", "")
    if plaintext:
        import bcrypt
        return bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
    return ""


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-string")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH: str = _resolve_password_hash()
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/data.db")
    UPLOAD_DIR: str = os.path.abspath(os.getenv("UPLOAD_DIR", "./uploads"))
    MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", "104857600"))


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
