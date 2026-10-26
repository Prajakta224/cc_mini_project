from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class FileRecordResponse(BaseModel):
    id: int
    original_filename: str
    original_size: int
    content_type: Optional[str] = None
    encrypted_object_key: str
    encrypted_size: Optional[int] = None
    encryption_algorithm: str
    format_version: int
    storage_provider: str
    upload_timestamp: datetime
    status: str

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: List[FileRecordResponse]
    total: int


class EncryptResponse(BaseModel):
    file_id: int
    original_filename: str
    encrypted_object_key: str
    encryption_algorithm: str
    original_size: int
    encrypted_size: int
    storage_provider: str
    upload_timestamp: datetime
    message: str


class DecryptResponse(BaseModel):
    filename: str
    content_type: str
    # actual file content returned as StreamingResponse
