"""
Models Package

Import tất cả models ở đây để dễ dàng import
VÍ DỤ: from app.models import User, UserActivity
"""

from app.models.user import User
from app.models.user_activity import UserActivity

__all__ = ["User", "UserActivity"]
