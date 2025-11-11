# 📚 HƯỚNG DẪN CHI TIẾT: ADMIN REPORTS API

---

## 🎯 1. CÁC API LẤY SỐ LƯỢNG USER MỚI

### **A. User Mới Hôm Nay**

**Endpoint:**
```
GET /api/v1/admin/reports/stats/new-users?period=today
```

**Authorization:**
```
Headers: Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total": 50,
  "period": "today",
  "start_date": "2024-01-10T00:00:00Z",
  "end_date": "2024-01-10T23:59:59Z"
}
```

**Cách hoạt động:**
```python
# 1. Backend nhận request với period="today"
# 2. Tính khoảng thời gian:
start_date = datetime.now().replace(hour=0, minute=0, second=0)  # 00:00:00 hôm nay
end_date = datetime.now().replace(hour=23, minute=59, second=59) # 23:59:59 hôm nay

# 3. Query database:
SELECT COUNT(*) FROM users
WHERE created_at >= '2024-01-10 00:00:00'
  AND created_at <= '2024-01-10 23:59:59'

# 4. Return kết quả
```

**Use case:**
- Dashboard admin: "Hôm nay có 50 user mới đăng ký"
- Real-time monitoring
- Alert nếu số user mới giảm đột ngột

---

### **B. User Mới Hôm Qua**

**Endpoint:**
```
GET /api/v1/admin/reports/stats/new-users?period=yesterday
```

**Response:**
```json
{
  "total": 45,
  "period": "yesterday",
  "start_date": "2024-01-09T00:00:00Z",
  "end_date": "2024-01-09T23:59:59Z"
}
```

**Cách hoạt động:**
```python
# 1. Tính ngày hôm qua
yesterday = datetime.now() - timedelta(days=1)
start_date = yesterday.replace(hour=0, minute=0, second=0)
end_date = yesterday.replace(hour=23, minute=59, second=59)

# 2. Query
SELECT COUNT(*) FROM users
WHERE created_at >= '2024-01-09 00:00:00'
  AND created_at <= '2024-01-09 23:59:59'
```

**Use case:**
- So sánh: "Hôm nay +10% so với hôm qua (50 vs 45)"
- Daily report

---

### **C. User Mới 7 Ngày Gần Đây**

**Endpoint:**
```
GET /api/v1/admin/reports/stats/new-users?period=last_7_days
```

**Response:**
```json
{
  "total": 300,
  "period": "last_7_days",
  "start_date": "2024-01-03T14:30:00Z",
  "end_date": "2024-01-10T14:30:00Z"
}
```

**Cách hoạt động:**
```python
# 1. Tính khoảng thời gian
end_date = datetime.now()                    # Bây giờ
start_date = end_date - timedelta(days=7)    # 7 ngày trước

# 2. Query
SELECT COUNT(*) FROM users
WHERE created_at >= '2024-01-03 14:30:00'
  AND created_at <= '2024-01-10 14:30:00'
```

**Use case:**
- Weekly report
- Growth tracking
- Marketing campaign effectiveness

---

### **D. User Mới 30 Ngày**

**Endpoint:**
```
GET /api/v1/admin/reports/stats/new-users?period=last_30_days
```

**Response:**
```json
{
  "total": 1200,
  "period": "last_30_days",
  "start_date": "2023-12-11T14:30:00Z",
  "end_date": "2024-01-10T14:30:00Z"
}
```

**Use case:**
- Monthly report
- Long-term trend analysis

---

## 🌍 2. API LẤY USER THEO QUỐC GIA

### **A. Thống Kê Tất Cả Quốc Gia**

**Endpoint:**
```
GET /api/v1/admin/reports/stats/by-country
```

**Response:**
```json
[
  {
    "country": "VN",
    "total_users": 1500,
    "active_users": 1200,
    "percentage": 35.5
  },
  {
    "country": "US",
    "total_users": 800,
    "active_users": 700,
    "percentage": 18.9
  },
  {
    "country": "JP",
    "total_users": 600,
    "active_users": 550,
    "percentage": 14.2
  }
]
```

**Cách hoạt động:**
```python
# 1. Lấy tổng số user
total_all_users = SELECT COUNT(*) FROM users  # Ví dụ: 4225

# 2. Group by country và đếm
SELECT
    country,
    COUNT(*) as total_users,
    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users
FROM users
WHERE country IS NOT NULL
GROUP BY country
ORDER BY total_users DESC

# Kết quả:
# country | total_users | active_users
# --------|-------------|-------------
# VN      | 1500        | 1200
# US      | 800         | 700
# JP      | 600         | 550

# 3. Tính phần trăm
for each country:
    percentage = (total_users / total_all_users) * 100
    # VN: (1500 / 4225) * 100 = 35.5%
```

**Use case:**
- Geographic analytics
- Market penetration analysis
- Localization planning
- Chart pie/bar chart phân bố quốc gia

---

### **B. Danh Sách User Từ 1 Quốc Gia Cụ Thể**

**Endpoint:**
```
GET /api/v1/admin/reports/users/country/VN?skip=0&limit=50
```

**Parameters:**
- `VN` = country code trong URL path
- `skip` = pagination offset (default: 0)
- `limit` = max records (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "email": "nguyen@example.com",
    "full_name": "Nguyen Van A",
    "country": "VN",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T10:00:00Z",
    "bio": "Developer"
  },
  {
    "id": 5,
    "email": "tran@example.com",
    "full_name": "Tran Thi B",
    "country": "VN",
    ...
  }
]
```

**Cách hoạt động:**
```python
# 1. Nhận country code từ URL: "VN"
# 2. Query database
SELECT * FROM users
WHERE country = 'VN'
ORDER BY id
LIMIT 50 OFFSET 0

# Nếu muốn page 2:
# skip=50, limit=50
# → LIMIT 50 OFFSET 50
```

**Use case:**
- Export danh sách user theo quốc gia
- Country-specific campaign
- Localized email marketing

---

## 🔥 3. DYNAMIC FILTERING (GRAPHQL-LIKE)

### **Endpoint Chính:**
```
GET /api/v1/admin/reports/users/filter?{dynamic_params}
```

### **🎛️ Tất Cả Parameters (TẤT CẢ OPTIONAL):**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `country` | string | Mã quốc gia (2 ký tự) | `country=VN` |
| `is_active` | boolean | Active status | `is_active=true` |
| `is_superuser` | boolean | Admin role | `is_superuser=false` |
| `days` | integer | User đăng ký trong N ngày | `days=7` |
| `skip` | integer | Pagination offset | `skip=0` |
| `limit` | integer | Max records (1-1000) | `limit=100` |

---

### **💡 VÍ DỤ THỰC TẾ:**

#### **Example 1: Lấy User Từ Vietnam**
```bash
GET /api/v1/admin/reports/users/filter?country=VN
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE country = 'VN'
LIMIT 100 OFFSET 0
```

**Response:** List 100 users từ VN

---

#### **Example 2: Active Users Từ Vietnam**
```bash
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE country = 'VN'
  AND is_active = TRUE
LIMIT 100 OFFSET 0
```

**Response:** Chỉ active users từ VN

---

#### **Example 3: User Đăng Ký Trong 7 Ngày Từ Vietnam**
```bash
GET /api/v1/admin/reports/users/filter?country=VN&days=7
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE country = 'VN'
  AND created_at >= '2024-01-03 14:30:00'  -- 7 ngày trước
LIMIT 100 OFFSET 0
```

**Response:** Users mới từ VN trong 7 ngày

---

#### **Example 4: Tất Cả Admin Users**
```bash
GET /api/v1/admin/reports/users/filter?is_superuser=true
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE is_superuser = TRUE
LIMIT 100 OFFSET 0
```

**Response:** Danh sách tất cả admin

---

#### **Example 5: Inactive Users Cần Re-engage**
```bash
GET /api/v1/admin/reports/users/filter?is_active=false&days=30
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE is_active = FALSE
  AND created_at >= '2023-12-11 14:30:00'  -- 30 ngày trước
LIMIT 100 OFFSET 0
```

**Use case:** Tìm users inactive để gửi email re-engagement

---

#### **Example 6: Combine TẤT CẢ Filters**
```bash
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true&days=7&limit=50
```

**SQL Generated:**
```sql
SELECT * FROM users
WHERE country = 'VN'
  AND is_active = TRUE
  AND created_at >= '2024-01-03 14:30:00'
LIMIT 50 OFFSET 0
```

**Response:** 50 active users từ VN đăng ký trong 7 ngày

---

### **🚀 Cách Hoạt Động Dynamic Filtering:**

```python
def get_users_with_filters(
    db: Session,
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    days: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    # 1. Bắt đầu với base query
    query = db.query(User)

    # 2. Build filters list
    filters = []

    # 3. CHỈ ADD filter nào có giá trị (dynamic!)
    if country is not None:
        filters.append(User.country == country)

    if is_active is not None:
        filters.append(User.is_active == is_active)

    if is_superuser is not None:
        filters.append(User.is_superuser == is_superuser)

    if days is not None:
        date_threshold = datetime.now() - timedelta(days=days)
        filters.append(User.created_at >= date_threshold)

    # 4. Apply tất cả filters với AND
    if filters:
        query = query.filter(and_(*filters))

    # 5. Apply pagination
    return query.offset(skip).limit(limit).all()
```

**Tại sao gọi là "GraphQL-like"?**
- ✅ Flexible filtering
- ✅ Client chọn fields cần thiết
- ✅ Combine nhiều điều kiện
- ✅ Không cần tạo endpoint riêng cho mỗi combo

---

## 🔐 4. PHÂN QUYỀN: ADMIN vs USER

### **A. CƠ CHẾ PHÂN QUYỀN**

```
┌─────────────────────────────────────┐
│         DATABASE SCHEMA             │
├─────────────────────────────────────┤
│ users table:                        │
│ - id                                │
│ - email                             │
│ - hashed_password                   │
│ - is_active       (boolean)         │
│ - is_superuser    (boolean) ← KEY!  │
│ - created_at                        │
│ - country                           │
└─────────────────────────────────────┘
```

**Field quan trọng:**
- `is_superuser = TRUE` → Admin
- `is_superuser = FALSE` → User thường

---

### **B. FLOW LOGIN - ADMIN vs USER**

#### **🔹 BƯỚC 1: Đăng Nhập (GIỐNG NHAU)**

**Endpoint:**
```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Backend xử lý:**
```python
# 1. Tìm user trong database
user = db.query(User).filter(User.email == email).first()

# 2. Verify password
if not verify_password(plain_password, user.hashed_password):
    raise HTTPException(401, "Invalid password")

# 3. Check active
if not user.is_active:
    raise HTTPException(400, "Inactive user")

# 4. Tạo JWT token (GỒM is_superuser trong payload)
access_token = create_access_token(
    data={"sub": user.email}  # Email trong token
)

# 5. Return token
return {
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
}
```

**Response (GIỐNG NHAU cho admin và user):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA1MDgwMDAwfQ.xxx",
  "token_type": "bearer"
}
```

---

#### **🔹 BƯỚC 2: Sử Dụng Token**

**Admin Token Example:**
```
Authorization: Bearer eyJhbGci...
```

**Decode Token → Lấy Email:**
```python
# Backend decode token
email = decode_access_token(token)  # "admin@example.com"

# Query user từ database
user = db.query(User).filter(User.email == email).first()

# user.is_superuser = True  ← Admin!
```

**User Token Example:**
```
Authorization: Bearer eyJhbGci...
```

**Decode Token:**
```python
email = decode_access_token(token)  # "user@example.com"
user = db.query(User).filter(User.email == email).first()

# user.is_superuser = False  ← User thường!
```

---

### **C. PHÂN QUYỀN ENDPOINTS**

#### **🟢 Public Endpoints (Không cần login)**

```python
# Không cần token
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /               # Health check
GET  /docs           # Swagger UI
```

---

#### **🟡 Protected Endpoints (Cần login - Admin & User đều OK)**

```python
# Dependency: get_current_user
GET  /api/v1/auth/me                          # Xem profile của chính mình
GET  /api/v1/users/{user_id}                  # Xem user (nếu user_id = current_user.id)
PUT  /api/v1/users/{user_id}                  # Update (chỉ update chính mình)
GET  /api/v1/users/{user_id}/activities       # Xem activities của chính mình
POST /api/v1/users/{user_id}/activities       # Log activity
```

**Ví dụ Code:**
```python
@router.get("/auth/me", response_model=User)
def read_current_user(
    current_user: User = Depends(get_current_user)  # ← Dependency
):
    # current_user đã được inject
    # Có thể là admin hoặc user thường
    return current_user
