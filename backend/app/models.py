from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, func

from app.database import Base


class Setting(Base):
    __tablename__ = "settings"

    key = Column(Text, primary_key=True)
    value = Column(Text, nullable=False)


class FileGroup(Base):
    __tablename__ = "file_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Text, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    upload_ip = Column(Text, nullable=False)
    upload_time = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    status = Column(Text, nullable=False, default="active")
    download_limit = Column(Integer, nullable=False, default=1)
    remaining_downloads = Column(Integer, nullable=False, default=1)
    is_deep_cleaned = Column(Boolean, nullable=False, default=False)
    file_count = Column(Integer, nullable=False, default=0)
    total_size = Column(Integer, nullable=False, default=0)
    share_type = Column(Text, nullable=False, default="multi")


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Text, nullable=False, index=True)
    original_filename = Column(Text, nullable=False)
    stored_filename = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(Text, nullable=False)
    upload_ip = Column(Text, nullable=False)
    upload_time = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    status = Column(Text, nullable=False, default="active")
    download_limit = Column(Integer, nullable=False, default=1)
    remaining_downloads = Column(Integer, nullable=False, default=1)
    is_deep_cleaned = Column(Boolean, nullable=False, default=False)

    group_id = Column(Integer, ForeignKey("file_groups.id"), nullable=True)
    relative_path = Column(Text, nullable=True)


class DownloadLog(Base):
    __tablename__ = "download_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    code = Column(Text, nullable=False)
    download_time = Column(DateTime, nullable=False, server_default=func.now())
    ip = Column(Text, nullable=False)
    user_agent = Column(Text, nullable=False, default="")
    success = Column(Boolean, nullable=False, default=True)
    reason = Column(Text, nullable=False, default="")


class ShowcaseTask(Base):
    __tablename__ = "showcase_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    stored_filename = Column(Text, nullable=False)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
