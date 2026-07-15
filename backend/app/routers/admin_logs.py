from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import DownloadLog, FileRecord, FileGroup
from app.schemas import AdminLogListResponse, AdminLogItem

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/logs", response_model=AdminLogListResponse)
async def list_logs(
    code: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    share_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    query = (
        db.query(DownloadLog, FileRecord)
        .outerjoin(FileRecord, DownloadLog.file_id == FileRecord.id)
    )

    if code:
        query = query.filter(DownloadLog.code == code)
    if start_time:
        query = query.filter(DownloadLog.download_time >= start_time)
    if end_time:
        query = query.filter(DownloadLog.download_time <= end_time)
    if share_type:
        # Filter by share_type via FileGroup
        share_types = [t.strip() for t in share_type.split(",") if t.strip()]
        if share_types:
            query = query.outerjoin(FileGroup, FileRecord.group_id == FileGroup.id)
            if "single" in share_types:
                query = query.filter(
                    (FileGroup.share_type.in_(share_types)) | (FileGroup.id.is_(None))
                )
            else:
                query = query.filter(FileGroup.share_type.in_(share_types))

    total = query.count()
    rows = (
        query.order_by(DownloadLog.download_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for l, f in rows:
        is_group = bool(f.group_id) if f else False
        group_name = ""
        share_type = "single"
        if is_group and f.group_id:
            grp = db.query(FileGroup).filter(FileGroup.id == f.group_id).first()
            if grp:
                group_name = grp.name or ""
                share_type = grp.share_type or "multi"
        items.append(
            AdminLogItem(
                id=l.id,
                code=l.code,
                filename=f.original_filename if f else "",
                is_group=is_group,
                group_name=group_name,
                share_type=share_type,
                download_time=l.download_time.isoformat() if l.download_time else "",
                ip=l.ip,
                user_agent=l.user_agent,
                success=l.success,
                reason=l.reason,
            )
        )

    return AdminLogListResponse(
        logs=items, total=total, page=page, page_size=page_size
    )
