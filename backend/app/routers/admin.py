from datetime import datetime, timedelta, timezone
import json
import os

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy import func
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.config import get_settings
from app.auth import verify_password, create_access_token, get_current_admin
from app.database import get_db
from app.models import FileRecord, DownloadLog, Setting
from app.schemas import AdminLoginRequest, AdminLoginResponse, AdminStatsResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_login_attempts: dict[str, list[float]] = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes


@router.post("/login", response_model=AdminLoginResponse)
@limiter.limit("10/minute")
async def admin_login(
    request: Request,
    body: AdminLoginRequest,
):
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"

    now = __import__("time").time()
    if client_ip in _login_attempts:
        attempts = _login_attempts[client_ip]
        attempts = [t for t in attempts if now - t < LOCKOUT_SECONDS]
        _login_attempts[client_ip] = attempts
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail=f"登录失败次数过多，请在 {_lockout_remaining(attempts)} 秒后重试",
            )

    if body.username != settings.ADMIN_USERNAME:
        _record_attempt(client_ip)
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not settings.ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="管理员密码未配置")

    if not verify_password(body.password, settings.ADMIN_PASSWORD_HASH):
        _record_attempt(client_ip)
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    _login_attempts.pop(client_ip, None)

    token = create_access_token({"sub": body.username})
    return AdminLoginResponse(access_token=token, token_type="bearer")


@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    total_files = db.query(FileRecord).count()

    total_upload = db.query(func.coalesce(func.sum(FileRecord.file_size), 0)).scalar()
    # 下载流量：每次成功下载算一次文件大小（近似值）
    total_download = (
        db.query(func.coalesce(func.sum(FileRecord.file_size), 0))
        .join(DownloadLog, DownloadLog.file_id == FileRecord.id)
        .filter(DownloadLog.success == True)  # noqa: E712
        .scalar()
    )
    total_transfer_bytes = int(total_upload) + int(total_download)

    active_shares = db.query(FileRecord).filter(FileRecord.status == "active").count()

    return AdminStatsResponse(
        total_files=total_files,
        total_transfer_bytes=total_transfer_bytes,
        active_shares=active_shares,
    )


def _record_attempt(ip: str):
    import time
    _login_attempts.setdefault(ip, []).append(time.time())


def _lockout_remaining(attempts: list[float]) -> int:
    import time
    now = time.time()
    if not attempts:
        return 0
    oldest_in_window = min(t for t in attempts if now - t < LOCKOUT_SECONDS)
    return int(LOCKOUT_SECONDS - (now - oldest_in_window))


