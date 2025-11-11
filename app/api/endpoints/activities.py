"""
User Activity Endpoints

USE CASES:
- View user activity history
- Activity tracking
- Audit logs
- Behavior analytics
"""

from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user_activity as crud_activity
from app.crud import user as crud_user
from app.schemas.user_activity import UserActivity, UserActivityCreate, UserActivityStats
from app.models.user import User as UserModel
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/{user_id}/activities", response_model=UserActivity, status_code=201)
def create_activity(
    user_id: int,
    activity_in: UserActivityCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create activity log

    VÍ DỤ REQUEST:
    POST /api/v1/users/1/activities
    {
        "action_type": "VIEW",
        "description": "Viewed user profile",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }

    USE CASE:
    - Log user actions
    - Audit trail
    - Activity tracking

    TỰ ĐỘNG LOG:
    - IP address từ request
    - User agent từ request headers
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check: chỉ log activity cho chính mình hoặc admin
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Tự động lấy IP và User Agent nếu không có
    if not activity_in.ip_address:
        activity_in.ip_address = request.client.host if request.client else None
    if not activity_in.user_agent:
        activity_in.user_agent = request.headers.get("user-agent")

    # Create activity
    activity = crud_activity.create(db, user_id=user_id, obj_in=activity_in)
    return activity


@router.get("/{user_id}/activities", response_model=List[UserActivity])
def read_user_activities(
    user_id: int,
    skip: int = Query(0, ge=0, description="Số record bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số record tối đa"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user activities với pagination

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities?skip=0&limit=20

    RESPONSE: 20 activities gần nhất

    USE CASE:
    - Activity feed
    - User history
    - Audit log viewer
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission: chỉ xem activities của mình hoặc admin xem tất cả
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    activities = crud_activity.get_user_activities(db, user_id=user_id, skip=skip, limit=limit)
    return activities


@router.get("/{user_id}/activities/date/{target_date}", response_model=List[UserActivity])
def read_activities_by_date(
    user_id: int,
    target_date: date,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get activities trong một ngày cụ thể

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities/date/2024-01-01

    RESPONSE: Tất cả activities trong ngày 01/01/2024

    USE CASE:
    - Daily activity report
    - "What did user do on this day?"
    - Historical analysis
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Convert date to datetime
    target_datetime = datetime.combine(target_date, datetime.min.time())

    activities = crud_activity.get_activities_by_date(
        db, user_id=user_id, date=target_datetime
    )
    return activities


@router.get("/{user_id}/activities/date-range", response_model=List[UserActivity])
def read_activities_by_date_range(
    user_id: int,
    start_date: date = Query(..., description="Ngày bắt đầu"),
    end_date: date = Query(..., description="Ngày kết thúc"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get activities trong khoảng thời gian

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities/date-range?start_date=2024-01-01&end_date=2024-01-31

    USE CASE:
    - Weekly/Monthly activity report
    - Behavior analysis over time
    - Custom date range queries
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    activities = crud_activity.get_activities_by_date_range(
        db, user_id=user_id, start_date=start_datetime, end_date=end_datetime
    )
    return activities


@router.get("/{user_id}/activities/type/{action_type}", response_model=List[UserActivity])
def read_activities_by_type(
    user_id: int,
    action_type: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get activities theo loại action

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities/type/LOGIN

    RESPONSE: Tất cả LOGIN activities

    USE CASE:
    - Security: Xem tất cả login attempts
    - Audit: Xem ai DELETE gì
    - Filter by action type
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    activities = crud_activity.get_activities_by_type(
        db, user_id=user_id, action_type=action_type
    )
    return activities


@router.get("/{user_id}/activities/stats/{target_date}", response_model=UserActivityStats)
def read_activity_stats(
    user_id: int,
    target_date: date,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get activity statistics cho một ngày

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities/stats/2024-01-01

    RESPONSE:
    {
        "user_id": 1,
        "date": "2024-01-01T00:00:00",
        "total_activities": 10,
        "activity_breakdown": {
            "LOGIN": 2,
            "VIEW": 5,
            "UPDATE": 3
        }
    }

    USE CASE:
    - Dashboard visualization
    - Daily activity breakdown
    - Analytics
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Convert to datetime
    target_datetime = datetime.combine(target_date, datetime.min.time())

    # Get stats
    stats = crud_activity.get_activity_stats(
        db, user_id=user_id, date=target_datetime
    )

    return UserActivityStats(
        user_id=user_id,
        date=target_datetime,
        total_activities=stats["total"],
        activity_breakdown=stats["breakdown"]
    )


@router.get("/{user_id}/activities/recent", response_model=List[UserActivity])
def read_recent_activities(
    user_id: int,
    hours: int = Query(24, ge=1, le=168, description="Số giờ gần đây (tối đa 7 ngày)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get activities gần đây (trong X giờ)

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/activities/recent?hours=24

    RESPONSE: Activities trong 24 giờ qua

    USE CASE:
    - Real-time activity feed
    - Recent actions widget
    - "What user did recently?"
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    activities = crud_activity.get_recent_activities(
        db, user_id=user_id, hours=hours
    )
    return activities
