"""Notification service."""

import uuid

from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    user_id: uuid.UUID,
    type: NotificationType,
    title: str,
    message: str,
    metadata: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        metadata_=metadata,
    )
    db.add(notification)
    return notification


def notify_admins(db: Session, *, type: NotificationType, title: str, message: str, metadata: dict | None = None) -> None:
    from app.models.enums import UserRole
    from app.models.user import User

    admins = db.query(User).filter(User.role == UserRole.ADMIN, User.is_active.is_(True)).all()
    for admin in admins:
        create_notification(db, user_id=admin.id, type=type, title=title, message=message, metadata=metadata)
