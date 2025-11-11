"""
Authentication Endpoints

USE CASES:
- User login
- Register new user
- Get current user info
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.crud import user as crud_user
from app.schemas.user import User, UserCreate
from app.schemas.token import Token
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user

    VÍ DỤ REQUEST:
    POST /api/v1/auth/register
    {
        "email": "newuser@example.com",
        "full_name": "Nguyễn Văn A",
        "password": "password123",
        "bio": "Software Engineer"
    }

    RESPONSE: User object (không có password)

    VALIDATION TỰ ĐỘNG:
    - Email phải đúng format
    - Password tối thiểu 8 ký tự
    - Email không được trùng
    """
    # Check email đã tồn tại chưa
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login endpoint - OAuth2 compatible

    VÍ DỤ REQUEST:
    POST /api/v1/auth/login
    Form Data:
    - username: user@example.com (OAuth2 dùng 'username' nhưng ta dùng email)
    - password: password123

    RESPONSE:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }

    WORKFLOW:
    1. Authenticate user (check email/password)
    2. Create JWT access token
    3. Return token
    """
    # Authenticate
    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user info

    VÍ DỤ REQUEST:
    GET /api/v1/auth/me
    Headers:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    RESPONSE: Current user info

    USE CASE:
    - Frontend lấy thông tin user hiện tại
    - Profile page
    - Check authentication status
    """
    return current_user


@router.post("/test-token", response_model=User)
def test_token(current_user: User = Depends(get_current_user)):
    """
    Test access token

    VÍ DỤ USE CASE:
    - Debug token
    - Verify token còn valid không

    REQUEST:
    POST /api/v1/auth/test-token
    Headers:
    Authorization: Bearer <token>

    RESPONSE: User info nếu token valid
    """
    return current_user
