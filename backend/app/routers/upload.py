import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import get_db
from app.models import FileRecord, FileGroup, Setting
from app.schemas import UploadResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


import logging

logger = logging.getLogger(__name__)

@router.post("/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    files: list[UploadFile] = File(...),
    expiry: int = Form(...),
    download_limit: int = Form(...),
    relative_paths: str = Form("[]"),  # JSON array of relative paths for each file
    db: Session = Depends(get_db),
):
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Upload request: {len(files)} files, expiry={expiry}, download_limit={download_limit}")
    for i, f in enumerate(files):
        logger.info(f"  File {i}: name={f.filename}, content_type={f.content_type}")

    # Parse relative paths
    try:
        paths = json.loads(relative_paths)
    except json.JSONDecodeError:
        paths = []

    # Validate expiry option
    expiry_setting = db.query(Setting).filter(Setting.key == "expiry_options").first()
    expiry_options = json.loads(expiry_setting.value) if expiry_setting else []
    valid_expiry_values = [opt["value"] for opt in expiry_options]
    if valid_expiry_values and expiry not in valid_expiry_values:
        raise HTTPException(status_code=400, detail="无效的有效期选项")

    # Validate download_limit option
    dl_setting = db.query(Setting).filter(Setting.key == "download_limit_options").first()
    dl_options = json.loads(dl_setting.value) if dl_setting else []
    valid_dl_values = [opt["value"] for opt in dl_options]
    if valid_dl_values and download_limit not in valid_dl_values:
        raise HTTPException(status_code=400, detail="无效的下载次数选项")

    # Get validation settings
    max_size_setting = db.query(Setting).filter(Setting.key == "max_upload_size_bytes").first()
    max_size = int(max_size_setting.value) if max_size_setting else settings.MAX_UPLOAD_SIZE_BYTES

    max_files_setting = db.query(Setting).filter(Setting.key == "max_files_per_task").first()
    max_files = int(max_files_setting.value) if max_files_setting else 100

    max_task_size_setting = db.query(Setting).filter(Setting.key == "max_task_size_bytes").first()
    max_task_size = int(max_task_size_setting.value) if max_task_size_setting else 5368709120

    control_mode_setting = db.query(Setting).filter(Setting.key == "upload_control_mode").first()
    control_mode = control_mode_setting.value if control_mode_setting else "whitelist"

    allowed_setting = db.query(Setting).filter(Setting.key == "allowed_extensions").first()
    allowed_extensions = json.loads(allowed_setting.value) if allowed_setting else []

    blocked_setting = db.query(Setting).filter(Setting.key == "blocked_extensions").first()
    blocked_extensions = json.loads(blocked_setting.value) if blocked_setting else []

    # Validate file count
    if len(files) > max_files:
        raise HTTPException(status_code=400, detail=f"单次最多上传 {max_files} 个文件")

    # Validate and save all files
    saved_files = []
    total_size = 0

    for i, file in enumerate(files):
        content = await file.read()
        file_size = len(content)
        total_size += file_size

        # Validate file size
        if file_size > max_size:
            raise HTTPException(status_code=413, detail=f"文件 {file.filename} 大小超过限制（最大 {max_size} 字节）")

        # Validate total task size
        if total_size > max_task_size:
            raise HTTPException(status_code=413, detail=f"单次分享任务总大小超过限制（最大 {max_task_size} 字节）")

        # Validate file extension based on control mode
        ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
        logger.info(f"File {i}: {file.filename}, ext=.{ext}, size={file_size}")
        if control_mode == "whitelist":
            if allowed_extensions and ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"不允许的文件类型: .{ext}")
        elif control_mode == "blacklist":
            if ext in blocked_extensions:
                raise HTTPException(status_code=400, detail=f"禁止上传的文件类型: .{ext}")
        # "none" mode: no extension validation

        # Get relative path
        relative_path = paths[i] if i < len(paths) else file.filename or "unknown"

        # Save file
        from app.services.file_service import save_upload_file
        stored_filename = save_upload_file(content, file.filename or "unknown")

        saved_files.append({
            "original_filename": file.filename or "unknown",
            "stored_filename": stored_filename,
            "file_size": file_size,
            "mime_type": file.content_type or "application/octet-stream",
            "relative_path": relative_path,
        })

    from app.services.file_service import generate_code

    code = generate_code(db)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expiry)
    remaining = download_limit  # -1 for unlimited
    is_group = len(saved_files) > 1

    # Calculate share_type
    if not is_group:
        share_type = "single"
    else:
        top_level_dirs = set()
        has_top_level_file = False
        for sf in saved_files:
            parts = sf["relative_path"].split("/")
            if len(parts) == 1:
                has_top_level_file = True
            else:
                top_level_dirs.add(parts[0])
        if len(top_level_dirs) == 1 and not has_top_level_file:
            share_type = "folder"
        else:
            share_type = "multi"

    if is_group:
        # Create group
        group_name = saved_files[0]["relative_path"].split("/")[0] if "/" in saved_files[0]["relative_path"] else "多文件上传"
        logger.info(f"Creating group: name={group_name}, files={len(saved_files)}, total_size={total_size}, share_type={share_type}")
        for sf in saved_files:
            logger.info(f"  File: {sf['original_filename']}, path={sf['relative_path']}, size={sf['file_size']}")
        group = FileGroup(
            code=code,
            name=group_name,
            upload_ip=client_ip,
            expires_at=expires_at,
            status="active",
            download_limit=download_limit,
            remaining_downloads=remaining,
            file_count=len(saved_files),
            total_size=total_size,
            share_type=share_type,
        )
        db.add(group)
        db.flush()  # Get group.id

        # Create file records linked to group
        for sf in saved_files:
            record = FileRecord(
                code=code,
                original_filename=sf["original_filename"],
                stored_filename=sf["stored_filename"],
                file_size=sf["file_size"],
                mime_type=sf["mime_type"],
                upload_ip=client_ip,
                expires_at=expires_at,
                status="active",
                download_limit=download_limit,
                remaining_downloads=remaining,
                group_id=group.id,
                relative_path=sf["relative_path"],
            )
            db.add(record)
            logger.info(f"  Created FileRecord: {sf['original_filename']}, group_id={group.id}, relative_path={sf['relative_path']}")
    else:
        # Single file - use existing structure
        sf = saved_files[0]
        record = FileRecord(
            code=code,
            original_filename=sf["original_filename"],
            stored_filename=sf["stored_filename"],
            file_size=sf["file_size"],
            mime_type=sf["mime_type"],
            upload_ip=client_ip,
            expires_at=expires_at,
            status="active",
            download_limit=download_limit,
            remaining_downloads=remaining,
        )
        db.add(record)

    logger.info(f"Committing: is_group={is_group}, code={code}, saved_files={len(saved_files)}")
    db.commit()
    logger.info(f"Committed successfully")

    return UploadResponse(
        code=code,
        url=f"/get/{code}",
        is_group=is_group,
        file_count=len(saved_files),
    )


