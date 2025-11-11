"""
Report Pydantic Schemas - Admin Analytics

Schemas cho các report endpoints dành cho admin
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NewUsersReport(BaseModel):
    """
    Schema cho báo cáo user mới

    VÍ DỤ RESPONSE:
    {
        "total": 150,
        "period": "last_7_days",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-07T23:59:59"
    }
    """
    total: int = Field(..., description="Tổng số user mới")
    period: str = Field(..., description="Khoảng thời gian (today, yesterday, last_7_days, etc.)")
    start_date: datetime = Field(..., description="Ngày bắt đầu")
    end_date: datetime = Field(..., description="Ngày kết thúc")


class UsersByCountryReport(BaseModel):
    """
    Schema cho báo cáo user theo quốc gia

    VÍ DỤ RESPONSE:
    {
        "country": "VN",
        "total_users": 1500,
        "active_users": 1200,
        "percentage": 35.5
    }
    """
    country: str = Field(..., description="Mã quốc gia")
    total_users: int = Field(..., description="Tổng số user")
    active_users: int = Field(..., description="Số user đang active")
    percentage: float = Field(..., description="Phần trăm so với tổng user")


class DailyUsersStats(BaseModel):
    """
    Schema cho thống kê user theo ngày

    VÍ DỤ RESPONSE:
    {
        "date": "2024-01-01",
        "new_users": 50,
        "active_users": 500,
        "total_users": 5000
    }
    """
    date: str = Field(..., description="Ngày (YYYY-MM-DD)")
    new_users: int = Field(..., description="User đăng ký mới trong ngày")
    active_users: int = Field(..., description="User active trong ngày")
    total_users: int = Field(..., description="Tổng user tính đến ngày đó")


class OverallStats(BaseModel):
    """
    Schema cho tổng quan thống kê

    VÍ DỤ RESPONSE:
    {
        "total_users": 10000,
        "active_users": 8000,
        "inactive_users": 2000,
        "new_today": 50,
        "new_yesterday": 45,
        "new_last_7_days": 300,
        "total_countries": 25
    }
    """
    total_users: int = Field(..., description="Tổng số user")
    active_users: int = Field(..., description="User đang active")
    inactive_users: int = Field(..., description="User inactive")
    new_today: int = Field(..., description="User mới hôm nay")
    new_yesterday: int = Field(..., description="User mới hôm qua")
    new_last_7_days: int = Field(..., description="User mới 7 ngày qua")
    total_countries: int = Field(..., description="Số quốc gia")


class UserListFilter(BaseModel):
    """
    Schema cho filter parameters (dynamic filters)

    VÍ DỤ REQUEST:
    GET /api/v1/admin/reports/users?country=VN&is_active=true&days=7

    Tương tự GraphQL filtering
    """
    country: Optional[str] = Field(None, description="Filter theo quốc gia")
    is_active: Optional[bool] = Field(None, description="Filter theo trạng thái active")
    is_superuser: Optional[bool] = Field(None, description="Filter theo role admin")
    days: Optional[int] = Field(None, description="Filter user tạo trong N ngày gần đây")
    skip: int = Field(0, ge=0, description="Số record bỏ qua (pagination)")
    limit: int = Field(100, ge=1, le=1000, description="Số record tối đa")
