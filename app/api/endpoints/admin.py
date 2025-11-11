"""
Admin Report Endpoints

Các API cho admin xem thống kê và báo cáo
CHỈ admin (is_superuser=True) mới truy cập được
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.api.dependencies import get_current_active_superuser
from app.models.user import User as UserModel
from app.schemas.user import User
from app.schemas.report import (
    NewUsersReport,
    UsersByCountryReport,
    DailyUsersStats,
    OverallStats
)
from app.crud import report as crud_report


router = APIRouter()


@router.get("/stats/overall", response_model=OverallStats)
def get_overall_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy tổng quan thống kê - ADMIN ONLY

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/stats/overall

    RESPONSE:
    {
        "total_users": 10000,
        "active_users": 8000,
        "inactive_users": 2000,
        "new_today": 50,
        "new_yesterday": 45,
        "new_last_7_days": 300,
        "total_countries": 25
    }

    USE CASE:
    - Dashboard admin overview
    - Quick stats summary
    """
    return crud_report.get_overall_stats(db)


@router.get("/stats/new-users", response_model=NewUsersReport)
def get_new_users_statistics(
    period: str = Query(
        "today",
        description="Khoảng thời gian: today, yesterday, last_7_days, last_30_days"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy thống kê user mới theo khoảng thời gian - ADMIN ONLY

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/stats/new-users?period=last_7_days

    RESPONSE:
    {
        "total": 300,
        "period": "last_7_days",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-07T23:59:59"
    }

    PARAMETERS:
    - period: today, yesterday, last_7_days, last_30_days

    USE CASE:
    - Xem growth user theo khoảng thời gian
    - Compare periods
    """
    now = datetime.now()

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "last_7_days":
        end_date = now
        start_date = now - timedelta(days=7)
    elif period == "last_30_days":
        end_date = now
        start_date = now - timedelta(days=30)
    else:
        # Default to today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    total = crud_report.get_new_users_count(db, start_date, end_date)

    return NewUsersReport(
        total=total,
        period=period,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/stats/by-country", response_model=List[UsersByCountryReport])
def get_users_by_country_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy thống kê user theo quốc gia - ADMIN ONLY

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/stats/by-country

    RESPONSE:
    [
        {
            "country": "VN",
            "total_users": 1500,
            "active_users": 1200,
            "percentage": 35.5
        },
        {
            "country": "US",
            "total_users": 800,
            "active_users": 700,
            "percentage": 18.9
        },
        ...
    ]

    USE CASE:
    - Xem phân bố user theo quốc gia
    - Geographic analytics
    - Market penetration analysis
    """
    stats = crud_report.get_all_countries_stats(db)
    return [UsersByCountryReport(**stat) for stat in stats]


@router.get("/stats/daily", response_model=List[DailyUsersStats])
def get_daily_statistics(
    days: int = Query(7, ge=1, le=90, description="Số ngày (1-90)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy thống kê theo từng ngày - ADMIN ONLY

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/stats/daily?days=7

    RESPONSE:
    [
        {
            "date": "2024-01-01",
            "new_users": 50,
            "active_users": 500,
            "total_users": 5000
        },
        {
            "date": "2024-01-02",
            "new_users": 45,
            "active_users": 520,
            "total_users": 5045
        },
        ...
    ]

    PARAMETERS:
    - days: Số ngày (1-90, mặc định 7)

    USE CASE:
    - Chart user growth theo ngày
    - Trend analysis
    - Daily performance tracking
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)  # -1 vì tính cả ngày hôm nay

    stats = crud_report.get_daily_stats_range(db, start_date, end_date)
    return [DailyUsersStats(**stat) for stat in stats]


@router.get("/users/filter", response_model=List[User])
def get_users_with_dynamic_filters(
    country: str = Query(None, description="Filter theo quốc gia (VN, US, JP, ...)"),
    is_active: bool = Query(None, description="Filter theo trạng thái active"),
    is_superuser: bool = Query(None, description="Filter theo role admin"),
    days: int = Query(None, ge=1, description="Filter user tạo trong N ngày gần đây"),
    skip: int = Query(0, ge=0, description="Pagination: skip"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination: limit"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy danh sách users với dynamic filters - ADMIN ONLY

    VÍ DỤ REQUEST 1: Lấy user từ Vietnam
    GET /api/v1/admin/reports/users/filter?country=VN

    VÍ DỤ REQUEST 2: Lấy user active từ Vietnam
    GET /api/v1/admin/reports/users/filter?country=VN&is_active=true

    VÍ DỤ REQUEST 3: Lấy admin users
    GET /api/v1/admin/reports/users/filter?is_superuser=true

    VÍ DỤ REQUEST 4: Lấy user đăng ký trong 7 ngày từ US
    GET /api/v1/admin/reports/users/filter?country=US&days=7

    VÍ DỤ REQUEST 5: Combine multiple filters
    GET /api/v1/admin/reports/users/filter?country=VN&is_active=true&days=7&limit=50

    PARAMETERS (tất cả optional - DYNAMIC FILTERING giống GraphQL):
    - country: Mã quốc gia (VN, US, JP, ...)
    - is_active: true/false
    - is_superuser: true/false
    - days: Số ngày gần đây (ví dụ: days=7 = user đăng ký trong 7 ngày)
    - skip: Pagination offset
    - limit: Số record tối đa (max 1000)

    USE CASE:
    - Admin user management với flexible filtering
    - Advanced search
    - Segment users
    - Export user lists
    """
    users = crud_report.get_users_with_filters(
        db=db,
        country=country,
        is_active=is_active,
        is_superuser=is_superuser,
        days=days,
        skip=skip,
        limit=limit
    )
    return users


@router.get("/users/country/{country}", response_model=List[User])
def get_users_by_specific_country(
    country: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Lấy danh sách user theo quốc gia cụ thể - ADMIN ONLY

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/users/country/VN?skip=0&limit=50

    RESPONSE: List of users from Vietnam

    PARAMETERS:
    - country: Mã quốc gia (VN, US, JP, ...)
    - skip, limit: Pagination

    USE CASE:
    - Xem tất cả user từ một quốc gia
    - Country-specific analysis
    """
    users = crud_report.get_users_by_country(
        db=db,
        country=country,
        skip=skip,
        limit=limit
    )
    return users
