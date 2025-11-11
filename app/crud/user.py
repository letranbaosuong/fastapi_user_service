"""
User CRUD Operations

KHÁI NIỆM CRUD:
- Create: Tạo user mới
- Read: Đọc thông tin user
- Update: Cập nhật thông tin
- Delete: Xóa user

VÍ DỤ:
crud.user.create(db, obj_in=user_data)
=> INSERT INTO users ...

REDIS CACHE:
- get_multi: Cache 5 phút
- get_by_id: Cache 5 phút
- Update/Delete: Tự động xóa cache
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.user import User
from app.models.user_activity import UserActivity
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.redis import cache_result, invalidate_cache_on_change


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Lấy user theo email

    VÍ DỤ:
    user = get_by_email(db, "test@example.com")
    => SELECT * FROM users WHERE email = 'test@example.com'
    """
    return db.query(User).filter(User.email == email).first()


@cache_result("user_by_id", ttl=300)
def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Lấy user theo ID (CACHED 5 phút)

    VÍ DỤ:
    user = get_by_id(db, 1)
    => SELECT * FROM users WHERE id = 1

    CACHE: Kết quả được cache 5 phút
    """
    return db.query(User).filter(User.id == user_id).first()


@cache_result("users_list", ttl=300)
def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Lấy danh sách users với pagination (CACHED 5 phút)

    VÍ DỤ:
    users = get_multi(db, skip=0, limit=10)
    => SELECT * FROM users LIMIT 10 OFFSET 0

    USE CASE: List users trong admin panel
    - Page 1: skip=0, limit=10
    - Page 2: skip=10, limit=10

    CACHE: Kết quả được cache 5 phút theo skip/limit
    """
    return db.query(User).offset(skip).limit(limit).all()


@cache_result("users_by_countries", ttl=300)
def get_multi_by_countries(
    db: Session,
    countries: List[str],
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Lấy danh sách users theo nhiều quốc gia (CACHED 5 phút)

    VÍ DỤ:
    users = get_multi_by_countries(db, countries=["VN", "US", "TH"], skip=0, limit=10)
    => SELECT * FROM users
       WHERE country IN ('VN', 'US', 'TH')
       LIMIT 10 OFFSET 0

    USE CASE:
    - Client filter users theo nhiều quốc gia (multiple choice)
    - Admin panel: xem users từ VN, US, Thái,...
    - Analytics: phân tích users theo vùng địa lý

    PAGINATION:
    - Page 1: skip=0, limit=10
    - Page 2: skip=10, limit=10

    CACHE: Kết quả được cache 5 phút theo countries/skip/limit
    """
    return db.query(User).filter(
        User.country.in_(countries)
    ).offset(skip).limit(limit).all()


def get_users_created_today(db: Session) -> List[User]:
    """
    Lấy danh sách users được tạo trong ngày hôm nay

    VÍ DỤ USE CASE:
    - Admin xem có bao nhiêu user đăng ký mới hôm nay
    - Daily report

    VÍ DỤ:
    users = get_users_created_today(db)
    => SELECT * FROM users
       WHERE DATE(created_at) = CURRENT_DATE
    """
    today = datetime.now().date()
    return db.query(User).filter(
        func.date(User.created_at) == today
    ).all()


def get_users_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[User]:
    """
    Lấy users trong khoảng thời gian

    VÍ DỤ USE CASE:
    - Báo cáo user đăng ký trong tuần/tháng
    - Analytics growth

    VÍ DỤ:
    users = get_users_by_date_range(db, start_date, end_date)
    => SELECT * FROM users
       WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31'
    """
    return db.query(User).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()


@invalidate_cache_on_change(["users_list:*", "users_by_countries:*", "user_by_id:*"])
def create(db: Session, obj_in: UserCreate) -> User:
    """
    Tạo user mới (INVALIDATE CACHE)

    VÍ DỤ:
    user_data = UserCreate(
        email="new@example.com",
        full_name="New User",
        password="password123"
    )
    user = create(db, obj_in=user_data)

    WORKFLOW:
    1. Hash password
    2. Create User object
    3. Add to database
    4. Commit transaction
    5. Refresh to get ID
    6. Xóa cache users (vì có user mới)

    CACHE INVALIDATION: Xóa cache users_list, users_by_countries
    """
    db_obj = User(
        email=obj_in.email,
        full_name=obj_in.full_name,
        hashed_password=get_password_hash(obj_in.password),
        bio=obj_in.bio,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@invalidate_cache_on_change(["users_list:*", "users_by_countries:*", "user_by_id:*"])
def update(
    db: Session,
    db_obj: User,
    obj_in: UserUpdate
) -> User:
    """
    Update user (INVALIDATE CACHE)

    VÍ DỤ:
    user = get_by_id(db, 1)
    update_data = UserUpdate(full_name="Updated Name")
    updated_user = update(db, db_obj=user, obj_in=update_data)

    WORKFLOW:
    1. Chỉ update fields có giá trị (không None)
    2. Commit changes
    3. Return updated object
    4. Xóa cache users (vì data đã thay đổi)

    CACHE INVALIDATION: Xóa cache users_list, users_by_countries, user_by_id
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@invalidate_cache_on_change(["users_list:*", "users_by_countries:*", "user_by_id:*"])
def delete(db: Session, user_id: int) -> Optional[User]:
    """
    Xóa user (INVALIDATE CACHE)

    VÍ DỤ:
    deleted_user = delete(db, user_id=1)
    => DELETE FROM users WHERE id = 1

    LƯU Ý:
    - Cascade delete: tất cả activities của user cũng bị xóa
    - Cache invalidation: xóa cache users

    CACHE INVALIDATION: Xóa cache users_list, users_by_countries, user_by_id
    """
    db_obj = get_by_id(db, user_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """
    Xác thực user (login)

    VÍ DỤ:
    user = authenticate(db, "user@example.com", "password123")
    if user:
        # Login successful
    else:
        # Invalid credentials

    WORKFLOW:
    1. Tìm user theo email
    2. Verify password với hashed password
    3. Return user nếu đúng, None nếu sai
    """
    user = get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_statistics(db: Session, user_id: int) -> dict:
    """
    Lấy thống kê của user

    VÍ DỤ USE CASE:
    - Dashboard hiển thị user stats
    - Admin analytics

    VÍ DỤ RETURN:
    {
        "total_activities": 150,
        "activities_today": 5,
        "last_login": "2024-01-01T10:00:00",
        "account_age_days": 30
    }
    """
    user = get_by_id(db, user_id)
    if not user:
        return {}

    total_activities = db.query(UserActivity).filter(
        UserActivity.user_id == user_id
    ).count()

    today = datetime.now().date()
    activities_today = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        func.date(UserActivity.created_at) == today
    ).count()

    last_login_activity = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.action_type == "LOGIN"
    ).order_by(UserActivity.created_at.desc()).first()

    account_age = (datetime.now() - user.created_at).days

    return {
        "total_activities": total_activities,
        "activities_today": activities_today,
        "last_login": last_login_activity.created_at if last_login_activity else None,
        "account_age_days": account_age
    }
