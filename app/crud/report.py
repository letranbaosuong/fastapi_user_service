"""
Report CRUD Operations - Admin Analytics

Các function để lấy thống kê và báo cáo cho admin
Tái sử dụng logic từ crud/user.py để tránh lặp code
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.models.user import User
from app.crud.user import get_users_by_date_range


def get_new_users_count(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> int:
    """
    Đếm số user mới trong khoảng thời gian

    VÍ DỤ:
    count = get_new_users_count(db, start_date, end_date)
    => SELECT COUNT(*) FROM users WHERE created_at BETWEEN ...

    TÁI SỬ DỤNG: Dùng get_users_by_date_range từ crud/user.py
    """
    users = get_users_by_date_range(db, start_date, end_date)
    return len(users)


def get_new_users_today(db: Session) -> int:
    """
    Đếm user mới hôm nay

    VÍ DỤ USE CASE:
    - Dashboard admin: "50 users mới hôm nay"
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    return get_new_users_count(db, today_start, today_end)


def get_new_users_yesterday(db: Session) -> int:
    """
    Đếm user mới hôm qua

    VÍ DỤ USE CASE:
    - So sánh growth: "Hôm nay +10% so với hôm qua"
    """
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    return get_new_users_count(db, yesterday_start, yesterday_end)


def get_new_users_last_n_days(db: Session, days: int = 7) -> int:
    """
    Đếm user mới trong N ngày gần đây

    VÍ DỤ:
    count = get_new_users_last_n_days(db, days=7)
    => User đăng ký trong 7 ngày qua

    THAM SỐ:
    - days: Số ngày (mặc định 7)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return get_new_users_count(db, start_date, end_date)


def get_users_by_country(
    db: Session,
    country: str,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Lấy danh sách user theo quốc gia

    VÍ DỤ:
    users = get_users_by_country(db, country="VN")
    => SELECT * FROM users WHERE country = 'VN'

    THAM SỐ:
    - country: Mã quốc gia (VN, US, JP, ...)
    - skip, limit: Pagination
    """
    return db.query(User).filter(
        User.country == country
    ).offset(skip).limit(limit).all()


def get_users_count_by_country(db: Session, country: str) -> int:
    """
    Đếm số user theo quốc gia

    VÍ DỤ:
    count = get_users_count_by_country(db, "VN")
    => 1500 users từ Vietnam
    """
    return db.query(User).filter(User.country == country).count()


def get_all_countries_stats(db: Session) -> List[Dict]:
    """
    Lấy thống kê tất cả quốc gia

    VÍ DỤ RETURN:
    [
        {"country": "VN", "total_users": 1500, "active_users": 1200, "percentage": 35.5},
        {"country": "US", "total_users": 800, "active_users": 700, "percentage": 18.9},
        ...
    ]

    SQL EQUIVALENT:
    SELECT
        country,
        COUNT(*) as total_users,
        SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_users
    FROM users
    WHERE country IS NOT NULL
    GROUP BY country
    ORDER BY total_users DESC
    """
    # Lấy tổng số user
    total_all_users = db.query(User).count()

    # Group by country
    results = db.query(
        User.country,
        func.count(User.id).label('total_users'),
        func.sum(func.cast(User.is_active, Integer)).label('active_users')
    ).filter(
        User.country.isnot(None)
    ).group_by(User.country).order_by(
        func.count(User.id).desc()
    ).all()

    # Format kết quả
    stats = []
    for row in results:
        stats.append({
            "country": row.country,
            "total_users": row.total_users,
            "active_users": row.active_users or 0,
            "percentage": round((row.total_users / total_all_users * 100), 2) if total_all_users > 0 else 0
        })

    return stats


def get_overall_stats(db: Session) -> Dict:
    """
    Lấy tổng quan thống kê

    VÍ DỤ RETURN:
    {
        "total_users": 10000,
        "active_users": 8000,
        "inactive_users": 2000,
        "new_today": 50,
        "new_yesterday": 45,
        "new_last_7_days": 300,
        "total_countries": 25
    }

    TÁI SỬ DỤNG: Gọi các function đã viết ở trên
    """
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = total_users - active_users

    # Số quốc gia distinct
    total_countries = db.query(func.count(func.distinct(User.country))).filter(
        User.country.isnot(None)
    ).scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "new_today": get_new_users_today(db),
        "new_yesterday": get_new_users_yesterday(db),
        "new_last_7_days": get_new_users_last_n_days(db, days=7),
        "total_countries": total_countries or 0
    }


def get_users_with_filters(
    db: Session,
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    days: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Lấy users với dynamic filters (giống GraphQL)

    VÍ DỤ 1:
    users = get_users_with_filters(db, country="VN", is_active=True)
    => User từ VN và đang active

    VÍ DỤ 2:
    users = get_users_with_filters(db, days=7)
    => User đăng ký trong 7 ngày qua

    VÍ DỤ 3:
    users = get_users_with_filters(db, country="VN", is_active=True, days=7)
    => User từ VN, active, đăng ký trong 7 ngày

    DYNAMIC FILTERS: Chỉ apply filter nào có giá trị
    """
    query = db.query(User)

    # Build filters dynamically
    filters = []

    if country is not None:
        filters.append(User.country == country)

    if is_active is not None:
        filters.append(User.is_active == is_active)

    if is_superuser is not None:
        filters.append(User.is_superuser == is_superuser)

    if days is not None:
        date_threshold = datetime.now() - timedelta(days=days)
        filters.append(User.created_at >= date_threshold)

    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))

    return query.offset(skip).limit(limit).all()


def get_daily_stats_range(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    """
    Lấy thống kê theo từng ngày trong khoảng thời gian

    VÍ DỤ RETURN:
    [
        {"date": "2024-01-01", "new_users": 50, "active_users": 500, "total_users": 5000},
        {"date": "2024-01-02", "new_users": 45, "active_users": 520, "total_users": 5045},
        ...
    ]

    USE CASE:
    - Chart growth theo ngày
    - Xem trend user registration
    """
    stats = []
    current_date = start_date

    while current_date <= end_date:
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # User mới trong ngày
        new_users = get_new_users_count(db, day_start, day_end)

        # Tổng user tính đến ngày đó
        total_users = db.query(User).filter(User.created_at <= day_end).count()

        # Active users (giả định active = đăng nhập trong 30 ngày gần đây)
        # Ở đây đơn giản hóa: active = is_active flag
        active_users = db.query(User).filter(
            User.created_at <= day_end,
            User.is_active == True
        ).count()

        stats.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "new_users": new_users,
            "active_users": active_users,
            "total_users": total_users
        })

        current_date += timedelta(days=1)

    return stats


# Import Integer for SQLAlchemy cast
from sqlalchemy import Integer
