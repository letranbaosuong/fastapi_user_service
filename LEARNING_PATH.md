# 🎓 LỘ TRÌNH HỌC FASTAPI + POSTGRESQL

Hướng dẫn từng bước để hiểu sâu project này.

---

## 📍 GIAI ĐOẠN 1: HIỂU CƠ BẢN (Ngày 1-2)

### 1.1 Hiểu Cấu Trúc Project

**Bắt đầu đọc theo thứ tự:**

1. **`app/core/config.py`**: Configuration
   - Pydantic Settings
   - Environment variables
   - Centralized config

2. **`app/db/session.py`**: Database connection
   - SQLAlchemy Engine
   - SessionLocal factory
   - Dependency injection

3. **`app/models/user.py`**: Database Model
   - ORM concepts
   - Table definition
   - Relationships

### 1.2 Thực Hành Cơ Bản

**Bài tập 1: Setup và chạy project**

```bash
# 1. Setup database
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
uvicorn app.main:app --reload

# 4. Mở Swagger UI
# http://localhost:8000/docs
```

**Bài tập 2: Test API với Swagger**

1. Register user mới
2. Login để lấy token
3. Authorize với token
4. Test các endpoints khác

### 1.3 Câu Hỏi Tự Kiểm Tra

- [ ] FastAPI tự động generate documentation như thế nào?
- [ ] Pydantic validation hoạt động ra sao?
- [ ] SQLAlchemy ORM là gì?
- [ ] Database session được tạo và đóng khi nào?

---

## 📍 GIAI ĐOẠN 2: AUTHENTICATION (Ngày 3-4)

### 2.1 Hiểu JWT Authentication

**Đọc files theo thứ tự:**

1. **`app/core/security.py`**
   - Password hashing (bcrypt)
   - JWT token creation
   - Token verification

2. **`app/api/dependencies.py`**
   - OAuth2 scheme
   - get_current_user dependency
   - Authorization levels

3. **`app/api/endpoints/auth.py`**
   - Register endpoint
   - Login flow
   - Token usage

### 2.2 Thực Hành

**Bài tập 3: Hiểu JWT Token**

```python
# Tạo một script test_jwt.py
from app.core.security import create_access_token, decode_access_token
from datetime import timedelta

# Tạo token
token = create_access_token({"sub": "test@example.com"}, timedelta(minutes=30))
print(f"Token: {token}")

# Decode token
email = decode_access_token(token)
print(f"Email: {email}")

# Đi tới jwt.io và paste token để xem payload
```

**Bài tập 4: Test Authentication Flow**

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "full_name": "Test User", "password": "password123"}'

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Save token từ response

# 3. Access protected endpoint
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2.3 Câu Hỏi Tự Kiểm Tra

- [ ] JWT token gồm những phần nào?
- [ ] Tại sao cần hash password?
- [ ] OAuth2PasswordBearer làm gì?
- [ ] Dependency Injection trong FastAPI hoạt động như thế nào?
- [ ] Token được verify ở đâu trong flow?

---

## 📍 GIAI ĐOẠN 3: CRUD OPERATIONS (Ngày 5-6)

### 3.1 Hiểu CRUD Pattern

**Đọc files:**

1. **`app/crud/user.py`**
   - Create, Read, Update, Delete operations
   - Query filters
   - Statistics functions

2. **`app/api/endpoints/users.py`**
   - API routes
   - Request/Response handling
   - Authorization checks

### 3.2 Thực Hành

**Bài tập 5: Implement Custom CRUD Function**

Thêm function mới vào `app/crud/user.py`:

```python
def search_users_by_name(
    db: Session,
    name: str,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Search users by full name (case insensitive)
    """
    return db.query(User).filter(
        User.full_name.ilike(f"%{name}%")
    ).offset(skip).limit(limit).all()
```

Thêm endpoint tương ứng vào `app/api/endpoints/users.py`:

