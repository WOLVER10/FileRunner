import os
import io
import urllib.parse
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import FileRecord, FileGroup, DownloadLog, Setting
from app.schemas import FileInfoResponse, FileCleanedResponse, GroupInfoResponse, GroupFileItem

router = APIRouter()


def _content_disposition(filename: str) -> str:
    """Build Content-Disposition header with RFC 5987 encoding for non-ASCII filenames."""
    encoded = urllib.parse.quote(filename, safe='')
    return f"attachment; filename*=UTF-8''{encoded}"
limiter = Limiter(key_func=get_remote_address)


def _check_and_log(record, code: str, request: Request, db: Session, reason: str = ""):
    """Check file status and log download attempt."""
    log = DownloadLog(
        file_id=record.id,
        code=code,
        ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", ""),
        success=False,
        reason=reason,
    )
    db.add(log)
    db.commit()


def _mark_expired_if_needed(record, db: Session) -> bool:
    """Check if an active record has expired and mark it. Returns True if expired."""
    if record.status == "active" and record.expires_at:
        now = datetime.now(timezone.utc)
        expires = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
        if expires < now:
            record.status = "expired"
            db.commit()
            return True
    return False


def _mark_group_expired_if_needed(group, db: Session) -> bool:
    """Check if an active group has expired and mark it. Returns True if expired."""
    if group.status == "active" and group.expires_at:
        now = datetime.now(timezone.utc)
        expires = group.expires_at if group.expires_at.tzinfo else group.expires_at.replace(tzinfo=timezone.utc)
        if expires < now:
            group.status = "expired"
            db.commit()
            return True
    return False


def _try_deep_clean_on_access(record, db: Session):
    """If auto deep clean is enabled and delay has passed, physically delete the file."""
    setting = db.query(Setting).filter(Setting.key == "auto_deep_clean_enabled").first()
    if not setting or setting.value != "true":
        return
    if record.status != "expired" or record.is_deep_cleaned:
        return

    delay_setting = db.query(Setting).filter(Setting.key == "auto_deep_clean_delay_min").first()
    delay_min = int(delay_setting.value) if delay_setting else 0

    if record.expires_at:
        now = datetime.now(timezone.utc)
        from datetime import timedelta
        expires = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
        if now >= expires + timedelta(minutes=delay_min):
            from app.services.file_service import delete_file_from_disk
            delete_file_from_disk(record.stored_filename)
            record.status = "deleted"
            record.is_deep_cleaned = True
            db.commit()


@router.get("/file/{code}/info")
@limiter.limit("20/minute")
async def get_file_info(
    request: Request,
    code: str,
    db: Session = Depends(get_db),
):
    # Check if it's a group
    group = db.query(FileGroup).filter(FileGroup.code == code).first()
    if group:
        if _mark_group_expired_if_needed(group, db):
            return FileCleanedResponse(status="cleaned", message="文件已过期")
        if group.status in ("expired", "deleted"):
            return FileCleanedResponse(status="cleaned", message="文件已被清理")

        files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()
        return GroupInfoResponse(
            code=group.code,
            name=group.name,
            file_count=group.file_count,
            total_size=group.total_size,
            remaining_downloads=group.remaining_downloads,
            expires_at=group.expires_at.isoformat(),
            status=group.status,
            share_type=group.share_type or "multi",
            files=[
                GroupFileItem(
                    id=f.id,
                    filename=f.original_filename,
                    relative_path=f.relative_path or f.original_filename,
                    size=f.file_size,
                    mime_type=f.mime_type,
                )
                for f in files
            ],
        )

    # Single file
    record = db.query(FileRecord).filter(FileRecord.code == code).first()
    if not record:
        raise HTTPException(status_code=404, detail="取件码不存在")

    if _mark_expired_if_needed(record, db):
        return FileCleanedResponse(status="cleaned", message="文件已过期")

    _try_deep_clean_on_access(record, db)

    if record.status in ("expired", "deleted"):
        return FileCleanedResponse(status="cleaned", message="文件已被清理")

    return FileInfoResponse(
        code=record.code,
        filename=record.original_filename,
        size=record.file_size,
        remaining_downloads=record.remaining_downloads,
        expires_at=record.expires_at.isoformat(),
        status=record.status,
        is_group=False,
        file_count=1,
    )


