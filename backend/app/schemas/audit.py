from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AuditEventResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    timestamp: datetime
    success: bool
    ip_address: Optional[str] = None
    correlation_id: Optional[str] = None
    details: Optional[str] = None

    model_config = {"from_attributes": True}


class AuditListResponse(BaseModel):
    events: List[AuditEventResponse]
    total: int
