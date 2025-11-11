"""
User Management Endpoints

USE CASES:
- CRUD users
- Get users list
- View user statistics
- Get users created today/by date range
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as crud_user
from app.schemas.user import User, UserUpdate
from app.models.user import User as UserModel
from app.api.dependencies import get_current_user, get_current_active_superuser

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0, description="Số record bỏ qua (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Số record tối đa trả về"),
    countries: Optional[List[str]] = Query(None, description="Filter theo nhiều quốc gia (VN, US, TH,...)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get danh sách users với pagination và filter theo quốc gia

    VÍ DỤ REQUEST:
    1. Không filter:
       GET /api/v1/users?skip=0&limit=10

    2. Filter theo 1 quốc gia:
       GET /api/v1/users?countries=VN

    3. Filter theo nhiều quốc gia (multiple choice):
       GET /api/v1/users?countries=VN&countries=US&countries=TH
    
    4. Kết hợp với pagination:
        GET /api/v1/users?countries=VN&countries=US&skip=0&limit=20

    Headers: Authorization: Bearer <token>

    RESPONSE: List users (có filter theo countries nếu có)

    USE CASE:
    - Admin panel user list
    - User directory với filter quốc gia
    - Analytics: xem users theo vùng địa lý
    - Client multiple choice countries filter

    PAGINATION:
    - Page 1: skip=0, limit=10
    - Page 2: skip=10, limit=10
    - Page 3: skip=20, limit=10
    """
    # Nếu có filter countries, dùng get_multi_by_countries
    if countries:
        users = crud_user.get_multi_by_countries(db, countries=countries, skip=skip, limit=limit)
    else:
        # Nếu không có filter, lấy tất cả users
        users = crud_user.get_multi(db, skip=skip, limit=limit)

    return users


@router.get("/today", response_model=List[User])
def read_users_created_today(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get danh sách users được tạo trong ngày hôm nay

    VÍ DỤ REQUEST:
    GET /api/v1/users/today

    USE CASE:
    - Admin dashboard: "New users today"
    - Daily report
    - Analytics

    RESPONSE: List users registered today
    """
    users = crud_user.get_users_created_today(db)
    return users


@router.get("/date-range", response_model=List[User])
def read_users_by_date_range(
    start_date: date = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get users trong khoảng thời gian

    VÍ DỤ REQUEST:
    GET /api/v1/users/date-range?start_date=2024-01-01&end_date=2024-01-31

    USE CASE:
    - Weekly/Monthly growth report
    - Analytics dashboard
    - User acquisition metrics

    RESPONSE: Users created between start_date and end_date
    """
    # Convert date to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    users = crud_user.get_users_by_date_range(db, start_datetime, end_datetime)
    return users


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user by ID

    VÍ DỤ REQUEST:
    GET /api/v1/users/1

    RESPONSE: User info

    USE CASE:
    - View user profile
    - User details page
    """
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/statistics")
def read_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user statistics

    VÍ DỤ REQUEST:
    GET /api/v1/users/1/statistics

    RESPONSE:
    {
        "total_activities": 150,
        "activities_today": 5,
        "last_login": "2024-01-01T10:00:00",
        "account_age_days": 30
    }

    USE CASE:
    - User dashboard
    - Admin analytics
    - User engagement metrics
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get statistics
    stats = crud_user.get_user_statistics(db, user_id=user_id)
    return stats


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update user

    VÍ DỤ REQUEST:
    PUT /api/v1/users/1
    {
        "full_name": "Updated Name",
        "bio": "New bio"
    }

    AUTHORIZATION:
    - User chỉ có thể update chính mình
    - Admin có thể update bất kỳ user nào

    USE CASE:
    - Edit profile
    - Update user information
    """
    # Check user exists
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permission: chỉ update chính mình hoặc là admin
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check email không bị trùng (nếu update email)
    if user_in.email and user_in.email != user.email:
        existing_user = crud_user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Delete user (Admin only)

    VÍ DỤ REQUEST:
    DELETE /api/v1/users/1
    Headers: Authorization: Bearer <admin-token>

    AUTHORIZATION: Admin only

    USE CASE:
    - Admin panel
    - Remove spam/abuse accounts
    - User requested account deletion

    LƯU Ý: Cascade delete - tất cả activities của user cũng bị xóa
    """
    user = crud_user.delete(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
