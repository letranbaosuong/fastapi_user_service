"""
User Database Model

KHÁI NIỆM ORM:
- Class Python = Table trong Database
- Class attribute = Column trong Table
- Instance = Row trong Table

VÍ DỤ:
user = User(email="test@example.com", full_name="Test User")
=> INSERT INTO users (email, full_name) VALUES (...)
"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    """
    User Model - Bảng lưu thông tin user

    TABLE STRUCTURE:
    +----+------------------+-----------+----------+---------------------+
    | id | email            | full_name | is_active| created_at          |
    +----+------------------+-----------+----------+---------------------+
    | 1  | user@example.com | John Doe  | true     | 2024-01-01 10:00:00 |
    +----+------------------+-----------+----------+---------------------+
    """
    __tablename__ = "users"

    # Primary Key - Auto increment
    id = Column(Integer, primary_key=True, index=True)

    # Email - Unique constraint (không duplicate)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Full Name
    full_name = Column(String(255), nullable=False)

    # Hashed Password (KHÔNG lưu plain password)
    hashed_password = Column(String(255), nullable=False)

    # Active Status
    is_active = Column(Boolean, default=True)

    # Role-based access control
    is_superuser = Column(Boolean, default=False)

    # Timestamps - Tự động set thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Bio/Description (optional)
    bio = Column(Text, nullable=True)

    # Country code (ISO 3166-1 alpha-2: VN, US, JP, etc.)
    country = Column(String(2), nullable=True, index=True)

    # RELATIONSHIP: One-to-Many với UserActivity
    # VÍ DỤ: user.activities sẽ trả về list các activity của user này
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
