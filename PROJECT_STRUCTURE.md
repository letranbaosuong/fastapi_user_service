# 📁 CẤU TRÚC PROJECT

Chi tiết về từng file và folder trong project.

---

## 🏗️ TỔNG QUAN

```
fastapi_user_service/
├── app/                    # Main application code
│   ├── api/               # API layer (routes, endpoints)
│   ├── core/              # Core functionality (config, security)
│   ├── crud/              # Database operations
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models (database tables)
│   ├── schemas/           # Pydantic schemas (validation)
│   └── main.py            # Application entry point
├── tests/                 # Test files (TODO)
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Docker setup for PostgreSQL
├── requirements.txt      # Python dependencies
├── test_api.py          # API testing script
├── README.md            # Main documentation
├── QUICKSTART.md        # Quick setup guide
├── LEARNING_PATH.md     # Learning roadmap
└── PROJECT_STRUCTURE.md # This file
```

---

## 📂 CHI TIẾT TỪNG FOLDER

### 1. `app/` - Main Application

#### 1.1 `app/main.py` ⭐ Entry Point
```python
# FastAPI application instance
# CORS middleware
# Include routers
# Health check endpoint
```

**Vai trò:**
- Tạo FastAPI app
- Configure middleware (CORS)
- Register routes
- Entry point để run server

**Quan hệ:**
```
main.py → api.py → endpoints/*.py
```

---

#### 1.2 `app/core/` - Core Functionality

##### `config.py`
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ...
```

**Vai trò:**
- Centralized configuration
- Load từ .env file
- Type validation với Pydantic

**Dùng ở đâu:** Toàn bộ app import `settings`

##### `security.py`
```python
def get_password_hash(password: str) -> str
def verify_password(plain_password: str, hashed_password: str) -> bool
def create_access_token(data: dict) -> str
def decode_access_token(token: str) -> Optional[str]
```

**Vai trò:**
- Password hashing (bcrypt)
- JWT token creation & verification
- Security utilities

**Dùng ở đâu:**
- `crud/user.py` - hash password khi create user
- `api/endpoints/auth.py` - create token khi login
- `api/dependencies.py` - verify token

---

#### 1.3 `app/db/` - Database

##### `session.py`
```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(...)
Base = declarative_base()

def get_db():
    # Dependency injection
```

**Vai trò:**
- Database connection
- Session factory
- Base class cho models

**Flow:**
```
Request → get_db() → yield session → route handler sử dụng → close session
```

---

#### 1.4 `app/models/` - Database Models (ORM)

##### `user.py`
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    ...
```

**Vai trò:**
- Define database table structure
- ORM mapping (Python class ↔ Database table)

**SQL Equivalent:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    ...
);
```

##### `user_activity.py`
```python
class UserActivity(Base):
    __tablename__ = "user_activities"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ...
```

**Relationship:**
```
User (1) ----< UserActivity (Many)
One user has many activities
```

---

#### 1.5 `app/schemas/` - Pydantic Schemas (Validation)

##### `user.py`
```python
class UserCreate(BaseModel):
    email: EmailStr  # Auto validate email
    password: str = Field(min_length=8)

class User(BaseModel):
    id: int
    email: EmailStr
    ...
```

**Vai trò:**
- Input validation (request body)
- Output serialization (response)
- Type checking

**Flow:**
```
Request JSON → Pydantic validates → Python object → Route handler
Route handler → Pydantic serializes → Response JSON
```

**Khác biệt Models vs Schemas:**
| Models (ORM) | Schemas (Pydantic) |
|--------------|-------------------|
| Database structure | Request/Response structure |
| SQLAlchemy | Pydantic |
| `app/models/` | `app/schemas/` |
| Include hashed_password | Không expose password |

---

#### 1.6 `app/crud/` - Database Operations

##### `user.py`
```python
def get_by_email(db: Session, email: str) -> Optional[User]
def create(db: Session, obj_in: UserCreate) -> User
def update(db: Session, db_obj: User, obj_in: UserUpdate) -> User
def delete(db: Session, user_id: int) -> Optional[User]
```

**Vai trò:**
- Encapsulate database queries
- Reusable database operations
- Separation of concerns

**Tại sao tách ra:**
```python
# ❌ BAD: Query trực tiếp trong endpoint
@router.get("/users")
def get_users(db: Session):
    return db.query(User).all()

# ✅ GOOD: Sử dụng CRUD function
@router.get("/users")
def get_users(db: Session):
    return crud_user.get_multi(db)
```

**Lợi ích:**
- Dễ test
- Reusable
- Maintain queries ở một chỗ

---

#### 1.7 `app/api/` - API Layer

##### `api.py`
```python
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
```

**Vai trò:**
- Tổng hợp tất cả routers
- Organize endpoints

**URL Structure:**
```
/api/v1/auth/login       ← auth.router
/api/v1/users            ← users.router
/api/v1/users/1/activities ← activities.router
```

##### `dependencies.py`
```python
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # Decode token
    # Get user from DB
    # Return user
