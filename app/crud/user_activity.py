"""
User Activity CRUD Operations

USE CASES:
- Log mọi action của user
- Audit trail
- Behavior analytics
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate


def create(
    db: Session,
    user_id: int,
    obj_in: UserActivityCreate
) -> UserActivity:
    """
    Tạo activity log

    VÍ DỤ:
    activity = create(
        db,
        user_id=1,
        obj_in=UserActivityCreate(
            action_type="LOGIN",
            description="User logged in",
            ip_address="192.168.1.1"
        )
    )
    """
    db_obj = UserActivity(
        user_id=user_id,
        action_type=obj_in.action_type,
        description=obj_in.description,
        ip_address=obj_in.ip_address,
        user_agent=obj_in.user_agent,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[UserActivity]:
    """
    Lấy danh sách activities của user với pagination

    VÍ DỤ USE CASE:
    GET /api/v1/users/1/activities?skip=0&limit=20

    RESPONSE: 20 activities gần nhất của user
    """
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id
    ).order_by(
        UserActivity.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_activities_by_date(
    db: Session,
    user_id: int,
    date: datetime
) -> List[UserActivity]:
    """
    Lấy activities của user trong một ngày cụ thể

    VÍ DỤ USE CASE:
    - Xem user đã làm gì trong ngày 01/01/2024
    - Daily activity report

    VÍ DỤ:
    activities = get_activities_by_date(db, user_id=1, date=datetime(2024,1,1))
    => SELECT * FROM user_activities
       WHERE user_id = 1 AND DATE(created_at) = '2024-01-01'
    """
    target_date = date.date()
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        func.date(UserActivity.created_at) == target_date
    ).order_by(UserActivity.created_at.desc()).all()


def get_activities_by_date_range(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[UserActivity]:
    """
    Lấy activities trong khoảng thời gian

    VÍ DỤ USE CASE:
    - Weekly/Monthly activity report
    - Behavior analysis

    VÍ DỤ:
    activities = get_activities_by_date_range(
        db, user_id=1,
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,1,31)
    )
    """
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).order_by(UserActivity.created_at.desc()).all()


def get_activities_by_type(
    db: Session,
    user_id: int,
    action_type: str
) -> List[UserActivity]:
    """
    Lấy activities theo loại action

    VÍ DỤ USE CASE:
    - Xem tất cả lần LOGIN của user
    - Security audit: Xem ai đã DELETE gì

    VÍ DỤ:
    login_activities = get_activities_by_type(db, user_id=1, action_type="LOGIN")
    """
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.action_type == action_type
    ).order_by(UserActivity.created_at.desc()).all()


def get_activity_stats(
    db: Session,
    user_id: int,
    date: datetime
) -> dict:
    """
    Lấy thống kê activities trong một ngày

    VÍ DỤ USE CASE:
    - Dashboard hiển thị breakdown activities
    - Analytics

    VÍ DỤ RETURN:
    {
        "date": "2024-01-01",
        "total": 10,
        "breakdown": {
            "LOGIN": 2,
            "VIEW": 5,
            "UPDATE": 3
        }
    }
    """
    target_date = date.date()
    activities = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        func.date(UserActivity.created_at) == target_date
    ).all()

    # Breakdown by action type
    breakdown = {}
    for activity in activities:
        action_type = activity.action_type
        breakdown[action_type] = breakdown.get(action_type, 0) + 1

    return {
        "date": target_date.isoformat(),
        "total": len(activities),
        "breakdown": breakdown
    }


def get_recent_activities(
    db: Session,
    user_id: int,
    hours: int = 24
) -> List[UserActivity]:
    """
    Lấy activities gần đây (trong X giờ)

    VÍ DỤ USE CASE:
    - Real-time activity feed
    - Recent actions widget

    VÍ DỤ:
    recent = get_recent_activities(db, user_id=1, hours=24)
    => Activities trong 24 giờ qua
    """
    since = datetime.now() - timedelta(hours=hours)
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= since
    ).order_by(UserActivity.created_at.desc()).all()


def delete_old_activities(
    db: Session,
    days: int = 90
) -> int:
    """
    Xóa activities cũ (retention policy)

    VÍ DỤ USE CASE:
    - Scheduled job chạy hàng ngày
    - Cleanup old logs để tiết kiệm storage

    VÍ DỤ:
    deleted_count = delete_old_activities(db, days=90)
    => Xóa activities cũ hơn 90 ngày
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    result = db.query(UserActivity).filter(
        UserActivity.created_at < cutoff_date
    ).delete()
    db.commit()
    return result
