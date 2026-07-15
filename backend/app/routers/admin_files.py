from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import FileRecord, FileGroup, DownloadLog
from app.schemas import (
    AdminFileListResponse,
    AdminFileItem,
    AdminFileDetailResponse,
    BatchDeepCleanRequest,
    MessageResponse,
)
from app.services.file_service import delete_file_from_disk

router = APIRouter(dependencies=[Depends(get_current_admin)])


class BatchExpireRequest(BaseModel):
    codes: list[str]


@router.get("/files", response_model=AdminFileListResponse)
async def list_files(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    search: str | None = None,
    share_type: str | None = None,
    db: Session = Depends(get_db),
):
    # Collect all unique share tasks (single files + groups)
    tasks = []

    single_query = db.query(FileRecord).filter(FileRecord.group_id.is_(None))
    if status:
        single_query = single_query.filter(FileRecord.status == status)
    if search:
        single_query = single_query.filter(
            FileRecord.code.contains(search) | FileRecord.original_filename.contains(search)
        )
    if share_type and "single" not in [t.strip() for t in share_type.split(",")]:
        single_query = single_query.filter(FileRecord.id < 0)  # empty result

    for f in single_query.all():
        tasks.append({
            "type": "single",
            "id": f.id,
            "code": f.code,
            "name": f.original_filename,
            "file_size": f.file_size,
            "upload_time": f.upload_time,
            "expires_at": f.expires_at,
            "status": f.status,
            "remaining_downloads": f.remaining_downloads,
            "is_deep_cleaned": f.is_deep_cleaned,
            "share_type": "single",
        })

    group_query = db.query(FileGroup)
    if status:
        group_query = group_query.filter(FileGroup.status == status)
    if search:
        group_query = group_query.filter(
            FileGroup.code.contains(search) | FileGroup.name.contains(search)
        )
    if share_type:
        share_types = [t.strip() for t in share_type.split(",") if t.strip() and t.strip() != "single"]
        if share_types:
            group_query = group_query.filter(FileGroup.share_type.in_(share_types))
        else:
            group_query = group_query.filter(FileGroup.id < 0)  # empty result

    for g in group_query.all():
        tasks.append({
            "type": "group",
            "id": g.id,
            "code": g.code,
            "name": g.name,
            "file_size": g.total_size,
            "upload_time": g.upload_time,
            "expires_at": g.expires_at,
            "status": g.status,
            "remaining_downloads": g.remaining_downloads,
            "is_deep_cleaned": g.is_deep_cleaned,
            "share_type": g.share_type or "multi",
        })

    tasks.sort(key=lambda t: t["upload_time"] or "", reverse=True)
    total = len(tasks)

    tasks = tasks[(page - 1) * page_size : page * page_size]

    items = [
        AdminFileItem(
            id=t["id"],
            code=t["code"],
            original_filename=t["name"],
            file_size=t["file_size"],
            upload_time=t["upload_time"].isoformat() if t["upload_time"] else "",
            expires_at=t["expires_at"].isoformat() if t["expires_at"] else "",
            status=t["status"],
            remaining_downloads=t["remaining_downloads"],
            is_deep_cleaned=t["is_deep_cleaned"],
            share_type=t["share_type"],
        )
        for t in tasks
    ]

    return AdminFileListResponse(
        files=items, total=total, page=page, page_size=page_size
    )


