from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# Create
class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    message: str
    notification_type: str
    priority: str = "MEDIUM"
    payload: dict = {}

# Update
class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    priority: Optional[str] = None
    payload: Optional[dict] = None
    is_read: Optional[bool] = None
    is_active: Optional[bool] = None

# Response
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    title: str
    message: str
    notification_type: str
    priority: str
    payload: dict
    is_read: bool
    read_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Notification Count
class NotificationCountResponse(BaseModel):
    total_notifications: int
    unread_notifications: int
    read_notifications: int

# Notification Filter
class NotificationFilter(BaseModel):
    notification_type: Optional[str] = None
    priority: Optional[str] = None
    is_read: Optional[bool] = None