```

**Vai trò:**
- Dependency injection functions
- Authentication & authorization

**Usage:**
```python
@router.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user)
):
    # current_user tự động được inject
    return current_user
```

---

#### 1.8 `app/api/endpoints/` - API Endpoints

##### `auth.py`
```python
@router.post("/register")
@router.post("/login")
@router.get("/me")
```

**Endpoints:**
- `POST /api/v1/auth/register` - Đăng ký
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Current user info

##### `users.py`
```python
@router.get("/")               # List users
@router.get("/today")          # Users today
@router.get("/{user_id}")      # Get by ID
@router.put("/{user_id}")      # Update
@router.delete("/{user_id}")   # Delete
```

**Authorization:**
- All endpoints require authentication
- DELETE requires admin (superuser)

##### `activities.py`
```python
@router.post("/{user_id}/activities")
@router.get("/{user_id}/activities")
@router.get("/{user_id}/activities/date/{date}")
@router.get("/{user_id}/activities/stats/{date}")
```

**Features:**
- Log activities
- View history
- Filter by date
- Statistics

---

## 🔄 REQUEST FLOW

### Ví dụ: Get Current User

```
1. Client Request
   GET /api/v1/auth/me
   Header: Authorization: Bearer eyJhbGci...

2. FastAPI receives request
   ↓
3. Route matching
   api/endpoints/auth.py → @router.get("/me")
   ↓
4. Dependency Injection
   get_current_user(token)
   ↓
5. dependencies.py
   - oauth2_scheme extracts token
   - decode_access_token(token) → email
   - crud_user.get_by_email(db, email) → user
   ↓
6. Route Handler
   def read_current_user(current_user: User):
       return current_user
   ↓
7. Pydantic Serialization
   User model → JSON
   ↓
8. Response
   {
     "id": 1,
     "email": "user@example.com",
     ...
   }
```

---

## 📊 DATA FLOW

### Ví dụ: Create User

```
Request JSON
    ↓
Pydantic Schema (UserCreate)
    ↓ validation
CRUD function (crud_user.create)
    ↓
SQLAlchemy Model (User)
    ↓
Database (INSERT)
    ↓
SQLAlchemy Model (with ID)
    ↓
Pydantic Schema (User)
    ↓ serialization
Response JSON
```

---

## 🎯 BEST PRACTICES ĐÃ ÁP DỤNG

### 1. Clean Architecture
```
Presentation Layer (API endpoints)
    ↓
Business Logic Layer (CRUD operations)
    ↓
Data Access Layer (SQLAlchemy models)
    ↓
Database
```

### 2. Dependency Injection
```python
# Tự động inject DB session
def endpoint(db: Session = Depends(get_db))

# Tự động check auth
def endpoint(current_user: User = Depends(get_current_user))
```

### 3. Separation of Concerns

| Layer | Responsibility |
|-------|---------------|
| **API** | HTTP handling, validation |
| **CRUD** | Database queries |
| **Models** | Database structure |
| **Schemas** | Data validation & serialization |
| **Core** | Configuration, security |

### 4. Security

- ✅ Password hashing (bcrypt)
- ✅ JWT tokens
- ✅ OAuth2 flow
- ✅ Authorization checks
- ✅ Input validation
- ✅ SQL injection prevention (ORM)

---

## 🔗 FILE DEPENDENCIES

```
main.py
├── api/api.py
│   ├── endpoints/auth.py
│   │   ├── crud/user.py
│   │   │   └── models/user.py
│   │   ├── schemas/user.py
│   │   ├── schemas/token.py
│   │   └── core/security.py
│   ├── endpoints/users.py
│   │   ├── crud/user.py
│   │   └── schemas/user.py
│   └── endpoints/activities.py
│       ├── crud/user_activity.py
│       │   └── models/user_activity.py
│       └── schemas/user_activity.py
├── api/dependencies.py
│   ├── db/session.py
│   ├── core/security.py
│   └── crud/user.py
└── core/config.py
```

---

## 📝 NEXT: MỞ RỘNG PROJECT

Khi thêm feature mới, follow cấu trúc này:

1. **Model** (`app/models/new_feature.py`)
   - Define database table

2. **Schema** (`app/schemas/new_feature.py`)
   - Define validation & serialization

3. **CRUD** (`app/crud/new_feature.py`)
   - Database operations

4. **Endpoint** (`app/api/endpoints/new_feature.py`)
   - API routes

5. **Register router** (`app/api/api.py`)
   - Include new router

---

## 💡 TIP: ĐỌC CODE THEO THỨ TỰ

**Cho người mới:**
1. `app/main.py` - Start here
2. `app/core/config.py` - Configuration
3. `app/models/user.py` - Database structure
4. `app/schemas/user.py` - Validation
5. `app/crud/user.py` - Database operations
6. `app/api/endpoints/auth.py` - API endpoints
7. `app/api/dependencies.py` - Authentication

**Understand flow:**
- Pick một endpoint (ví dụ: login)
- Follow từ endpoint → CRUD → model → database
- Hiểu từng bước xử lý

---

Chúc bạn học tốt! 🚀