@router.get("/files/{file_id}", response_model=AdminFileDetailResponse)
async def get_file_detail(
    file_id: int,
    db: Session = Depends(get_db),
):
    group = db.query(FileGroup).filter(FileGroup.id == file_id).first()
    if group:
        group_files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()
        first_file = group_files[0] if group_files else None

        file_ids = [f.id for f in group_files]
        logs = (
            db.query(DownloadLog)
            .filter(DownloadLog.file_id.in_(file_ids))
            .order_by(DownloadLog.download_time.desc())
            .limit(50)
            .all()
        )

        recent_downloads = [
            {
                "download_time": l.download_time.isoformat() if l.download_time else "",
                "ip": l.ip,
                "user_agent": l.user_agent,
                "success": l.success,
                "reason": l.reason,
            }
            for l in logs
        ]

        files = [
            {
                "id": f.id,
                "filename": f.original_filename,
                "relative_path": f.relative_path or f.original_filename,
                "size": f.file_size,
                "mime_type": f.mime_type,
                "status": f.status,
            }
            for f in group_files
        ]

        return AdminFileDetailResponse(
            id=group.id,
            code=group.code,
            original_filename=first_file.original_filename if first_file else "",
            file_size=first_file.file_size if first_file else 0,
            upload_time=group.upload_time.isoformat() if group.upload_time else "",
            expires_at=group.expires_at.isoformat() if group.expires_at else "",
            status=group.status,
            remaining_downloads=group.remaining_downloads,
            is_deep_cleaned=group.is_deep_cleaned,
            stored_filename=first_file.stored_filename if first_file else "",
            mime_type=first_file.mime_type if first_file else "",
            upload_ip=group.upload_ip or "",
            download_limit=group.download_limit,
            recent_downloads=recent_downloads,
            is_group=True,
            share_type=group.share_type or "multi",
            group_name=group.name or "",
            group_total_size=group.total_size or 0,
            file_count=group.file_count or 0,
            files=files,
        )

    record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")

    logs = (
        db.query(DownloadLog)
        .filter(DownloadLog.file_id == file_id)
        .order_by(DownloadLog.download_time.desc())
        .limit(50)
        .all()
    )

    recent_downloads = [
        {
            "download_time": l.download_time.isoformat() if l.download_time else "",
            "ip": l.ip,
            "user_agent": l.user_agent,
            "success": l.success,
            "reason": l.reason,
        }
        for l in logs
    ]

    is_group = False
    share_type = "single"
    group_name = ""
    group_total_size = 0
    group_file_count = 0
    files = []

    if record.group_id:
        group = db.query(FileGroup).filter(FileGroup.id == record.group_id).first()
        if group:
            is_group = True
            share_type = group.share_type or "multi"
            group_name = group.name or ""
            group_total_size = group.total_size or 0
            group_file_count = group.file_count or 0
            group_files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()
            files = [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "relative_path": f.relative_path or f.original_filename,
                    "size": f.file_size,
                    "mime_type": f.mime_type,
                    "status": f.status,
                }
                for f in group_files
            ]

    return AdminFileDetailResponse(
        id=record.id,
        code=record.code,
        original_filename=record.original_filename,
        file_size=record.file_size,
        upload_time=record.upload_time.isoformat() if record.upload_time else "",
        expires_at=record.expires_at.isoformat() if record.expires_at else "",
        status=record.status,
        remaining_downloads=record.remaining_downloads,
        is_deep_cleaned=record.is_deep_cleaned,
        stored_filename=record.stored_filename,
        mime_type=record.mime_type,
        upload_ip=record.upload_ip,
        download_limit=record.download_limit,
        recent_downloads=recent_downloads,
        is_group=is_group,
        share_type=share_type,
        group_name=group_name,
        group_total_size=group_total_size,
        group_file_count=group_file_count,
        files=files,
    )


@router.delete("/files/{file_id}/deep-clean", response_model=MessageResponse)
async def deep_clean_file(
    file_id: int,
    db: Session = Depends(get_db),
):
    record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")

    if record.status != "expired":
        raise HTTPException(status_code=400, detail="只能深度清理已过期的文件")

    if record.is_deep_cleaned:
        raise HTTPException(status_code=400, detail="文件已被深度清理")

    delete_file_from_disk(record.stored_filename)
    record.status = "deleted"
    record.is_deep_cleaned = True
    db.commit()

    return MessageResponse(message="文件已深度清理")


@router.post("/files/batch-deep-clean", response_model=MessageResponse)
async def batch_deep_clean(
    body: BatchDeepCleanRequest,
    db: Session = Depends(get_db),
):
    cleaned = 0
    errors = []

    for file_id in body.ids:
        record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not record:
            errors.append(f"文件 {file_id} 不存在")
            continue
        if record.status != "expired":
            errors.append(f"文件 {file_id} 状态不是已过期")
            continue
        if record.is_deep_cleaned:
            errors.append(f"文件 {file_id} 已被深度清理")
            continue

        delete_file_from_disk(record.stored_filename)
        record.status = "deleted"
        record.is_deep_cleaned = True
        cleaned += 1

    db.commit()

    msg = f"成功深度清理 {cleaned} 个文件"
    if errors:
        msg += f"，{len(errors)} 个文件跳过"
    return MessageResponse(message=msg)


# --- Expire endpoints ---

@router.post("/files/{code}/expire", response_model=MessageResponse)
async def expire_share(
    code: str,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    group = db.query(FileGroup).filter(FileGroup.code == code).first()
    if group:
        if group.status != "active":
            return MessageResponse(message="该分享已不是生效状态")
        group.status = "expired"
        files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()
        for f in files:
            if f.status == "active":
                f.status = "expired"
        db.commit()
        return MessageResponse(message="分享已失效")

    # Single file
    record = db.query(FileRecord).filter(FileRecord.code == code).first()
    if not record:
        raise HTTPException(status_code=404, detail="分享不存在")
    if record.status != "active":
        return MessageResponse(message="该分享已不是生效状态")
    record.status = "expired"
    db.commit()
    return MessageResponse(message="分享已失效")


@router.post("/files/batch-expire", response_model=MessageResponse)
async def batch_expire(
    body: BatchExpireRequest,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    expired = 0
    for code in body.codes:
        group = db.query(FileGroup).filter(FileGroup.code == code).first()
        if group:
            if group.status == "active":
                group.status = "expired"
                files = db.query(FileRecord).filter(FileRecord.group_id == group.id).all()
                for f in files:
                    if f.status == "active":
                        f.status = "expired"
                expired += 1
        else:
            record = db.query(FileRecord).filter(FileRecord.code == code).first()
            if record and record.status == "active":
                record.status = "expired"
                expired += 1
    db.commit()
    return MessageResponse(message=f"已失效 {expired} 个分享")
