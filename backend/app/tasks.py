import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Setting
from app.services.cleanup_service import mark_expired, deep_clean

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def cleanup_job():
    db = SessionLocal()
    try:
        marked = mark_expired(db)
        if marked:
            logger.info("Marked %d files as expired", marked)

        setting = db.query(Setting).filter(Setting.key == "auto_deep_clean_enabled").first()
        if setting and setting.value == "true":
            cleaned = deep_clean(db)
            if cleaned:
                logger.info("Auto deep cleaned %d files", cleaned)
    except Exception:
        logger.exception("Cleanup job failed")
    finally:
        db.close()


def start_scheduler():
    db = SessionLocal()
    try:
        interval_setting = db.query(Setting).filter(Setting.key == "cleanup_scan_interval_min").first()
        interval = int(interval_setting.value) if interval_setting else 10
    finally:
        db.close()

    scheduler.add_job(
        cleanup_job,
        "interval",
        minutes=interval,
        id="cleanup_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Cleanup scheduler started with %d minute interval", interval)
