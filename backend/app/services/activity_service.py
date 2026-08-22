"""Activity logging service."""

import uuid

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.enums import ActivityAction


def log_activity(
    db: Session,
    *,
    user_id: uuid.UUID | None,
    action: ActivityAction,
    description: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    metadata: dict | None = None,
) -> ActivityLog:
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_=metadata,
    )
    db.add(entry)
    return entry
