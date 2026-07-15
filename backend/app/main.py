import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import create_tables, SessionLocal
from app.models import Setting
from app.routers import upload, pickup, admin, admin_files, admin_logs, admin_settings

settings = get_settings()

DEFAULT_SETTINGS = {
    "upload_control_mode": "whitelist",
    "allowed_extensions": json.dumps(["jpg", "jpeg", "png", "gif", "webp", "bmp", "ai", "psd", "psb", "svg", "pdf", "txt", "md", "csv", "zip", "rar", "7z", "tar", "gz", "doc", "xlsm", "ppt", "docx", "xlsx", "pptx", "ofd", "wps", "aac", "mp3", "flac", "ape", "wav", "mp4", "mov", "mkv", "m2ts"]),
    "blocked_extensions": json.dumps(["exe", "msi", "bat", "cmd", "sh", "ps1", "vbs", "com", "scr", "pif", "php", "asp", "jsp", "dll", "sys", "drv", "ocx", "cpl", "docm", "xlsm", "pptm"]),
    "max_upload_size_bytes": "1073741824",
    "max_files_per_task": "100",
    "max_task_size_bytes": "5368709120",
    "expiry_options": json.dumps([
        {"value": 3600, "label": "1小时"},
        {"value": 86400, "label": "24小时"},
        {"value": 604800, "label": "7天"},
    ]),
    "download_limit_options": json.dumps([
        {"value": 1, "label": "1次"},
        {"value": 5, "label": "5次"},
        {"value": 10, "label": "10次"},
        {"value": -1, "label": "无限次"},
    ]),
    "cleanup_scan_interval_min": "10",
    "auto_deep_clean_enabled": "false",
    "auto_deep_clean_delay_min": "0",
}


def init_default_settings():
    db = SessionLocal()
    try:
        for key, value in DEFAULT_SETTINGS.items():
            existing = db.query(Setting).filter(Setting.key == key).first()
            if existing:
                if key in ("allowed_extensions", "blocked_extensions"):
                    existing.value = value
            else:
                db.add(Setting(key=key, value=value))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "banner"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "showcase"), exist_ok=True)
    create_tables()
    init_default_settings()
    from app.tasks import start_scheduler
    start_scheduler()
    yield


app = FastAPI(title="FileRunner", version="1.0.0", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pickup.router, prefix="/api", tags=["pickup"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin-auth"])
app.include_router(admin_files.router, prefix="/api/admin", tags=["admin-files"])
app.include_router(admin_logs.router, prefix="/api/admin", tags=["admin-logs"])
app.include_router(admin_settings.router, prefix="/api/admin", tags=["admin-settings"])

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    from starlette.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
