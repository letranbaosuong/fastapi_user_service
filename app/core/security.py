"""
Security Module - Authentication & Authorization

KHÁI NIỆM QUAN TRỌNG:
1. Password Hashing: Mã hóa password trước khi lưu DB (không lưu plain text)
2. JWT Token: Json Web Token để xác thực user mà không cần session
3. OAuth2: Flow chuẩn để authentication trong API
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password Hashing Context
# VÍ DỤ: "mypassword123" -> "$2b$12$KIXn8..."
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh plain password với hashed password

    VÍ DỤ:
    plain: "mypassword123"
    hashed: "$2b$12$KIXn8..."
    return: True nếu khớp
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password trước khi lưu vào database

    VÍ DỤ:
    Input: "mypassword123"
    Output: "$2b$12$KIXn8.../9xRLrQYXU2koOe"
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT Access Token

    KHÁI NIỆM JWT:
    - Header: Algorithm & Token Type
    - Payload: User data (subject, expiration)
    - Signature: Verify token không bị thay đổi

    VÍ DỤ:
    Input: {"sub": "user@example.com"}
    Output: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Token này client gửi trong header: Authorization: Bearer <token>
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode token với SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode và verify JWT token

    VÍ DỤ:
    Input: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    Output: "user@example.com" (email trong token)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None