```python
@router.get("/search", response_model=List[User])
def search_users(
    name: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Search users by name"""
    from app.crud import user as crud_user
    return crud_user.search_users_by_name(db, name, skip, limit)
```

Test endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/users/search?name=John" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Bài tập 6: Implement Pagination**

Test pagination với các queries khác nhau:

```bash
# Page 1
curl "http://localhost:8000/api/v1/users?skip=0&limit=5"

# Page 2
curl "http://localhost:8000/api/v1/users?skip=5&limit=5"

# Page 3
curl "http://localhost:8000/api/v1/users?skip=10&limit=5"
```

### 3.3 Câu Hỏi Tự Kiểm Tra

- [ ] Tại sao tách CRUD logic ra khỏi API routes?
- [ ] Pagination hoạt động như thế nào?
- [ ] Query filters (filter, ilike, offset, limit) là gì?
- [ ] Authorization checks được thực hiện ở đâu?

---

## 📍 GIAI ĐOẠN 4: ACTIVITY TRACKING (Ngày 7-8)

### 4.1 Hiểu Relationship

**Đọc files:**

1. **`app/models/user_activity.py`**
   - Foreign key
   - Many-to-One relationship
   - Cascade delete

2. **`app/crud/user_activity.py`**
   - Activity logging
   - Date-based queries
   - Statistics

### 4.2 Thực Hành

**Bài tập 7: Log Activities**

Tạo script để auto-generate activities:

```python
# generate_activities.py
import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register và login để lấy token
# ...

# 2. Generate random activities
action_types = ["LOGIN", "VIEW", "UPDATE", "CREATE", "DELETE"]

for i in range(50):
    activity = {
        "action_type": random.choice(action_types),
        "description": f"Test activity {i}",
        "ip_address": f"192.168.1.{random.randint(1, 255)}"
    }

    response = requests.post(
        f"{BASE_URL}/users/1/activities",
        json=activity,
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Created activity {i}: {response.status_code}")
```

**Bài tập 8: Query Activities**

```bash
# 1. Tất cả activities
curl "http://localhost:8000/api/v1/users/1/activities" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Activities trong ngày
curl "http://localhost:8000/api/v1/users/1/activities/date/2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Statistics
curl "http://localhost:8000/api/v1/users/1/activities/stats/2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. By action type
curl "http://localhost:8000/api/v1/users/1/activities/type/LOGIN" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4.3 Câu Hỏi Tự Kiểm Tra

- [ ] Foreign key constraint là gì?
- [ ] Cascade delete hoạt động như thế nào?
- [ ] relationship() trong SQLAlchemy làm gì?
- [ ] Làm thế nào để query data theo date range?

---

## 📍 GIAI ĐOẠN 5: NÂNG CAO (Ngày 9-14)

### 5.1 Bài Tập Mở Rộng

#### Bài tập 9: Thêm Phone Number Field

**Yêu cầu:**
1. Thêm `phone_number` field vào User model
2. Update schema (UserCreate, UserUpdate, User)
3. Thêm validation (format số điện thoại)
4. Test API

**Hướng dẫn:**

```python
# 1. app/models/user.py
phone_number = Column(String(20), nullable=True, unique=True)

# 2. app/schemas/user.py
from pydantic import validator

phone_number: Optional[str] = None

@validator('phone_number')
def validate_phone(cls, v):
    if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
        raise ValueError('Invalid phone number')
    return v

# 3. Recreate database hoặc migration
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

#### Bài tập 10: Change Password Endpoint

**Yêu cầu:**
Implement endpoint để user đổi password

**Endpoint design:**
```
POST /api/v1/users/me/change-password
Body: {
  "current_password": "old_pass",
  "new_password": "new_pass"
}
```

**Implementation:**

```python
# app/schemas/user.py
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# app/api/endpoints/users.py
@router.post("/me/change-password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 1. Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Incorrect current password")

    # 2. Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
```

