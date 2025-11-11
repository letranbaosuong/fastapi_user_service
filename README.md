# User Management Service - FastAPI + PostgreSQL

Đây là một **Backend Service hoàn chỉnh** để học FastAPI và PostgreSQL. Project bao gồm User Management, Authentication, và Activity Tracking với các use cases thực tế.

## 🎯 MỤC ĐÍCH HỌC TẬP

Project này giúp bạn nắm vững:

1. **FastAPI Framework**: REST API, Dependency Injection, Async/Await
2. **PostgreSQL**: Database design, relationships, queries
3. **Authentication**: JWT, OAuth2, Password hashing
4. **Clean Architecture**: Separation of concerns, maintainability
5. **Real-world Use Cases**: User management, Activity tracking, Analytics

---

## 📚 CÁC KHÁI NIỆM QUAN TRỌNG

### 1. Clean Architecture

```
app/
├── models/          # Database Models (ORM)
│   ├── user.py
│   └── user_activity.py
├── schemas/         # Pydantic Schemas (Validation)
│   ├── user.py
│   ├── user_activity.py
│   └── token.py
├── crud/            # Database Operations (CRUD)
│   ├── user.py
│   └── user_activity.py
├── api/
│   ├── endpoints/   # API Routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── activities.py
│   └── dependencies.py  # Dependency Injection
├── core/
│   ├── config.py    # Configuration
│   └── security.py  # Security utilities
└── db/
    └── session.py   # Database connection
```

**Tại sao phân chia như vậy?**
- **Models**: Định nghĩa cấu trúc database
- **Schemas**: Validate input/output data
- **CRUD**: Tách logic database ra khỏi API
- **API**: Chỉ xử lý HTTP requests/responses

### 2. FastAPI Core Concepts

#### a) Dependency Injection

```python
# Tự động inject database session
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Tự động check authentication
@app.get("/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Lợi ích:**
- Code sạch hơn
- Dễ test
- Tự động xử lý resources (close DB connection)

#### b) Pydantic Validation

```python
class UserCreate(BaseModel):
    email: EmailStr  # Tự động validate email format
    password: str = Field(min_length=8)  # Tối thiểu 8 ký tự

# FastAPI tự động reject request nếu invalid
```

#### c) Async/Await (Optional - nâng cao)

```python
# Synchronous (đơn giản)
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Asynchronous (hiệu năng cao hơn)
async def get_users(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(User))
```

### 3. Authentication Flow (JWT + OAuth2)

```
1. User gửi email/password
   POST /api/v1/auth/login
   {username: "user@example.com", password: "pass123"}

2. Server verify và tạo JWT token
   Response: {access_token: "eyJhbGci...", token_type: "bearer"}

3. Client lưu token và gửi trong mọi request
   Header: Authorization: Bearer eyJhbGci...

4. Server verify token mỗi request
   Depends(get_current_user) -> Tự động decode token
```

**JWT Token Structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  <- Header
eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0.  <- Payload (user data)
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV  <- Signature (verify)
```

### 4. Database Relationships

```python
# One-to-Many: 1 User có nhiều Activities
class User:
    activities = relationship("UserActivity", back_populates="user")

class UserActivity:
    user = relationship("User", back_populates="activities")

# Usage:
user = db.query(User).first()
user.activities  # List tất cả activities của user
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT

### 1. Cài đặt PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
- Download từ: https://www.postgresql.org/download/windows/

### 2. Tạo Database

```bash
# Login PostgreSQL
psql postgres

# Tạo database
CREATE DATABASE user_service_db;

# Tạo user (optional)
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO myuser;

# Exit
\q
```

### 3. Setup Python Environment

```bash
# Tạo virtual environment
python -m venv venv

# Activate
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copy .env.example thành .env
cp .env.example .env

# Chỉnh sửa .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/user_service_db
SECRET_KEY=your-secret-key-change-this
```

**Tạo SECRET_KEY mới:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Run Application

```bash
# Method 1: Uvicorn command
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Python script
python app/main.py
```

**Truy cập:**
- API: http://localhost:8000
- Swagger UI (Interactive docs): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📖 USE CASES THỰC TẾ

### Use Case 1: User Registration & Login

**Đăng ký user mới:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "password123",
    "bio": "Software Engineer"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=password123"

# Response: {"access_token": "eyJhbGci...", "token_type": "bearer"}
```

**Lấy thông tin user hiện tại:**
```bash
TOKEN="your-access-token"
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Use Case 2: Xem Users Đăng Ký Trong Ngày

**Endpoint:**
```
GET /api/v1/users/today
```

**Use case thực tế:**
- Admin dashboard hiển thị "New users today: 15"
- Daily report: Email summary hàng ngày
- Analytics: Track growth rate

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/today" \
  -H "Authorization: Bearer $TOKEN"
```

### Use Case 3: Xem Lịch Sử Hoạt Động User

**Endpoint:**
```
GET /api/v1/users/{user_id}/activities
GET /api/v1/users/{user_id}/activities/date/{date}
GET /api/v1/users/{user_id}/activities/stats/{date}
```

**Use case thực tế:**

1. **Audit Log**: Admin xem user đã làm gì
```bash
curl -X GET "http://localhost:8000/api/v1/users/1/activities" \
  -H "Authorization: Bearer $TOKEN"
```

2. **Daily Report**: Xem activities trong một ngày cụ thể
```bash
curl -X GET "http://localhost:8000/api/v1/users/1/activities/date/2024-01-01" \
  -H "Authorization: Bearer $TOKEN"
```

