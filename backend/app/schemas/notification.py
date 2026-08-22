"""Notification schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import NotificationType


class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")

    model_config = {"from_attributes": True, "populate_by_name": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int