@router.get("/banner")
async def get_banner(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    def get_val(key: str, default=""):
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else default

    stored = get_val("banner_stored_filename", "")
    return {
        "banner_image_url": get_val("banner_image_url", ""),
        "banner_stored_filename": stored,
        "banner_valid_from": get_val("banner_valid_from", ""),
        "banner_valid_until": get_val("banner_valid_until", ""),
    }


@router.post("/banner")
async def upload_banner(
    file: UploadFile = File(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="图片大小不能超过 5MB")

    from app.services.file_service import save_banner_image, delete_banner_image

    def get_val(key: str, default=""):
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else default

    old_stored = get_val("banner_stored_filename", "")
    if old_stored:
        delete_banner_image(old_stored)

    stored_name = save_banner_image(content, file.filename or "banner.jpg")

    def set_val(key: str, value: str):
        s = db.query(Setting).filter(Setting.key == key).first()
        if s:
            s.value = value
        else:
            db.add(Setting(key=key, value=value))

    set_val("banner_stored_filename", stored_name)
    set_val("banner_image_url", f"/api/admin/banner/image/{stored_name}")
    set_val("banner_valid_from", valid_from)
    set_val("banner_valid_until", valid_until)
    db.commit()

    return {
        "message": "Banner uploaded successfully",
        "banner_image_url": f"/api/admin/banner/image/{stored_name}",
        "banner_stored_filename": stored_name,
        "banner_valid_from": valid_from,
        "banner_valid_until": valid_until,
    }


@router.delete("/banner")
async def delete_banner(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.services.file_service import delete_banner_image

    def get_val(key: str, default=""):
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else default

    stored = get_val("banner_stored_filename", "")
    if stored:
        delete_banner_image(stored)

    def set_val(key: str, value: str):
        s = db.query(Setting).filter(Setting.key == key).first()
        if s:
            s.value = value
        else:
            db.add(Setting(key=key, value=value))

    set_val("banner_stored_filename", "")
    set_val("banner_image_url", "")
    set_val("banner_valid_from", "")
    set_val("banner_valid_until", "")
    db.commit()

    return {"message": "Banner deleted"}


@router.get("/banner/image/{filename}")
async def serve_banner_image(filename: str):
    """Serve banner image file."""
    from app.services.file_service import get_banner_path
    file_path = get_banner_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@router.get("/showcases")
async def list_showcases(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.models import ShowcaseTask
    tasks = db.query(ShowcaseTask).order_by(ShowcaseTask.sort_order, ShowcaseTask.id).all()
    now = datetime.now(timezone.utc)
    return {
        "tasks": [
            {
                "id": t.id,
                "name": t.name,
                "image_url": t.image_url,
                "stored_filename": t.stored_filename,
                "valid_from": t.valid_from.isoformat() if t.valid_from else None,
                "valid_until": t.valid_until.isoformat() if t.valid_until else None,
                "sort_order": t.sort_order,
                "is_active": _is_showcase_active(t, now),
            }
            for t in tasks
        ]
    }


def _is_showcase_active(task, now):
    if task.valid_from:
        vf = task.valid_from if task.valid_from.tzinfo else task.valid_from.replace(tzinfo=timezone.utc)
        if vf > now:
            return False
    if task.valid_until:
        vu = task.valid_until if task.valid_until.tzinfo else task.valid_until.replace(tzinfo=timezone.utc)
        if vu < now:
            return False
    return True


@router.post("/showcases")
async def create_showcase(
    file: UploadFile = File(...),
    name: str = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.models import ShowcaseTask
    from app.services.file_service import save_banner_image

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="图片大小不能超过 5MB")

    stored_name = save_banner_image(content, file.filename or "showcase.jpg")

    vf = _parse_datetime(valid_from) if valid_from else None
    vu = _parse_datetime(valid_until) if valid_until else None

    max_order = db.query(func.coalesce(func.max(ShowcaseTask.sort_order), 0)).scalar()

    task = ShowcaseTask(
        name=name,
        image_url=f"/api/admin/showcases/image/{stored_name}",
        stored_filename=stored_name,
        valid_from=vf,
        valid_until=vu,
        sort_order=max_order + 1,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "name": task.name,
        "image_url": task.image_url,
        "stored_filename": task.stored_filename,
        "valid_from": task.valid_from.isoformat() if task.valid_from else None,
        "valid_until": task.valid_until.isoformat() if task.valid_until else None,
        "sort_order": task.sort_order,
        "is_active": _is_showcase_active(task, datetime.now(timezone.utc)),
    }


@router.put("/showcases/{task_id}")
async def update_showcase(
    task_id: int,
    name: str = Form(None),
    valid_from: str = Form(None),
    valid_until: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.models import ShowcaseTask
    from app.services.file_service import save_banner_image, delete_banner_image

    task = db.query(ShowcaseTask).filter(ShowcaseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if name is not None:
        task.name = name
    if valid_from is not None:
        task.valid_from = _parse_datetime(valid_from) if valid_from else None
    if valid_until is not None:
        task.valid_until = _parse_datetime(valid_until) if valid_until else None

    # Replace image if new file provided
    if file:
        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="图片大小不能超过 5MB")

        delete_banner_image(task.stored_filename)

        stored_name = save_banner_image(content, file.filename or "showcase.jpg")
        task.stored_filename = stored_name
        task.image_url = f"/api/admin/showcases/image/{stored_name}"

    db.commit()
    return {"message": "更新成功"}


@router.delete("/showcases/{task_id}")
async def delete_showcase(
    task_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.models import ShowcaseTask
    from app.services.file_service import delete_banner_image

    task = db.query(ShowcaseTask).filter(ShowcaseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    delete_banner_image(task.stored_filename)

    db.delete(task)
    db.commit()
    return {"message": "删除成功"}


@router.post("/showcases/{task_id}/sort")
async def update_showcase_sort(
    task_id: int,
    direction: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    from app.models import ShowcaseTask

    task = db.query(ShowcaseTask).filter(ShowcaseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if direction == -1:
        neighbor = (
            db.query(ShowcaseTask)
            .filter(ShowcaseTask.sort_order < task.sort_order)
            .order_by(ShowcaseTask.sort_order.desc())
            .first()
        )
    else:
        neighbor = (
            db.query(ShowcaseTask)
            .filter(ShowcaseTask.sort_order > task.sort_order)
            .order_by(ShowcaseTask.sort_order.asc())
            .first()
        )

    if neighbor:
        task.sort_order, neighbor.sort_order = neighbor.sort_order, task.sort_order
        db.commit()

    return {"message": "排序已更新"}


@router.get("/showcases/image/{filename}")
async def serve_showcase_image(filename: str):
    """Serve showcase image file."""
    from app.services.file_service import get_banner_path
    file_path = get_banner_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


def _parse_datetime(s: str):
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None