```

**Flow:**
```
1. Client gửi: GET /api/v1/auth/me
   Header: Authorization: Bearer {token}

2. FastAPI gọi get_current_user():
   - Decode token → email
   - Query user từ DB
   - Check is_active
   - Return user object

3. Endpoint nhận user object → Return user info
```

---

#### **🔴 Admin-Only Endpoints (CHỈ is_superuser=true)**

```python
# Dependency: get_current_active_superuser
GET  /api/v1/admin/reports/stats/overall               # Admin stats
GET  /api/v1/admin/reports/stats/new-users             # New users report
GET  /api/v1/admin/reports/stats/by-country            # Country stats
GET  /api/v1/admin/reports/stats/daily                 # Daily stats
GET  /api/v1/admin/reports/users/filter                # Dynamic filtering
GET  /api/v1/admin/reports/users/country/{country}     # Users by country
DELETE /api/v1/users/{user_id}                         # Delete user (admin only)
```

**Ví dụ Code:**
```python
@router.get("/admin/reports/stats/overall")
def get_overall_statistics(
    current_user: User = Depends(get_current_active_superuser)  # ← Admin check
):
    # Chỉ admin mới vào được đây
    return get_overall_stats(db)
```

**Flow:**
```
1. Client gửi: GET /api/v1/admin/reports/stats/overall
   Header: Authorization: Bearer {token}

2. FastAPI gọi get_current_active_superuser():
   - Decode token → email
   - Query user từ DB
   - Check is_active
   - CHECK is_superuser ← KEY!

   if not user.is_superuser:
       raise HTTPException(403, "Not enough privileges")

   - Return user object

3. Endpoint nhận admin user → Thực thi logic
```

---

### **D. SO SÁNH ADMIN vs USER**

| Feature | User Thường<br>(is_superuser=false) | Admin<br>(is_superuser=true) |
|---------|-------------------------------------|------------------------------|
| **Login** | ✅ Giống nhau | ✅ Giống nhau |
| **Token Format** | ✅ Giống nhau | ✅ Giống nhau |
| **Xem profile chính mình** | ✅ Yes | ✅ Yes |
| **Update profile chính mình** | ✅ Yes | ✅ Yes |
| **Xem activities chính mình** | ✅ Yes | ✅ Yes |
| **Xem profile user khác** | ❌ No | ✅ Yes |
| **Update user khác** | ❌ No | ✅ Yes |
| **Delete user** | ❌ No | ✅ Yes |
| **Admin reports** | ❌ No (403 error) | ✅ Yes |
| **View all users** | ❌ No | ✅ Yes |
| **Filter users** | ❌ No | ✅ Yes |
| **Country statistics** | ❌ No | ✅ Yes |

---

### **E. DEPENDENCIES COMPARISON**

```python
# File: app/api/dependencies.py

# 1. Get current user (Admin + User đều OK)
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    email = decode_access_token(token)
    user = crud_user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(404, "User not found")
    if not user.is_active:
        raise HTTPException(400, "Inactive user")

    return user  # ← Return bất kể admin hay user


# 2. Get current ADMIN (CHỈ admin)
def get_current_active_superuser(
    current_user: User = Depends(get_current_user)  # ← Reuse get_current_user
) -> User:
    # Check thêm is_superuser
    if not current_user.is_superuser:
        raise HTTPException(
            403,
            "The user doesn't have enough privileges"
        )

    return current_user  # ← Return CHỈ KHI là admin
```

---

### **F. TEST PHÂN QUYỀN**

#### **Test 1: User thường gọi admin endpoint**

```bash
# 1. Login với user thường
POST /api/v1/auth/login
Body: {
  "username": "user@example.com",  # is_superuser = false
  "password": "password123"
}

Response: {
  "access_token": "user_token_xxx",
  "token_type": "bearer"
}

# 2. Thử gọi admin endpoint
GET /api/v1/admin/reports/stats/overall
Header: Authorization: Bearer user_token_xxx

# 3. Response: ERROR!
{
  "detail": "The user doesn't have enough privileges"
}
Status: 403 Forbidden
```

---

#### **Test 2: Admin gọi admin endpoint**

```bash
# 1. Login với admin
POST /api/v1/auth/login
Body: {
  "username": "admin@admin.com",  # is_superuser = true
  "password": "admin123"
}

