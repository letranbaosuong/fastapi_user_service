"""
Project Pydantic Schemas - Data Validation

KHÁI NIỆM PYDANTIC:
- Validate dữ liệu input từ client
- Serialize dữ liệu output trả về client
- Type hints + auto validation

VÍ DỤ:
Client gửi: {"name": ""}
=> Pydantic tự động reject với error: "Name cannot be empty"
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    """
    Base schema - Shared fields giữa các schemas
    """
    name: str = Field(..., min_length=1, max_length=255, description="Tên dự án")
    description: Optional[str] = Field(None, description="Mô tả chi tiết dự án")
    status: Optional[str] = Field("planning", description="Trạng thái: planning, in_progress, completed, on_hold, cancelled")
    is_active: Optional[bool] = Field(True, description="Project có đang active không")
    start_date: Optional[datetime] = Field(None, description="Ngày bắt đầu dự án")
    end_date: Optional[datetime] = Field(None, description="Ngày kết thúc dự án")


class ProjectCreate(ProjectBase):
    """
    Schema cho Create Project Request

    VÍ DỤ REQUEST:
    POST /api/v1/projects
    {
        "name": "Website Redesign",
        "description": "Redesign company website with modern UI",
        "status": "planning",
        "start_date": "2024-01-01T00:00:00Z"
    }

    VALIDATION TỰ ĐỘNG:
    - name không được rỗng
    - status phải là 1 trong các giá trị hợp lệ
    """
    pass


class ProjectUpdate(BaseModel):
    """
    Schema cho Update Project Request

    VÍ DỤ REQUEST:
    PUT /api/v1/projects/1
    {
        "name": "Website Redesign v2",
        "status": "in_progress",
        "is_active": true
    }

    LƯU Ý: Tất cả fields đều optional (partial update)
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectMemberAdd(BaseModel):
    """
    Schema cho Add Member to Project

    VÍ DỤ REQUEST:
    POST /api/v1/projects/1/members
    {
        "user_id": 2,
        "role": "member"
    }
    """
    user_id: int = Field(..., description="ID của user cần thêm vào project")
    role: str = Field("member", description="Role: owner, admin, member")


class ProjectMemberRemove(BaseModel):
    """
    Schema cho Remove Member from Project

    VÍ DỤ REQUEST:
    DELETE /api/v1/projects/1/members
    {
        "user_id": 2
    }
    """
    user_id: int = Field(..., description="ID của user cần xóa khỏi project")


# Schema cho response - chỉ basic info của User
class UserBasicInfo(BaseModel):
    """
    Basic User info cho Project response
    Tránh circular dependency và reduce response size
    """
    id: int
    email: str
    full_name: str
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectInDBBase(ProjectBase):
    """
    Base schema cho Project từ Database

    KHÁI NIỆM: Kế thừa ProjectBase + thêm fields từ DB
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Project(ProjectInDBBase):
    """
    Schema cho Project Response (không include members list)

    VÍ DỤ RESPONSE:
    {
        "id": 1,
        "name": "Website Redesign",
        "description": "Redesign company website",
        "status": "in_progress",
        "is_active": true,
        "start_date": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T10:00:00Z"
    }

    USE CASE: List projects, get project info
    """
    pass


class ProjectWithMembers(ProjectInDBBase):
    """
    Schema cho Project Response WITH members list

    VÍ DỤ RESPONSE:
    {
        "id": 1,
        "name": "Website Redesign",
        "description": "Redesign company website",
        "status": "in_progress",
        "members": [
            {"id": 1, "email": "john@example.com", "full_name": "John Doe"},
            {"id": 2, "email": "alice@example.com", "full_name": "Alice Smith"}
        ]
    }

    USE CASE: Get project details với danh sách members
    """
    members: List[UserBasicInfo] = []
