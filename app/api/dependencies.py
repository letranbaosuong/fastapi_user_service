"""
API Dependencies - Dependency Injection

KHÁI NIỆM DEPENDENCY INJECTION:
FastAPI tự động gọi các function này và inject kết quả vào route handlers

VÍ DỤ:
@app.get("/users/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    # current_user đã được inject tự động
    return current_user
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.crud import user as crud_user
from app.models.user import User

# OAuth2 scheme
# VÍ DỤ: Client gửi token trong header: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user từ token

    WORKFLOW:
    1. Lấy token từ Authorization header
    2. Decode token để lấy email
    3. Query user từ database
    4. Return user

    VÍ DỤ:
    @app.get("/users/me")
    def read_current_user(current_user: User = Depends(get_current_user)):
        return current_user

    SECURITY:
    - Nếu token invalid => Raise 401 Unauthorized
    - Nếu user không tồn tại => Raise 404 Not Found
    - Nếu user inactive => Raise 400 Bad Request
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # Get user from DB
    user = crud_user.get_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user

    VÍ DỤ USE CASE:
    - Endpoints chỉ cho phép user active
    - Đã check is_active trong get_current_user rồi, giữ lại để tường minh
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active superuser (admin)

    VÍ DỤ USE CASE:
    - Admin-only endpoints
    - Delete user, view all users, etc.

    VÍ DỤ:
    @app.delete("/users/{user_id}")
    def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_active_superuser)
    ):
        # Chỉ admin mới được xóa user
        ...
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user
