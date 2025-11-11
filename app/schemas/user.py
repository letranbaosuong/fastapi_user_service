"""
User Pydantic Schemas - Data Validation

KHÁI NIỆM PYDANTIC:
- Validate dữ liệu input từ client
- Serialize dữ liệu output trả về client
- Type hints + auto validation

VÍ DỤ:
Client gửi: {"email": "invalid-email"}
=> Pydantic tự động reject với error: "Invalid email format"
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base schema - Shared fields giữa các schemas
    """
    email: EmailStr = Field(..., description="Email address của user")
    full_name: str = Field(..., min_length=1, max_length=255, description="Họ tên đầy đủ")
    bio: Optional[str] = Field(None, description="Tiểu sử/Mô tả")
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="Mã quốc gia (VN, US, JP, ...)")


class UserCreate(UserBase):
    """
    Schema cho Create User Request

    VÍ DỤ REQUEST:
    POST /api/v1/users
    {
        "email": "newuser@example.com",
        "full_name": "Nguyễn Văn A",
        "password": "securepassword123",
        "bio": "Software Engineer"
    }

    VALIDATION TỰ ĐỘNG:
    - email phải đúng format (có @, domain hợp lệ)
    - full_name không được rỗng
    - password tối thiểu 8 ký tự
    """
    password: str = Field(..., min_length=8, description="Mật khẩu (tối thiểu 8 ký tự)")


class UserUpdate(BaseModel):
    """
    Schema cho Update User Request

    VÍ DỤ REQUEST:
    PUT /api/v1/users/1
    {
        "full_name": "Nguyễn Văn B",
        "bio": "Senior Engineer",
        "country": "VN"
    }

    LƯU Ý: Tất cả fields đều optional (partial update)
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = None
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """
    Base schema cho User từ Database

    KHÁI NIỆM: Kế thừa UserBase + thêm fields từ DB
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """
    Schema cho User Response (trả về client)

    VÍ DỤ RESPONSE:
    GET /api/v1/users/1
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Nguyễn Văn A",
        "bio": "Software Engineer",
        "is_active": true,
        "is_superuser": false,
        "created_at": "2024-01-01T10:00:00",
        "updated_at": null
    }

    LƯU Ý: KHÔNG trả về hashed_password (security)
    """
    pass


class UserInDB(UserInDBBase):
    """
    Schema cho User trong Database (internal use)

    KHÁC BIỆT với User schema:
    - Có hashed_password (để verify login)
    - Chỉ dùng internal, KHÔNG trả về client
    """
    hashed_password: str
