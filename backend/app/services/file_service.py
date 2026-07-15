import io
import os
import random
import uuid
import zipfile

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import FileRecord


def generate_code(db: Session) -> str:
    for _ in range(100):
        code = str(random.randint(100000, 999999))
        existing = db.query(FileRecord).filter(FileRecord.code == code).first()
        if not existing:
            return code
    raise RuntimeError("Failed to generate unique code after 100 attempts")


def save_upload_file(file_content: bytes, original_filename: str) -> str:
    settings = get_settings()
    ext = os.path.splitext(original_filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    return stored_name


def get_file_path(stored_filename: str) -> str:
    settings = get_settings()
    return os.path.join(settings.UPLOAD_DIR, stored_filename)


def delete_file_from_disk(stored_filename: str) -> bool:
    file_path = get_file_path(stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def get_banner_dir() -> str:
    settings = get_settings()
    banner_dir = os.path.join(settings.UPLOAD_DIR, "banner")
    os.makedirs(banner_dir, exist_ok=True)
    return banner_dir


def save_banner_image(file_content: bytes, original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1].lower() or ".jpg"
    stored_name = f"{uuid.uuid4().hex[:12]}{ext}"
    file_path = os.path.join(get_banner_dir(), stored_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    return stored_name


def get_banner_path(stored_filename: str) -> str:
    return os.path.join(get_banner_dir(), stored_filename)


def delete_banner_image(stored_filename: str) -> bool:
    file_path = get_banner_path(stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def create_zip_from_files(file_records: list[FileRecord]) -> io.BytesIO:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for record in file_records:
            file_path = get_file_path(record.stored_filename)
            if os.path.exists(file_path):
                arcname = record.relative_path or record.original_filename
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer
