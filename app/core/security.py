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


def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """
    Truncate password để phù hợp với giới hạn của bcrypt (72 bytes)

    KHÁI NIỆM:
    - bcrypt có giới hạn 72 bytes cho password
    - Nếu password dài hơn, cần truncate để tránh ValueError

    VÍ DỤ:
    Input: "very_long_password_that_exceeds_72_bytes..." (100 bytes)
    Output: "very_long_password_that_exceeds_72_bytes..." (72 bytes)

    LƯU Ý:
    - Truncate theo bytes, không phải characters (vì UTF-8 multi-byte)
    - Đảm bảo không cắt giữa multi-byte character
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= max_bytes:
        return password

    # Truncate và decode, xử lý trường hợp cắt giữa multi-byte character
    truncated = password_bytes[:max_bytes]
    # Decode với errors='ignore' để bỏ qua byte cuối cùng nếu bị cắt giữa character
    return truncated.decode('utf-8', errors='ignore')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh plain password với hashed password

    VÍ DỤ:
    plain: "mypassword123"
    hashed: "$2b$12$KIXn8..."
    return: True nếu khớp

    LƯU Ý:
    - Tự động truncate password về 72 bytes (giới hạn của bcrypt)
    - Đảm bảo không bị ValueError khi password quá dài
    """
    # Truncate password trước khi verify
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password trước khi lưu vào database

    VÍ DỤ:
    Input: "mypassword123"
    Output: "$2b$12$KIXn8.../9xRLrQYXU2koOe"

    LƯU Ý:
    - Tự động truncate password về 72 bytes (giới hạn của bcrypt)
    - Đảm bảo không bị ValueError khi password quá dài
    """
    # Truncate password trước khi hash
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)


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
