# 🔐 CƠ CHẾ LOGIN TRONG PROJECT

Giải thích chi tiết từng bước về authentication & authorization.

---

## 🎯 1. TỔNG QUAN

### **Công nghệ sử dụng:**
- ✅ **OAuth2 Password Flow** - Chuẩn authentication cho API
- ✅ **JWT (JSON Web Token)** - Stateless authentication
- ✅ **Bcrypt** - Password hashing
- ✅ **FastAPI OAuth2PasswordBearer** - Token extraction
- ✅ **Pydantic** - Data validation

### **Flow tổng quan:**
```
1. REGISTER → Hash password → Lưu vào DB
2. LOGIN → Verify password → Tạo JWT token → Return token
3. AUTHENTICATED REQUEST → Gửi token → Verify token → Access resource
```

---

## 📝 2. BƯỚC 1: ĐĂNG KÝ (REGISTER)

### **Endpoint:**
```
POST /api/v1/auth/register
```

### **Request:**
```json
{
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "password": "mypassword123",
  "bio": "Developer",
  "country": "VN"
}
```

### **Flow chi tiết:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT GỬI REQUEST                                       │
└─────────────────────────────────────────────────────────────┘
POST /api/v1/auth/register
Body: {
  "email": "user@example.com",
  "password": "mypassword123",  ← Plain text password
  ...
}

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 2. BACKEND VALIDATION (Pydantic)                            │
└─────────────────────────────────────────────────────────────┘
- Email đúng format? ✓
- Password >= 8 ký tự? ✓
- Full name không rỗng? ✓

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 3. CHECK EMAIL ĐÃ TỒN TẠI CHƯA                              │
└─────────────────────────────────────────────────────────────┘
SQL: SELECT * FROM users WHERE email = 'user@example.com'

IF exists → Return 400 "Email already registered"
IF not exists → Continue

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 4. HASH PASSWORD (Bcrypt)                                   │
└─────────────────────────────────────────────────────────────┘
Input:  "mypassword123"
        ↓
Bcrypt hash với salt (cost factor = 12)
        ↓
Output: "$2b$12$KIXn8.../9xRLrQYXU2koOe"

⚠️ KHÔNG BAO GIỜ LƯU PLAIN PASSWORD VÀO DB!

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 5. LƯU VÀO DATABASE                                         │
└─────────────────────────────────────────────────────────────┘
SQL: INSERT INTO users (
  email,
  full_name,
  hashed_password,           ← Hashed password
  is_active,
  is_superuser,
  country,
  bio,
  created_at
) VALUES (
  'user@example.com',
  'Nguyen Van A',
  '$2b$12$KIXn8.../9xRLrQYXU2koOe',
  TRUE,
  FALSE,
  'VN',
  'Developer',
  NOW()
)

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 6. RESPONSE                                                 │
└─────────────────────────────────────────────────────────────┘
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-10T10:00:00Z",
  "country": "VN",
  "bio": "Developer"
}
⚠️ KHÔNG TRẢ VỀ hashed_password!
```

### **Code:**

```python
# File: app/api/endpoints/auth.py