Response: {
  "access_token": "admin_token_yyy",
  "token_type": "bearer"
}

# 2. Gọi admin endpoint
GET /api/v1/admin/reports/stats/overall
Header: Authorization: Bearer admin_token_yyy

# 3. Response: SUCCESS!
{
  "total_users": 10000,
  "active_users": 8000,
  "inactive_users": 2000,
  "new_today": 50,
  "new_yesterday": 45,
  "new_last_7_days": 300,
  "total_countries": 25
}
Status: 200 OK
```

---

### **G. CÁCH TẠO ADMIN USER**

#### **Option 1: SQL Direct**
```sql
-- Set user hiện tại thành admin
UPDATE users SET is_superuser = true WHERE email = 'user@example.com';

-- Verify
SELECT email, is_superuser FROM users WHERE email = 'user@example.com';
```

#### **Option 2: Script Python**
```bash
python create_admin.py --email admin@admin.com --password admin123
```

#### **Option 3: Khi Register**
```python
# Trong code (không khuyến khích cho production)
user = User(
    email="admin@example.com",
    hashed_password=get_password_hash("password"),
    is_superuser=True  # ← Set admin ngay khi tạo
)
```

---

## 🎯 5. USE CASES THỰC TẾ

### **Use Case 1: Dashboard Admin**

```bash
# 1. Lấy tổng quan
GET /api/v1/admin/reports/stats/overall
→ Hiển thị: Total users, Active users, New today, etc.

# 2. Chart growth 7 ngày
GET /api/v1/admin/reports/stats/daily?days=7
→ Vẽ line chart: new_users theo ngày

# 3. Pie chart quốc gia
GET /api/v1/admin/reports/stats/by-country
→ Vẽ pie chart: % users theo country
```

---

### **Use Case 2: Marketing Campaign Analysis**

```bash
# So sánh trước/sau campaign
GET /api/v1/admin/reports/stats/new-users?period=last_7_days
# Response: {"total": 300}

GET /api/v1/admin/reports/stats/new-users?period=last_30_days
# Response: {"total": 800}

# Tính growth rate
weekly_avg = 300 / 7 = 43 users/day
monthly_avg = 800 / 30 = 27 users/day
growth = (43 - 27) / 27 * 100 = +59% 🚀
```

---

### **Use Case 3: User Segmentation**

```bash
# Segment 1: Active users từ VN (gửi promotion VN)
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true

# Segment 2: Inactive users cần re-engage
GET /api/v1/admin/reports/users/filter?is_active=false&days=30

# Segment 3: New users cần onboarding
GET /api/v1/admin/reports/users/filter?days=7&is_active=true
```

---

### **Use Case 4: Security Audit**

```bash
# Xem tất cả admin users
GET /api/v1/admin/reports/users/filter?is_superuser=true

# Check admin mới được tạo
GET /api/v1/admin/reports/users/filter?is_superuser=true&days=30
```

---

## 📋 6. TÓM TẮT NHANH

### **APIs chính:**
1. ✅ `GET /admin/reports/stats/new-users?period=` - User mới theo period
2. ✅ `GET /admin/reports/stats/by-country` - Phân bố quốc gia
3. ✅ `GET /admin/reports/users/filter?{params}` - Dynamic filtering (GraphQL-like)
4. ✅ `GET /admin/reports/users/country/{country}` - Users từ 1 quốc gia
5. ✅ `GET /admin/reports/stats/overall` - Tổng quan hệ thống
6. ✅ `GET /admin/reports/stats/daily?days=` - Daily statistics

### **Phân quyền:**
- 🔐 Login giống nhau (admin + user)
- 🔐 Token format giống nhau
- 🔐 Phân biệt bằng `is_superuser` field trong DB
- 🔐 Admin endpoints dùng `get_current_active_superuser` dependency
- 🔐 User thường gọi admin endpoint → 403 Forbidden

### **Dynamic Filtering:**
- ✅ Combine nhiều điều kiện: country, is_active, is_superuser, days
- ✅ Tất cả parameters optional
- ✅ Build SQL query động (chỉ add filter nào có giá trị)
- ✅ Giống GraphQL flexibility

---

Chúc bạn sử dụng thành công! 🚀
