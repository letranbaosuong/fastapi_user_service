"""
User Activity Pydantic Schemas

USE CASES:
1. Log mọi action của user
2. Audit trail cho security
3. Analytics behavior
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserActivityBase(BaseModel):
    """
    Base Activity Schema
    """
    action_type: str = Field(..., description="Loại action: LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW")
    description: Optional[str] = Field(None, description="Mô tả chi tiết action")
    ip_address: Optional[str] = Field(None, description="IP address của user")
    user_agent: Optional[str] = Field(None, description="Browser/Device info")


class UserActivityCreate(UserActivityBase):
    """
    Schema tạo Activity

    VÍ DỤ:
    {
        "action_type": "LOGIN",
        "description": "User logged in successfully",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
    """
    pass


class UserActivity(UserActivityBase):
    """
    Schema Activity Response

    VÍ DỤ RESPONSE:
    GET /api/v1/users/1/activities
    [
        {
            "id": 1,
            "user_id": 1,
            "action_type": "LOGIN",
            "description": "User logged in",
            "ip_address": "192.168.1.1",
            "created_at": "2024-01-01T10:00:00"
        },
        {
            "id": 2,
            "user_id": 1,
            "action_type": "UPDATE",
            "description": "Updated profile",
            "ip_address": "192.168.1.1",
            "created_at": "2024-01-01T10:15:00"
        }
    ]
    """
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserActivityStats(BaseModel):
    """
    Schema cho Activity Statistics

    VÍ DỤ USE CASE:
    GET /api/v1/users/1/activity-stats?date=2024-01-01

    RESPONSE:
    {
        "user_id": 1,
        "date": "2024-01-01",
        "total_activities": 10,
        "activity_breakdown": {
            "LOGIN": 2,
            "VIEW": 5,
            "UPDATE": 3
        }
    }
    """
    user_id: int
    date: datetime
    total_activities: int
    activity_breakdown: dict[str, int] = Field(..., description="Breakdown by action type")