3. **Analytics Dashboard**: Thống kê activities breakdown
```bash
curl -X GET "http://localhost:8000/api/v1/users/1/activities/stats/2024-01-01" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "user_id": 1,
  "date": "2024-01-01",
  "total_activities": 25,
  "activity_breakdown": {
    "LOGIN": 3,
    "VIEW": 15,
    "UPDATE": 5,
    "DELETE": 2
  }
}
```

### Use Case 4: Track User Behavior

**Log activity:**
```bash
curl -X POST "http://localhost:8000/api/v1/users/1/activities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "VIEW",
    "description": "Viewed product page",
    "ip_address": "192.168.1.1"
  }'
```

**Recent activities (24 hours):**
```bash
curl -X GET "http://localhost:8000/api/v1/users/1/activities/recent?hours=24" \
  -H "Authorization: Bearer $TOKEN"
```

### Use Case 5: User Statistics

**Endpoint:**
```
GET /api/v1/users/{user_id}/statistics
```

**Response:**
```json
{
  "total_activities": 150,
  "activities_today": 5,
  "last_login": "2024-01-01T10:00:00",
  "account_age_days": 30
}
```

**Use case thực tế:**
- User dashboard
- Admin analytics
- Engagement metrics

---

## 🧪 TESTING VỚI SWAGGER UI

FastAPI tự động tạo interactive documentation tại `/docs`

**Cách dùng:**

1. Mở http://localhost:8000/docs
2. Click endpoint muốn test
3. Click "Try it out"
4. Nhập parameters
5. Click "Execute"

**Với authenticated endpoints:**

1. Register user tại `/api/v1/auth/register`
2. Login tại `/api/v1/auth/login` để lấy token
3. Click nút "Authorize" ở trên đầu
4. Nhập token (không cần "Bearer" prefix)
5. Bây giờ có thể test tất cả protected endpoints

---

## 💡 CÁC TÍNH NĂNG NÂNG CAO

### 1. Pagination

```python
@router.get("/users")
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud_user.get_multi(db, skip=skip, limit=limit)
```

**Usage:**
- Page 1: `?skip=0&limit=10`
- Page 2: `?skip=10&limit=10`

### 2. Query by Date Range

```python
@router.get("/users/date-range")
def get_users_by_range(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    ...
```

**Usage:**
```
?start_date=2024-01-01&end_date=2024-01-31
```

### 3. Authorization Levels

```python
# Public - Không cần login
@router.get("/public")
def public_endpoint():
    ...

# Authenticated - Cần login
@router.get("/protected")
def protected(current_user: User = Depends(get_current_user)):
    ...

# Admin only
@router.delete("/admin")
def admin_only(current_user: User = Depends(get_current_active_superuser)):
    ...
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. Password Hashing

```python
# ĐÚNG: Luôn hash password
hashed = get_password_hash("password123")
# => "$2b$12$KIXn8..."

# SAI: Không bao giờ lưu plain text password
user.password = "password123"  # ❌ KHÔNG!!!
```

### 2. JWT Secret Key

```bash
# Development: OK dùng key đơn giản
SECRET_KEY=dev-key

# Production: PHẢI dùng secure random key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 3. CORS Configuration

```python
# Development: Allow all
allow_origins=["*"]

# Production: Specific origins only
allow_origins=[
    "https://myapp.com",
    "https://admin.myapp.com"
]
```

---

## 📊 DATABASE SCHEMA

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    bio TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- User Activities Table
CREATE TABLE user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_activities_user_id ON user_activities(user_id);
CREATE INDEX idx_activities_created_at ON user_activities(created_at);
CREATE INDEX idx_activities_action_type ON user_activities(action_type);
```

---

## 🎓 BÀI TẬP MỞ RỘNG

### Cơ Bản

1. Thêm field `phone_number` vào User model
2. Thêm endpoint search users by name
3. Thêm endpoint change password

### Trung Bình

1. Implement refresh token (thay vì chỉ access token)
2. Thêm email verification khi register
3. Implement forgot password flow
4. Thêm avatar upload cho user

### Nâng Cao

1. Implement role-based access control (RBAC)
2. Thêm rate limiting (giới hạn số request)
3. Implement WebSocket cho real-time notifications
4. Thêm Redis cache cho performance
5. Docker deployment với docker-compose

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Database connection failed"

```bash
# Check PostgreSQL đang chạy
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Check connection string trong .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Lỗi: "Could not validate credentials"

- Check token có đúng format không: `Bearer <token>`
- Token có hết hạn chưa (default: 30 phút)
- Login lại để lấy token mới

### Lỗi: "Table does not exist"

```python
# Chạy lại để tạo tables
from app.db.session import engine, Base
from app.models import User, UserActivity

Base.metadata.create_all(bind=engine)
```

---

## 📝 NEXT STEPS

1. **Đọc code**: Bắt đầu từ `app/main.py`, follow flow
2. **Test API**: Dùng Swagger UI tại `/docs`
3. **Modify**: Thêm fields, endpoints mới
4. **Deploy**: Docker, AWS, Heroku, etc.

---

## 🔗 TÀI LIỆU THAM KHẢO

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JWT.io](https://jwt.io/) - Decode/verify JWT tokens
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 📧 CONTACT

Nếu có câu hỏi, tạo issue hoặc liên hệ!

Happy Learning! 🚀
