"""Notification routes."""

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.models.notification import Notification
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(db: DBSession, current_user: CurrentUser, unread_only: bool = Query(False), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    total = query.count()
    unread = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).count()
    items = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return NotificationListResponse(items=items, total=total, unread_count=unread)


@router.put("/{notification_id}/read")
def mark_read(notification_id: int, db: DBSession, current_user: CurrentUser):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if notification:
        notification.is_read = True
        db.commit()
    return {"is_read": True}


@router.put("/read-all")
def mark_all_read(db: DBSession, current_user: CurrentUser):
    updated = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).update({"is_read": True})
    db.commit()
    return {"updated_count": updated}
