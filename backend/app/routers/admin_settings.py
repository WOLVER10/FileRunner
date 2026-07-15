import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import Setting
from app.schemas import AdminSettingsRequest, AdminSettingsResponse

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/settings", response_model=AdminSettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    def get_val(key: str, default=""):
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else default

    def get_json(key: str, default=None):
        val = get_val(key, "")
        if not val:
            return default if default is not None else []
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return default if default is not None else []

    return AdminSettingsResponse(
        upload_control_mode=get_val("upload_control_mode", "whitelist") or "whitelist",
        allowed_extensions=get_json("allowed_extensions", []),
        blocked_extensions=get_json("blocked_extensions", []),
        max_upload_size_bytes=int(get_val("max_upload_size_bytes", "1073741824") or "1073741824"),
        max_files_per_task=int(get_val("max_files_per_task", "100") or "100"),
        max_task_size_bytes=int(get_val("max_task_size_bytes", "5368709120") or "5368709120"),
        expiry_options=get_json("expiry_options", []),
        download_limit_options=get_json("download_limit_options", []),
        cleanup_scan_interval_min=int(get_val("cleanup_scan_interval_min", "10") or "10"),
        auto_deep_clean_enabled=get_val("auto_deep_clean_enabled", "false") == "true",
        auto_deep_clean_delay_min=int(get_val("auto_deep_clean_delay_min", "0") or "0"),
        expiry_default_index=int(get_val("expiry_default_index", "0") or "0"),
        dl_default_index=int(get_val("dl_default_index", "0") or "0"),
        banner_image_url=get_val("banner_image_url", "") or "",
        banner_valid_from=get_val("banner_valid_from", "") or "",
        banner_valid_until=get_val("banner_valid_until", "") or "",
    )


@router.put("/settings", response_model=AdminSettingsResponse)
async def update_settings(
    body: AdminSettingsRequest,
    db: Session = Depends(get_db),
):
    try:
        def set_val(key: str, value: str):
            s = db.query(Setting).filter(Setting.key == key).first()
            if s:
                s.value = value
            else:
                db.add(Setting(key=key, value=str(value)))

        set_val("upload_control_mode", body.upload_control_mode or "whitelist")
        set_val("allowed_extensions", json.dumps(body.allowed_extensions or []))
        set_val("blocked_extensions", json.dumps(body.blocked_extensions or []))
        set_val("max_upload_size_bytes", str(body.max_upload_size_bytes or 1073741824))
        set_val("max_files_per_task", str(body.max_files_per_task or 100))
        set_val("max_task_size_bytes", str(body.max_task_size_bytes or 5368709120))
        expiry_opts = [{"value": o.value, "label": o.label or ""} for o in (body.expiry_options or [])]
        dl_opts = [{"value": o.value, "label": o.label or ""} for o in (body.download_limit_options or [])]
        set_val("expiry_options", json.dumps(expiry_opts))
        set_val("download_limit_options", json.dumps(dl_opts))
        set_val("cleanup_scan_interval_min", str(body.cleanup_scan_interval_min or 10))
        set_val("auto_deep_clean_enabled", "true" if body.auto_deep_clean_enabled else "false")
        set_val("auto_deep_clean_delay_min", str(body.auto_deep_clean_delay_min or 0))
        set_val("expiry_default_index", str(body.expiry_default_index or 0))
        set_val("dl_default_index", str(body.dl_default_index or 0))
        set_val("banner_image_url", body.banner_image_url or "")
        set_val("banner_valid_from", body.banner_valid_from or "")
        set_val("banner_valid_until", body.banner_valid_until or "")

        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception("Failed to save settings")
        raise

    # Restart scheduler with new interval
    try:
        from app.tasks import scheduler
        if scheduler.get_job("cleanup_job"):
            scheduler.reschedule_job(
                "cleanup_job",
                trigger="interval",
                minutes=body.cleanup_scan_interval_min or 10,
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Failed to reschedule cleanup job: %s", e)

    return await get_settings(db)