@router.get("/file/{code}/download")
@limiter.limit("20/minute")
async def download_file(
    request: Request,
    code: str,
    file_id: int = Query(None),  # For group: download specific file
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    # Check if it's a group
    group = db.query(FileGroup).filter(FileGroup.code == code).first()
    if group:
        if group.status == "deleted":
            raise HTTPException(status_code=410, detail="文件已被清理，无法下载")
        if group.status == "expired":
            raise HTTPException(status_code=410, detail="文件已过期，无法下载")
        if group.remaining_downloads == 0:
            raise HTTPException(status_code=403, detail="下载次数已用完")

        # Mark expired on access
        if _mark_group_expired_if_needed(group, db):
            raise HTTPException(status_code=410, detail="文件已过期")

        # Decrement remaining downloads
        if group.remaining_downloads > 0:
            group.remaining_downloads -= 1

        files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()

        # Download specific file
        if file_id:
            target = next((f for f in files if f.id == file_id), None)
            if not target:
                raise HTTPException(status_code=404, detail="文件不存在")

            log = DownloadLog(
                file_id=target.id,
                code=code,
                ip=client_ip,
                user_agent=user_agent,
                success=True,
            )
            db.add(log)
            db.commit()

            from app.services.file_service import get_file_path
            file_path = get_file_path(target.stored_filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="文件不存在")

            def iter_file():
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):
                        yield chunk

            return StreamingResponse(
                iter_file(),
                media_type=target.mime_type,
                headers={
                    "Content-Disposition": _content_disposition(target.original_filename),
                    "X-Content-Type-Options": "nosniff",
                },
            )

        # Download all as ZIP
        from app.services.file_service import create_zip_from_files
        zip_buffer = create_zip_from_files(files)

        log = DownloadLog(
            file_id=files[0].id,
            code=code,
            ip=client_ip,
            user_agent=user_agent,
            success=True,
        )
        db.add(log)
        db.commit()

        def iter_zip():
            while chunk := zip_buffer.read(8192):
                yield chunk

        zip_buffer.seek(0)
        return StreamingResponse(
            iter_zip(),
            media_type="application/zip",
            headers={
                "Content-Disposition": _content_disposition(f"{group.name}.zip"),
                "X-Content-Type-Options": "nosniff",
            },
        )

    # Single file download
    record = db.query(FileRecord).filter(FileRecord.code == code).first()
    if not record:
        raise HTTPException(status_code=404, detail="取件码不存在")

    if record.status == "deleted":
        _check_and_log(record, code, request, db, "文件已被清理")
        raise HTTPException(status_code=410, detail="文件已被清理，无法下载")

    if _mark_expired_if_needed(record, db):
        _check_and_log(record, code, request, db, "文件已过期")
        raise HTTPException(status_code=410, detail="文件已过期，无法下载")

    _try_deep_clean_on_access(record, db)

    if record.status in ("deleted", "expired"):
        _check_and_log(record, code, request, db, "文件已被清理")
        raise HTTPException(status_code=410, detail="文件已被清理，无法下载")

    if record.remaining_downloads == 0:
        _check_and_log(record, code, request, db, "下载次数已用完")
        raise HTTPException(status_code=403, detail="下载次数已用完")

    if record.remaining_downloads > 0:
        record.remaining_downloads -= 1

    log = DownloadLog(
        file_id=record.id,
        code=code,
        ip=client_ip,
        user_agent=user_agent,
        success=True,
    )
    db.add(log)
    db.commit()

    from app.services.file_service import get_file_path
    file_path = get_file_path(record.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    def iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type=record.mime_type,
        headers={
            "Content-Disposition": _content_disposition(record.original_filename),
            "X-Content-Type-Options": "nosniff",
        },
    )
