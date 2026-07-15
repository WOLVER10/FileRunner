from pydantic import BaseModel


# --- Upload ---
class UploadResponse(BaseModel):
    code: str
    url: str
    is_group: bool = False
    file_count: int = 1


# --- File Info ---
class FileInfoResponse(BaseModel):
    code: str
    filename: str
    size: int
    remaining_downloads: int
    expires_at: str
    status: str
    is_group: bool = False
    share_type: str = "single"
    file_count: int = 1


class FileCleanedResponse(BaseModel):
    status: str
    message: str


# --- Group File List ---
class GroupFileItem(BaseModel):
    id: int
    filename: str
    relative_path: str
    size: int
    mime_type: str


class GroupInfoResponse(BaseModel):
    code: str
    name: str
    file_count: int
    total_size: int
    remaining_downloads: int
    expires_at: str
    status: str
    is_group: bool = True
    share_type: str = "multi"
    files: list[GroupFileItem]


# --- Options ---
class ExpiryOption(BaseModel):
    value: int  # seconds
    label: str


class DownloadLimitOption(BaseModel):
    value: int  # -1 for unlimited
    label: str


class OptionsResponse(BaseModel):
    expiry_options: list[ExpiryOption]
    download_limit_options: list[DownloadLimitOption]
    max_size_bytes: int
    allowed_extensions: list[str]
    banner_image_url: str = ""
    banner_valid_from: str = ""
    banner_valid_until: str = ""


# --- Admin Login ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str


# --- Admin Files ---
class AdminFileItem(BaseModel):
    id: int
    code: str
    original_filename: str
    file_size: int
    upload_time: str
    expires_at: str
    status: str
    remaining_downloads: int
    is_deep_cleaned: bool
    share_type: str = "single"


class AdminFileListResponse(BaseModel):
    files: list[AdminFileItem]
    total: int
    page: int
    page_size: int


class AdminFileDetailResponse(AdminFileItem):
    stored_filename: str
    mime_type: str
    upload_ip: str
    download_limit: int
    recent_downloads: list[dict]
    # Group fields (populated when file belongs to a group)
    is_group: bool = False
    share_type: str = "single"
    group_name: str = ""
    group_total_size: int = 0
    group_file_count: int = 0
    files: list[dict] = []


class BatchDeepCleanRequest(BaseModel):
    ids: list[int]


# --- Admin Logs ---
class AdminLogItem(BaseModel):
    id: int
    code: str
    filename: str = ""
    is_group: bool = False
    group_name: str = ""
    share_type: str = "single"
    download_time: str
    ip: str
    user_agent: str
    success: bool
    reason: str


class AdminLogListResponse(BaseModel):
    logs: list[AdminLogItem]
    total: int
    page: int
    page_size: int


# --- Admin Stats ---
class AdminStatsResponse(BaseModel):
    total_files: int
    total_transfer_bytes: int
    active_shares: int


# --- Admin Settings ---
class ExpiryOptionManage(BaseModel):
    value: int
    label: str


class DownloadLimitOptionManage(BaseModel):
    value: int
    label: str


class AdminSettingsRequest(BaseModel):
    upload_control_mode: str = "whitelist"
    allowed_extensions: list[str]
    blocked_extensions: list[str] = []
    max_upload_size_bytes: int
    max_files_per_task: int = 100
    max_task_size_bytes: int = 5368709120
    expiry_options: list[ExpiryOptionManage]
    download_limit_options: list[DownloadLimitOptionManage]
    cleanup_scan_interval_min: int
    auto_deep_clean_enabled: bool
    auto_deep_clean_delay_min: int
    expiry_default_index: int = 0
    dl_default_index: int = 0
    banner_image_url: str = ""
    banner_valid_from: str = ""
    banner_valid_until: str = ""


class AdminSettingsResponse(AdminSettingsRequest):
    pass


# --- Showcase Tasks ---
class ShowcaseTaskResponse(BaseModel):
    id: int
    name: str
    image_url: str
    stored_filename: str
    valid_from: str | None = None
    valid_until: str | None = None
    sort_order: int = 0
    is_active: bool = False


class ShowcaseTaskListResponse(BaseModel):
    tasks: list[ShowcaseTaskResponse]


class ShowcaseTaskUpdateRequest(BaseModel):
    name: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    sort_order: int | None = None


# --- Generic ---
class MessageResponse(BaseModel):
    message: str
