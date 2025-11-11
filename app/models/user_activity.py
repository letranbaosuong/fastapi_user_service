"""
User Activity Model - Track lịch sử hoạt động

USE CASE THỰC TẾ:
- Audit log: Ai đã làm gì, khi nào
- Analytics: Thống kê user behavior
- Security: Phát hiện hoạt động bất thường
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class UserActivity(Base):
    """
    User Activity Model - Bảng lưu lịch sử hoạt động

    VÍ DỤ DATA:
    +----+---------+-------------+---------------------------+---------------------+
    | id | user_id | action_type | description               | created_at          |
    +----+---------+-------------+---------------------------+---------------------+
    | 1  | 1       | LOGIN       | User logged in            | 2024-01-01 10:00:00 |
    | 2  | 1       | UPDATE      | Updated profile           | 2024-01-01 10:15:00 |
    | 3  | 1       | VIEW        | Viewed user list          | 2024-01-01 10:30:00 |
    +----+---------+-------------+---------------------------+---------------------+

    USE CASES:
    1. Xem user đã làm gì trong ngày
    2. Audit trail cho security
    3. Analytics behavior
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key tới User table
    # VÍ DỤ: user_id=1 => activity này của user có id=1
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Action Type: LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW
    action_type = Column(String(50), nullable=False, index=True)

    # Mô tả chi tiết action
    description = Column(Text, nullable=True)

    # IP Address của user (optional - for security)
    ip_address = Column(String(45), nullable=True)

    # User Agent (Browser/Device info)
    user_agent = Column(String(255), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # RELATIONSHIP: Many-to-One với User
    # VÍ DỤ: activity.user sẽ trả về User object
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action={self.action_type})>"