@router.get("/options")
async def get_options(db: Session = Depends(get_db)):
    settings = get_settings()

    expiry_setting = db.query(Setting).filter(Setting.key == "expiry_options").first()
    expiry_options = json.loads(expiry_setting.value) if expiry_setting else []

    dl_setting = db.query(Setting).filter(Setting.key == "download_limit_options").first()
    dl_options = json.loads(dl_setting.value) if dl_setting else []

    max_size_setting = db.query(Setting).filter(Setting.key == "max_upload_size_bytes").first()
    max_size = int(max_size_setting.value) if max_size_setting else settings.MAX_UPLOAD_SIZE_BYTES

    max_files_setting = db.query(Setting).filter(Setting.key == "max_files_per_task").first()
    max_files = int(max_files_setting.value) if max_files_setting else 100

    max_task_size_setting = db.query(Setting).filter(Setting.key == "max_task_size_bytes").first()
    max_task_size = int(max_task_size_setting.value) if max_task_size_setting else 5368709120

    allowed_setting = db.query(Setting).filter(Setting.key == "allowed_extensions").first()
    allowed = json.loads(allowed_setting.value) if allowed_setting else []

    control_mode_setting = db.query(Setting).filter(Setting.key == "upload_control_mode").first()
    control_mode = control_mode_setting.value if control_mode_setting else "whitelist"

    blocked_setting = db.query(Setting).filter(Setting.key == "blocked_extensions").first()
    blocked = json.loads(blocked_setting.value) if blocked_setting else []

    def get_val(key: str, default=""):
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else default

    # Get active showcase tasks
    from app.models import ShowcaseTask
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    showcases = db.query(ShowcaseTask).order_by(ShowcaseTask.sort_order, ShowcaseTask.id).all()
    active_showcases = []
    for s in showcases:
        is_active = True
        if s.valid_from:
            vf = s.valid_from if s.valid_from.tzinfo else s.valid_from.replace(tzinfo=timezone.utc)
            if vf > now:
                is_active = False
        if s.valid_until:
            vu = s.valid_until if s.valid_until.tzinfo else s.valid_until.replace(tzinfo=timezone.utc)
            if vu < now:
                is_active = False
        if is_active:
            active_showcases.append({
                "id": s.id,
                "name": s.name,
                "image_url": s.image_url,
            })

    return {
        "expiry_options": expiry_options,
        "download_limit_options": dl_options,
        "max_size_bytes": max_size,
        "max_files_per_task": max_files,
        "max_task_size_bytes": max_task_size,
        "allowed_extensions": allowed,
        "control_mode": control_mode,
        "blocked_extensions": blocked,
        "expiry_default_index": int(get_val("expiry_default_index", "0") or "0"),
        "dl_default_index": int(get_val("dl_default_index", "0") or "0"),
        "banner_image_url": get_val("banner_image_url", ""),
        "banner_valid_from": get_val("banner_valid_from", ""),
        "banner_valid_until": get_val("banner_valid_until", ""),
        "showcases": active_showcases,
    }