@router.post("/register", response_model=User, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Check email exists
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(400, "Email already registered")

    # 2. Create user (password will be hashed inside)
    user = crud_user.create(db, obj_in=user_in)
    return user


# File: app/crud/user.py

def create(db: Session, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        full_name=obj_in.full_name,
        hashed_password=get_password_hash(obj_in.password),  # ← Hash here
        bio=obj_in.bio,
        country=obj_in.country,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# File: app/core/security.py

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)  # Bcrypt hash
```

---

## 🔑 3. BƯỚC 2: ĐĂNG NHẬP (LOGIN)

### **Endpoint:**
```
POST /api/v1/auth/login
```

### **Request Format (OAuth2 Standard):**
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com    ← OAuth2 dùng "username" nhưng ta dùng email
password=mypassword123
```

### **Flow chi tiết:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT GỬI LOGIN REQUEST (OAuth2 Format)                │
└─────────────────────────────────────────────────────────────┘
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
Body: username=user@example.com&password=mypassword123

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 2. BACKEND NHẬN VIA OAuth2PasswordRequestForm               │
└─────────────────────────────────────────────────────────────┘
form_data = OAuth2PasswordRequestForm(
    username = "user@example.com",    ← Tự động parse
    password = "mypassword123"
)

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 3. TÌM USER TRONG DATABASE                                  │
└─────────────────────────────────────────────────────────────┘
SQL: SELECT * FROM users WHERE email = 'user@example.com'

Result: {
  id: 1,
  email: "user@example.com",
  hashed_password: "$2b$12$KIXn8.../9xRLrQYXU2koOe",
  is_active: true,
  is_superuser: false,
  ...
}

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 4. VERIFY PASSWORD (Bcrypt)                                 │
└─────────────────────────────────────────────────────────────┘
Input:
  Plain password: "mypassword123"
  Hashed password: "$2b$12$KIXn8.../9xRLrQYXU2koOe"

Bcrypt compare:
  ↓
verify_password("mypassword123", "$2b$12$KIXn8.../9xRLrQYXU2koOe")
  ↓
Result: TRUE ✓ (Password đúng)

IF FALSE → Return 401 "Incorrect email or password"

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 5. CHECK USER ACTIVE                                        │
└─────────────────────────────────────────────────────────────┘
IF user.is_active == FALSE:
  → Return 400 "Inactive user"

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 6. TẠO JWT ACCESS TOKEN                                     │
└─────────────────────────────────────────────────────────────┘

A. Chuẩn bị payload:
   data = {
     "sub": "user@example.com"  # subject = user identifier
   }

B. Tính expiration time:
   expire = utcnow() + timedelta(minutes=30)  # 30 minutes

   data = {
     "sub": "user@example.com",
     "exp": 1704067200  # Unix timestamp
   }

C. Encode JWT với SECRET_KEY:

   Header:
   {
     "alg": "HS256",       # Algorithm: HMAC SHA-256
     "typ": "JWT"          # Type: JWT
   }

   Payload:
   {
     "sub": "user@example.com",
     "exp": 1704067200
   }

   Signature:
   HMACSHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     SECRET_KEY
   )

   ↓

   Final JWT Token:
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA0MDY3MjAwfQ.SIGNATURE

   |         Header          |           Payload            |  Signature |
   |-------------------------|------------------------------|------------|

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 7. RESPONSE                                                 │
└─────────────────────────────────────────────────────────────┘
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

⚠️ Client LƯU TOKEN NÀY để dùng cho các request tiếp theo!
```

### **Code:**

```python
# File: app/api/endpoints/auth.py

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()  # ← OAuth2 form
):
    # 1. Authenticate (verify email + password)
    user = crud_user.authenticate(
        db,
        email=form_data.username,  # OAuth2 dùng "username"
        password=form_data.password
    )

    if not user:
        raise HTTPException(401, "Incorrect email or password")

    if not user.is_active:
        raise HTTPException(400, "Inactive user")

    # 2. Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # 3. Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# File: app/crud/user.py

def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    # 1. Find user
    user = get_by_email(db, email)
    if not user:
        return None

    # 2. Verify password
    if not verify_password(password, user.hashed_password):
        return None

    return user


# File: app/core/security.py

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # Add expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

---

## 🔓 4. BƯỚC 3: SỬ DỤNG TOKEN (AUTHENTICATED REQUEST)

### **Request Example:**
```
GET /api/v1/auth/me
Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Flow chi tiết:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT GỬI REQUEST VỚI TOKEN                             │
└─────────────────────────────────────────────────────────────┘
GET /api/v1/auth/me
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 2. FASTAPI ROUTE MATCHING                                   │
└─────────────────────────────────────────────────────────────┘
@router.get("/auth/me")
def read_current_user(
    current_user: User = Depends(get_current_user)  ← Dependency!
):
    return current_user

FastAPI nhận thấy dependency → Gọi get_current_user()

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 3. EXTRACT TOKEN TỪ HEADER (OAuth2PasswordBearer)          │
└─────────────────────────────────────────────────────────────┘
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

Tự động extract từ header:
"Authorization: Bearer eyJhbGci..."
                       ↑
                  Extract token

Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA0MDY3MjAwfQ.SIGNATURE"

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 4. DECODE & VERIFY TOKEN                                    │
└─────────────────────────────────────────────────────────────┘

A. Decode JWT:
   jwt.decode(
     token,
     SECRET_KEY,
     algorithms=["HS256"]
   )

   ↓

B. Verify signature:
   - Recalculate signature với SECRET_KEY
   - Compare với signature trong token
   - IF khác nhau → Token bị modify → Reject!

   ↓

C. Check expiration:
   current_time = utcnow()
   token_exp = payload["exp"]

   IF current_time > token_exp:
     → Token expired → Return 401

   ↓

D. Extract email:
   email = payload["sub"]  # "user@example.com"

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 5. QUERY USER TỪ DATABASE                                   │
└─────────────────────────────────────────────────────────────┘
SQL: SELECT * FROM users WHERE email = 'user@example.com'

Result: User object
{
  id: 1,
  email: "user@example.com",
  full_name: "Nguyen Van A",
  is_active: true,
  is_superuser: false,
  ...
}

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 6. VALIDATION CHECKS                                        │
└─────────────────────────────────────────────────────────────┘

A. User tồn tại?
   IF user is None:
     → Return 404 "User not found"

B. User active?
   IF user.is_active == FALSE:
     → Return 400 "Inactive user"

C. (Admin endpoint) Check is_superuser?
   IF endpoint requires admin AND user.is_superuser == FALSE:
     → Return 403 "Not enough privileges"

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 7. INJECT USER VÀO ENDPOINT                                 │
└─────────────────────────────────────────────────────────────┘
get_current_user() returns User object
   ↓
FastAPI inject vào parameter:
   current_user: User = <User object>
   ↓
Endpoint handler chạy:
   def read_current_user(current_user: User):
       return current_user  # User đã được verify!

         ↓

┌─────────────────────────────────────────────────────────────┐
│ 8. RESPONSE                                                 │
└─────────────────────────────────────────────────────────────┘
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-10T10:00:00Z",
  "country": "VN"
}
```