#### Bài tập 11: Email Verification

**Yêu cầu:**
Implement email verification flow khi register

**Flow:**
1. User register
2. Tạo verification token
3. Gửi email với link verification
4. User click link để verify
5. Update `is_active = True`

**Hint:**
- Thêm field `email_verified: bool`
- Thêm table `verification_tokens`
- Sử dụng library như `fastapi-mail`

#### Bài tập 12: Role-Based Access Control (RBAC)

**Yêu cầu:**
Implement system với nhiều roles

**Design:**

```python
# Models
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)  # "admin", "user", "moderator"

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

# Dependency
def require_role(role_name: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if not any(r.name == role_name for r in current_user.roles):
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return role_checker

# Usage
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin"))
):
    ...
```

---

## 📍 GIAI ĐOẠN 6: PRODUCTION READY (Ngày 15-21)

### 6.1 Database Migration với Alembic

**Setup:**

```bash
# Install alembic
pip install alembic

# Initialize
alembic init alembic

# Configure alembic.ini
# sqlalchemy.url = postgresql://...

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 6.2 Testing

```bash
pip install pytest httpx

# Create tests/test_users.py
# pytest
```

### 6.3 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.4 Environment-Specific Config

```python
# app/core/config.py
class Settings(BaseSettings):
    ENVIRONMENT: str = "development"  # development, staging, production

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
```

---

## 🎯 CHECKLIST HOÀN THÀNH

### Backend Fundamentals
- [ ] Hiểu REST API design
- [ ] Hiểu HTTP methods (GET, POST, PUT, DELETE)
- [ ] Hiểu status codes (200, 201, 400, 401, 403, 404, 500)
- [ ] Hiểu request/response cycle

### FastAPI
- [ ] Dependency Injection
- [ ] Pydantic validation
- [ ] Path/Query parameters
- [ ] Request body
- [ ] Response models
- [ ] Error handling
- [ ] Middleware

### Database
- [ ] SQL basics (SELECT, INSERT, UPDATE, DELETE)
- [ ] SQLAlchemy ORM
- [ ] Relationships (One-to-Many, Many-to-Many)
- [ ] Migrations
- [ ] Indexes
- [ ] Transactions

### Authentication
- [ ] Password hashing
- [ ] JWT tokens
- [ ] OAuth2 flow
- [ ] Authorization vs Authentication
- [ ] Role-based access

### Best Practices
- [ ] Clean architecture
- [ ] Error handling
- [ ] Input validation
- [ ] Security (CORS, SQL injection, XSS)
- [ ] Testing
- [ ] Documentation

---

## 📚 TÀI LIỆU BỔ SUNG

### Videos
- [FastAPI Full Course - FreeCodeCamp](https://www.youtube.com/watch?v=0sOvCWFmrtA)
- [SQLAlchemy Tutorial](https://www.youtube.com/watch?v=AKQ3XEDI9Mw)

### Books
- "FastAPI Web Development" by Bill Lubanovic
- "Learning SQL" by Alan Beaulieu

### Practice Projects
1. Blog API với comments
2. E-commerce API với products, orders
3. Social Media API với posts, likes, follows
4. Task Management API với projects, tasks

---

## 💪 THÁCH THỨC

**Challenge: Build a Complete Feature**

Implement một feature hoàn chỉnh từ đầu đến cuối:

**Feature: Post Management System**

Requirements:
1. Users có thể tạo posts
2. Posts có title, content, tags
3. Users có thể like posts
4. Users có thể comment trên posts
5. Pagination cho posts list
6. Search posts by title/content/tags
7. Activity tracking cho post actions

Design và implement:
- Models
- Schemas
- CRUD operations
- API endpoints
- Authorization
- Tests

---

Chúc bạn học tốt! Nếu gặp khó khăn, đừng ngần ngại tìm hiểu thêm hoặc hỏi! 🚀
