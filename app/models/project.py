"""
Project Model - Quản lý dự án

KHÁI NIỆM MANY-TO-MANY:
- 1 User có thể tham gia nhiều Projects
- 1 Project có thể có nhiều Users (members)
- Cần association table (user_projects) để liên kết

USE CASE THỰC TẾ:
- Project management: Quản lý dự án, team members
- Collaboration: Nhiều users cùng làm việc trên 1 project
- Access control: Chỉ members mới được access project

VÍ DỤ:
- Project "Website Redesign" có members: John, Alice, Bob
- User John tham gia projects: "Website Redesign", "Mobile App", "API Gateway"
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


# ASSOCIATION TABLE cho Many-to-Many relationship
# VÍ DỤ DATA:
# +----+---------+------------+-------------------+---------------------+
# | id | user_id | project_id | role              | joined_at           |
# +----+---------+------------+-------------------+---------------------+
# | 1  | 1       | 1          | owner             | 2024-01-01 10:00:00 |
# | 2  | 2       | 1          | member            | 2024-01-01 11:00:00 |
# | 3  | 1       | 2          | member            | 2024-01-02 09:00:00 |
# +----+---------+------------+-------------------+---------------------+
#
# USE CASE:
# - Row 1: User #1 là owner của Project #1
# - Row 2: User #2 là member của Project #1
# - Row 3: User #1 là member của Project #2
user_projects = Table(
    "user_projects",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
    Column("role", String(50), default="member", nullable=False),  # owner, admin, member
    Column("joined_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


class Project(Base):
    """
    Project Model - Bảng lưu thông tin dự án

    TABLE STRUCTURE:
    +----+------------------+---------------------------+----------+---------------------+
    | id | name             | description               | is_active| created_at          |
    +----+------------------+---------------------------+----------+---------------------+
    | 1  | Website Redesign | Redesign company website  | true     | 2024-01-01 10:00:00 |
    | 2  | Mobile App       | iOS and Android app       | true     | 2024-01-02 09:00:00 |
    +----+------------------+---------------------------+----------+---------------------+

    MANY-TO-MANY RELATIONSHIP:
    - project.members => List[User] - Tất cả users trong project
    - user.projects => List[Project] - Tất cả projects của user
    """
    __tablename__ = "projects"

    # Primary Key - Auto increment
    id = Column(Integer, primary_key=True, index=True)

    # Project Name
    name = Column(String(255), nullable=False, index=True)

    # Project Description
    description = Column(Text, nullable=True)

    # Active Status - Project có đang active không
    is_active = Column(Boolean, default=True)

    # Project Status: planning, in_progress, completed, on_hold, cancelled
    status = Column(String(50), default="planning", nullable=False, index=True)

    # Start Date
    start_date = Column(DateTime(timezone=True), nullable=True)

    # End Date
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # RELATIONSHIP: Many-to-Many với User thông qua user_projects table
    # VÍ DỤ:
    # - project.members sẽ trả về list các User trong project này
    # - user.projects sẽ trả về list các Project mà user tham gia
    members = relationship(
        "User",
        secondary=user_projects,
        back_populates="projects"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