### **Code:**

```python
# File: app/api/dependencies.py

# OAuth2 scheme - Tự động extract token từ header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)  # ← Extract token
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decode token
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # 2. Get user from DB
    user = crud_user.get_by_email(db, email=email)
    if user is None:
        raise HTTPException(404, "User not found")

    # 3. Check active
    if not user.is_active:
        raise HTTPException(400, "Inactive user")

    return user


# File: app/core/security.py

def decode_access_token(token: str) -> Optional[str]:
    try:
        # Decode & verify JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None  # Invalid token
```

---

## 🔒 5. SECURITY FEATURES

### **A. Password Hashing (Bcrypt)**

**Tại sao dùng Bcrypt?**
- ✅ **Slow by design** - Khó brute force
- ✅ **Automatic salt** - Mỗi hash khác nhau dù password giống nhau
- ✅ **Cost factor** - Có thể tăng độ khó khi hardware mạnh hơn

**Example:**
```python
# Same password → Different hashes
password = "mypassword123"

hash1 = bcrypt.hash(password)
# → "$2b$12$KIXn8.../9xRLrQYXU2koOe"

hash2 = bcrypt.hash(password)
# → "$2b$12$ABC123.../xyz789XYZ"  ← KHÁC NHAU!

# But both verify correctly
bcrypt.verify(password, hash1)  # → True
bcrypt.verify(password, hash2)  # → True
```

**Config:**
```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12  # Cost factor (default=12)
)
```

---

### **B. JWT Token Security**

**Thành phần JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA0MDY3MjAwfQ.SIGNATURE

|         Header          |           Payload            |  Signature |
```

**1. Header:**
```json
{
  "alg": "HS256",  // Algorithm: HMAC SHA-256
  "typ": "JWT"     // Type: JSON Web Token
}
```

**2. Payload:**
```json
{
  "sub": "user@example.com",  // Subject: user identifier
  "exp": 1704067200           // Expiration: Unix timestamp
}
```

**3. Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY  // ← SECRET này phải giữ bí mật!
)
```

**Tại sao an toàn?**
- ✅ **Tamper-proof** - Không thể modify payload mà không có SECRET_KEY
- ✅ **Expiration** - Token tự hết hạn sau 30 phút
- ✅ **Stateless** - Server không cần lưu session
- ✅ **Self-contained** - Chứa đủ info để authenticate

**Tại sao KHÔNG an toàn tuyệt đối?**
- ⚠️ **Token theft** - Nếu bị steal, attacker dùng được đến khi expire
- ⚠️ **Không thể revoke** - Một khi issue, không thu hồi được (cần blacklist)
- ⚠️ **Payload visible** - Base64 decode được (không encrypt, chỉ sign)

---

### **C. OAuth2 Password Flow**

**Chuẩn OAuth2:**
- ✅ Form-encoded request (not JSON)
- ✅ Field "username" & "password"
- ✅ Return "access_token" & "token_type"
- ✅ Header "Authorization: Bearer {token}"

