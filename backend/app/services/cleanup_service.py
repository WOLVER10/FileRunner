from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import FileRecord, FileGroup
from app.services.file_service import delete_file_from_disk


def mark_expired(db: Session | None = None) -> int:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        now = datetime.now(timezone.utc)
        count = 0

        expired_files = (
            db.query(FileRecord)
            .filter(FileRecord.status == "active", FileRecord.expires_at < now)
            .all()
        )
        for f in expired_files:
            f.status = "expired"
            count += 1

        expired_groups = (
            db.query(FileGroup)
            .filter(FileGroup.status == "active", FileGroup.expires_at < now)
            .all()
        )
        for g in expired_groups:
            g.status = "expired"
            count += 1

        db.commit()
        return count
    finally:
        if close_db:
            db.close()


def deep_clean(db: Session | None = None) -> int:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        now = datetime.now(timezone.utc)
        expired = (
            db.query(FileRecord)
            .filter(
                FileRecord.status == "expired",
                FileRecord.is_deep_cleaned == False,  # noqa: E712
            )
            .all()
        )
        count = 0
        for f in expired:
            delete_file_from_disk(f.stored_filename)
            f.status = "deleted"
            f.is_deep_cleaned = True
            count += 1
        db.commit()
        return count
    finally:
        if close_db:
            db.close()
