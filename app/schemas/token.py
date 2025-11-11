"""
Authentication Token Schemas

KHÁI NIỆM OAuth2 Flow:
1. Client gửi username/password
2. Server trả về access_token
3. Client gửi token trong header cho mọi request tiếp theo
4. Server verify token và authorize
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Token Response Schema

    VÍ DỤ:
    POST /api/v1/auth/login
    Request: {"username": "user@example.com", "password": "pass123"}

    Response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }

    Client sau đó dùng token này:
    Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Token Payload Schema

    KHÁI NIỆM: Data được encode trong JWT token

    VÍ DỤ Decoded Token:
    {
        "sub": "user@example.com",  # subject = user identifier
        "exp": 1704067200            # expiration timestamp
    }
    """
    sub: Optional[str] = None  # subject: user email
    exp: Optional[int] = None  # expiration time