**Config:**
```python
# File: app/core/config.py

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

⚠️ **PRODUCTION:** Dùng secret key mạnh hơn, load từ env variable!

---

## 🧪 6. TESTING

### **Test 1: Register User**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "password123",
    "country": "VN"
  }'
```

**Response:**
```json
{
  "id": 2,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-10T10:30:00Z",
  "country": "VN"
}
```

---

### **Test 2: Login**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzA0MDY5MjAwfQ.xxx",
  "token_type": "bearer"
}
```

---

### **Test 3: Use Token**

```bash
# Lưu token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get current user
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": 2,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-10T10:30:00Z",
  "country": "VN"
}
```

---

### **Test 4: Wrong Password**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=wrongpass"
```

**Response:**
```json
{
  "detail": "Incorrect email or password"
}
```
**Status:** 401 Unauthorized

---

### **Test 5: Invalid Token**

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer invalid_token_xyz"
```

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```
**Status:** 401 Unauthorized

---

### **Test 6: Expired Token**

```bash
# Sau 30 phút (ACCESS_TOKEN_EXPIRE_MINUTES=30)
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $EXPIRED_TOKEN"
```

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```
**Status:** 401 Unauthorized

---

## 📊 7. FLOW DIAGRAM

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │
       │ 1. POST /auth/register
       │    Body: {email, password, ...}
       ├──────────────────────────────────────►┌──────────────┐
       │                                       │   BACKEND    │
       │                                       └──────┬───────┘
       │                                              │
       │                                              │ Hash password (bcrypt)
       │                                              │ INSERT INTO users
       │                                              │
       │ 2. Response: User object                    │
       │◄────────────────────────────────────────────┤
       │                                              │
       │                                              │
       │ 3. POST /auth/login                         │
       │    Body: username=email&password=pass       │
       ├──────────────────────────────────────►      │
       │                                              │
       │                                              │ SELECT user WHERE email
       │                                              │ Verify password (bcrypt)
       │                                              │ Create JWT token
       │                                              │
       │ 4. Response: {access_token, token_type}     │
       │◄────────────────────────────────────────────┤
       │                                              │
       │ 💾 SAVE TOKEN                               │
       │                                              │
       │                                              │
       │ 5. GET /auth/me                             │
       │    Header: Authorization: Bearer {token}    │
       ├──────────────────────────────────────►      │
       │                                              │
       │                                              │ Extract token from header
       │                                              │ Decode & verify JWT
       │                                              │ SELECT user WHERE email
       │                                              │ Check is_active
       │                                              │ Return user object
       │                                              │
       │ 6. Response: User info                      │
       │◄────────────────────────────────────────────┤
       │                                              │
       │                                              │
       │ 7. GET /admin/reports/* (Admin endpoint)    │
       │    Header: Authorization: Bearer {token}    │
       ├──────────────────────────────────────►      │
       │                                              │
       │                                              │ Extract & verify token
       │                                              │ SELECT user
       │                                              │ Check is_superuser
       │                                              │
       │                                              │ IF is_superuser = FALSE:
       │                                              │   → 403 Forbidden
       │                                              │
       │                                              │ IF is_superuser = TRUE:
       │                                              │   → Process request
       │                                              │
       │ 8. Response: Report data (if admin)         │
       │    OR 403 Forbidden (if not admin)          │
       │◄────────────────────────────────────────────┤
       │                                              │
└──────┘                                        └──────────────┘
```

---

## 🎯 8. TÓM TẮT

### **Công nghệ:**
- ✅ **OAuth2 Password Flow** - Chuẩn API authentication
- ✅ **JWT Token** - Stateless, self-contained
- ✅ **Bcrypt** - Secure password hashing
- ✅ **FastAPI Dependencies** - Elegant authentication check

### **Security Features:**
- ✅ Password hashing (never store plain text)
- ✅ Token expiration (30 minutes)
- ✅ Token signature verification
- ✅ Active user check
- ✅ Admin role check (is_superuser)

### **Flow:**
1. **Register** → Hash password → Save to DB
2. **Login** → Verify password → Create JWT → Return token
3. **Authenticated Request** → Verify token → Inject user → Process

### **Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Key Points:**
- 🔐 Token chứa email trong payload (`sub` field)
- 🔐 Signature verify token không bị modify
- 🔐 Expiration tự động invalidate old tokens
- 🔐 Stateless - server không lưu session
- 🔐 Admin check bằng `is_superuser` field

---

Chúc bạn hiểu rõ cơ chế login! 🚀
